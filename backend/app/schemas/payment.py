"""
Payment schemas
Supports:
- transactions table
- invoice table
- Razorpay payment flow

Stored Procedures:
- sp_process_payment

Import from:
app.schemas.payment
"""

from pydantic import BaseModel
from typing import Optional, Dict, Any
from decimal import Decimal
from datetime import datetime
from enum import Enum


# =====================================================
# ENUMS
# =====================================================

class TransactionStatus(str, Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"


class PaymentMethod(str, Enum):
    UPI = "UPI"
    CARD = "CARD"
    NET_BANKING = "NET_BANKING"
    NEFT = "NEFT"
    RTGS = "RTGS"
    COD = "COD"
    BANK_TRANSFER = "BANK_TRANSFER"
    RAZORPAY = "RAZORPAY"


# =====================================================
# PAYMENT PROCESSING
# =====================================================

class ProcessPaymentRequest(BaseModel):
    order_id: int
    payment_method: PaymentMethod
    status: TransactionStatus
    transaction_ref: str


# =====================================================
# RAZORPAY REQUESTS
# =====================================================

class RazorpayCreateOrderRequest(BaseModel):
    # ✅ frontend should not send amount
    # backend will calculate from cart + coupon + DB logic
    user_id: int
    address_id: int
    coupon_code: Optional[str] = None
    currency: str = "INR"


class RazorpayVerifyPaymentRequest(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str

    user_id: int
    address_id: int

    # optional only for compatibility
    order_id: Optional[int] = None


# =====================================================
# TRANSACTION OUTPUTS
# =====================================================

class TransactionOut(BaseModel):
    id: int
    order_id: Optional[int] = None
    amount: Decimal
    payment_method: Optional[str] = None
    status: str

    transaction_ref: Optional[str] = None
    payment_gateway: Optional[str] = None
    gateway_transaction_id: Optional[str] = None
    currency: Optional[str] = None

    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PaymentViewOut(BaseModel):
    transaction_id: int
    order_id: Optional[int] = None

    amount: Optional[Decimal] = None
    payment_method: Optional[str] = None
    status: Optional[str] = None

    user_id: Optional[int] = None
    total_amount: Optional[Decimal] = None
    order_status: Optional[str] = None

    class Config:
        from_attributes = True


# =====================================================
# INVOICE
# =====================================================

class InvoiceCreate(BaseModel):
    order_id: int
    invoice_number: str
    gst_number: Optional[str] = None
    total_tax: Optional[float] = None
    billing_address: Optional[Dict[str, Any]] = None


class InvoiceOut(BaseModel):
    id: int
    order_id: Optional[int] = None
    invoice_number: str

    invoice_date: Optional[datetime] = None
    billing_address: Optional[Dict[str, Any]] = None
    gst_number: Optional[str] = None
    total_tax: Optional[Decimal] = None

    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# =====================================================
# REVENUE SUMMARY
# =====================================================

class RevenueSummaryOut(BaseModel):
    total_transactions: Optional[int] = None
    total_amount: Optional[Decimal] = None
    successful_amount: Optional[Decimal] = None
    refunded_amount: Optional[Decimal] = None