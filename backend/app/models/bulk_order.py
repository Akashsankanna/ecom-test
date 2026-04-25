from sqlalchemy import Column, Integer, String, Numeric, Text, Date, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.sql import func
from app.db.base import Base


class BulkOrderRequest(Base):
    __tablename__ = "bulk_order_request"

    id                     = Column(Integer, primary_key=True, index=True)
    organization_id        = Column(Integer, ForeignKey("organization.id", ondelete="CASCADE"), nullable=True)
    user_id                = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    request_number         = Column(String(50), nullable=False, unique=True)
    # DB CHECK: PENDING|QUOTED|APPROVED|REJECTED|CONVERTED
    status                 = Column(String(20), default="PENDING")
    notes                  = Column(Text, nullable=True)
    expected_delivery_date = Column(Date, nullable=True)
    created_at             = Column(TIMESTAMP, server_default=func.now())
    updated_at             = Column(TIMESTAMP, server_default=func.now())


class BulkOrderRequestItem(Base):
    __tablename__ = "bulk_order_request_item"

    id               = Column(Integer, primary_key=True, index=True)
    bulk_request_id  = Column(Integer, ForeignKey("bulk_order_request.id", ondelete="CASCADE"), nullable=True)
    variant_id       = Column(Integer, ForeignKey("product_variant.id"), nullable=True)
    quantity         = Column(Integer, nullable=False)
    requested_price  = Column(Numeric(10, 2), nullable=True)
    quoted_price     = Column(Numeric(10, 2), nullable=True)
    notes            = Column(Text, nullable=True)


class BulkOrder(Base):
    __tablename__ = "bulk_order"

    id                     = Column(Integer, primary_key=True, index=True)
    bulk_request_id        = Column(Integer, ForeignKey("bulk_order_request.id", ondelete="SET NULL"), nullable=True, unique=True)
    organization_id        = Column(Integer, ForeignKey("organization.id"), nullable=True)
    order_number           = Column(String(50), nullable=False, unique=True)
    address_id             = Column(Integer, ForeignKey("address.id"), nullable=True)
    total_amount           = Column(Numeric(12, 2), nullable=False)
    # DB CHECK: PLACED|CONFIRMED|PROCESSING|SHIPPED|DELIVERED|CANCELLED
    status                 = Column(String(20), default="PLACED")
    # DB CHECK: PENDING|PAID|PARTIAL|FAILED
    payment_status         = Column(String(20), default="PENDING")
    created_by             = Column(Integer, ForeignKey("users.id"), nullable=True)
    updated_by             = Column(Integer, ForeignKey("users.id"), nullable=True)
    # new in ecomdb21
    expected_delivery_date = Column(Date, nullable=True)
    is_urgent              = Column(Boolean, default=False)
    # trigger fn_set_bulk_order_urgency auto-sets is_urgent based on expected_delivery_date
    created_at             = Column(TIMESTAMP, server_default=func.now())
    updated_at             = Column(TIMESTAMP, server_default=func.now())


class BulkOrderItem(Base):
    __tablename__ = "bulk_order_item"

    id           = Column(Integer, primary_key=True, index=True)
    bulk_order_id = Column(Integer, ForeignKey("bulk_order.id", ondelete="CASCADE"), nullable=True)
    variant_id   = Column(Integer, ForeignKey("product_variant.id"), nullable=True)
    quantity     = Column(Integer, nullable=False)
    price        = Column(Numeric(10, 2), nullable=False)
    # subtotal is GENERATED ALWAYS AS quantity*price STORED — read-only