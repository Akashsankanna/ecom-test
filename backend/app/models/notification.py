from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import TIMESTAMP, JSONB
from sqlalchemy.sql import func
from app.db.base import Base


class Notification(Base):
    __tablename__ = "notification"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    # DB CHECK: ORDER_PLACED | ORDER_CONFIRMED | ORDER_CANCELLED | PAYMENT_SUCCESS |
    #           PAYMENT_FAILED | SHIPPED | DELIVERED | EXCHANGE_REQUESTED |
    #           EXCHANGE_COMPLETED | COUPON_APPLIED | PROMOTIONAL | REVIEW_REMINDER
    notification_type = Column(String(20), nullable=False)
    # DB CHECK: EMAIL | SMS | PUSH | IN_APP
    channel = Column(String(20), nullable=False)
    title = Column(Text, nullable=False)
    message = Column(Text, nullable=False)
    reference_id = Column(Integer, nullable=True)
    reference_type = Column(String(30), nullable=True)
    # DB CHECK: PENDING | SENT | FAILED
    status = Column(String(20), default="PENDING")
    is_read = Column(Boolean, default=False)
    sent_at = Column(TIMESTAMP, nullable=True)
    external_message_id = Column(String(100), nullable=True)
    provider_response = Column(JSONB, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now())