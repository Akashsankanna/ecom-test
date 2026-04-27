from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import Optional

from app.repositories.payment_repo import PaymentRepository
import razorpay
from app.core.config import settings
# from app.services.payment_service import (
#     create_razorpay_order_service,
#     verify_razorpay_payment_service,
# )

client = razorpay.Client(
    auth=(
        settings.RAZORPAY_KEY_ID,
        settings.RAZORPAY_KEY_SECRET
    )
)


def create_razorpay_order_service(
    amount: float,
    currency: str = "INR",
    receipt: str = "receipt"
):
    return client.order.create({
        "amount": int(amount * 100),
        "currency": currency,
        "receipt": receipt
    })


def verify_razorpay_payment_service(
    db=None,
    razorpay_order_id=None,
    razorpay_payment_id=None,
    razorpay_signature=None,
    user_id=None,
    address_id=None
):
    client.utility.verify_payment_signature({
        "razorpay_order_id": razorpay_order_id,
        "razorpay_payment_id": razorpay_payment_id,
        "razorpay_signature": razorpay_signature
    })

    return {
        "success": True,
        "message": "Payment verified"
    }
class PaymentService:

    # =====================================================
    # PAYMENTS / TRANSACTIONS
    # =====================================================

    @staticmethod
    def get_all_payments(
        db: Session,
        status: Optional[str] = None,
        payment_method: Optional[str] = None,
        limit: int = 100,
    ):
        return PaymentRepository.get_all_transactions(
            db=db,
            status=status,
            payment_method=payment_method,
            limit=limit
        )

    @staticmethod
    def get_payments_by_order(
        db: Session,
        order_id: int
    ):
        txns = PaymentRepository.get_transactions_by_order(
            db,
            order_id
        )

        if not txns:
            raise HTTPException(
                status_code=404,
                detail="No transactions found for this order"
            )

        return txns

    @staticmethod
    def get_payment_view(
        db: Session,
        order_id: Optional[int] = None
    ):
        return PaymentRepository.get_payment_view(
            db,
            order_id
        )

    @staticmethod
    def get_revenue_summary(db: Session):
        return PaymentRepository.get_revenue_summary(db)

    @staticmethod
    def process_payment(
        db: Session,
        order_id: int,
        payment_method: str,
        pay_status: str,
        txn_ref: str,
    ):
        valid_methods = {
            "UPI",
            "CARD",
            "NET_BANKING",
            "NEFT",
            "RTGS",
            "COD",
            "BANK_TRANSFER",
            "RAZORPAY",
        }

        method = payment_method.upper()

        if method not in valid_methods:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Invalid payment_method. "
                    f"Valid: {valid_methods}"
                ),
            )

        valid_statuses = {
            "PENDING",
            "SUCCESS",
            "FAILED",
            "REFUNDED",
        }

        status = pay_status.upper()

        if status not in valid_statuses:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Invalid status. "
                    f"Valid: {valid_statuses}"
                ),
            )

        try:
            return PaymentRepository.process_payment(
                db=db,
                order_id=order_id,
                payment_method=method,
                pay_status=status,
                txn_ref=txn_ref,
            )

        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=str(e)
            )

    # =====================================================
    # RAZORPAY FLOW
    # =====================================================

    @staticmethod
    def create_razorpay_order(
        amount: float,
        currency: str = "INR",
        receipt: str = "receipt"
    ):
        try:
            return create_razorpay_order_service(
                amount=amount,
                currency=currency,
                receipt=receipt
            )

        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=str(e)
            )

    @staticmethod
    def verify_razorpay_payment(
        db: Session,
        razorpay_order_id: str,
        razorpay_payment_id: str,
        razorpay_signature: str,
        user_id: int,
        address_id: int
    ):
        try:
            return verify_razorpay_payment_service(
                db=db,
                razorpay_order_id=razorpay_order_id,
                razorpay_payment_id=razorpay_payment_id,
                razorpay_signature=razorpay_signature,
                user_id=user_id,
                address_id=address_id
            )

        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=str(e)
            )