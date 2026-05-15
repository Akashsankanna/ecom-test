from sqlalchemy import (
    Column,
    Integer,
    Numeric,
    String,
    DateTime,
    ForeignKey,
    Computed,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.db.base import Base


class PaymentTransaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)

    order_id = Column(
        Integer,
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    amount = Column(Numeric(10, 2), nullable=False)

    payment_method = Column(String(50), nullable=True)

    status = Column(String(20), nullable=False, default="PENDING")

    transaction_ref = Column(String(100), nullable=True, index=True)

    created_at = Column(DateTime, server_default=func.now())

    payment_gateway = Column(String(50), nullable=True)

    gateway_transaction_id = Column(String(100), nullable=True, index=True)

    currency = Column(String(10), nullable=False, default="INR")

    gateway_response = Column(JSONB, nullable=True)

    payment_stage = Column(String(20), nullable=True)

    transaction_status = Column(String(20), nullable=True, default="SUCCESS")

    razorpay_payment_id = Column(
        String,
        Computed("(gateway_response ->> 'razorpay_payment_id')", persisted=True),
    )

    order = relationship(
        "Order",
        back_populates="transactions",
    )