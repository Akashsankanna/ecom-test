from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey,
    Text,
)
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.sql import func

from app.db.base import Base


class Product(Base):
    __tablename__ = "product"

    # =====================================================
    # PRIMARY KEY
    # =====================================================
    id = Column(Integer, primary_key=True, index=True)

    # =====================================================
    # BASIC PRODUCT INFO
    # =====================================================
    name = Column(
        Text,
        nullable=False
    )

    description = Column(
        Text,
        nullable=True
    )

    sku = Column(
        Text,
        unique=True,
        nullable=False
    )

    slug = Column(
        String(255),
        unique=True,
        nullable=False
    )

    # =====================================================
    # FOREIGN KEYS
    # =====================================================
    category_id = Column(
        Integer,
        ForeignKey("category.id"),
        nullable=True
    )

    tax_rate_id = Column(
        Integer,
        ForeignKey("tax_rate.id"),
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

    bestseller_marked_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )

    # =====================================================
    # STATUS FLAGS
    # =====================================================
    is_deleted = Column(
        Boolean,
        default=False
    )

    is_active = Column(
        Boolean,
        default=True
    )

    is_bestseller = Column(
        Boolean,
        default=False
    )

    # =====================================================
    # EXTRA CONTENT
    # =====================================================
    details_and_fit = Column(
        Text,
        nullable=True
    )

    fabric_and_care = Column(
        Text,
        nullable=True
    )

    return_and_exchange = Column(
        Text,
        nullable=True
    )

    # =====================================================
    # BESTSELLER TRACKING
    # =====================================================
    bestseller_marked_at = Column(
        TIMESTAMP(timezone=True),
        nullable=True
    )

    # =====================================================
    # TIMESTAMPS
    # =====================================================
    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=True
    )