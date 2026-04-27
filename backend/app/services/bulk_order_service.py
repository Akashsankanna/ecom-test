from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import Optional
from sqlalchemy.exc import IntegrityError

from app.repositories.bulk_order_repo import BulkOrderRepository
from app.schemas.bulk_order import BulkOrderConvert
from app.models.organization import Organization


class BulkOrderService:

    # ════════════════════════════════════════════════════════════
    # ORGANIZATIONS
    # ════════════════════════════════════════════════════════════

    @staticmethod
    def get_all_organizations(
        db: Session
    ):
        return BulkOrderRepository.get_all_organizations(db)

    @staticmethod
    def create_organization(
        db: Session,
        data
    ):
        try:
            return BulkOrderRepository.create_organization(
                db,
                data
            )

        except IntegrityError:
            db.rollback()

            raise HTTPException(
                status_code=409,
                detail="Organization with this email already exists"
            )

    # ════════════════════════════════════════════════════════════
    # BULK REQUESTS
    # ════════════════════════════════════════════════════════════

    @staticmethod
    def get_all_bulk_requests(
        db: Session,
        status: Optional[str] = None
    ):
        return BulkOrderRepository.get_all_bulk_requests(
            db,
            status
        )

    @staticmethod
    def get_bulk_request(
        db: Session,
        request_id: int
    ):
        req = BulkOrderRepository.get_bulk_request_by_id(
            db,
            request_id
        )

        if not req:
            raise HTTPException(
                status_code=404,
                detail="Bulk request not found"
            )

        items = BulkOrderRepository.get_bulk_request_items(
            db,
            request_id
        )

        return req, items

    @staticmethod
    def approve_bulk_request(
        db: Session,
        request_id: int
    ):
        req = BulkOrderRepository.get_bulk_request_by_id(
            db,
            request_id
        )

        if not req:
            raise HTTPException(
                status_code=404,
                detail="Bulk request not found"
            )

        if req.status not in (
            "PENDING",
            "QUOTED"
        ):
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Cannot approve request "
                    f"in '{req.status}' status"
                )
            )

        return BulkOrderRepository.update_bulk_request_status(
            db,
            request_id,
            "APPROVED"
        )

    @staticmethod
    def reject_bulk_request(
        db: Session,
        request_id: int
    ):
        req = BulkOrderRepository.get_bulk_request_by_id(
            db,
            request_id
        )

        if not req:
            raise HTTPException(
                status_code=404,
                detail="Bulk request not found"
            )

        return BulkOrderRepository.update_bulk_request_status(
            db,
            request_id,
            "REJECTED"
        )

    @staticmethod
    def convert_to_order(
        db: Session,
        request_id: int,
        data: BulkOrderConvert,
        admin_id: int
    ):
        req = BulkOrderRepository.get_bulk_request_by_id(
            db,
            request_id
        )

        if not req:
            raise HTTPException(
                status_code=404,
                detail="Bulk request not found"
            )

        if req.status != "APPROVED":
            raise HTTPException(
                status_code=400,
                detail=(
                    "Only APPROVED bulk requests "
                    "can be converted to orders"
                )
            )

        try:
            return BulkOrderRepository.convert_bulk_request_to_order(
                db,
                request_id,
                data.address_id,
                admin_id
            )

        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=str(e)
            )

    # ════════════════════════════════════════════════════════════
    # BULK ORDERS
    # ════════════════════════════════════════════════════════════

    @staticmethod
    def get_all_bulk_orders(
        db: Session,
        status: Optional[str] = None
    ):
        return BulkOrderRepository.get_all_bulk_orders(
            db,
            status
        )

    @staticmethod
    def get_bulk_order(
        db: Session,
        bulk_order_id: int
    ):
        order = BulkOrderRepository.get_bulk_order_by_id(
            db,
            bulk_order_id
        )

        if not order:
            raise HTTPException(
                status_code=404,
                detail="Bulk order not found"
            )

        items = BulkOrderRepository.get_bulk_order_items(
            db,
            bulk_order_id
        )

        return order, items

    @staticmethod
    def get_bulk_order_view(
        db: Session
    ):
        return BulkOrderRepository.get_bulk_order_view(db)

    @staticmethod
    def update_bulk_order_status(
        db: Session,
        bulk_order_id: int,
        new_status: str,
        admin_id: int
    ):
        valid = {
            "PLACED",
            "CONFIRMED",
            "PROCESSING",
            "SHIPPED",
            "DELIVERED",
            "CANCELLED"
        }

        if new_status.upper() not in valid:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Invalid status. "
                    f"Must be one of: {valid}"
                )
            )

        order = BulkOrderRepository.get_bulk_order_by_id(
            db,
            bulk_order_id
        )

        if not order:
            raise HTTPException(
                status_code=404,
                detail="Bulk order not found"
            )

        try:
            return BulkOrderRepository.update_bulk_order_status(
                db,
                bulk_order_id,
                new_status,
                admin_id
            )

        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=str(e)
            )

    @staticmethod
    def get_bulk_order_status_history(
        db: Session,
        bulk_order_id: int
    ):
        order = BulkOrderRepository.get_bulk_order_by_id(
            db,
            bulk_order_id
        )

        if not order:
            raise HTTPException(
                status_code=404,
                detail="Bulk order not found"
            )

        return BulkOrderRepository.get_bulk_order_status_history(
            db,
            bulk_order_id
        )

    @staticmethod
    def toggle_urgent(
        db: Session,
        bulk_order_id: int
    ):
        val = BulkOrderRepository.toggle_bulk_order_urgent(
            db,
            bulk_order_id
        )

        if val is None:
            raise HTTPException(
                status_code=404,
                detail="Bulk order not found"
            )

        return {
            "bulk_order_id": bulk_order_id,
            "is_urgent": val
        }