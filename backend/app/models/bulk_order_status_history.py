from sqlalchemy import Column, Integer, String, Numeric, Text, Date, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.sql import func
from app.db.base import Base

class BulkOrderStatusHistory(Base):
    __tablename__ = "bulk_order_status_history"

    id            = Column(Integer, primary_key=True, index=True)
    bulk_order_id = Column(Integer, ForeignKey("bulk_order.id", ondelete="CASCADE"), nullable=True)
    status        = Column(String(20), nullable=False)
    changed_at    = Column(TIMESTAMP, server_default=func.now())
    changed_by    = Column(Integer, ForeignKey("users.id"), nullable=True)
    notes         = Column(Text, nullable=True)