from sqlalchemy import Column, Integer, String, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import TIMESTAMP, JSONB
from sqlalchemy.sql import func
from app.db.base import Base


class Invoice(Base):
    __tablename__ = "invoice"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), unique=True, nullable=True)
    invoice_number = Column(String(50), nullable=False, unique=True)
    invoice_date = Column(TIMESTAMP(timezone=True), server_default=func.now())
    billing_address = Column(JSONB, nullable=True)
    gst_number = Column(String(20), nullable=True)
    total_tax = Column(Numeric(10, 2), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())