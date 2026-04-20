from decimal import Decimal, ROUND_HALF_UP
import hmac
import hashlib

import razorpay
from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.repositories.checkout_repo import (
    get_cart_id_by_user_id,
    is_valid_user_address,
    get_order_by_id,
    get_order_items_by_order_id,
    call_sp_process_payment,
    transaction_ref_exists,
)

MONEY_PLACES = Decimal("0.01")

RAZORPAY_KEY_ID = settings.RAZORPAY_KEY_ID
RAZORPAY_KEY_SECRET = settings.RAZORPAY_KEY_SECRET

razorpay_client = None
if RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET:
    razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))


def _extract_db_error_message(exc: Exception) -> str:
    if hasattr(exc, "orig") and exc.orig:
        return str(exc.orig)
    return str(exc)


def _to_decimal(value) -> Decimal:
    if value is None:
        return Decimal("0.00")
    return Decimal(str(value)).quantize(MONEY_PLACES, rounding=ROUND_HALF_UP)


def _get_cart_items_for_checkout(db: Session, cart_id: int):
    rows = db.execute(
        text(
            """
            SELECT
                ci.id AS cart_item_id,
                ci.variant_id,
                ci.quantity,
                pv.price,
                pv.stock,
                pv.variant_name,
                p.id AS product_id,
                p.name AS product_name,
                COALESCE(pi.image_url, '') AS image_url,
                COALESCE(tr.rate, 0) AS tax_rate
            FROM cart_item ci
            JOIN product_variant pv ON pv.id = ci.variant_id
            JOIN product p ON p.id = pv.product_id
            LEFT JOIN product_image pi
                ON pi.product_id = p.id
               AND pi.is_primary = true
            LEFT JOIN tax_rate tr
                ON tr.id = p.tax_rate_id
               AND tr.is_active = true
            WHERE ci.cart_id = :cart_id
            ORDER BY ci.id
            """
        ),
        {"cart_id": cart_id},
    ).mappings().all()

    if not rows:
        raise HTTPException(status_code=400, detail="Cart is empty")

    for row in rows:
        stock = row["stock"] if row["stock"] is not None else 0
        if row["quantity"] > stock:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock for variant_id {row['variant_id']}",
            )

    return rows


def _validate_coupon(
    db: Session,
    coupon_code: str | None,
    user_id: int,
    order_amount: Decimal,
) -> dict:
    if not coupon_code:
        return {
            "coupon_id": None,
            "discount_amount": Decimal("0.00"),
            "message": "No coupon applied",
            "code": None,
        }

    result = db.execute(
        text(
            """
            SELECT coupon_id, discount_amount, message
            FROM fn_validate_coupon(:coupon_code, :user_id, :order_amount)
            """
        ),
        {
            "coupon_code": coupon_code,
            "user_id": user_id,
            "order_amount": order_amount,
        },
    ).mappings().first()

    if not result or result["coupon_id"] is None:
        raise HTTPException(
            status_code=400,
            detail=result["message"] if result else "Invalid coupon",
        )

    return {
        "coupon_id": result["coupon_id"],
        "discount_amount": _to_decimal(result["discount_amount"]),
        "message": result["message"],
        "code": coupon_code,
    }


def _calculate_checkout_summary(
    cart_rows,
    discount_amount: Decimal = Decimal("0.00"),
    shipping_amount: Decimal = Decimal("0.00"),
    other_charge_amount: Decimal = Decimal("0.00"),
):
    subtotal = Decimal("0.00")
    tax_amount = Decimal("0.00")
    order_items = []

    for row in cart_rows:
        quantity = Decimal(str(row["quantity"]))
        price = _to_decimal(row["price"])
        line_subtotal = (price * quantity).quantize(MONEY_PLACES, rounding=ROUND_HALF_UP)

        item_tax_rate = Decimal(str(row["tax_rate"] or 0))
        line_tax = ((line_subtotal * item_tax_rate) / Decimal("100")).quantize(
            MONEY_PLACES,
            rounding=ROUND_HALF_UP,
        )

        subtotal += line_subtotal
        tax_amount += line_tax

        order_items.append(
            {
                "variant_id": row["variant_id"],
                "quantity": int(row["quantity"]),
                "price": price,
                "product_name": row["product_name"],
                "variant_name": row["variant_name"],
                "image_url": row["image_url"],
                "tax_rate": str(item_tax_rate),
                "line_subtotal": str(line_subtotal),
                "line_tax": str(line_tax),
            }
        )

    subtotal = subtotal.quantize(MONEY_PLACES, rounding=ROUND_HALF_UP)
    tax_amount = tax_amount.quantize(MONEY_PLACES, rounding=ROUND_HALF_UP)
    shipping_amount = _to_decimal(shipping_amount)
    other_charge_amount = _to_decimal(other_charge_amount)
    discount_amount = _to_decimal(discount_amount)

    if discount_amount > subtotal:
        discount_amount = subtotal

    total_amount = (
        subtotal
        - discount_amount
        + tax_amount
        + shipping_amount
        + other_charge_amount
    ).quantize(MONEY_PLACES, rounding=ROUND_HALF_UP)

    if total_amount < Decimal("0.00"):
        total_amount = Decimal("0.00")

    return {
        "subtotal_amount": subtotal,
        "discount_amount": discount_amount,
        "tax_amount": tax_amount,
        "shipping_amount": shipping_amount,
        "other_charge_amount": other_charge_amount,
        "total_amount": total_amount,
        "order_items": order_items,
    }


def _create_order(
    db: Session,
    user_id: int,
    address_id: int,
    total_amount: Decimal,
):
    row = db.execute(
        text(
            """
            INSERT INTO orders (
                user_id,
                address_id,
                total_amount,
                status,
                payment_status,
                created_at,
                updated_at
            )
            VALUES (
                :user_id,
                :address_id,
                :total_amount,
                'PENDING',
                'PENDING',
                CURRENT_TIMESTAMP,
                CURRENT_TIMESTAMP
            )
            RETURNING id
            """
        ),
        {
            "user_id": user_id,
            "address_id": address_id,
            "total_amount": total_amount,
        },
    ).first()

    if not row:
        raise HTTPException(status_code=500, detail="Order could not be created")

    return row[0]


def _insert_order_items(db: Session, order_id: int, order_items: list[dict]):
    for item in order_items:
        db.execute(
            text(
                """
                INSERT INTO order_items (
                    order_id,
                    variant_id,
                    quantity,
                    price
                )
                VALUES (
                    :order_id,
                    :variant_id,
                    :quantity,
                    :price
                )
                """
            ),
            {
                "order_id": order_id,
                "variant_id": item["variant_id"],
                "quantity": item["quantity"],
                "price": item["price"],
            },
        )


def _record_coupon_usage(
    db: Session,
    coupon_id: int | None,
    user_id: int,
    order_id: int,
):
    if not coupon_id:
        return

    db.execute(
        text(
            """
            INSERT INTO coupon_usage (coupon_id, user_id, order_id)
            VALUES (:coupon_id, :user_id, :order_id)
            """
        ),
        {
            "coupon_id": coupon_id,
            "user_id": user_id,
            "order_id": order_id,
        },
    )

    db.execute(
        text(
            """
            UPDATE coupon
            SET used_count = used_count + 1,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = :coupon_id
            """
        ),
        {"coupon_id": coupon_id},
    )


def _clear_cart(db: Session, cart_id: int):
    db.execute(
        text("DELETE FROM cart_item WHERE cart_id = :cart_id"),
        {"cart_id": cart_id},
    )


def _get_cart_id_for_order_user(db: Session, order_id: int) -> int | None:
    row = db.execute(
        text(
            """
            SELECT c.id
            FROM orders o
            JOIN cart c ON c.user_id = o.user_id
            WHERE o.id = :order_id
            ORDER BY c.id DESC
            LIMIT 1
            """
        ),
        {"order_id": order_id},
    ).first()

    return row[0] if row else None


def get_checkout_summary_service(
    db: Session,
    user_id: int,
    address_id: int,
    coupon_code: str | None = None,
    payment_method: str | None = None,
):
    cart_id = get_cart_id_by_user_id(db, user_id)

    if not cart_id:
        raise HTTPException(status_code=404, detail="User cart not found")

    if not is_valid_user_address(db, user_id, address_id):
        raise HTTPException(status_code=400, detail="Invalid address for this user")

    cart_rows = _get_cart_items_for_checkout(db, cart_id)

    raw_subtotal = sum(
        _to_decimal(row["price"]) * Decimal(str(row["quantity"]))
        for row in cart_rows
    ).quantize(MONEY_PLACES, rounding=ROUND_HALF_UP)

    coupon_data = _validate_coupon(
        db=db,
        coupon_code=coupon_code,
        user_id=user_id,
        order_amount=raw_subtotal,
    )

    pricing = _calculate_checkout_summary(
        cart_rows=cart_rows,
        discount_amount=coupon_data["discount_amount"],
        shipping_amount=Decimal("0.00"),
        other_charge_amount=Decimal("0.00"),
    )

    return {
        "success": True,
        "message": "Checkout summary fetched successfully",
        "payment_method": payment_method,
        "coupon": {
            "code": coupon_data["code"],
            "message": coupon_data["message"],
        },
        "pricing": {
            "subtotal_amount": str(pricing["subtotal_amount"]),
            "discount_amount": str(pricing["discount_amount"]),
            "tax_amount": str(pricing["tax_amount"]),
            "shipping_amount": str(pricing["shipping_amount"]),
            "other_charge_amount": str(pricing["other_charge_amount"]),
            "total_amount": str(pricing["total_amount"]),
        },
        "items": pricing["order_items"],
    }


def checkout_service(
    db: Session,
    user_id: int,
    address_id: int,
    coupon_code: str | None = None,
    shipping_amount: float | Decimal = 0,
    other_charge_amount: float | Decimal = 0,
    payment_method: str = "COD",
):
    cart_id = get_cart_id_by_user_id(db, user_id)

    if not cart_id:
        raise HTTPException(status_code=404, detail="User cart not found")

    if not is_valid_user_address(db, user_id, address_id):
        raise HTTPException(status_code=400, detail="Invalid address for this user")

    try:
        payment_method = (payment_method or "COD").strip().upper()

        cart_rows = _get_cart_items_for_checkout(db, cart_id)

        raw_subtotal = sum(
            _to_decimal(row["price"]) * Decimal(str(row["quantity"]))
            for row in cart_rows
        ).quantize(MONEY_PLACES, rounding=ROUND_HALF_UP)

        coupon_data = _validate_coupon(
            db=db,
            coupon_code=coupon_code,
            user_id=user_id,
            order_amount=raw_subtotal,
        )

        pricing = _calculate_checkout_summary(
            cart_rows=cart_rows,
            discount_amount=coupon_data["discount_amount"],
            shipping_amount=_to_decimal(shipping_amount),
            other_charge_amount=_to_decimal(other_charge_amount),
        )

        order_id = _create_order(
            db=db,
            user_id=user_id,
            address_id=address_id,
            total_amount=pricing["total_amount"],
        )

        _insert_order_items(db, order_id, pricing["order_items"])
        _record_coupon_usage(db, coupon_data["coupon_id"], user_id, order_id)

        if payment_method == "COD":
            call_sp_process_payment(
                db=db,
                order_id=order_id,
                payment_method="COD",
                payment_status="PENDING",
                transaction_ref=f"COD_ORDER_{order_id}",
            )
            _clear_cart(db, cart_id)

        db.commit()

        order = get_order_by_id(db, order_id)
        items = get_order_items_by_order_id(db, order_id)

        if not order:
            raise HTTPException(status_code=500, detail="Checkout completed but order fetch failed")

        return {
            "success": True,
            "message": "Checkout created successfully" if payment_method != "COD" else "Checkout completed successfully",
            "payment_method": payment_method,
            "pricing": {
                "subtotal_amount": str(pricing["subtotal_amount"]),
                "discount_amount": str(pricing["discount_amount"]),
                "tax_amount": str(pricing["tax_amount"]),
                "shipping_amount": str(pricing["shipping_amount"]),
                "other_charge_amount": str(pricing["other_charge_amount"]),
                "total_amount": str(pricing["total_amount"]),
            },
            "coupon": {
                "code": coupon_data["code"],
                "message": coupon_data["message"],
            },
            "order": order,
            "items": items,
        }

    except HTTPException:
        db.rollback()
        raise
    except IntegrityError as exc:
        db.rollback()
        error_message = _extract_db_error_message(exc)
        raise HTTPException(status_code=400, detail=error_message)
    except SQLAlchemyError as exc:
        db.rollback()
        error_message = _extract_db_error_message(exc)

        if "Insufficient stock" in error_message:
            raise HTTPException(status_code=400, detail="Insufficient stock")
        if "Cart is empty" in error_message:
            raise HTTPException(status_code=400, detail="Cart is empty")
        if "Cart not found" in error_message:
            raise HTTPException(status_code=404, detail="Cart not found")
        if "Invalid or expired coupon" in error_message:
            raise HTTPException(status_code=400, detail="Invalid or expired coupon")
        if "Order amount below minimum requirement" in error_message:
            raise HTTPException(status_code=400, detail="Order amount below minimum requirement")
        if "Coupon usage limit reached" in error_message:
            raise HTTPException(status_code=400, detail="Coupon usage limit reached")

        raise HTTPException(status_code=500, detail=error_message)


def process_payment_service(
    db: Session,
    order_id: int,
    payment_method: str,
    payment_status: str,
    transaction_ref: str,
):
    order = get_order_by_id(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if transaction_ref_exists(db, transaction_ref):
        raise HTTPException(status_code=400, detail="transaction_ref already exists")

    try:
        normalized_payment_method = payment_method.strip().upper()
        normalized_payment_status = payment_status.strip().upper()

        call_sp_process_payment(
            db=db,
            order_id=order_id,
            payment_method=normalized_payment_method,
            payment_status=normalized_payment_status,
            transaction_ref=transaction_ref,
        )

        if normalized_payment_status == "SUCCESS":
            cart_id = _get_cart_id_for_order_user(db, order_id)
            if cart_id:
                _clear_cart(db, cart_id)

        db.commit()

        updated_order = get_order_by_id(db, order_id)
        items = get_order_items_by_order_id(db, order_id)

        return {
            "success": True,
            "message": "Payment processed successfully",
            "order": updated_order,
            "items": items,
        }

    except HTTPException:
        db.rollback()
        raise
    except IntegrityError as exc:
        db.rollback()
        error_message = _extract_db_error_message(exc)
        raise HTTPException(status_code=400, detail=error_message)
    except SQLAlchemyError as exc:
        db.rollback()
        error_message = _extract_db_error_message(exc)

        if "Order not found" in error_message:
            raise HTTPException(status_code=404, detail="Order not found")

        raise HTTPException(status_code=500, detail=error_message)


def create_razorpay_order_service(
    db: Session,
    user_id: int,
    amount: float,
    currency: str = "INR",
    receipt: str = "receipt_demo",
):
    if not razorpay_client:
        raise HTTPException(status_code=500, detail="Razorpay is not configured")

    try:
        amount_in_paise = int(round(float(amount) * 100))

        if amount_in_paise <= 0:
            raise HTTPException(status_code=400, detail="Amount must be greater than 0")

        razorpay_order = razorpay_client.order.create(
            {
                "amount": amount_in_paise,
                "currency": currency,
                "receipt": receipt,
            }
        )

        return {
            "success": True,
            "key": RAZORPAY_KEY_ID,
            "user_id": user_id,
            "amount": razorpay_order["amount"],
            "currency": razorpay_order["currency"],
            "razorpay_order_id": razorpay_order["id"],
            "receipt": razorpay_order["receipt"],
        }

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create Razorpay order: {str(exc)}",
        )


def verify_razorpay_payment_service(
    db: Session,
    order_id: int,
    razorpay_order_id: str,
    razorpay_payment_id: str,
    razorpay_signature: str,
):
    if not RAZORPAY_KEY_SECRET:
        raise HTTPException(status_code=500, detail="Razorpay secret is not configured")

    generated_signature = hmac.new(
        RAZORPAY_KEY_SECRET.encode(),
        f"{razorpay_order_id}|{razorpay_payment_id}".encode(),
        hashlib.sha256,
    ).hexdigest()

    if generated_signature != razorpay_signature:
        raise HTTPException(status_code=400, detail="Invalid Razorpay signature")

    return process_payment_service(
        db=db,
        order_id=order_id,
        payment_method="RAZORPAY",
        payment_status="SUCCESS",
        transaction_ref=razorpay_payment_id,
    )