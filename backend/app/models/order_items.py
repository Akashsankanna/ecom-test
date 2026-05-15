from sqlalchemy import (
    Column,
    Integer,
    Numeric,
    DateTime,
    ForeignKey,
    text,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.base import Base


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)

    order_id = Column(
        Integer,
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    product_id = Column(
        Integer,
        ForeignKey("product.id"),
        nullable=True,
        index=True,
    )

    variant_id = Column(
        Integer,
        ForeignKey("product_variant.id"),
        nullable=False,
        index=True,
    )

    quantity = Column(Integer, nullable=False, default=1)

    # Your old backend uses price
    price = Column(Numeric(10, 2), nullable=True)

    # Your payment service / DB view may use unit_price
    unit_price = Column(Numeric(10, 2), nullable=True)

    customization_total = Column(
        Numeric(10, 2),
        nullable=False,
        server_default=text("0"),
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    order = relationship(
        "Order",
        back_populates="items",
    )