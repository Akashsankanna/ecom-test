from sqlalchemy import Column, Integer, String, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import TIMESTAMP, JSONB
from sqlalchemy.sql import func
from app.db.base import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)
    amount = Column(Numeric(10, 2), nullable=False)
    payment_method = Column(String(50), nullable=True)
    # DB CHECK: PENDING | SUCCESS | FAILED | REFUNDED
    status = Column(String(20), default="PENDING")
    transaction_ref = Column(String(100), nullable=True)
    payment_gateway = Column(String(50), nullable=True)
    gateway_transaction_id = Column(String(100), nullable=True)
    currency = Column(String(10), default="INR")
    gateway_response = Column(JSONB, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())