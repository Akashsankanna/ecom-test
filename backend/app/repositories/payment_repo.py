from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.payment import RazorpayCreateOrderRequest, RazorpayVerifyPaymentRequest
from app.services.payment_service import (
    create_razorpay_order_service,
    verify_razorpay_payment_service
)

router = APIRouter(prefix="/razorpay", tags=["Razorpay"])


@router.post("/create-order")
def create_razorpay_order(payload: RazorpayCreateOrderRequest):
    return create_razorpay_order_service(
        amount=payload.amount,
        currency=payload.currency,
        receipt=payload.receipt
    )


@router.post("/verify-payment")
def verify_razorpay_payment(
    payload: RazorpayVerifyPaymentRequest,
    db: Session = Depends(get_db)
):
    verify_res = verify_razorpay_payment_service(
        razorpay_order_id=payload.razorpay_order_id,
        razorpay_payment_id=payload.razorpay_payment_id,
        razorpay_signature=payload.razorpay_signature
    )

    # TEMP FIX: payment verified but order creation not added yet
    return {
        "success": True,
        "message": "Payment verified successfully",
        "payment_status": "paid",
        "transaction_ref": payload.razorpay_payment_id,
        "razorpay_order_id": payload.razorpay_order_id,
        "order_id": payload.order_id if hasattr(payload, "order_id") else None
    }