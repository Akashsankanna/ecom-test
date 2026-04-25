from sqlalchemy import Column, Integer, String, Text, Boolean, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.sql import func
from app.db.base import Base


class Coupon(Base):
    __tablename__ = "coupon"

    id = Column(Integer, primary_key=True, index=True)

    code = Column(String(50), unique=True, nullable=False, index=True)

    description = Column(Text)

    discount_type = Column(String(20), nullable=False)   # PERCENTAGE / FIXED

    discount_value = Column(Numeric(10, 2), nullable=False)

    min_order_amount = Column(Numeric(10, 2), default=0)

    max_discount_amount = Column(Numeric(10, 2))

    usage_limit = Column(Integer)

    used_count = Column(Integer, default=0)

    valid_from = Column(TIMESTAMP)

    valid_to = Column(TIMESTAMP)

    is_active = Column(Boolean, default=True)

    created_by = Column(Integer, ForeignKey("users.id"))

    updated_by = Column(Integer, ForeignKey("users.id"))

    created_at = Column(TIMESTAMP, server_default=func.now())

    updated_at = Column(
        TIMESTAMP,
        server_default=func.now(),
        onupdate=func.now()
    )