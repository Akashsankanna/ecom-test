from fastapi import APIRouter
from app.schemas.payment import (
    RazorpayCreateOrderRequest,
    RazorpayVerifyPaymentRequest
)
from app.services.payment_service import (
    create_razorpay_order_service,
    verify_razorpay_payment_service
)

router = APIRouter(prefix="/razorpay", tags=["Razorpay"])


@router.post("/create-order")
def create_razorpay_order(data: RazorpayCreateOrderRequest):
    return create_razorpay_order_service(
        amount=data.amount,
        currency=data.currency,
        receipt=data.receipt
    )


@router.post("/verify-payment")
def verify_razorpay_payment(data: RazorpayVerifyPaymentRequest):
    return verify_razorpay_payment_service(
        razorpay_order_id=data.razorpay_order_id,
        razorpay_payment_id=data.razorpay_payment_id,
        razorpay_signature=data.razorpay_signature,
                
    )