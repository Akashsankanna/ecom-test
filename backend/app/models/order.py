from sqlalchemy import Column, Integer, Numeric, String, ForeignKey, Text, Computed
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.sql import func
from app.db.base import Base


class Order(Base):
    __tablename__ = "orders"

    id                         = Column(Integer, primary_key=True, index=True)
    user_id                    = Column(Integer, ForeignKey("users.id"), nullable=True)
    total_amount               = Column(Numeric(10, 2), nullable=False)
    status                     = Column(String(20), default="PENDING")
    address_id                 = Column(Integer, ForeignKey("address.id"), nullable=True)
    payment_status             = Column(String(20), default="PENDING")
    created_by                 = Column(Integer, ForeignKey("users.id"), nullable=True)
    updated_by                 = Column(Integer, ForeignKey("users.id"), nullable=True)
    # new in ecomdb21
    coupon_id                  = Column(Integer, ForeignKey("coupon.id"), nullable=True)
    coupon_discount_amount     = Column(Numeric(12, 2), default=0)
    additional_discount_amount = Column(Numeric(12, 2), default=0)
    # final_amount is GENERATED ALWAYS AS STORED — read-only, do NOT write to it
    final_amount               = Column(Numeric(12, 2), Computed(
        "(total_amount - coupon_discount_amount) - additional_discount_amount",
        persisted=True
    ))
    discount_reason            = Column(Text, nullable=True)
    # ─────────────────────────────────────────────────────────
    created_at                 = Column(TIMESTAMP, server_default=func.now())
    updated_at                 = Column(TIMESTAMP, server_default=func.now())