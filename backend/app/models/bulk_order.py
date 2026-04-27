from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base


class BulkOrder(Base):
    __tablename__ = "bulk_order"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organization.id"), nullable=False)
    status = Column(String(50), default="PENDING", nullable=False)
    expected_delivery_date = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    total_amount = Column(Numeric(10, 2), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    organization = relationship("Organization", back_populates="bulk_orders")
    items = relationship(
        "BulkOrderItem",
        back_populates="bulk_order",
        cascade="all, delete-orphan"
    )