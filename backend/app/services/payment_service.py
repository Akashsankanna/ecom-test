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

# ✅ One-way import: service → repository (never the other way around)
from app.repositories.payment_repo import PaymentRepository

load_dotenv()

RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")


# =====================================================
# HELPERS
# =====================================================

def get_razorpay_client():
    if not RAZORPAY_KEY_ID or not RAZORPAY_KEY_SECRET:
        raise HTTPException(
            status_code=500,
            detail="Razorpay keys are missing in environment variables",
        )
    return razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))


# =====================================================
# CREATE ORDER
# =====================================================

def create_razorpay_order_service(amount: float, currency: str, receipt: str):
    try:
        amount_in_paise = int(round(float(amount) * 100))

        if amount_in_paise <= 0:
            raise HTTPException(
                status_code=400, detail="Amount must be greater than 0"
            )

        client = get_razorpay_client()

        razorpay_order = client.order.create(
            {
                "amount": amount_in_paise,
                "currency": currency,
                "receipt": receipt,
                "payment_capture": 1,
            }
        )

        return {
            "success": True,
            "key": RAZORPAY_KEY_ID,
            "key_id": RAZORPAY_KEY_ID,
            "razorpay_order_id": razorpay_order["id"],
            "amount": razorpay_order["amount"],
            "currency": razorpay_order["currency"],
            "receipt": razorpay_order["receipt"],
            "status": razorpay_order.get("status"),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create Razorpay order: {str(e)}",
        )


# =====================================================
# VERIFY PAYMENT  (fixes hmac.new → hmac.new is wrong;
#                  correct call is hmac.new)
# =====================================================

def verify_razorpay_payment_service(
    db: Session,
    razorpay_order_id: str,
    razorpay_payment_id: str,
    razorpay_signature: str,
    user_id: int,
    address_id: int,
):
    try:
        print("VERIFY PAYMENT START")
        print("USER ID:", user_id)
        print("ADDRESS ID:", address_id)
        print("RAZORPAY ORDER ID:", razorpay_order_id)
        print("RAZORPAY PAYMENT ID:", razorpay_payment_id)

        if not RAZORPAY_KEY_SECRET:
            raise HTTPException(
                status_code=500,
                detail="Razorpay key secret is missing in environment variables",
            )

        # ✅ FIX: was incorrectly written as hmac.new(...) in original;
        #    the correct function is hmac.new() — Python's stdlib uses hmac.new()
        body = f"{razorpay_order_id}|{razorpay_payment_id}"
        generated_signature = hmac.new(
            RAZORPAY_KEY_SECRET.encode("utf-8"),
            body.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

        if generated_signature != razorpay_signature:
            raise HTTPException(
                status_code=400, detail="Invalid Razorpay signature"
            )

        # --------------------------------------------------
        # Fetch active cart for this user
        # --------------------------------------------------
        cart = (
            db.execute(
                text(
                    "SELECT id FROM cart "
                    "WHERE user_id = :user_id "
                    "ORDER BY id DESC LIMIT 1"
                ),
                {"user_id": user_id},
            )
            .mappings()
            .first()
        )

        print("CART:", cart)

        if not cart:
            raise HTTPException(
                status_code=400, detail="Cart not found for this user"
            )

        cart_id = cart["id"]

        # --------------------------------------------------
        # Fetch cart items with pricing
        # --------------------------------------------------
        cart_items = (
            db.execute(
                text(
                    """
                    SELECT
                        ci.id,
                        ci.cart_id,
                        ci.variant_id,
                        ci.quantity,
                        COALESCE(ci.price, pv.price, 0)          AS price,
                        COALESCE(ci.customization_total, 0)       AS customization_total
                    FROM cart_item ci
                    LEFT JOIN product_variant pv ON pv.id = ci.variant_id
                    WHERE ci.cart_id = :cart_id
                    """
                ),
                {"cart_id": cart_id},
            )
            .mappings()
            .all()
        )

        print("CART ITEMS:", cart_items)

        if not cart_items:
            raise HTTPException(status_code=400, detail="Cart is empty")

        # --------------------------------------------------
        # Calculate total
        # --------------------------------------------------
        total_amount = Decimal("0.00")
        for item in cart_items:
            price = Decimal(str(item["price"] or 0))
            qty = Decimal(str(item["quantity"] or 0))
            customization = Decimal(str(item["customization_total"] or 0))
            total_amount += (price + customization) * qty

        print("TOTAL AMOUNT:", total_amount)

        # --------------------------------------------------
        # Create order
        # --------------------------------------------------
        order_row = (
            db.execute(
                text(
                    """
                    INSERT INTO orders (
                        user_id, total_amount, gross_amount, status,
                        address_id, payment_status,
                        created_at, updated_at, created_by, updated_by,
                        coupon_discount_amount, additional_discount_amount
                    )
                    VALUES (
                        :user_id, :total_amount, :gross_amount, 'CONFIRMED',
                        :address_id, 'SUCCESS',
                        CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, :user_id, :user_id,
                        0, 0
                    )
                    RETURNING id
                    """
                ),
                {
                    "user_id": user_id,
                    "address_id": address_id,
                    "total_amount": total_amount,
                    "gross_amount": total_amount,
                },
            )
            .mappings()
            .first()
        )

        order_id = order_row["id"]
        print("ORDER CREATED:", order_id)

        # --------------------------------------------------
        # Insert order items
        # --------------------------------------------------
        for item in cart_items:
            db.execute(
                text(
                    """
                    INSERT INTO order_items (
                        order_id, variant_id, quantity, price,
                        customization_total, created_at
                    )
                    VALUES (
                        :order_id, :variant_id, :quantity, :price,
                        :customization_total, CURRENT_TIMESTAMP
                    )
                    """
                ),
                {
                    "order_id": order_id,
                    "variant_id": item["variant_id"],
                    "quantity": item["quantity"],
                    "price": item["price"],
                    "customization_total": item["customization_total"] or 0,
                },
            )

        # --------------------------------------------------
        # Create transaction record
        # --------------------------------------------------
        transaction_row = (
            db.execute(
                text(
                    """
                    INSERT INTO transactions (
                        order_id, amount, payment_method, status,
                        transaction_ref, payment_gateway, gateway_transaction_id,
                        currency, gateway_response, created_at
                    )
                    VALUES (
                        :order_id, :amount, 'RAZORPAY', 'SUCCESS',
                        :transaction_ref, 'RAZORPAY', :gateway_transaction_id,
                        'INR', CAST(:gateway_response AS jsonb), CURRENT_TIMESTAMP
                    )
                    RETURNING id
                    """
                ),
                {
                    "order_id": order_id,
                    "amount": total_amount,
                    "transaction_ref": razorpay_payment_id,
                    "gateway_transaction_id": razorpay_order_id,
                    "gateway_response": json.dumps(
                        {
                            "razorpay_order_id": razorpay_order_id,
                            "razorpay_payment_id": razorpay_payment_id,
                            "razorpay_signature": razorpay_signature,
                        }
                    ),
                },
            )
            .mappings()
            .first()
        )

        transaction_id = transaction_row["id"]
        print("TRANSACTION CREATED:", transaction_id)

        # --------------------------------------------------
        # Link transaction back to order
        # --------------------------------------------------
        db.execute(
            text(
                "UPDATE orders "
                "SET transaction_id = :transaction_id, updated_at = CURRENT_TIMESTAMP "
                "WHERE id = :order_id"
            ),
            {"transaction_id": transaction_id, "order_id": order_id},
        )

        # --------------------------------------------------
        # Clear cart
        # --------------------------------------------------
        db.execute(
            text("DELETE FROM cart_item WHERE cart_id = :cart_id"),
            {"cart_id": cart_id},
        )

        print("CART CLEARED")
        print("ABOUT TO COMMIT")

        db.commit()

        print("COMMIT SUCCESS")

        return {
            "success": True,
            "message": "Payment verified and order created successfully",
            "payment_status": "SUCCESS",
            "transaction_ref": razorpay_payment_id,
            "razorpay_order_id": razorpay_order_id,
            "transaction_id": transaction_id,
            "order_id": order_id,
        }

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        print("PAYMENT VERIFY ERROR:", str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to verify payment and create order: {str(e)}",
        )


# =====================================================
# SERVICE CLASS  (thin wrapper — delegates to repo)
# =====================================================

class PaymentService:

    @staticmethod
    def get_all_payments(db, status=None, payment_method=None, limit=100):
        return PaymentRepository.get_all_transactions(
            db=db,
            status=status,
            payment_method=payment_method,
            limit=limit,
        )

    @staticmethod
    def get_payments_by_order(db, order_id: int):
        txns = PaymentRepository.get_transactions_by_order(db, order_id)
        if not txns:
            raise HTTPException(
                status_code=404,
                detail="No transactions found for this order",
            )
        return txns

    @staticmethod
    def get_payment_view(db, order_id=None):
        return PaymentRepository.get_payment_view(db, order_id)

    @staticmethod
    def get_revenue_summary(db):
        return PaymentRepository.get_revenue_summary(db)

    @staticmethod
    def process_payment(
        db,
        order_id: int,
        payment_method: str,
        pay_status: str,
        txn_ref: str,
    ):
        return PaymentRepository.process_payment(
            db=db,
            order_id=order_id,
            payment_method=payment_method.upper(),
            pay_status=pay_status.upper(),
            txn_ref=txn_ref,
        )

    @staticmethod
    def create_razorpay_order(
        amount: float,
        currency: str = "INR",
        receipt: str = "receipt",
    ):
        return create_razorpay_order_service(
            amount=amount,
            currency=currency,
            receipt=receipt,
        )

    @staticmethod
    def verify_razorpay_payment(
        db,
        razorpay_order_id: str,
        razorpay_payment_id: str,
        razorpay_signature: str,
        user_id: int,
        address_id: int,
    ):
        return verify_razorpay_payment_service(
            db=db,
            razorpay_order_id=razorpay_order_id,
            razorpay_payment_id=razorpay_payment_id,
            razorpay_signature=razorpay_signature,
            user_id=user_id,
            address_id=address_id,
        )