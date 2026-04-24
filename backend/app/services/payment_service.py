import os
import hmac
import json
import hashlib
from decimal import Decimal

import razorpay
from dotenv import load_dotenv
from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

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
            raise HTTPException(status_code=400, detail="Amount must be greater than 0")

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
    db: Session,
    razorpay_order_id: str,
    razorpay_payment_id: str,
    razorpay_signature: str,
    user_id: int,
    address_id: int
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
            raise HTTPException(status_code=400, detail="Invalid Razorpay signature")

        cart = db.execute(
            text("""
                SELECT id
                FROM cart
                WHERE user_id = :user_id
                LIMIT 1
            """),
            {"user_id": user_id}
        ).mappings().first()

        if not cart:
            raise HTTPException(status_code=400, detail="Cart not found for this user")

        cart_items = db.execute(
            text("""
                SELECT
                    id,
                    cart_id,
                    product_id,
                    variant_id,
                    quantity,
                    price,
                    customization_total
                FROM cart_item
                WHERE cart_id = :cart_id
            """),
            {"cart_id": cart["id"]}
        ).mappings().all()

        if not cart_items:
            raise HTTPException(status_code=400, detail="Cart is empty")

        total_amount = Decimal("0.00")

        for item in cart_items:
            price = Decimal(str(item["price"] or 0))
            qty = Decimal(str(item["quantity"] or 0))
            customization = Decimal(str(item["customization_total"] or 0))
            total_amount += (price * qty) + customization

        order_row = db.execute(
            text("""
                INSERT INTO orders (
                    user_id,
                    total_amount,
                    gross_amount,
                    status,
                    address_id,
                    payment_status,
                    created_by,
                    updated_by
                )
                VALUES (
                    :user_id,
                    :total_amount,
                    :gross_amount,
                    'CONFIRMED',
                    :address_id,
                    'SUCCESS',
                    :user_id,
                    :user_id
                )
                RETURNING id
            """),
            {
                "user_id": user_id,
                "address_id": address_id,
                "total_amount": total_amount,
                "gross_amount": total_amount
            }
        ).mappings().first()

        order_id = order_row["id"]

        for item in cart_items:
            db.execute(
                text("""
                    INSERT INTO order_items (
                        order_id,
                        product_id,
                        variant_id,
                        quantity,
                        price,
                        customization_total
                    )
                    VALUES (
                        :order_id,
                        :product_id,
                        :variant_id,
                        :quantity,
                        :price,
                        :customization_total
                    )
                """),
                {
                    "order_id": order_id,
                    "product_id": item["product_id"],
                    "variant_id": item["variant_id"],
                    "quantity": item["quantity"],
                    "price": item["price"],
                    "customization_total": item["customization_total"] or 0
                }
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
                    gateway_response
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
                    CAST(:gateway_response AS jsonb)
                )
                RETURNING id
            """),
            {
                "order_id": order_id,
                "amount": total_amount,
                "transaction_ref": razorpay_payment_id,
                "gateway_transaction_id": razorpay_order_id,
                "gateway_response": json.dumps({
                    "razorpay_order_id": razorpay_order_id,
                    "razorpay_payment_id": razorpay_payment_id,
                    "razorpay_signature": razorpay_signature
                })
            }
        ).mappings().first()

        transaction_id = transaction_row["id"]

        db.execute(
            text("""
                UPDATE orders
                SET transaction_id = :transaction_id,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = :order_id
            """),
            {
                "transaction_id": transaction_id,
                "order_id": order_id
            }
        )

        db.execute(
            text("""
                DELETE FROM cart_item
                WHERE cart_id = :cart_id
            """),
            {"cart_id": cart["id"]}
        )

        db.commit()

        return {
            "success": True,
            "message": "Payment verified and order created successfully",
            "payment_status": "paid",
            "transaction_ref": razorpay_payment_id,
            "razorpay_order_id": razorpay_order_id,
            "transaction_id": transaction_id,
            "order_id": order_id
        }

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to verify payment: {str(e)}"
        )