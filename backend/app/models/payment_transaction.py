from sqlalchemy import Column, Integer, Numeric, String, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.db.session import Base   # change this import if needed


class PaymentTransaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)
    amount = Column(Numeric(10, 2), nullable=False)
    payment_method = Column(String(50), nullable=True)
    status = Column(String(20), nullable=False, default="PENDING")
    transaction_ref = Column(String(100), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    payment_gateway = Column(String(50), nullable=True)
    gateway_transaction_id = Column(String(100), nullable=True)
    currency = Column(String(10), nullable=False, default="INR")
    gateway_response = Column(JSONB, nullable=True)

    order = relationship("Order", back_populates="transactions")