from sqlalchemy import Column, Integer, String, Text, Boolean, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.sql import func
from app.db.base import Base


class CustomizationType(Base):
    """Types of customization: e.g. embroidery, print, monogram."""
    __tablename__ = "customization_type"

    id              = Column(Integer, primary_key=True, index=True)
    name            = Column(String(50), nullable=False)
    description     = Column(Text, nullable=True)
    is_active       = Column(Boolean, default=True)
    # new in ecomdb21
    additional_price = Column(Numeric(10, 2), default=0)
    created_at      = Column(TIMESTAMP(timezone=True), server_default=func.now())


class CustomizationPosition(Base):
    """Where on the garment: e.g. chest, sleeve, back."""
    __tablename__ = "customization_position"

    id              = Column(Integer, primary_key=True, index=True)
    name            = Column(String(50), nullable=False)
    description     = Column(Text, nullable=True)
    # new in ecomdb21
    additional_price = Column(Numeric(10, 2), default=0)
    created_at      = Column(TIMESTAMP(timezone=True), server_default=func.now())


class ProductCustomization(Base):
    """Which customizations are allowed per product."""
    __tablename__ = "product_customization"

    id                    = Column(Integer, primary_key=True, index=True)
    product_id            = Column(Integer, ForeignKey("product.id", ondelete="CASCADE"), nullable=False)
    customization_type_id = Column(Integer, ForeignKey("customization_type.id"), nullable=False)
    price                 = Column(Numeric(10, 2), default=0)
    is_required           = Column(Boolean, default=False)
    max_text_length       = Column(Integer, nullable=True)
    allowed_file_types    = Column(String(100), nullable=True)
    # new in ecomdb21
    is_active             = Column(Boolean, default=True)
    created_at            = Column(TIMESTAMP(timezone=True), server_default=func.now())


class OrderItemCustomization(Base):
    """Actual customization applied to an ordered item."""
    __tablename__ = "order_item_customization"

    id                    = Column(Integer, primary_key=True, index=True)
    order_item_id         = Column(Integer, ForeignKey("order_items.id", ondelete="CASCADE"), nullable=False)
    customization_type_id = Column(Integer, ForeignKey("customization_type.id"), nullable=False)
    position_id           = Column(Integer, ForeignKey("customization_position.id"), nullable=True)
    text_value            = Column(String(255), nullable=True)
    image_url             = Column(Text, nullable=True)
    image_name            = Column(String(255), nullable=True)
    approved_by           = Column(Integer, ForeignKey("users.id"), nullable=True)
    # DB CHECK: PENDING | APPROVED | REJECTED
    approval_status       = Column(String(20), default="PENDING")
    # new in ecomdb21
    customization_value   = Column(Text, nullable=True)
    approved              = Column(Boolean, default=False)
    additional_price      = Column(Numeric(10, 2), default=0)
    created_at            = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at            = Column(TIMESTAMP(timezone=True), server_default=func.now())