from pydantic import BaseModel,EmailStr
from typing import Optional
from decimal import Decimal
from datetime import datetime, date
from enum import Enum



# ════════════════════════════════════════════════════════════
# ENUMS
# ════════════════════════════════════════════════════════════

class DiscountType(str, Enum):
    PERCENTAGE = "PERCENTAGE"
    FIXED      = "FIXED"


class TransactionStatus(str, Enum):
    PENDING  = "PENDING"
    SUCCESS  = "SUCCESS"
    FAILED   = "FAILED"
    REFUNDED = "REFUNDED"


class BulkRequestStatus(str, Enum):
    PENDING   = "PENDING"
    QUOTED    = "QUOTED"
    APPROVED  = "APPROVED"
    REJECTED  = "REJECTED"
    CONVERTED = "CONVERTED"


class BulkOrderStatus(str, Enum):
    PLACED     = "PLACED"
    CONFIRMED  = "CONFIRMED"
    PROCESSING = "PROCESSING"
    SHIPPED    = "SHIPPED"
    DELIVERED  = "DELIVERED"
    CANCELLED  = "CANCELLED"


class BulkPaymentStatus(str, Enum):
    PENDING = "PENDING"
    PAID    = "PAID"
    PARTIAL = "PARTIAL"
    FAILED  = "FAILED"


# ════════════════════════════════════════════════════════════
# REQUEST / INPUT SCHEMAS
# ════════════════════════════════════════════════════════════

class BulkOrderConvert(BaseModel):
    address_id: int


class BulkRequestStatusUpdate(BaseModel):
    status: BulkRequestStatus


class BulkOrderStatusUpdate(BaseModel):        # ← THIS WAS MISSING
    status: BulkOrderStatus


# ════════════════════════════════════════════════════════════
# RESPONSE / OUTPUT SCHEMAS
# ════════════════════════════════════════════════════════════

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
    email: Optional[str] = None
    phone: Optional[str] = None
    gst_number: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True

# Add this to your existing bulk_order.py schemas file

class OrganizationCreate(BaseModel):
    name: str
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    gst_number: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = "India"
    postal_code: Optional[str] = None
    is_active: Optional[bool] = True