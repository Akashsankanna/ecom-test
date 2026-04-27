from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from decimal import Decimal
from datetime import datetime, date
from enum import Enum


# =====================================================
# ENUMS
# =====================================================

class DiscountType(str, Enum):
    PERCENTAGE = "PERCENTAGE"
    FIXED = "FIXED"


class TransactionStatus(str, Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"


class BulkRequestStatus(str, Enum):
    PENDING = "PENDING"
    QUOTED = "QUOTED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CONVERTED = "CONVERTED"


class BulkOrderStatus(str, Enum):
    PLACED = "PLACED"
    CONFIRMED = "CONFIRMED"
    PROCESSING = "PROCESSING"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"


class BulkPaymentStatus(str, Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    PARTIAL = "PARTIAL"
    FAILED = "FAILED"


# =====================================================
# REQUEST / INPUT SCHEMAS
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


class BulkOrderConvert(BaseModel):
    address_id: int


class BulkRequestStatusUpdate(BaseModel):
    status: BulkRequestStatus


class BulkOrderStatusUpdate(BaseModel):
    status: BulkOrderStatus


class OrganizationCreate(BaseModel):
    name: str
    contact_person: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    gst_number: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = "India"
    postal_code: Optional[str] = None
    is_active: Optional[bool] = True


# =====================================================
# RESPONSE / OUTPUT SCHEMAS
# =====================================================

class BulkOrderRequestResponse(BaseModel):
    success: bool
    message: str
    bulk_request_id: int
    request_number: str
    organization_id: int


class BulkRequestItemOut(BaseModel):
    id: int
    variant_id: Optional[int] = None
    quantity: int
    requested_price: Optional[Decimal] = None
    quoted_price: Optional[Decimal] = None
    notes: Optional[str] = None

    class Config:
        from_attributes = True


class BulkRequestOut(BaseModel):
    id: int
    organization_id: Optional[int] = None
    user_id: Optional[int] = None
    request_number: str
    status: str
    notes: Optional[str] = None
    expected_delivery_date: Optional[date] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class BulkOrderOut(BaseModel):
    id: int
    order_number: str
    organization_id: Optional[int] = None
    total_amount: Decimal
    status: str
    payment_status: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class OrganizationOut(BaseModel):
    id: int
    name: str
    contact_person: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    gst_number: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True