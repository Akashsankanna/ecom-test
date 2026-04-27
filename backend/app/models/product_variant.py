from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    ForeignKey,
    Boolean,
    Numeric,
)
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.sql import func

from app.db.base import Base


class ProductVariant(Base):
    __tablename__ = "product_variant"

    # =====================================================
    # PRIMARY KEY
    # =====================================================
    id = Column(Integer, primary_key=True, index=True)

    # =====================================================
    # FOREIGN KEYS
    # =====================================================
    product_id = Column(
        Integer,
        ForeignKey("product.id", ondelete="CASCADE"),
        nullable=False
    )

    color_id = Column(
        Integer,
        ForeignKey("color.id"),
        nullable=True
    )

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

    # =====================================================
    # VARIANT DETAILS
    # =====================================================
    variant_name = Column(
        Text,
        nullable=True
    )

    price = Column(
        Numeric(10, 2),
        nullable=False
    )

    stock = Column(
        Integer,
        default=0
    )

    sku = Column(
        Text,
        unique=True,
        nullable=True
    )

    # legacy/manual color text field kept from second file
    color = Column(
        String(50),
        nullable=True
    )

    size = Column(
        String(10),
        nullable=True
    )

    reserved_stock = Column(
        Integer,
        default=0
    )

    low_stock_threshold = Column(
        Integer,
        default=5
    )

    is_deleted = Column(
        Boolean,
        default=False
    )

    # =====================================================
    # TIMESTAMPS
    # =====================================================
    created_at = Column(
        TIMESTAMP,
        server_default=func.now()
    )

    updated_at = Column(
        TIMESTAMP,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=True
    )