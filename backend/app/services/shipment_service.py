"""
app/services/shipment_service.py

FIXED: Shipment → Order status sync is now guaranteed on every update.
- Uses ORM .refresh() after every commit
- Validates transitions
- Returns synced order status in response
- Full debug logging
"""

from __future__ import annotations

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.shipment import Shipment
from app.repositories.shipment_repository import ShipmentRepository
from app.schemas.shipment import (
    ShipmentCreate,
    ShipmentDetail,
    ShipmentListItem,
    ShipmentRead,
    ShipmentStats,
    ShipmentStatus,
    ShipmentStatusUpdate,
)

# ── Shipment → Order status mapping ───────────────────────────────────────────
SHIPMENT_TO_ORDER_STATUS: dict[str, str] = {
    "PENDING":          "CONFIRMED",
    "SHIPPED":          "SHIPPED",
    "OUT_FOR_DELIVERY": "SHIPPED",
    "DELIVERED":        "DELIVERED",
    "FAILED":           "CONFIRMED",
    "RETURNED":         "RETURNED",
}

# ── Valid transitions ─────────────────────────────────────────────────────────
VALID_TRANSITIONS: dict[str, set[str]] = {
    "PENDING":          {"SHIPPED", "FAILED"},
    "SHIPPED":          {"OUT_FOR_DELIVERY", "FAILED", "RETURNED"},
    "OUT_FOR_DELIVERY": {"DELIVERED", "FAILED", "RETURNED"},
    "DELIVERED":        set(),
    "FAILED":           {"SHIPPED"},
    "RETURNED":         set(),
}


def _normalize_status(value) -> str:
    """Extract string value from enum or plain string, uppercase."""
    if hasattr(value, "value"):
        return str(value.value).upper()
    return str(value).upper()


class ShipmentService:

    # ── Create Shipment ───────────────────────────────────────────────────────
    @staticmethod
    def create_shipment(
        db: Session, order_id: int, data: ShipmentCreate
    ) -> ShipmentRead:

        # Guard: no duplicate shipment per order
        existing = ShipmentRepository.get_by_order(db, order_id)
        if existing:
            raise HTTPException(
                status_code=409,
                detail=f"Shipment already exists for order {order_id}",
            )

        # Guard: unique tracking number
        dup = ShipmentRepository.get_by_tracking(db, data.tracking_number)
        if dup:
            raise HTTPException(
                status_code=409,
                detail=f"Tracking number '{data.tracking_number}' already used",
            )

        shipment = ShipmentRepository.create(db, order_id, data)

        # Sync order → SHIPPED on shipment creation
        ShipmentService._sync_order_status(db, order_id, "SHIPPED")

        db.refresh(shipment)

        print(f"[ShipmentService] Shipment created for order {order_id} "
              f"| tracking={data.tracking_number} | order synced → SHIPPED")

        return ShipmentRead.model_validate(shipment)

    # ── Get Shipment by Order ─────────────────────────────────────────────────
    @staticmethod
    def get_shipment_by_order(db: Session, order_id: int) -> ShipmentDetail:
        shipment = ShipmentRepository.get_by_order(db, order_id)

        if not shipment:
            raise HTTPException(404, f"No shipment for order {order_id}")

        from app.models.order import Order
        order = db.query(Order).filter(Order.id == order_id).first()

        detail = ShipmentDetail.model_validate(shipment)

        if order:
            detail.order_status = order.status
            detail.user_id = order.user_id

        return detail

    # ── Get Shipment by ID ────────────────────────────────────────────────────
    @staticmethod
    def get_shipment_by_id(db: Session, shipment_id: int) -> ShipmentRead:
        shipment = ShipmentRepository.get_by_id(db, shipment_id)

        if not shipment:
            raise HTTPException(404, f"Shipment {shipment_id} not found")

        return ShipmentRead.model_validate(shipment)

    # ── CORE: Update Shipment Status ──────────────────────────────────────────
    @staticmethod
    def update_shipment_status(
        db: Session,
        tracking_number: str,
        data: ShipmentStatusUpdate,
    ) -> dict:
        """
        Updates shipment status and ALWAYS syncs order.status.

        Returns a dict with full shipment data + synced_order_status
        so the frontend can update both panels from one API call.
        """
        # 1. Fetch shipment (fresh from DB)
        shipment = ShipmentRepository.get_by_tracking(db, tracking_number)

        if not shipment:
            raise HTTPException(
                status_code=404,
                detail=f"Shipment with tracking '{tracking_number}' not found",
            )

        current_status = shipment.shipment_status
        new_status     = _normalize_status(data.status)

        print(f"[ShipmentService] update_shipment_status called | "
              f"tracking={tracking_number} | {current_status} → {new_status}")

        # 2. Validate transition
        allowed = VALID_TRANSITIONS.get(current_status, set())
        if new_status not in allowed:
            raise HTTPException(
                status_code=422,
                detail=(
                    f"Invalid status transition: {current_status} → {new_status}. "
                    f"Allowed: {sorted(allowed) or 'none (terminal state)'}"
                ),
            )

        order_id = shipment.order_id

        # 3. Update shipment via repository (calls SP + commits)
        updated_shipment = ShipmentRepository.update_status(
            db, tracking_number, new_status
        )

        # 4. ALWAYS sync order status (this is the critical fix)
        order_status = SHIPMENT_TO_ORDER_STATUS.get(new_status)

        if order_status:
            updated_order = ShipmentService._sync_order_status(
                db, order_id, order_status
            )
            synced_order_status = updated_order.status if updated_order else order_status
        else:
            synced_order_status = None

        # 5. Final refresh to ensure we return latest DB state
        db.refresh(updated_shipment)

        print(f"[ShipmentService] Shipment updated: {current_status} → {updated_shipment.shipment_status}")
        print(f"[ShipmentService] Order {order_id} synced → {synced_order_status}")

        # 6. Return full response dict (router will pass this straight to client)
        return {
            # Shipment fields
            "id":                  updated_shipment.id,
            "order_id":            updated_shipment.order_id,
            "courier_name":        updated_shipment.courier_name,
            "tracking_number":     updated_shipment.tracking_number,
            "shipment_status":     updated_shipment.shipment_status,
            "tracking_url":        updated_shipment.tracking_url,
            "shipping_label_url":  updated_shipment.shipping_label_url,
            "estimated_delivery":  (
                str(updated_shipment.estimated_delivery)
                if updated_shipment.estimated_delivery else None
            ),
            "shipped_at":          updated_shipment.shipped_at,
            "delivered_at":        updated_shipment.delivered_at,
            "created_at":          updated_shipment.created_at,
            "updated_at":          updated_shipment.updated_at,
            # Synced order info — frontend uses this to update order panel immediately
            "synced_order_status": synced_order_status,
            "order": {
                "id":     order_id,
                "status": synced_order_status,
            },
        }

    # ── List Shipments ────────────────────────────────────────────────────────
    @staticmethod
    def list_shipments(
        db: Session,
        status_filter: ShipmentStatus | None = None,
        order_id: int | None = None,
        courier_name: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[ShipmentListItem]:

        shipments = ShipmentRepository.list_all(
            db, status_filter, order_id, courier_name, skip, limit
        )

        return [ShipmentListItem.model_validate(s) for s in shipments]

    # ── Stats ─────────────────────────────────────────────────────────────────
    @staticmethod
    def get_stats(db: Session) -> ShipmentStats:
        counts = ShipmentRepository.count_by_status(db)
        total  = ShipmentRepository.total_count(db)

        return ShipmentStats(
            total            = total,
            pending          = counts.get("PENDING", 0),
            shipped          = counts.get("SHIPPED", 0),
            out_for_delivery = counts.get("OUT_FOR_DELIVERY", 0),
            delivered        = counts.get("DELIVERED", 0),
            failed           = counts.get("FAILED", 0),
            returned         = counts.get("RETURNED", 0),
        )

    # ── PRIVATE: Sync Order Status ────────────────────────────────────────────
    @staticmethod
    def _sync_order_status(db: Session, order_id: int, new_order_status: str):
        """
        Directly updates orders.status via ORM (bypasses SP to avoid conflicts).
        Always commits and refreshes so subsequent reads see the new value.
        """
        from app.models.order import Order

        # Fetch fresh order object — never reuse a stale reference
        order = db.query(Order).filter(Order.id == order_id).first()

        if not order:
            print(f"[ShipmentService] WARNING: Order {order_id} not found for sync")
            return None

        old_status  = order.status
        order.status = new_order_status

        # Commit the order change
        db.add(order)
        db.commit()

        # Refresh so the object reflects the committed state
        db.refresh(order)

        print(f"[ShipmentService] _sync_order_status: order {order_id} "
              f"{old_status} → {order.status}")

        return order