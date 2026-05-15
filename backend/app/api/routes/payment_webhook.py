from fastapi import APIRouter, Request, Header, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
import hmac
import hashlib
import json
import os
from decimal import Decimal, ROUND_HALF_UP

from app.db.session import get_db

router = APIRouter(prefix="/razorpay", tags=["Razorpay Webhook"])

WEBHOOK_SECRET = os.getenv("RAZORPAY_WEBHOOK_SECRET")


def round_money(value) -> Decimal:
    return Decimal(str(value or 0)).quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP
    )


@router.post("/webhook")
async def razorpay_webhook(
    request: Request,
    x_razorpay_signature: str = Header(None),
    db: Session = Depends(get_db),
):
    body = await request.body()

    if not WEBHOOK_SECRET:
        raise HTTPException(status_code=500, detail="Webhook secret missing")

    generated_signature = hmac.new(
        WEBHOOK_SECRET.encode("utf-8"),
        body,
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(generated_signature, x_razorpay_signature or ""):
        raise HTTPException(status_code=400, detail="Invalid webhook signature")

    payload = json.loads(body.decode("utf-8"))
    event = payload.get("event")

    if event not in ["payment.captured", "order.paid", "payment.failed"]:
        return {"success": True, "status": "ignored", "event": event}

    payment = (
        payload.get("payload", {})
        .get("payment", {})
        .get("entity", {})
    )

    if not payment:
        return {"success": True, "status": "ignored_no_payment_entity"}

    razorpay_payment_id = payment.get("id")
    razorpay_order_id = payment.get("order_id")
    amount = round_money(Decimal(str(payment.get("amount", 0))) / Decimal("100"))

    if not razorpay_payment_id or not razorpay_order_id:
        return {"success": True, "status": "missing_payment_or_order_id"}

    try:
        if event == "payment.failed":
            db.execute(
                text("""
                    UPDATE orders
                    SET payment_status = 'FAILED',
                        updated_at = CURRENT_TIMESTAMP
                    WHERE razorpay_order_id = :razorpay_order_id
                      AND payment_status = 'PENDING'
                """),
                {"razorpay_order_id": razorpay_order_id},
            )
            db.commit()
            return {"success": True, "status": "payment_failed"}

        existing_txn = db.execute(
            text("""
                SELECT id
                FROM transactions
                WHERE transaction_ref = :payment_id
                   OR razorpay_payment_id = :payment_id
                LIMIT 1
            """),
            {"payment_id": razorpay_payment_id},
        ).mappings().first()

        if existing_txn:
            return {
                "success": True,
                "status": "already_processed",
                "transaction_id": existing_txn["id"],
            }

        order_row = db.execute(
            text("""
                SELECT id, remaining_amount, final_amount, total_amount
                FROM orders
                WHERE razorpay_order_id = :razorpay_order_id
                LIMIT 1
                FOR UPDATE
            """),
            {"razorpay_order_id": razorpay_order_id},
        ).mappings().first()

        if not order_row:
            return {
                "success": True,
                "status": "order_not_found",
                "razorpay_order_id": razorpay_order_id,
            }

        payable_amount = round_money(
            order_row["remaining_amount"]
            or order_row["final_amount"]
            or order_row["total_amount"]
            or amount
        )

        transaction_row = db.execute(
            text("""
                INSERT INTO transactions (
                    order_id,
                    amount,
                    payment_method,
                    status,
                    transaction_ref,
                    payment_gateway,
                    gateway_transaction_id,
                    currency,
                    gateway_response,
                    created_at
                )
                VALUES (
                    :order_id,
                    :amount,
                    'RAZORPAY',
                    'SUCCESS',
                    :transaction_ref,
                    'RAZORPAY',
                    :gateway_transaction_id,
                    'INR',
                    CAST(:gateway_response AS jsonb),
                    CURRENT_TIMESTAMP
                )
                RETURNING id
            """),
            {
                "order_id": order_row["id"],
                "amount": payable_amount,
                "transaction_ref": razorpay_payment_id,
                "gateway_transaction_id": razorpay_order_id,
                "gateway_response": json.dumps(payload),
            },
        ).mappings().first()

        db.execute(
            text("""
                UPDATE orders
                SET transaction_id = :transaction_id,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = :order_id
            """),
            {
                "transaction_id": transaction_row["id"],
                "order_id": order_row["id"],
            },
        )

        db.commit()

        return {
            "success": True,
            "status": "payment_processed",
            "transaction_id": transaction_row["id"],
            "order_id": order_row["id"],
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))