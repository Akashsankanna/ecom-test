from sqlalchemy import Column, Integer, DateTime, ForeignKey, text
from sqlalchemy.orm import relationship
from app.db.session import Base


class Cart(Base):
    __tablename__ = "cart"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    guest_id = Column(Integer, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"))

    items = relationship("CartItem", cascade="all, delete-orphan")