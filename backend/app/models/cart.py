from sqlalchemy import Column, Integer, Numeric, ForeignKey, DateTime, text
from app.db.session import Base


class CartItem(Base):
    __tablename__ = "cart_item"

    id = Column(Integer, primary_key=True, index=True)

    cart_id = Column(Integer, ForeignKey("cart.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey("product.id"), nullable=False)
    variant_id = Column(Integer, ForeignKey("product_variant.id"), nullable=False)

    quantity = Column(Integer, nullable=False, default=1)
    price = Column(Numeric(10, 2), nullable=False)
    customization_total = Column(Numeric(10, 2), nullable=False, server_default=text("0"))

    created_at = Column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"))