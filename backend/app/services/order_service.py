from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import Optional

from app.repositories.order_repo import OrderRepository
from app.schemas.order import (
    OrderStatusUpdate,
    ShipmentCreate,
    ShipmentStatusUpdate,
    ReturnRequestCreate,
    ReturnApprove,
    ExchangeCreate,
    ExchangeStatusUpdate,
    ExchangeCompleteData,
)


class OrderService:

    # =====================================================
    # ORDERS
    # =====================================================

    @staticmethod
    def get_all_orders(
        db: Session,
        status: Optional[str] = None,
        payment_status: Optional[str] = None,
        user_id: Optional[int] = None,
    ):
        # supports newer repo signature with optional user_id
        return OrderRepository.get_all_orders(
            db,
            status,
            payment_status,
            user_id
        )

    @staticmethod
    def get_order_detail(
        db: Session,
        order_id: int
    ):
        order = OrderRepository.get_order_by_id(
            db,
            order_id
        )

        if not order:
            raise HTTPException(
                status_code=404,
                detail="Order not found"
            )

        items = OrderRepository.get_order_items(
            db,
            order_id
        )

        return order, items

    @staticmethod
    def get_user_orders(
        db: Session,
        user_id: int
    ):
        return OrderRepository.get_orders_by_user(
            db,
            user_id
        )

    @staticmethod
    def update_order_status(
        db: Session,
        order_id: int,
        data: OrderStatusUpdate
    ):
        order = OrderRepository.get_order_by_id(
            db,
            order_id
        )

        if not order:
            raise HTTPException(
                status_code=404,
                detail="Order not found"
            )

        valid_statuses = {
            "PENDING",
            "PAID",
            "PROCESSING",
            "SHIPPED",
            "DELIVERED",
            "CANCELLED"
        }

        status_value = (
            data.status.value
            if hasattr(data.status, "value")
            else str(data.status)
        ).upper()

        if status_value not in valid_statuses:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Invalid status. Must be one of: "
                    + ", ".join(valid_statuses)
                )
            )

        try:
            return OrderRepository.update_order_status(
                db,
                order_id,
                status_value
            )

        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=str(e)
            )

    @staticmethod
    def cancel_order(
        db: Session,
        order_id: int
    ):
        order = OrderRepository.get_order_by_id(
            db,
            order_id
        )

        if not order:
            raise HTTPException(
                status_code=404,
                detail="Order not found"
            )

        if order.status == "DELIVERED":
            raise HTTPException(
                status_code=400,
                detail="Cannot cancel a delivered order"
            )

        try:
            return OrderRepository.cancel_order(
                db,
                order_id
            )

        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=str(e)
            )

    # =====================================================
    # ORDER STATUS HISTORY
    # =====================================================

    @staticmethod
    def get_status_history(
        db: Session,
        order_id: int
    ):
        order = OrderRepository.get_order_by_id(
            db,
            order_id
        )

        if not order:
            raise HTTPException(
                status_code=404,
                detail="Order not found"
            )

        return OrderRepository.get_order_status_history(
            db,
            order_id
        )

    # =====================================================
    # SHIPMENT
    # =====================================================

    @staticmethod
    def create_shipment(
        db: Session,
        order_id: int,
        data: ShipmentCreate
    ):
        order = OrderRepository.get_order_by_id(
            db,
            order_id
        )

        if not order:
            raise HTTPException(
                status_code=404,
                detail="Order not found"
            )

        if order.status == "CANCELLED":
            raise HTTPException(
                status_code=400,
                detail=(
                    "Cannot create shipment "
                    "for a cancelled order"
                )
            )

        existing = OrderRepository.get_shipment_by_order(
            db,
            order_id
        )

        if existing:
            raise HTTPException(
                status_code=409,
                detail=(
                    "Shipment already exists "
                    "for this order"
                )
            )

        try:
            shipment = OrderRepository.create_shipment(
                db,
                order_id,
                data
            )

            OrderRepository.update_order_status(
                db,
                order_id,
                "SHIPPED"
            )

            return shipment

        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=str(e)
            )

    @staticmethod
    def update_shipment_status(
        db: Session,
        tracking_number: str,
        data: ShipmentStatusUpdate
    ):
        shipment = OrderRepository.get_shipment_by_tracking(
            db,
            tracking_number
        )

        if not shipment:
            raise HTTPException(
                status_code=404,
                detail="Shipment not found"
            )

        valid = {
            "SHIPPED",
            "OUT_FOR_DELIVERY",
            "DELIVERED"
        }

        status_value = (
            data.status.value
            if hasattr(data.status, "value")
            else str(data.status)
        ).upper()

        if status_value not in valid:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Invalid shipment status. "
                    "Must be one of: "
                    + ", ".join(valid)
                )
            )

        try:
            updated = OrderRepository.update_shipment_status(
                db,
                tracking_number,
                status_value
            )

            if status_value == "DELIVERED":
                OrderRepository.update_order_status(
                    db,
                    updated.order_id,
                    "DELIVERED"
                )

            return updated

        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=str(e)
            )

    @staticmethod
    def get_shipment(
        db: Session,
        order_id: int
    ):
        shipment = OrderRepository.get_shipment_by_order(
            db,
            order_id
        )

        if not shipment:
            raise HTTPException(
                status_code=404,
                detail="Shipment not found for this order"
            )

        return shipment

    # =====================================================
    # RETURN REQUESTS
    # =====================================================

    @staticmethod
    def create_return_request(
        db: Session,
        user_id: int,
        data: ReturnRequestCreate
    ):
        try:
            return OrderRepository.create_return_request(
                db,
                user_id,
                data
            )

        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=str(e)
            )

    @staticmethod
    def get_all_return_requests(
        db: Session,
        status: Optional[str] = None
    ):
        return OrderRepository.get_all_return_requests(
            db,
            status
        )

    @staticmethod
    def get_return_request(
        db: Session,
        return_id: int
    ):
        rr = OrderRepository.get_return_request_by_id(
            db,
            return_id
        )

        if not rr:
            raise HTTPException(
                status_code=404,
                detail="Return request not found"
            )

        return rr

    @staticmethod
    def approve_return(
        db: Session,
        return_id: int,
        data: ReturnApprove
    ):
        rr = OrderRepository.get_return_request_by_id(
            db,
            return_id
        )

        if not rr:
            raise HTTPException(
                status_code=404,
                detail="Return request not found"
            )

        if rr.status != "REQUESTED":
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Cannot approve a return "
                    f"in '{rr.status}' status"
                )
            )

        method = (
            data.refund_method.value
            if hasattr(data.refund_method, "value")
            else str(data.refund_method)
        ).upper()

        valid_methods = {
            "ORIGINAL_PAYMENT",
            "STORE_CREDIT",
            "BANK_TRANSFER"
        }

        if method not in valid_methods:
            raise HTTPException(
                status_code=400,
                detail="Invalid refund method"
            )

        try:
            return OrderRepository.approve_return_request(
                db,
                return_id,
                method
            )

        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=str(e)
            )

    @staticmethod
    def reject_return(
        db: Session,
        return_id: int
    ):
        rr = OrderRepository.get_return_request_by_id(
            db,
            return_id
        )

        if not rr:
            raise HTTPException(
                status_code=404,
                detail="Return request not found"
            )

        if rr.status != "REQUESTED":
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Cannot reject a return "
                    f"in '{rr.status}' status"
                )
            )

        return OrderRepository.reject_return_request(
            db,
            return_id
        )

    @staticmethod
    def complete_refund(
        db: Session,
        return_id: int
    ):
        rr = OrderRepository.get_return_request_by_id(
            db,
            return_id
        )

        if not rr:
            raise HTTPException(
                status_code=404,
                detail="Return request not found"
            )

        if rr.status != "APPROVED":
            raise HTTPException(
                status_code=400,
                detail=(
                    "Refund can only be completed "
                    "for APPROVED returns"
                )
            )

        try:
            return OrderRepository.complete_refund(
                db,
                return_id
            )

        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=str(e)
            )

    # =====================================================
    # EXCHANGE REQUESTS
    # =====================================================

    @staticmethod
    def create_exchange(
        db: Session,
        data: ExchangeCreate
    ):
        try:
            return OrderRepository.create_exchange(
                db,
                data
            )

        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=str(e)
            )

    @staticmethod
    def get_all_exchanges(
        db: Session,
        status: Optional[str] = None
    ):
        return OrderRepository.get_all_exchanges(
            db,
            status
        )

    @staticmethod
    def get_exchange(
        db: Session,
        exchange_id: int
    ):
        ex = OrderRepository.get_exchange_by_id(
            db,
            exchange_id
        )

        if not ex:
            raise HTTPException(
                status_code=404,
                detail="Exchange request not found"
            )

        return ex

    @staticmethod
    def update_exchange_status(
        db: Session,
        exchange_id: int,
        data: ExchangeStatusUpdate
    ):
        ex = OrderRepository.get_exchange_by_id(
            db,
            exchange_id
        )

        if not ex:
            raise HTTPException(
                status_code=404,
                detail="Exchange request not found"
            )

        if ex.status == "COMPLETED":
            raise HTTPException(
                status_code=400,
                detail=(
                    "Cannot update a completed exchange"
                )
            )

        status_value = (
            data.status.value
            if hasattr(data.status, "value")
            else str(data.status)
        ).upper()

        try:
            return OrderRepository.update_exchange_status(
                db,
                exchange_id,
                status_value
            )

        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=str(e)
            )

    @staticmethod
    def complete_exchange(
        db: Session,
        exchange_id: int,
        data: ExchangeCompleteData
    ):
        ex = OrderRepository.get_exchange_by_id(
            db,
            exchange_id
        )

        if not ex:
            raise HTTPException(
                status_code=404,
                detail="Exchange request not found"
            )

        if ex.status not in (
            "REQUESTED",
            "APPROVED"
        ):
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Cannot complete exchange "
                    f"in '{ex.status}' status"
                )
            )

        try:
            return OrderRepository.complete_exchange(
                db,
                exchange_id,
                data.new_variant_id
            )

        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=str(e)
            )

    # =====================================================
    # ANALYTICS
    # =====================================================

    @staticmethod
    def get_top_selling(db: Session):
        return OrderRepository.get_top_selling_products(db)

    @staticmethod
    def get_returns_view(db: Session):
        return OrderRepository.get_return_requests_view(db)

    @staticmethod
    def get_return_requests_view(db: Session):
        return OrderService.get_returns_view(db)

    @staticmethod
    def get_exchange_view(db: Session):
        return OrderRepository.get_exchange_view(db)

    # =====================================================
    # DISCOUNTS / COUPONS
    # =====================================================

    @staticmethod
    def apply_additional_discount(
        db: Session,
        data
    ):
        order = OrderRepository.get_order_by_id(
            db,
            data.order_id
        )

        if not order:
            raise HTTPException(
                status_code=404,
                detail="Order not found"
            )

        if order.status == "CANCELLED":
            raise HTTPException(
                status_code=400,
                detail=(
                    "Cannot discount a "
                    "cancelled order"
                )
            )

        try:
            return OrderRepository.apply_additional_discount(
                db,
                data.order_id,
                float(data.discount_amount),
                data.reason
            )

        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=str(e)
            )

    @staticmethod
    def apply_coupon(
        db: Session,
        data
    ):
        order = OrderRepository.get_order_by_id(
            db,
            data.order_id
        )

        if not order:
            raise HTTPException(
                status_code=404,
                detail="Order not found"
            )

        try:
            return OrderRepository.apply_coupon(
                db,
                data.coupon_code,
                data.user_id,
                data.order_id,
                float(data.order_amount),
                float(
                    getattr(
                        data,
                        "additional_discount",
                        0
                    ) or 0
                ),
            )

        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=str(e)
            )