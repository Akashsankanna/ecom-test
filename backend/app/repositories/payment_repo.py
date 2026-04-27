from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional, List

from app.db.session import get_db
from app.schemas.payment import (
    RazorpayCreateOrderRequest,
    RazorpayVerifyPaymentRequest,
)
# from app.services.payment_service import (
#     create_razorpay_order_service,
#     verify_razorpay_payment_service,
# )

from app.models.transaction import Transaction
from app.models.order import Order


# =====================================================
# FASTAPI ROUTER
# =====================================================
router = APIRouter(
    prefix="/razorpay",
    tags=["Razorpay"]
)


# =====================================================
# RAZORPAY ROUTES
# =====================================================

@router.post("/create-order")
def create_razorpay_order(payload: RazorpayCreateOrderRequest):
    return create_razorpay_order_service(
        amount=payload.amount,
        currency=payload.currency,
        receipt=payload.receipt
    )


@router.post("/verify-payment")
def verify_razorpay_payment(
    payload: RazorpayVerifyPaymentRequest,
    db: Session = Depends(get_db)
):
    # Verify signature/payment
    verify_razorpay_payment_service(
        razorpay_order_id=payload.razorpay_order_id,
        razorpay_payment_id=payload.razorpay_payment_id,
        razorpay_signature=payload.razorpay_signature
    )

    # If order_id exists, save payment transaction
    if hasattr(payload, "order_id") and payload.order_id:
        PaymentRepository.process_payment(
            db=db,
            order_id=payload.order_id,
            payment_method="RAZORPAY",
            pay_status="SUCCESS",
            txn_ref=payload.razorpay_payment_id
        )

    return {
        "success": True,
        "message": "Payment verified successfully",
        "payment_status": "paid",
        "transaction_ref": payload.razorpay_payment_id,
        "razorpay_order_id": payload.razorpay_order_id,
        "order_id": payload.order_id if hasattr(payload, "order_id") else None
    }


# =====================================================
# PAYMENT REPOSITORY
# =====================================================
class PaymentRepository:

    @staticmethod
    def get_all_transactions(
        db: Session,
        status: Optional[str] = None,
        payment_method: Optional[str] = None,
        limit: int = 100,
    ) -> List[Transaction]:

        query = db.query(Transaction)

        if status:
            query = query.filter(Transaction.status == status.upper())

        if payment_method:
            query = query.filter(
                Transaction.payment_method == payment_method
            )

        return (
            query.order_by(Transaction.created_at.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_transactions_by_order(
        db: Session,
        order_id: int
    ) -> List[Transaction]:

        return (
            db.query(Transaction)
            .filter(Transaction.order_id == order_id)
            .order_by(Transaction.created_at.desc())
            .all()
        )

    @staticmethod
    def get_transaction_by_id(
        db: Session,
        txn_id: int
    ) -> Optional[Transaction]:

        return (
            db.query(Transaction)
            .filter(Transaction.id == txn_id)
            .first()
        )

    @staticmethod
    def get_payment_view(
        db: Session,
        order_id: Optional[int] = None
    ):
        if order_id:
            result = db.execute(
                text(
                    "SELECT * FROM payment_view "
                    "WHERE order_id = :oid"
                ),
                {"oid": order_id}
            )
        else:
            result = db.execute(
                text("SELECT * FROM payment_view LIMIT 200")
            )

        return [dict(row) for row in result.mappings()]

    @staticmethod
    def process_payment(
        db: Session,
        order_id: int,
        payment_method: str,
        pay_status: str,
        txn_ref: str,
    ) -> Transaction:

        db.execute(
            text(
                "CALL sp_process_payment("
                ":oid, :method, :status, :ref)"
            ),
            {
                "oid": order_id,
                "method": payment_method,
                "status": pay_status.upper(),
                "ref": txn_ref,
            }
        )

        db.commit()
        db.expire_all()

        return (
            db.query(Transaction)
            .filter(Transaction.order_id == order_id)
            .order_by(Transaction.created_at.desc())
            .first()
        )

    @staticmethod
    def get_revenue_summary(db: Session):
        result = db.execute(
            text(
                "SELECT "
                "COUNT(id) as total_transactions, "
                "SUM(amount) as total_amount, "
                "SUM(CASE WHEN status='SUCCESS' "
                "THEN amount ELSE 0 END) as successful_amount, "
                "SUM(CASE WHEN status='REFUNDED' "
                "THEN amount ELSE 0 END) as refunded_amount "
                "FROM transactions"
            )
        )

        return dict(result.mappings().first())