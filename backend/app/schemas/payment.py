from pydantic import BaseModel
from typing import Optional


class RazorpayCreateOrderRequest(BaseModel):
    amount: float
    currency: str = "INR"
    receipt: str
    user_id: Optional[int] = None


class RazorpayVerifyPaymentRequest(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str
    user_id: int
    address_id: int