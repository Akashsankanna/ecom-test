from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.payment import (
    RazorpayCreateOrderRequest,
    RazorpayVerifyPaymentRequest,
)

# ✅ Routes import from service ONLY — never from repository directly
from app.services.payment_service import (
    create_razorpay_order_service,
    verify_razorpay_payment_service,
)

router = APIRouter(prefix="/razorpay", tags=["Razorpay"])


# =====================================================
# CREATE ORDER
# =====================================================

@router.post("/create-order")
def create_razorpay_order(data: RazorpayCreateOrderRequest):
    return create_razorpay_order_service(
        amount=data.amount,
        currency=data.currency,
        receipt=data.receipt,
    )


# =====================================================
# VERIFY PAYMENT
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