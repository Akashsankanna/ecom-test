"""
app/repositories/shipment_repository.py

All DB operations for the shipment module.
KEY FIX: update_status accepts both ShipmentStatus enum AND plain string.
"""

from __future__ import annotations

from typing import List, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.models.shipment import Shipment
from app.schemas.shipment import ShipmentCreate, ShipmentStatus


class ShipmentRepository:

    # ── Create ─────────────────────────────────────────────────────────────
    @staticmethod
    def create(db: Session, order_id: int, data: ShipmentCreate) -> Shipment:
        """
        Calls sp_create_shipment(order_id, courier_name, tracking_number, estimated_delivery).
        SP inserts shipment with status='SHIPPED' and sets shipped_at = NOW().
        """
        db.execute(
            text(
                "CALL sp_create_shipment("
                ":order_id, :courier_name, :tracking_number, :estimated_delivery"
                ")"
            ),
            {
                "order_id":           order_id,
                "courier_name":       data.courier_name,
                "tracking_number":    data.tracking_number,
                "estimated_delivery": data.estimated_delivery,
            },
        )
        db.commit()

        return (
            db.query(Shipment)
            .filter(Shipment.tracking_number == data.tracking_number)
            .first()
        )

    # ── Get by order ───────────────────────────────────────────────────────
    @staticmethod
    def get_by_order(db: Session, order_id: int) -> Optional[Shipment]:
        return (
            db.query(Shipment)
            .filter(Shipment.order_id == order_id)
            .first()
        )

    # ── Get by tracking number ─────────────────────────────────────────────
    @staticmethod
    def get_by_tracking(db: Session, tracking_number: str) -> Optional[Shipment]:
        return (
            db.query(Shipment)
            .filter(Shipment.tracking_number == tracking_number)
            .first()
        )

    # ── Get by ID ──────────────────────────────────────────────────────────
    @staticmethod
    def get_by_id(db: Session, shipment_id: int) -> Optional[Shipment]:
        return db.query(Shipment).filter(Shipment.id == shipment_id).first()

    # ── List all with optional filters ────────────────────────────────────
    @staticmethod
    def list_all(
        db: Session,
        status: Optional[ShipmentStatus] = None,
        order_id: Optional[int] = None,
        courier_name: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Shipment]:
        q = db.query(Shipment)
        if status:
            val = status.value if hasattr(status, "value") else str(status)
            q = q.filter(Shipment.shipment_status == val.upper())
        if order_id:
            q = q.filter(Shipment.order_id == order_id)
        if courier_name:
            q = q.filter(Shipment.courier_name.ilike(f"%{courier_name}%"))
        return q.order_by(Shipment.created_at.desc()).offset(skip).limit(limit).all()

    # ── Count per status (for stats) ───────────────────────────────────────
    @staticmethod
    def count_by_status(db: Session) -> dict:
        rows = db.execute(
            text(
                "SELECT shipment_status, COUNT(*) AS cnt "
                "FROM shipment "
                "GROUP BY shipment_status"
            )
        ).fetchall()
        return {row[0]: row[1] for row in rows}

    # ── Total count ────────────────────────────────────────────────────────
    @staticmethod
    def total_count(db: Session) -> int:
        return db.query(Shipment).count()

    # ── Update status via stored procedure ────────────────────────────────
    @staticmethod
    def update_status(
        db: Session,
        tracking_number: str,
        status: ShipmentStatus | str,
    ) -> Shipment:
        """
        Calls sp_update_shipment_status(tracking_number, status).
        SP behaviour:
          - Updates shipment_status
          - If DELIVERED → sets delivered_at = NOW()
          - If DELIVERED → updates orders.status = 'DELIVERED' (SP side)

        NOTE: ShipmentService._sync_order_status() handles the full mapping
              for all statuses (SHIPPED, OUT_FOR_DELIVERY, RETURNED, etc.)
              so order sync is reliable even if the SP only covers DELIVERED.
        """
        # Accept both enum and plain string
        status_val = (
            status.value if hasattr(status, "value") else str(status)
        ).upper()

        db.execute(
            text("CALL sp_update_shipment_status(:tracking_number, :status)"),
            {"tracking_number": tracking_number, "status": status_val},
        )
        db.commit()
        db.expire_all()

        return (
            db.query(Shipment)
            .filter(Shipment.tracking_number == tracking_number)
            .first()
        )

    # ── Update tracking_url ────────────────────────────────────────────────
    @staticmethod
    def update_tracking_url(
        db: Session, shipment_id: int, tracking_url: str
    ) -> Optional[Shipment]:
        shipment = db.query(Shipment).filter(Shipment.id == shipment_id).first()
        if not shipment:
            return None
        shipment.tracking_url = tracking_url
        db.commit()
        db.refresh(shipment)
        return shipment