from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text,DateTime
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.sql import func
from app.db.base import Base


class Product(Base):
    __tablename__ = "product"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(Text, nullable=False)
    description = Column(Text)
    sku = Column(Text, unique=True, nullable=False)
    category_id = Column(Integer, ForeignKey("category.id"))
    is_deleted = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)

    created_by = Column(Integer, ForeignKey("users.id"))
    updated_by = Column(Integer, ForeignKey("users.id"))

    details_and_fit = Column(Text)
    fabric_and_care = Column(Text)
    return_and_exchange = Column(Text)

    tax_rate_id = Column(Integer, ForeignKey("tax_rate.id"))

    is_bestseller = Column(Boolean, default=False)
    bestseller_marked_at = Column(TIMESTAMP(timezone=True))
    bestseller_marked_by = Column(Integer, ForeignKey("users.id"))

    slug = Column(String(255), unique=True, nullable=False)

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True))

    