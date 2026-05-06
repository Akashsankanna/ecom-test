from sqlalchemy import (
    Column,
    Integer,
    Numeric,
    String,
    DateTime,
    ForeignKey,
    Text,
    Computed,
    func,
)
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import relationship

from app.db.base import Base


class Order(Base):
    __tablename__ = "orders"

    # =====================================================
    # PRIMARY KEY
    # =====================================================
    id = Column(Integer, primary_key=True, index=True)

    # =====================================================
    # FOREIGN KEYS
    # =====================================================
    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )

    address_id = Column(
        Integer,
        ForeignKey("address.id"),
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

    coupon_id = Column(
        Integer,
        ForeignKey("coupon.id"),
        nullable=True
    )

    # =====================================================
    # ORDER DETAILS
    # =====================================================
    total_amount = Column(
        Numeric(10, 2),
        nullable=False
    )

    status = Column(
        String(20),
        nullable=False,
        default="PENDING"
    )

    payment_status = Column(
        String(20),
        nullable=False,
        default="PENDING"
    )

    coupon_discount_amount = Column(
        Numeric(12, 2),
        default=0
    )

    additional_discount_amount = Column(
        Numeric(12, 2),
        default=0
    )

    # DB generated final payable amount
    final_amount = Column(
        Numeric(12, 2),
        Computed(
            "(total_amount - coupon_discount_amount) - additional_discount_amount",
            persisted=True
        )
    )

    discount_reason = Column(
        Text,
        nullable=True
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
    items = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan"
    )

    transactions = relationship(
        "PaymentTransaction",
        back_populates="order",
        cascade="all, delete-orphan"
    )# =====================================================
# MISSING FIELDS (ADD THIS)
# =====================================================

    gross_amount = Column(
        Numeric(12, 2),
        nullable=True
    )

    transaction_id = Column(
         Integer,
         nullable=True
    )
    shipment = relationship(
    "Shipment",
    back_populates="order",
    uselist=False   # because 1 order = 1 shipment
)