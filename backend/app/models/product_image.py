from sqlalchemy import Column, Integer, Text, Boolean, ForeignKey, String
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.sql import func
from app.db.base import Base


class ProductImage(Base):
    __tablename__ = "product_image"
    id = Column(Integer, primary_key=True, index=True)

    product_id = Column(Integer, ForeignKey("product.id", ondelete="CASCADE"))
    variant_id = Column(Integer, ForeignKey("product_variant.id"), nullable=True)

    image_url = Column(Text, nullable=False)
    image_name = Column(String(255), nullable=True)

    is_primary = Column(Boolean, default=False)

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, nullable=True)