# app/schemas/admin.py

"""
CENTRAL ADMIN COMPATIBILITY SCHEMA FILE

Purpose:
- Old routes importing from app.schemas.admin continue to work
- New split schema structure also works
- Prevents ImportError / ModuleNotFoundError

Paste this file inside:

app/schemas/admin.py
"""

from pydantic import BaseModel, field_validator
from typing import Optional, List, Dict, Any
from decimal import Decimal
from datetime import datetime, date
from enum import Enum


# ==========================================================
# IMPORT FROM SPLIT FILES (safe fallback)
# ==========================================================

# user.py
try:
    from app.schemas.user import *
except:
    pass

# auth.py
try:
    from app.schemas.auth import *
except:
    pass

# payment.py
try:
    from app.schemas.payment import *
except:
    pass

# bulk_order.py
try:
    from app.schemas.bulk_order import *
except:
    pass

# coupon.py
try:
    from app.schemas.coupon import *
except:
    pass

# notification.py
try:
    from app.schemas.notification import *
except:
    pass

# review.py
try:
    from app.schemas.review import *
except:
    pass

# analytics.py
try:
    from app.schemas.analytics import *
except:
    pass


# ==========================================================
# ENUMS
# ==========================================================

class AddressType(str, Enum):
    HOME = "HOME"
    WORK = "WORK"
    OTHER = "OTHER"


class GenderType(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


# ==========================================================
# TAX RATE
# ==========================================================

class TaxRateCreate(BaseModel):
    name: str
    rate: float

    @field_validator("rate")
    @classmethod
    def validate_rate(cls, v):
        if v < 0 or v > 100:
            raise ValueError("Rate must be between 0 and 100")
        return v


class TaxRateUpdate(BaseModel):
    name: Optional[str] = None
    rate: Optional[float] = None
    is_active: Optional[bool] = None


class TaxRateOut(BaseModel):
    id: int
    name: str
    rate: Decimal
    is_active: bool

    class Config:
        from_attributes = True


# ==========================================================
# SIZE MASTER
# ==========================================================

class SizeCreate(BaseModel):
    size_code: str
    sort_order: Optional[int] = None


class SizeOut(BaseModel):
    id: int
    size_code: str
    sort_order: Optional[int] = None

    class Config:
        from_attributes = True


# ==========================================================
# ADDITIONAL DISCOUNT
# ==========================================================

class ApplyAdditionalDiscount(BaseModel):
    order_id: int
    discount_amount: Decimal
    reason: Optional[str] = "Manual Discount"

    @field_validator("discount_amount")
    @classmethod
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError("Discount must be > 0")
        return v


# ==========================================================
# ADDRESS
# ==========================================================

class AddressCreate(BaseModel):
    full_name: str
    phone: str
    address_line1: str
    address_line2: Optional[str] = None
    landmark: Optional[str] = None
    city: str
    state: str
    country: Optional[str] = "India"
    postal_code: str
    address_type: AddressType = AddressType.HOME
    is_default: Optional[bool] = False


class AddressUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    landmark: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    address_type: Optional[AddressType] = None
    is_default: Optional[bool] = None


class AddressOut(BaseModel):
    id: int
    user_id: int
    full_name: str
    phone: str
    address_line1: str
    city: str
    state: str
    postal_code: str
    is_default: bool

    class Config:
        from_attributes = True


# ==========================================================
# BESTSELLER
# ==========================================================

class BestsellerToggle(BaseModel):
    is_bestseller: bool


# ==========================================================
# FALLBACK BULK SCHEMAS
# ==========================================================

class BulkOrderStatusUpdate(BaseModel):
    status: str


class BulkRequestStatusUpdate(BaseModel):
    status: str


class BulkOrderConvert(BaseModel):
    address_id: int


# ==========================================================
# FALLBACK PAYMENT
# ==========================================================

class InvoiceCreate(BaseModel):
    order_id: int
    invoice_number: str


class InvoiceOut(BaseModel):
    id: int
    order_id: int
    invoice_number: str

    class Config:
        from_attributes = True


# ==========================================================
# DASHBOARD FALLBACK
# ==========================================================

class DashboardOut(BaseModel):
    total_users: int
    total_products: int
    total_orders: int
    total_revenue: float