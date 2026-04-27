from sqlalchemy import Column, Integer, Numeric, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship

from app.db.session import Base   # change this import if your Base is in another file


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    total_amount = Column(Numeric(10, 2), nullable=False)
    status = Column(String(20), nullable=False, default="PENDING")
    address_id = Column(Integer, ForeignKey("address.id"), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    payment_status = Column(String(20), nullable=False, default="PENDING")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    transactions = relationship("PaymentTransaction", back_populates="order", cascade="all, delete-orphan")