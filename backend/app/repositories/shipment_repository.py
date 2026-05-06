"""
app/repositories/shipment_repository.py

FIXED: update_status() no longer calls db.commit() itself.
       The caller (ShipmentService) owns the commit + refresh cycle,
       so there is exactly ONE commit per request — no double-write conflicts.
"""

from __future__ import annotations

from typing import List, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.models.shipment import Shipment
from app.schemas.shipment import ShipmentCreate, ShipmentStatus


class ShipmentRepository:

    # ── Create ────────────────────────────────────────────────────────────────
    @staticmethod
    def create(db: Session, order_id: int, data: ShipmentCreate) -> Shipment:
        """
        Calls sp_create_shipment(order_id, courier_name, tracking_number, estimated_delivery).
        SP inserts the shipment row; we commit here so the row is visible.
        Order-status sync is handled by ShipmentService.create_shipment().
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
        # Flush so the row exists; the caller will commit after syncing order status.
        db.flush()

        shipment = (
            db.query(Shipment)
            .filter(Shipment.tracking_number == data.tracking_number)
            .first()
        )

        # Persist optional tracking_url (not in SP signature)
        if shipment and getattr(data, "tracking_url", None):
            shipment.tracking_url = data.tracking_url

        return shipment

    # ── Get by order ──────────────────────────────────────────────────────────
    @staticmethod
    def get_by_order(db: Session, order_id: int) -> Optional[Shipment]:
        return (
            db.query(Shipment)
            .filter(Shipment.order_id == order_id)
            .first()
        )

    # ── Get by tracking number ────────────────────────────────────────────────
    @staticmethod
    def get_by_tracking(db: Session, tracking_number: str) -> Optional[Shipment]:
        return (
            db.query(Shipment)
            .filter(Shipment.tracking_number == tracking_number)
            .first()
        )

    # ── Get by ID ─────────────────────────────────────────────────────────────
    @staticmethod
    def get_by_id(db: Session, shipment_id: int) -> Optional[Shipment]:
        return db.query(Shipment).filter(Shipment.id == shipment_id).first()

    # ── List all ──────────────────────────────────────────────────────────────
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

    # ── Count per status ──────────────────────────────────────────────────────
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

    # ── Total count ───────────────────────────────────────────────────────────
    @staticmethod
    def total_count(db: Session) -> int:
        return db.query(Shipment).count()

    # ── Update status via SP ──────────────────────────────────────────────────
    @staticmethod
    def update_status(
        db: Session,
        tracking_number: str,
        status: ShipmentStatus | str,
    ) -> Shipment:
        """
        Calls sp_update_shipment_status(tracking_number, status).

        IMPORTANT: This method does NOT commit or expire_all.
        The owning service (ShipmentService.update_shipment_status) is
        responsible for syncing order.status, then committing once,
        then refreshing both objects.  This prevents double-commit races.
        """
        status_val = (
            status.value if hasattr(status, "value") else str(status)
        ).upper()

        db.execute(
            text("CALL sp_update_shipment_status(:tracking_number, :status)"),
            {"tracking_number": tracking_number, "status": status_val},
        )
        # Flush so the SP writes are visible in the current transaction,
        # but do NOT commit — the caller commits after updating the order too.
        db.flush()

        return (
            db.query(Shipment)
            .filter(Shipment.tracking_number == tracking_number)
            .first()
        )

    # ── Update tracking URL ───────────────────────────────────────────────────
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