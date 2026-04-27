"""
Coupon schemas — coupon table + coupon_usage + fn_validate_coupon + sp_apply_coupon.
Import from: app.schemas.coupon
"""
from pydantic import BaseModel, field_validator
from typing import Optional
from decimal import Decimal
from datetime import datetime
from enum import Enum


class DiscountType(str, Enum):
    PERCENTAGE = "PERCENTAGE"
    FIXED      = "FIXED"


class CouponCreate(BaseModel):
    code: str
    description: Optional[str] = None
    discount_type: DiscountType
    discount_value: Decimal
    min_order_amount: Optional[Decimal] = Decimal("0")
    max_discount_amount: Optional[Decimal] = None
    usage_limit: Optional[int] = None
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None
    is_active: Optional[bool] = True

    @field_validator("discount_value")
    @classmethod
    def discount_positive(cls, v):
        if v <= 0:
            raise ValueError("discount_value must be > 0")
        return v

    @field_validator("code")
    @classmethod
    def code_uppercase(cls, v):
        return v.strip().upper()


class CouponUpdate(BaseModel):
    description: Optional[str] = None
    discount_type: Optional[DiscountType] = None
    discount_value: Optional[Decimal] = None
    min_order_amount: Optional[Decimal] = None
    max_discount_amount: Optional[Decimal] = None
    usage_limit: Optional[int] = None
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None
    is_active: Optional[bool] = None


class CouponOut(BaseModel):
    id: int
    code: str
    description: Optional[str] = None
    discount_type: str
    discount_value: Decimal
    min_order_amount: Optional[Decimal] = None
    max_discount_amount: Optional[Decimal] = None
    usage_limit: Optional[int] = None
    used_count: int
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None
    is_active: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ApplyCouponRequest(BaseModel):
    """Input for sp_apply_coupon (5-param version)."""
    coupon_code: str
    user_id: int
    order_id: int
    order_amount: Decimal
    additional_discount: Optional[Decimal] = Decimal("0")


class ApplyAdditionalDiscount(BaseModel):
    """Input for sp_apply_additional_discount stored procedure."""
    order_id: int
    discount_amount: Decimal
    reason: Optional[str] = "Manual discount"

    @field_validator("discount_amount")
    @classmethod
    def discount_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("discount_amount must be greater than zero")
        return v


class ValidateCouponRequest(BaseModel):
    """Input for fn_validate_coupon DB function."""
    coupon_code: str
    user_id: int
    order_amount: Decimal


class CouponValidationResult(BaseModel):
    coupon_id: Optional[int] = None
    discount_amount: Decimal
    message: str
