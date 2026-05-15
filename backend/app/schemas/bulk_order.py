from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import date
from enum import Enum


# =====================================================
# BULK ORDER STATUS ENUM
# =====================================================

class BulkOrderStatusEnum(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    converted = "converted"
    processing = "processing"
    confirmed = "confirmed"
    shipped = "shipped"
    delivered = "delivered"
    cancelled = "cancelled"


# =====================================================
# PUBLIC BULK ORDER REQUEST SCHEMAS
# =====================================================

class BulkOrderItemCreate(BaseModel):
    product_category_id: int
    quantity: int = Field(..., gt=0)
    size: str
    gender: Optional[str] = None
    color: Optional[str] = None


class BulkOrderRequestCreate(BaseModel):
    user_id: Optional[int] = None

    organization_name: str
    contact_person: str
    email: Optional[EmailStr] = None
    phone: str
    gst_number: Optional[str] = None
    state: str
    city: str
    address: str
    postal_code: str

    expected_delivery_date: Optional[date] = None
    fabric_preference: Optional[str] = None
    additional_requirements: Optional[str] = None
    branding_required: bool = False

    items: List[BulkOrderItemCreate]


class BulkOrderRequestResponse(BaseModel):
    success: bool
    message: str
    bulk_request_id: int
    request_number: str
    organization_id: int


# =====================================================
# ADMIN ORGANIZATION SCHEMA
# Used in admin/bulk_admin.py
# =====================================================

class OrganizationCreate(BaseModel):
    name: str
    contact_person: str
    email: EmailStr
    phone: str
    gst_number: Optional[str] = None
    state: str
    city: str
    address: Optional[str] = None
    postal_code: Optional[str] = None


# =====================================================
# ADMIN BULK REQUEST CONVERT SCHEMA
# Used in admin/bulk_admin.py
# =====================================================

class BulkOrderConvert(BaseModel):
    payment_status: Optional[str] = "pending"
    payment_method: Optional[str] = "razorpay"
    shipping_amount: Optional[float] = 0
    discount_amount: Optional[float] = 0
    is_urgent: Optional[bool] = False
    expected_delivery_date: Optional[date] = None
    notes: Optional[str] = None


# =====================================================
# ADMIN BULK ORDER STATUS UPDATE SCHEMA
# Used in admin/bulk_admin.py
# =====================================================

class BulkOrderStatusUpdate(BaseModel):
    status: BulkOrderStatusEnum
    notes: Optional[str] = None