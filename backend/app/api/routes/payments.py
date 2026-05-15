from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.payment import (
    RazorpayCreateOrderRequest,
    RazorpayVerifyPaymentRequest,
)

from app.services.payment_service import (
    create_razorpay_order_service,
    verify_razorpay_payment_service,
)

router = APIRouter(prefix="/razorpay", tags=["Razorpay"])


# =====================================================
# CREATE RAZORPAY ORDER
# =====================================================

@router.post("/create-order")
def create_razorpay_order(
    data: RazorpayCreateOrderRequest,
    db: Session = Depends(get_db),
):
    return create_razorpay_order_service(
        db=db,
        user_id=data.user_id,
        address_id=data.address_id,
        coupon_code=data.coupon_code,
        currency=data.currency,
    )


# =====================================================
# VERIFY RAZORPAY PAYMENT
# =====================================================

@router.post("/verify-payment")
def verify_razorpay_payment(
    data: RazorpayVerifyPaymentRequest,
    db: Session = Depends(get_db),
):
    return verify_razorpay_payment_service(
        db=db,
        razorpay_order_id=data.razorpay_order_id,
        razorpay_payment_id=data.razorpay_payment_id,
        razorpay_signature=data.razorpay_signature,
        user_id=data.user_id,
        address_id=data.address_id,
    )