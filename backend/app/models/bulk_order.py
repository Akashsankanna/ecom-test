from sqlalchemy import (
    Column,
    Integer,
    String,
    Numeric,
    Text,
    Date,
    DateTime,
    Boolean,
    ForeignKey,
)
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.base import Base


# =====================================================
# BULK ORDER REQUEST
# =====================================================
class BulkOrderRequest(Base):
    __tablename__ = "bulk_order_request"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(
        Integer,
        ForeignKey("organization.id", ondelete="CASCADE"),
        nullable=True
    )
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )
    request_number = Column(String(50), unique=True, nullable=False)

    # PENDING | QUOTED | APPROVED | REJECTED | CONVERTED
    status = Column(String(20), default="PENDING")

    notes = Column(Text, nullable=True)
    expected_delivery_date = Column(Date, nullable=True)

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now())

    # Relationships
    items = relationship(
        "BulkOrderRequestItem",
        back_populates="bulk_request",
        cascade="all, delete-orphan"
    )


# =====================================================
# BULK ORDER REQUEST ITEMS
# =====================================================
class BulkOrderRequestItem(Base):
    __tablename__ = "bulk_order_request_item"

    id = Column(Integer, primary_key=True, index=True)

    bulk_request_id = Column(
        Integer,
        ForeignKey("bulk_order_request.id", ondelete="CASCADE"),
        nullable=True
    )

    variant_id = Column(
        Integer,
        ForeignKey("product_variant.id"),
        nullable=True
    )

    quantity = Column(Integer, nullable=False)

    requested_price = Column(Numeric(10, 2), nullable=True)
    quoted_price = Column(Numeric(10, 2), nullable=True)

    notes = Column(Text, nullable=True)

    # Relationships
    bulk_request = relationship(
        "BulkOrderRequest",
        back_populates="items"
    )


# =====================================================
# BULK ORDER
# =====================================================
class BulkOrder(Base):
    __tablename__ = "bulk_order"

    id = Column(Integer, primary_key=True, index=True)

    bulk_request_id = Column(
        Integer,
        ForeignKey("bulk_order_request.id", ondelete="SET NULL"),
        unique=True,
        nullable=True
    )

    organization_id = Column(
        Integer,
        ForeignKey("organization.id"),
        nullable=True
    )

    order_number = Column(String(50), unique=True, nullable=False)

    address_id = Column(
        Integer,
        ForeignKey("address.id"),
        nullable=True
    )

    total_amount = Column(Numeric(12, 2), nullable=False)

    # PLACED | CONFIRMED | PROCESSING | SHIPPED | DELIVERED | CANCELLED
    status = Column(String(20), default="PLACED")

    # PENDING | PAID | PARTIAL | FAILED
    payment_status = Column(String(20), default="PENDING")

    created_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )

    updated_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )

    expected_delivery_date = Column(Date, nullable=True)

    is_urgent = Column(Boolean, default=False)

    notes = Column(Text, nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    # Relationships
    organization = relationship(
        "Organization",
        back_populates="bulk_orders"
    )

    items = relationship(
        "BulkOrderItem",
        back_populates="bulk_order",
        cascade="all, delete-orphan"
    )


# =====================================================
# BULK ORDER ITEMS
# =====================================================
class BulkOrderItem(Base):
    __tablename__ = "bulk_order_item"

    id = Column(Integer, primary_key=True, index=True)

    bulk_order_id = Column(
        Integer,
        ForeignKey("bulk_order.id", ondelete="CASCADE"),
        nullable=True
    )

    variant_id = Column(
        Integer,
        ForeignKey("product_variant.id"),
        nullable=True
    )

    quantity = Column(Integer, nullable=False)

    price = Column(Numeric(10, 2), nullable=False)

    # subtotal generated in DB

    # Relationships
    bulk_order = relationship(
        "BulkOrder",
        back_populates="items"
    )