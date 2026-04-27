from sqlalchemy import Column, Integer, Numeric, DateTime, ForeignKey, text
from sqlalchemy.orm import relationship
from app.db.base import Base


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)

    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey("product.id"), nullable=False)
    variant_id = Column(Integer, ForeignKey("product_variant.id"), nullable=False)

    quantity = Column(Integer, nullable=False, default=1)
    price = Column(Numeric(10, 2), nullable=False)
    customization_total = Column(Numeric(10, 2), nullable=False, server_default=text("0"))

    created_at = Column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"))

    order = relationship("Order", back_populates="items")