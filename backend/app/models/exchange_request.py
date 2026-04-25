from sqlalchemy import Column, Integer, Text, String, ForeignKey
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.sql import func
from app.db.base import Base


class ExchangeRequest(Base):
    __tablename__ = "exchange_requests"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"))
    order_item_id = Column(Integer, ForeignKey("order_items.id"))
    reason = Column(Text, nullable=True)
    # DB CHECK: REQUESTED | APPROVED | REJECTED | COMPLETED | CANCELLED
    status = Column(String(20), default="REQUESTED")
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now())