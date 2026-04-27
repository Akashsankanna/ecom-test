# app/schemas/notification.py

from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum


# ════════════════════════════════════════════════════════════
# ENUMS
# ════════════════════════════════════════════════════════════

class NotificationType(str, Enum):
    """DB CHECK constraints exactly."""
    ORDER_PLACED       = "ORDER_PLACED"
    ORDER_CONFIRMED    = "ORDER_CONFIRMED"
    ORDER_CANCELLED    = "ORDER_CANCELLED"
    PAYMENT_SUCCESS    = "PAYMENT_SUCCESS"
    PAYMENT_FAILED     = "PAYMENT_FAILED"
    SHIPPED            = "SHIPPED"
    DELIVERED          = "DELIVERED"
    EXCHANGE_REQUESTED = "EXCHANGE_REQUESTED"
    EXCHANGE_COMPLETED = "EXCHANGE_COMPLETED"
    COUPON_APPLIED     = "COUPON_APPLIED"
    PROMOTIONAL        = "PROMOTIONAL"
    REVIEW_REMINDER    = "REVIEW_REMINDER"
    REFUND_PROCESSED   = "REFUND_PROCESSED"  # ecomdb21


class NotificationChannel(str, Enum):
    EMAIL  = "EMAIL"
    SMS    = "SMS"
    PUSH   = "PUSH"
    IN_APP = "IN_APP"


class NotificationStatus(str, Enum):
    PENDING = "PENDING"
    SENT    = "SENT"
    FAILED  = "FAILED"


class AddressType(str, Enum):
    HOME  = "HOME"
    WORK  = "WORK"
    OTHER = "OTHER"


class GenderType(str, Enum):
    MALE   = "male"
    FEMALE = "female"
    OTHER  = "other"


# ════════════════════════════════════════════════════════════
# NOTIFICATION SCHEMAS
# ════════════════════════════════════════════════════════════

class NotificationCreate(BaseModel):
    """Input for sp_create_notification stored procedure."""
    user_id: int
    notification_type: NotificationType
    channel: NotificationChannel
    title: str
    message: str
    reference_id: Optional[int] = None
    reference_type: Optional[str] = None


class NotificationOut(BaseModel):
    id: int
    user_id: Optional[int] = None
    notification_type: str
    channel: str
    title: str
    message: str
    reference_id: Optional[int] = None
    reference_type: Optional[str] = None
    status: str
    is_read: bool
    sent_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True