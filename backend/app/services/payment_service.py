import os
import hmac
import hashlib
from fastapi import HTTPException
import razorpay
from dotenv import load_dotenv

load_dotenv()

RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")


def get_razorpay_client():
    if not RAZORPAY_KEY_ID or not RAZORPAY_KEY_SECRET:
        raise HTTPException(
            status_code=500,
            detail="Razorpay keys are missing in environment variables"
        )
    return razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))


def create_razorpay_order_service(amount: float, currency: str, receipt: str):
    try:
        amount_in_paise = int(round(float(amount) * 100))

        if amount_in_paise <= 0:
            raise HTTPException(
                status_code=400,
                detail="Amount must be greater than 0"
            )

        client = get_razorpay_client()

        razorpay_order = client.order.create({
            "amount": amount_in_paise,
            "currency": currency,
            "receipt": receipt,
            "payment_capture": 1
        })

        return {
            "success": True,
            "key": RAZORPAY_KEY_ID,
            "key_id": RAZORPAY_KEY_ID,
            "razorpay_order_id": razorpay_order["id"],
            "amount": razorpay_order["amount"],
            "currency": razorpay_order["currency"],
            "receipt": razorpay_order["receipt"],
            "status": razorpay_order.get("status")
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create Razorpay order: {str(e)}"
        )


def verify_razorpay_payment_service(
    razorpay_order_id: str,
    razorpay_payment_id: str,
    razorpay_signature: str
):
    try:
        if not RAZORPAY_KEY_SECRET:
            raise HTTPException(
                status_code=500,
                detail="Razorpay key secret is missing in environment variables"
            )

        body = f"{razorpay_order_id}|{razorpay_payment_id}"

        generated_signature = hmac.new(
            RAZORPAY_KEY_SECRET.encode("utf-8"),
            body.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()

        if generated_signature != razorpay_signature:
            raise HTTPException(
                status_code=400,
                detail="Invalid Razorpay signature"
            )

        return {
            "success": True,
            "message": "Payment verified successfully",
            "payment_status": "paid",
            "transaction_ref": razorpay_payment_id,
            "razorpay_order_id": razorpay_order_id
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to verify payment: {str(e)}"
        )