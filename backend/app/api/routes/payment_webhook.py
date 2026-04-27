from fastapi import APIRouter, Request, Header, HTTPException, Depends
from sqlalchemy.orm import Session
import hmac
import hashlib
import json
import os

from app.db.session import get_db
from app.models.order import Order 
from app.models.payment_transaction import PaymentTransaction

router = APIRouter(prefix="/razorpay", tags=["Razorpay Webhook"])

WEBHOOK_SECRET = os.getenv("RAZORPAY_WEBHOOK_SECRET")


@router.post("/webhook")
async def razorpay_webhook(
    request: Request,
    x_razorpay_signature: str = Header(None),
    db: Session = Depends(get_db)
):
    from app.models.cart import Cart
    from app.models.cart_item import CartItem

    body = await request.body()

    if not WEBHOOK_SECRET:
        raise HTTPException(status_code=500, detail="Webhook secret missing")

    generated_signature = hmac.new(
        WEBHOOK_SECRET.encode(),
        body,
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(generated_signature, x_razorpay_signature or ""):
        raise HTTPException(status_code=400, detail="Invalid webhook signature")

    payload = json.loads(body)
    event = payload.get("event")

    if event == "payment.captured":
        payment = payload["payload"]["payment"]["entity"]

        razorpay_payment_id = payment.get("id")
        razorpay_order_id = payment.get("order_id")
        amount = payment.get("amount", 0) / 100

        notes = payment.get("notes", {})
        order_id = notes.get("order_id")

        if not order_id:
            raise HTTPException(status_code=400, detail="Order id missing in payment notes")

        order = db.query(Order).filter(Order.id == int(order_id)).first()

        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        if order.payment_status == "PAID":
            return {"status": "already_processed"}

        order.payment_status = "PAID"
        order.status = "CONFIRMED"
        order.transaction_id = razorpay_payment_id

        transaction = PaymentTransaction(
            order_id=order.id,
            user_id=order.user_id,
            transaction_ref=razorpay_payment_id,
            razorpay_order_id=razorpay_order_id,
            amount=amount,
            status="SUCCESS",
            payment_method="RAZORPAY"
        )

        db.add(transaction)

        cart = db.query(Cart).filter(Cart.user_id == order.user_id).first()

        if cart:
            db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()

        db.commit()

        return {"status": "payment_captured"}

    elif event == "payment.failed":
        payment = payload["payload"]["payment"]["entity"]

        notes = payment.get("notes", {})
        order_id = notes.get("order_id")

        if order_id:
            order = db.query(Order).filter(Order.id == int(order_id)).first()

            if order:
                order.payment_status = "FAILED"
                order.status = "PAYMENT_FAILED"
                db.commit()

        return {"status": "payment_failed"}

    return {"status": "ignored"}