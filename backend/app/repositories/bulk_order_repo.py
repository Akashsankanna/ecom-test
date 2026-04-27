from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional, List

from app.models.bulk_order import (
    BulkOrderRequest,
    BulkOrderRequestItem,
    BulkOrder,
    BulkOrderItem,
)
from app.models.organization import Organization


class BulkOrderRepository:

    # ───────────────── ORGANIZATIONS ─────────────────

    @staticmethod
    def get_all_organizations(db: Session):
        result = db.execute(text("""
            SELECT *
            FROM organization
            WHERE is_active = true
            ORDER BY name
        """))
        return result.mappings().all()

    @staticmethod
    def get_organization_by_id(db: Session, org_id: int):
        return (
            db.query(Organization)
            .filter(Organization.id == org_id)
            .first()
        )

    @staticmethod
    def create_organization(db: Session, data):
        org = Organization(
            name=data.name,
            contact_person=data.contact_person,
            email=data.email,
            phone=data.phone,
            gst_number=data.gst_number,
            city=data.city,
            state=data.state,
            is_active=True
        )
        db.add(org)
        db.commit()
        db.refresh(org)
        return org

    # ───────────────── BULK REQUESTS ─────────────────

    @staticmethod
    def get_all_bulk_requests(
        db: Session,
        status: Optional[str] = None
    ):
        sql = """
            SELECT bor.id,
                   bor.organization_id,
                   bor.user_id,
                   bor.request_number,
                   bor.status,
                   bor.notes,
                   bor.expected_delivery_date,
                   bor.created_at,
                   org.name AS organization_name,
                   u.email AS user_email
            FROM bulk_order_request bor
            LEFT JOIN organization org ON bor.organization_id = org.id
            LEFT JOIN users u ON bor.user_id = u.id
            WHERE 1=1
        """

        params = {}

        if status:
            sql += " AND bor.status = :status"
            params["status"] = status.upper()

        sql += " ORDER BY bor.created_at DESC"

        result = db.execute(text(sql), params)
        return result.mappings().all()

    @staticmethod
    def get_bulk_request_by_id(db: Session, request_id: int):
        return (
            db.query(BulkOrderRequest)
            .filter(BulkOrderRequest.id == request_id)
            .first()
        )

    @staticmethod
    def get_bulk_request_items(db: Session, request_id: int):
        return (
            db.query(BulkOrderRequestItem)
            .filter(BulkOrderRequestItem.bulk_request_id == request_id)
            .all()
        )

    @staticmethod
    def update_bulk_request_status(
        db: Session,
        request_id: int,
        status: str
    ):
        req = (
            db.query(BulkOrderRequest)
            .filter(BulkOrderRequest.id == request_id)
            .first()
        )

        if not req:
            return None

        req.status = status.upper()

        db.commit()
        db.refresh(req)

        return req

    @staticmethod
    def convert_bulk_request_to_order(
        db: Session,
        request_id: int,
        address_id: int,
        admin_id: int
    ):
        db.execute(
            text("SET LOCAL app.current_user_id = :uid"),
            {"uid": str(admin_id)}
        )

        db.execute(
            text("""
                CALL sp_convert_bulk_request_to_order(
                    :req_id,
                    :addr_id
                )
            """),
            {
                "req_id": request_id,
                "addr_id": address_id
            }
        )

        db.commit()
        db.expire_all()

        return (
            db.query(BulkOrder)
            .filter(BulkOrder.bulk_request_id == request_id)
            .first()
        )

    # ───────────────── BULK ORDERS ─────────────────

    @staticmethod
    def get_all_bulk_orders(
        db: Session,
        status: Optional[str] = None
    ):
        sql = """
            SELECT bo.id,
                   bo.order_number,
                   bo.organization_id,
                   bo.total_amount,
                   bo.status,
                   bo.payment_status,
                   bo.is_urgent,
                   bo.expected_delivery_date,
                   bo.created_at,
                   org.name AS organization_name
            FROM bulk_order bo
            LEFT JOIN organization org
                   ON bo.organization_id = org.id
            WHERE 1=1
        """

        params = {}

        if status:
            sql += " AND bo.status = :status"
            params["status"] = status.upper()

        sql += " ORDER BY bo.created_at DESC"

        result = db.execute(text(sql), params)
        return result.mappings().all()

    @staticmethod
    def get_bulk_order_by_id(
        db: Session,
        bulk_order_id: int
    ):
        return (
            db.query(BulkOrder)
            .filter(BulkOrder.id == bulk_order_id)
            .first()
        )

    @staticmethod
    def get_bulk_order_items(
        db: Session,
        bulk_order_id: int
    ):
        return (
            db.query(BulkOrderItem)
            .filter(BulkOrderItem.bulk_order_id == bulk_order_id)
            .all()
        )

    @staticmethod
    def get_bulk_order_view(db: Session):
        result = db.execute(
            text("SELECT * FROM bulk_order_view")
        )
        return [dict(row) for row in result.mappings()]

    @staticmethod
    def update_bulk_order_status(
        db: Session,
        bulk_order_id: int,
        new_status: str,
        admin_id: int
    ):
        db.execute(
            text("SET LOCAL app.current_user_id = :uid"),
            {"uid": str(admin_id)}
        )

        db.execute(
            text("""
                CALL sp_update_bulk_order_status(
                    :bid,
                    :status
                )
            """),
            {
                "bid": bulk_order_id,
                "status": new_status.upper()
            }
        )

        db.commit()
        db.expire_all()

        return (
            db.query(BulkOrder)
            .filter(BulkOrder.id == bulk_order_id)
            .first()
        )

    @staticmethod
    def get_bulk_order_status_history(
        db: Session,
        bulk_order_id: int
    ):
        result = db.execute(text("""
            SELECT bosh.id,
                   bosh.bulk_order_id,
                   bosh.status,
                   bosh.changed_by,
                   bosh.notes,
                   bosh.changed_at,
                   u.name AS changed_by_name
            FROM bulk_order_status_history bosh
            LEFT JOIN users u
                   ON bosh.changed_by = u.id
            WHERE bosh.bulk_order_id = :id
            ORDER BY bosh.changed_at ASC
        """), {"id": bulk_order_id})

        return result.mappings().all()

    @staticmethod
    def toggle_bulk_order_urgent(
        db: Session,
        bulk_order_id: int
    ):
        row = db.execute(text("""
            SELECT id, is_urgent
            FROM bulk_order
            WHERE id = :id
        """), {"id": bulk_order_id}).mappings().first()

        if not row:
            return None

        new_val = not row["is_urgent"]

        db.execute(text("""
            UPDATE bulk_order
            SET is_urgent = :val,
                updated_at = NOW()
            WHERE id = :id
        """), {
            "val": new_val,
            "id": bulk_order_id
        })

        db.commit()

        return new_val