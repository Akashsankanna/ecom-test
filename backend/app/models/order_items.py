from sqlalchemy import (
    Column,
    Integer,
    Numeric,
    DateTime,
    ForeignKey,
    text,
)
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.base import Base


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)

    # =====================================================
    # FOREIGN KEYS
    # =====================================================
    order_id = Column(
        Integer,
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False
    )

    product_id = Column(
        Integer,
        ForeignKey("product.id"),
        nullable=False
    )

    variant_id = Column(
        Integer,
        ForeignKey("product_variant.id"),
        nullable=False
    )

    # =====================================================
    # ORDER DETAILS
    # =====================================================
    quantity = Column(Integer, nullable=False, default=1)

    price = Column(Numeric(10, 2), nullable=False)

    customization_total = Column(
        Numeric(10, 2),
        nullable=False,
        server_default=text("0")
    )

    # =====================================================
    # TIMESTAMPS
    # =====================================================
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    # =====================================================
    # RELATIONSHIPS
    # =====================================================
    order = relationship(
        "Order",
        back_populates="items"
    )