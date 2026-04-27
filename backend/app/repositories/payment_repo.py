from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models.transaction import Transaction
from app.models.order import Order
from typing import Optional, List


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
            query = query.filter(Transaction.payment_method == payment_method)
        return query.order_by(Transaction.created_at.desc()).limit(limit).all()

    @staticmethod
    def get_transactions_by_order(db: Session, order_id: int) -> List[Transaction]:
        return (
            db.query(Transaction)
            .filter(Transaction.order_id == order_id)
            .order_by(Transaction.created_at.desc())
            .all()
        )

    @staticmethod
    def get_transaction_by_id(db: Session, txn_id: int) -> Optional[Transaction]:
        return db.query(Transaction).filter(Transaction.id == txn_id).first()

    @staticmethod
    def get_payment_view(db: Session, order_id: Optional[int] = None):
        """Uses payment_view DB view — joins transactions + orders."""
        if order_id:
            result = db.execute(
                text("SELECT * FROM payment_view WHERE order_id = :oid"),
                {"oid": order_id},
            )
        else:
            result = db.execute(text("SELECT * FROM payment_view LIMIT 200"))
        return [dict(row) for row in result.mappings()]

    @staticmethod
    def process_payment(
        db: Session,
        order_id: int,
        payment_method: str,
        pay_status: str,
        txn_ref: str,
    ) -> Transaction:
        """Uses sp_process_payment stored procedure."""
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
            db.query(Transaction)
            .filter(Transaction.order_id == order_id)
            .order_by(Transaction.created_at.desc())
            .first()
        )

    @staticmethod
    def get_revenue_summary(db: Session):
        """Total revenue from non-cancelled orders."""
        result = db.execute(
            text(
                "SELECT COUNT(id) as total_transactions, "
                "SUM(amount) as total_amount, "
                "SUM(CASE WHEN status='SUCCESS' THEN amount ELSE 0 END) as successful_amount, "
                "SUM(CASE WHEN status='REFUNDED' THEN amount ELSE 0 END) as refunded_amount "
                "FROM transactions"
            )
        )
        return dict(result.mappings().first())