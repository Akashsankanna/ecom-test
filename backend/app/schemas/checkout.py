from typing import Optional

from pydantic import BaseModel, Field, field_validator


class CheckoutRequest(BaseModel):
    user_id: int = Field(..., gt=0)
    address_id: int = Field(..., gt=0)
    coupon_code: Optional[str] = None
    shipping_amount: float = Field(default=0, ge=0)
    payment_method: str = Field(..., min_length=2, max_length=50)

    @field_validator("coupon_code")
    @classmethod
    def normalize_coupon(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        value = value.strip().upper()
        return value if value else None

    @field_validator("payment_method")
    @classmethod
    def normalize_payment_method(cls, value: str) -> str:
        value = value.strip().upper()
        if not value:
            raise ValueError("payment_method cannot be empty")
        return value


class PaymentRequest(BaseModel):
    order_id: int = Field(..., gt=0)
    payment_method: str = Field(..., min_length=2, max_length=50)
    payment_status: str = Field(..., min_length=2, max_length=20)
    transaction_ref: str = Field(..., min_length=2, max_length=100)

    @field_validator("payment_method")
    @classmethod
    def normalize_payment_method(cls, value: str) -> str:
        value = value.strip().upper()
        if not value:
            raise ValueError("payment_method cannot be empty")
        return value

    @field_validator("payment_status")
    @classmethod
    def validate_payment_status(cls, value: str) -> str:
        value = value.strip().upper()
        allowed = {"SUCCESS", "FAILED", "PENDING"}
        if not value:
            raise ValueError("payment_status cannot be empty")
        if value not in allowed:
            raise ValueError(f"payment_status must be one of {allowed}")
        return value

    @field_validator("transaction_ref")
    @classmethod
    def normalize_transaction_ref(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("transaction_ref cannot be empty")
        return value


class RazorpayCreateOrderRequest(BaseModel):
    user_id: int = Field(..., gt=0)
    amount: float = Field(..., gt=0)
    currency: str = Field(default="INR", min_length=3, max_length=10)
    receipt: str = Field(..., min_length=2, max_length=100)

    @field_validator("currency")
    @classmethod
    def normalize_currency(cls, value: str) -> str:
        value = value.strip().upper()
        if not value:
            raise ValueError("currency cannot be empty")
        return value

    @field_validator("receipt")
    @classmethod
    def normalize_receipt(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("receipt cannot be empty")
        return value


class RazorpayVerifyPaymentRequest(BaseModel):
    order_id: int = Field(..., gt=0)
    razorpay_order_id: str = Field(..., min_length=2, max_length=100)
    razorpay_payment_id: str = Field(..., min_length=2, max_length=100)
    razorpay_signature: str = Field(..., min_length=2, max_length=255)

    @field_validator("razorpay_order_id", "razorpay_payment_id", "razorpay_signature")
    @classmethod
    def strip_values(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Field cannot be empty")
        return value