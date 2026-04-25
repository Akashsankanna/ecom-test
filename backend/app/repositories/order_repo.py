from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models.order import Order
from app.models.order_items import OrderItem
from app.models.shipment import Shipment
from app.models.order_status_history import OrderStatusHistory
from app.models.return_request import ReturnRequest
from app.models.exchange_request import ExchangeRequest
from typing import Optional, List


class OrderRepository:

    # ════════════════════════════════════════════════════════════
    # ORDERS
    # ════════════════════════════════════════════════════════════

    @staticmethod
    def get_all_orders(
        db: Session,
        status: Optional[str] = None,
        payment_status: Optional[str] = None,
        user_id: Optional[int] = None,
    ) -> List[Order]:
        query = db.query(Order)
        if status:
            query = query.filter(Order.status == status.upper())
        if payment_status:
            query = query.filter(Order.payment_status == payment_status.upper())
        if user_id:
            query = query.filter(Order.user_id == user_id)
        return query.order_by(Order.created_at.desc()).all()

    @staticmethod
    def get_order_by_id(db: Session, order_id: int) -> Optional[Order]:
        return db.query(Order).filter(Order.id == order_id).first()

    @staticmethod
    def get_orders_by_user(db: Session, user_id: int) -> List[Order]:
        return (
            db.query(Order)
            .filter(Order.user_id == user_id)
            .order_by(Order.created_at.desc())
            .all()
        )

    @staticmethod
    def update_order_status(db: Session, order_id: int, new_status: str) -> Order:
        """Uses sp_update_order_status(p_order_id, p_new_status) — new DB param names."""
        db.execute(
            text("CALL sp_update_order_status(:p_order_id, :p_new_status)"),
            {"p_order_id": order_id, "p_new_status": new_status.upper()},
        )
        db.commit()
        db.expire_all()
        return db.query(Order).filter(Order.id == order_id).first()

    @staticmethod
    def cancel_order(db: Session, order_id: int) -> Order:
        """Uses sp_cancel_order(p_order_id) — new DB param name. Restores stock automatically."""
        db.execute(
            text("CALL sp_cancel_order(:p_order_id)"),
            {"p_order_id": order_id},
        )
        db.commit()
        db.expire_all()
        return db.query(Order).filter(Order.id == order_id).first()

    @staticmethod
    def get_order_items(db: Session, order_id: int) -> List[OrderItem]:
        return db.query(OrderItem).filter(OrderItem.order_id == order_id).all()

    # ════════════════════════════════════════════════════════════
    # ORDER STATUS HISTORY
    # ════════════════════════════════════════════════════════════

    @staticmethod
    def get_order_status_history(db: Session, order_id: int) -> List[OrderStatusHistory]:
        return (
            db.query(OrderStatusHistory)
            .filter(OrderStatusHistory.order_id == order_id)
            .order_by(OrderStatusHistory.changed_at.asc())
            .all()
        )

    # ════════════════════════════════════════════════════════════
    # SHIPMENT
    # ════════════════════════════════════════════════════════════

    @staticmethod
    def create_shipment(db: Session, order_id: int, data) -> Optional[Shipment]:
        """Uses sp_create_shipment stored procedure."""
        db.execute(
            text("CALL sp_create_shipment(:oid, :courier, :tracking, :est)"),
            {
                "oid": order_id,
                "courier": data.courier_name,
                "tracking": data.tracking_number,
                "est": data.estimated_delivery,
            },
        )
        db.commit()
        db.expire_all()
        return db.query(Shipment).filter(Shipment.order_id == order_id).first()

    @staticmethod
    def update_shipment_status(db: Session, tracking_number: str, status: str) -> Optional[Shipment]:
        """Uses sp_update_shipment_status stored procedure."""
        db.execute(
            text("CALL sp_update_shipment_status(:tracking, :status)"),
            {"tracking": tracking_number, "status": status.upper()},
        )
        db.commit()
        db.expire_all()
        return (
            db.query(Shipment)
            .filter(Shipment.tracking_number == tracking_number)
            .first()
        )

    @staticmethod
    def get_shipment_by_order(db: Session, order_id: int) -> Optional[Shipment]:
        return db.query(Shipment).filter(Shipment.order_id == order_id).first()

    @staticmethod
    def get_shipment_by_tracking(db: Session, tracking_number: str) -> Optional[Shipment]:
        return (
            db.query(Shipment)
            .filter(Shipment.tracking_number == tracking_number)
            .first()
        )

    # ════════════════════════════════════════════════════════════
    # RETURN REQUESTS
    # ════════════════════════════════════════════════════════════

    @staticmethod
    def create_return_request(db: Session, user_id: int, data) -> Optional[ReturnRequest]:
        """Uses sp_create_return_request — validates DELIVERED status internally."""
        db.execute(
            text("CALL sp_create_return_request(:order_id, :item_id, :user_id, :qty, :reason)"),
            {
                "order_id": data.order_id,
                "item_id": data.order_item_id,
                "user_id": user_id,
                "qty": data.quantity,
                "reason": data.reason,
            },
        )
        db.commit()
        db.expire_all()
        return (
            db.query(ReturnRequest)
            .filter(
                ReturnRequest.order_id == data.order_id,
                ReturnRequest.user_id == user_id,
            )
            .order_by(ReturnRequest.created_at.desc())
            .first()
        )

    @staticmethod
    def get_all_return_requests(
        db: Session, status: Optional[str] = None
    ) -> List[ReturnRequest]:
        query = db.query(ReturnRequest)
        if status:
            query = query.filter(ReturnRequest.status == status.upper())
        return query.order_by(ReturnRequest.created_at.desc()).all()

    @staticmethod
    def get_return_request_by_id(db: Session, return_id: int) -> Optional[ReturnRequest]:
        return db.query(ReturnRequest).filter(ReturnRequest.id == return_id).first()

    @staticmethod
    def approve_return_request(
        db: Session, return_id: int, refund_method: str
    ) -> Optional[ReturnRequest]:
        """Uses sp_approve_return_request — restores stock + creates IN_APP notification."""
        db.execute(
            text("CALL sp_approve_return_request(:rid, :method)"),
            {"rid": return_id, "method": refund_method.upper()},
        )
        db.commit()
        db.expire_all()
        return db.query(ReturnRequest).filter(ReturnRequest.id == return_id).first()

    @staticmethod
    def reject_return_request(db: Session, return_id: int) -> Optional[ReturnRequest]:
        rr = db.query(ReturnRequest).filter(ReturnRequest.id == return_id).first()
        if not rr:
            return None
        rr.status = "REJECTED"
        db.commit()
        db.refresh(rr)
        return rr

    @staticmethod
    def complete_refund(db: Session, return_id: int) -> Optional[ReturnRequest]:
        """Uses sp_complete_refund — sets REFUNDED + triggers PAYMENT_SUCCESS notification."""
        db.execute(
            text("CALL sp_complete_refund(:rid)"),
            {"rid": return_id},
        )
        db.commit()
        db.expire_all()
        return db.query(ReturnRequest).filter(ReturnRequest.id == return_id).first()

    # ════════════════════════════════════════════════════════════
    # EXCHANGE REQUESTS
    # ════════════════════════════════════════════════════════════

    @staticmethod
    def create_exchange(db: Session, data) -> Optional[ExchangeRequest]:
        """Uses sp_create_exchange — validates DELIVERED status internally."""
        db.execute(
            text("CALL sp_create_exchange(:oid, :oi_id, :reason)"),
            {
                "oid": data.order_id,
                "oi_id": data.order_item_id,
                "reason": data.reason,
            },
        )
        db.commit()
        db.expire_all()
        return (
            db.query(ExchangeRequest)
            .filter(ExchangeRequest.order_id == data.order_id)
            .order_by(ExchangeRequest.created_at.desc())
            .first()
        )

    @staticmethod
    def get_all_exchanges(
        db: Session, status: Optional[str] = None
    ) -> List[ExchangeRequest]:
        query = db.query(ExchangeRequest)
        if status:
            query = query.filter(ExchangeRequest.status == status.upper())
        return query.order_by(ExchangeRequest.created_at.desc()).all()

    @staticmethod
    def get_exchange_by_id(db: Session, exchange_id: int) -> Optional[ExchangeRequest]:
        return db.query(ExchangeRequest).filter(ExchangeRequest.id == exchange_id).first()

    @staticmethod
    def update_exchange_status(
        db: Session, exchange_id: int, new_status: str
    ) -> Optional[ExchangeRequest]:
        """Uses sp_update_exchange_status stored procedure."""
        db.execute(
            text("CALL sp_update_exchange_status(:ex_id, :status)"),
            {"ex_id": exchange_id, "status": new_status.upper()},
        )
        db.commit()
        db.expire_all()
        return (
            db.query(ExchangeRequest)
            .filter(ExchangeRequest.id == exchange_id)
            .first()
        )

    @staticmethod
    def complete_exchange(
        db: Session, exchange_id: int, new_variant_id: int
    ) -> Optional[ExchangeRequest]:
        """Uses sp_complete_exchange — reduces stock of new variant."""
        db.execute(
            text("CALL sp_complete_exchange(:ex_id, :new_variant)"),
            {"ex_id": exchange_id, "new_variant": new_variant_id},
        )
        db.commit()
        db.expire_all()
        return (
            db.query(ExchangeRequest)
            .filter(ExchangeRequest.id == exchange_id)
            .first()
        )

    # ════════════════════════════════════════════════════════════
    # ANALYTICS VIEWS
    # ════════════════════════════════════════════════════════════

    @staticmethod
    def get_order_tracking_view(db: Session, order_id: Optional[int] = None):
        if order_id:
            result = db.execute(
                text("SELECT * FROM order_tracking_view WHERE id = :oid"),
                {"oid": order_id},
            )
        else:
            result = db.execute(text("SELECT * FROM order_tracking_view"))
        return [dict(row) for row in result.mappings()]

    @staticmethod
    def get_top_selling_products(db: Session):
        result = db.execute(text("SELECT * FROM top_selling_products LIMIT 20"))
        return [dict(row) for row in result.mappings()]

    @staticmethod
    def get_return_requests_view(db: Session):
        result = db.execute(text("SELECT * FROM return_request_view"))
        return [dict(row) for row in result.mappings()]

    @staticmethod
    def get_exchange_view(db: Session):
        result = db.execute(text("SELECT * FROM exchange_view"))
        return [dict(row) for row in result.mappings()]

    # ════════════════════════════════════════════════════════════
    # NEW IN ecomdb21 — DISCOUNT SPs
    # ════════════════════════════════════════════════════════════

    @staticmethod
    def apply_additional_discount(db: Session, order_id: int, discount_amount: float, reason: str):
        """Uses sp_apply_additional_discount(p_order_id, p_discount_amount, p_reason)."""
        from app.models.order import Order
        db.execute(
            text("CALL sp_apply_additional_discount(:oid, :amt, :reason)"),
            {"oid": order_id, "amt": discount_amount, "reason": reason},
        )
        db.commit()
        db.expire_all()
        return db.query(Order).filter(Order.id == order_id).first()

    @staticmethod
    def apply_coupon(
        db: Session,
        coupon_code: str,
        user_id: int,
        order_id: int,
        order_amount: float,
        additional_discount: float = 0,
    ):
        """Uses sp_apply_coupon (5-param version from ecomdb21)."""
        from app.models.order import Order
        db.execute(
            text("CALL sp_apply_coupon(:code, :uid, :oid, :amount, :extra_disc)"),
            {
                "code": coupon_code.upper(),
                "uid": user_id,
                "oid": order_id,
                "amount": order_amount,
                "extra_disc": additional_discount,
            },
        )
        db.commit()
        db.expire_all()
        return db.query(Order).filter(Order.id == order_id).first()
    

    @staticmethod
    def apply_additional_discount(db: Session, order_id: int, discount_amount: float, reason: str):
        """Uses sp_apply_additional_discount(p_order_id, p_discount_amount, p_reason)."""
        from app.models.order import Order
        db.execute(
            text("CALL sp_apply_additional_discount(:oid, :amt, :reason)"),
            {"oid": order_id, "amt": discount_amount, "reason": reason},
        )
        db.commit()
        db.expire_all()
        return db.query(Order).filter(Order.id == order_id).first()

    @staticmethod
    def apply_coupon(
        db: Session,
        coupon_code: str,
        user_id: int,
        order_id: int,
        order_amount: float,
        additional_discount: float = 0,
    ):
        """Uses sp_apply_coupon (5-param version from ecomdb21)."""
        from app.models.order import Order
        db.execute(
            text("CALL sp_apply_coupon(:code, :uid, :oid, :amount, :extra_disc)"),
            {
                "code": coupon_code.upper(),
                "uid": user_id,
                "oid": order_id,
                "amount": order_amount,
                "extra_disc": additional_discount,
            },
        )
        db.commit()
        db.expire_all()
        return db.query(Order).filter(Order.id == order_id).first()