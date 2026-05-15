from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Text,
    Numeric,
    Boolean
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


# =====================================================
# BULK ORDER REQUEST
# Table: bulk_order_request
# =====================================================

class BulkOrderRequest(Base):
    __tablename__ = "bulk_order_request"

    id = Column(Integer, primary_key=True, index=True)

    organization_id = Column(
        Integer,
        ForeignKey("organization.id"),
        nullable=False,
        index=True
    )

    user_id = Column(Integer, nullable=True)

    request_number = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True
    )

    status = Column(
        String(50),
        default="PENDING",
        nullable=False,
        index=True
    )

    notes = Column(Text, nullable=True)

    expected_delivery_date = Column(DateTime, nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    organization = relationship(
        "Organization",
        back_populates="bulk_requests"
    )

    items = relationship(
        "BulkOrderRequestItem",
        back_populates="bulk_request",
        cascade="all, delete-orphan"
    )


# =====================================================
# BULK ORDER REQUEST ITEMS
# Table: bulk_order_request_item
# =====================================================

class BulkOrderRequestItem(Base):
    __tablename__ = "bulk_order_request_item"

    id = Column(Integer, primary_key=True, index=True)

    bulk_request_id = Column(
        Integer,
        ForeignKey("bulk_order_request.id"),
        nullable=False,
        index=True
    )

    variant_id = Column(
        Integer,
        ForeignKey("product_variant.id"),
        nullable=False,
        index=True
    )

    quantity = Column(Integer, nullable=False)

    requested_price = Column(Numeric(10, 2), nullable=True)

    quoted_price = Column(Numeric(10, 2), nullable=True)

    notes = Column(Text, nullable=True)

    bulk_request = relationship(
        "BulkOrderRequest",
        back_populates="items"
    )


# =====================================================
# BULK ORDER
# Table: bulk_order
# =====================================================

class BulkOrder(Base):
    __tablename__ = "bulk_order"

    id = Column(Integer, primary_key=True, index=True)

    organization_id = Column(
        Integer,
        ForeignKey("organization.id"),
        nullable=False,
        index=True
    )

    order_number = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True
    )

    status = Column(
        String(50),
        default="PENDING",
        nullable=False,
        index=True
    )

    payment_status = Column(
        String(50),
        default="PENDING",
        nullable=False
    )

    expected_delivery_date = Column(DateTime, nullable=True)

    notes = Column(Text, nullable=True)

    total_amount = Column(
        Numeric(10, 2),
        nullable=False,
        default=0
    )

    is_urgent = Column(
        Boolean,
        default=False,
        nullable=False
    )

    created_by = Column(Integer, nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

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
# Table: bulk_order_item
# =====================================================

class BulkOrderItem(Base):
    __tablename__ = "bulk_order_item"

    id = Column(Integer, primary_key=True, index=True)

    bulk_order_id = Column(
        Integer,
        ForeignKey("bulk_order.id"),
        nullable=False,
        index=True
    )

    variant_id = Column(
        Integer,
        ForeignKey("product_variant.id"),
        nullable=False,
        index=True
    )

    quantity = Column(Integer, nullable=False)

    price = Column(Numeric(10, 2), nullable=False)

    bulk_order = relationship(
        "BulkOrder",
        back_populates="items"
    )