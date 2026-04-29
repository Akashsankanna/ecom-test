from typing import Optional, List

from sqlalchemy.orm import Session
from sqlalchemy import text

from app.models.payment_transaction import PaymentTransaction


class PaymentRepository:

    @staticmethod
    def get_all_transactions(
        db: Session,
        status: Optional[str] = None,
        payment_method: Optional[str] = None,
        limit: int = 100,
    ) -> List[PaymentTransaction]:

        query = db.query(PaymentTransaction)

        if status:
            query = query.filter(PaymentTransaction.status == status.upper())

        if payment_method:
            query = query.filter(
                PaymentTransaction.payment_method == payment_method
            )

        return (
            query.order_by(PaymentTransaction.created_at.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_transactions_by_order(
        db: Session,
        order_id: int,
    ) -> List[PaymentTransaction]:

        return (
            db.query(PaymentTransaction)
            .filter(PaymentTransaction.order_id == order_id)
            .order_by(PaymentTransaction.created_at.desc())
            .all()
        )

    @staticmethod
    def get_transaction_by_id(
        db: Session,
        txn_id: int,
    ) -> Optional[PaymentTransaction]:

        return (
            db.query(PaymentTransaction)
            .filter(PaymentTransaction.id == txn_id)
            .first()
        )

    @staticmethod
    def get_payment_view(
        db: Session,
        order_id: Optional[int] = None,
    ):
        if order_id:
            result = db.execute(
                text("SELECT * FROM payment_view WHERE order_id = :oid"),
                {"oid": order_id},
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
    ) -> Optional[PaymentTransaction]:

        db.execute(
            text("CALL sp_process_payment(:oid, :method, :status, :ref)"),
            {
                "oid": order_id,
                "method": payment_method,
                "status": pay_status.upper(),
                "ref": txn_ref,
            },
        )

        db.commit()
        db.expire_all()

        return (
            db.query(PaymentTransaction)
            .filter(PaymentTransaction.order_id == order_id)
            .order_by(PaymentTransaction.created_at.desc())
            .first()
        )

    @staticmethod
    def get_revenue_summary(db: Session):
        result = db.execute(
            text(
                "SELECT "
                "COUNT(id) AS total_transactions, "
                "SUM(amount) AS total_amount, "
                "SUM(CASE WHEN status='SUCCESS' THEN amount ELSE 0 END) AS successful_amount, "
                "SUM(CASE WHEN status='REFUNDED' THEN amount ELSE 0 END) AS refunded_amount "
                "FROM transactions"
            )
        )

        return dict(result.mappings().first())