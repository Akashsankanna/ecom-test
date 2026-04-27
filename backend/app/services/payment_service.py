from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.repositories.payment_repo import PaymentRepository
from typing import Optional


class PaymentService:

    @staticmethod
    def get_all_payments(
        db: Session,
        status: Optional[str] = None,
        payment_method: Optional[str] = None,
        limit: int = 100,
    ):
        return PaymentRepository.get_all_transactions(db, status, payment_method, limit)

    @staticmethod
    def get_payments_by_order(db: Session, order_id: int):
        txns = PaymentRepository.get_transactions_by_order(db, order_id)
        if not txns:
            raise HTTPException(
                status_code=404, detail="No transactions found for this order"
            )
        return txns

    @staticmethod
    def get_payment_view(db: Session, order_id: Optional[int] = None):
        return PaymentRepository.get_payment_view(db, order_id)

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
        valid_methods = {"UPI", "CARD", "NET_BANKING", "NEFT", "RTGS", "COD", "BANK_TRANSFER"}
        if payment_method.upper() not in valid_methods:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid payment_method. Valid: {valid_methods}",
            )
        valid_statuses = {"PENDING", "SUCCESS", "FAILED"}
        if pay_status.upper() not in valid_statuses:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status. Valid: {valid_statuses}",
            )
        try:
            return PaymentRepository.process_payment(
                db, order_id, payment_method.upper(), pay_status.upper(), txn_ref
            )
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))