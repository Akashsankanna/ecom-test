from sqlalchemy import Column, Integer, ForeignKey, DateTime, text
from app.db.session import Base


class Wishlist(Base):
    __tablename__ = "wishlist"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    guest_id = Column(Integer, ForeignKey("guest.id"), nullable=True)

    product_id = Column(Integer, ForeignKey("product.id"), nullable=False)
    variant_id = Column(Integer, ForeignKey("product_variant.id"), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"))