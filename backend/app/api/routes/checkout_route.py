from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.checkout import (
    CheckoutRequest,
    PaymentRequest,
    RazorpayCreateOrderRequest,
    RazorpayVerifyPaymentRequest,
)
from app.services.checkout_service import (
    checkout_service,
    process_payment_service,
    get_checkout_summary_service,
    create_razorpay_order_service,
    verify_razorpay_payment_service,
)

router = APIRouter(prefix="/checkout", tags=["Checkout"])


# =========================================================
# 1) SUMMARY API
# frontend page: /checkout/summary
# =========================================================
@router.get("/summary")
def get_checkout_summary(
    user_id: int = Query(...),
    address_id: int = Query(...),
    coupon_code: Optional[str] = Query(None),
    payment_method: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    return get_checkout_summary_service(
        db=db,
        user_id=user_id,
        address_id=address_id,
        coupon_code=coupon_code,
        payment_method=payment_method,
    )


# =========================================================
# 2) PLACE ORDER API
# frontend page: place order button on summary page
# =========================================================
@router.post("/")
def checkout(data: CheckoutRequest, db: Session = Depends(get_db)):
    return checkout_service(
        db=db,
        user_id=data.user_id,
        address_id=data.address_id,
        coupon_code=data.coupon_code,
        shipping_amount=data.shipping_amount,
        payment_method=data.payment_method,
    )


# =========================================================
# 3) SAVE / UPDATE PAYMENT API
# after order creation, update payment status
# =========================================================
@router.post("/payment")
def process_payment(data: PaymentRequest, db: Session = Depends(get_db)):
    return process_payment_service(
        db=db,
        order_id=data.order_id,
        payment_method=data.payment_method,
        payment_status=data.payment_status,
        transaction_ref=data.transaction_ref,
    )


# =========================================================
# 4) RAZORPAY CREATE ORDER
# frontend page: /checkout/payment
# =========================================================
@router.post("/razorpay/create-order")
def create_razorpay_order(
    data: RazorpayCreateOrderRequest,
    db: Session = Depends(get_db),
):
    return create_razorpay_order_service(
        db=db,
        user_id=data.user_id,
        amount=data.amount,
        currency=data.currency,
        receipt=data.receipt,
    )


# =========================================================
# 5) RAZORPAY VERIFY PAYMENT
# frontend page: /checkout/payment
# =========================================================
@router.post("/razorpay/verify-payment")
def verify_razorpay_payment(
    data: RazorpayVerifyPaymentRequest,
    db: Session = Depends(get_db),
):
    return verify_razorpay_payment_service(
        db=db,
        order_id=data.order_id,
        razorpay_order_id=data.razorpay_order_id,
        razorpay_payment_id=data.razorpay_payment_id,
        razorpay_signature=data.razorpay_signature,
    )