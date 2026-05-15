import os
import hmac
import json
import hashlib
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime

import razorpay
from dotenv import load_dotenv
from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.repositories.payment_repo import PaymentRepository
from app.schemas.invoice_schema import InvoiceCreate
from app.services.invoice_service import InvoiceService
from app.models.invoice_model import Invoice, InvoiceItem

load_dotenv()

RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")


def get_razorpay_client():
    if not RAZORPAY_KEY_ID or not RAZORPAY_KEY_SECRET:
        raise HTTPException(status_code=500, detail="Razorpay keys missing")
    return razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))


def round_money(value) -> Decimal:
    return Decimal(str(value or 0)).quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP
    )


def get_user_cart(db: Session, user_id: int):
    cart = db.execute(
        text("""
            SELECT id
            FROM cart
            WHERE user_id = :user_id
            ORDER BY id DESC
            LIMIT 1
        """),
        {"user_id": user_id},
    ).mappings().first()

    if not cart:
        raise HTTPException(status_code=400, detail="Cart not found")

    return cart["id"]


def get_cart_items(db: Session, cart_id: int):
    items = db.execute(
        text("""
            SELECT
                ci.id,
                ci.cart_id,
                ci.variant_id,
                ci.quantity,
                COALESCE(ci.price, pv.price, 0) AS price,
                COALESCE(ci.customization_total, 0) AS customization_total,
                pv.product_id,
                COALESCE(p.name, 'Product') AS product_name,
                COALESCE(p.description, '') AS product_description
            FROM cart_item ci
            LEFT JOIN product_variant pv ON pv.id = ci.variant_id
            LEFT JOIN product p ON p.id = pv.product_id
            WHERE ci.cart_id = :cart_id
        """),
        {"cart_id": cart_id},
    ).mappings().all()

    if not items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    return items


def calculate_cart_total(cart_items):
    total = Decimal("0.00")

    for item in cart_items:
        price = Decimal(str(item["price"] or 0))
        qty = Decimal(str(item["quantity"] or 0))
        customization = Decimal(str(item["customization_total"] or 0))
        total += (price + customization) * qty

    return round_money(total)


def apply_coupon_if_any(db: Session, coupon_code: str, user_id: int, gross_amount: Decimal):
    if not coupon_code:
        return None, Decimal("0.00")

    row = db.execute(
        text("""
            SELECT coupon_id, discount_amount, message
            FROM fn_validate_coupon(:coupon_code, :user_id, :gross_amount)
        """),
        {
            "coupon_code": coupon_code,
            "user_id": user_id,
            "gross_amount": gross_amount,
        },
    ).mappings().first()

    if not row or not row["coupon_id"]:
        raise HTTPException(
            status_code=400,
            detail=row["message"] if row else "Invalid coupon",
        )

    return row["coupon_id"], round_money(row["discount_amount"])


def safe_get_address(db: Session, address_id: int):
    if not address_id:
        return None

    for table_name in ["address", "addresses"]:
        try:
            table_exists = db.execute(
                text("SELECT to_regclass(:table_name)"),
                {"table_name": f"public.{table_name}"}
            ).scalar()

            if not table_exists:
                continue

            row = db.execute(
                text(f"""
                    SELECT *
                    FROM {table_name}
                    WHERE id = :address_id
                    LIMIT 1
                """),
                {"address_id": address_id},
            ).mappings().first()

            if row:
                return row

        except Exception as e:
            print("ADDRESS FETCH ERROR:", str(e))
            db.rollback()

    return None


def generate_invoice_after_successful_payment(
    db: Session,
    order_id: int,
    user_id: int,
    address_id: int,
    cart_items,
):
    invoice_no = f"INV-ORDER-{order_id}"

    existing_invoice = (
        db.query(Invoice)
        .filter(Invoice.invoice_number == invoice_no)
        .first()
    )

    if existing_invoice:
        return {
            "invoice_id": existing_invoice.id,
            "invoice_no": existing_invoice.invoice_number,
            "message": "Invoice already exists",
        }

    address = safe_get_address(db, address_id)

    buyer_name = "Customer"
    buyer_contact = ""
    buyer_state = "Maharashtra"
    buyer_state_code = "27"
    buyer_gstin = ""
    buyer_address = ""

    if address:
        buyer_name = address.get("full_name") or address.get("name") or "Customer"
        buyer_contact = address.get("phone") or ""
        buyer_state = address.get("state") or "Maharashtra"

        address_parts = [
            address.get("address_line1") or "",
            address.get("address_line2") or "",
            address.get("landmark") or "",
            address.get("city") or "",
            address.get("state") or "",
            address.get("postal_code") or address.get("pincode") or "",
        ]
        buyer_address = ", ".join([part for part in address_parts if part])

    if str(buyer_state).strip().lower() == "maharashtra":
        buyer_state_code = "27"

    invoice_items = []

    for item in cart_items:
        quantity = int(item["quantity"] or 1)
        price = Decimal(str(item["price"] or 0))
        customization_total = Decimal(str(item["customization_total"] or 0))
        final_rate = price + customization_total

        invoice_items.append({
            "name": item.get("product_name") or f"Product Variant {item['variant_id']}",
            "description": item.get("product_description") or "",
            "hsn": item.get("hsn") or "6205",
            "quantity": quantity,
            "rate": float(final_rate),
            "gst_rate": 5,
            "variant_id": item.get("variant_id"),
            "product_id": item.get("product_id"),
        })

    if not invoice_items:
        raise Exception("Cannot generate invoice because order has no items")

    payload = InvoiceCreate(
        invoice_no=invoice_no,
        invoice_date=datetime.now().strftime("%Y-%m-%d"),
        dispatch_through="Courier",
        destination=buyer_state,
        buyer={
            "name": buyer_name,
            "address": buyer_address,
            "gstin": buyer_gstin,
            "state": buyer_state,
            "state_code": buyer_state_code,
            "contact": buyer_contact,
        },
        items=invoice_items,
    )

    taxable_amount = Decimal("0.00")
    tax_amount = Decimal("0.00")

    for item in payload.items:
        item_amount = round_money(
            Decimal(str(item.quantity)) * Decimal(str(item.rate))
        )
        item_tax = round_money(
            item_amount * Decimal(str(item.gst_rate)) / Decimal("100")
        )

        taxable_amount += item_amount
        tax_amount += item_tax

    final_amount = round_money(taxable_amount + tax_amount)

    pdf_path = InvoiceService.generate_invoice_pdf(payload)

    billing_address_json = {
        "buyer_name": payload.buyer.name,
        "address": payload.buyer.address,
        "state": payload.buyer.state or "",
        "state_code": payload.buyer.state_code or "",
        "contact": payload.buyer.contact or "",
    }

    invoice = Invoice(
        invoice_number=payload.invoice_no,
        billing_address=billing_address_json,
        gst_number=payload.buyer.gstin or "",
        total_tax=tax_amount,
        total_amount=taxable_amount,
        tax_amount=tax_amount,
        final_amount=final_amount,
        reference_type="order",
        reference_id=order_id,
        order_id=order_id,
    )

    db.add(invoice)
    db.flush()

    for index, item in enumerate(payload.items):
        item_amount = round_money(
            Decimal(str(item.quantity)) * Decimal(str(item.rate))
        )
        item_tax = round_money(
            item_amount * Decimal(str(item.gst_rate)) / Decimal("100")
        )
        item_total = round_money(item_amount + item_tax)

        source_item = invoice_items[index]

        invoice_item = InvoiceItem(
            invoice_id=invoice.id,
            product_id=source_item.get("product_id"),
            product_name=item.name,
            description=item.description,
            hsn_code=item.hsn,
            variant_id=source_item.get("variant_id"),
            quantity=item.quantity,
            price=item.rate,
            taxable_value=item_amount,
            gst_rate=item.gst_rate,
            gst_amount=item_tax,
            total_price=item_total,
        )

        db.add(invoice_item)

    db.flush()

    return {
        "invoice_id": invoice.id,
        "invoice_no": invoice_no,
        "file_path": pdf_path,
        "message": "Invoice generated successfully",
    }


def create_pending_order(
    db: Session,
    user_id: int,
    address_id: int,
    cart_items,
    gross_amount: Decimal,
    coupon_id=None,
    coupon_discount: Decimal = Decimal("0.00"),
):
    final_amount = round_money(gross_amount - coupon_discount)

    if final_amount <= 0:
        raise HTTPException(
            status_code=400,
            detail="Final amount must be greater than 0",
        )

    order_row = db.execute(
        text("""
            INSERT INTO orders (
                user_id,
                total_amount,
                gross_amount,
                status,
                address_id,
                payment_status,
                created_at,
                updated_at,
                created_by,
                updated_by,
                coupon_id,
                coupon_discount_amount,
                additional_discount_amount,
                amount_paid,
                paid_amount,
                remaining_amount
            )
            VALUES (
                :user_id,
                :total_amount,
                :gross_amount,
                'PENDING',
                :address_id,
                'PENDING',
                CURRENT_TIMESTAMP,
                CURRENT_TIMESTAMP,
                :user_id,
                :user_id,
                :coupon_id,
                :coupon_discount_amount,
                0,
                0,
                0,
                :remaining_amount
            )
            RETURNING id
        """),
        {
            "user_id": user_id,
            "address_id": address_id,
            "total_amount": final_amount,
            "gross_amount": gross_amount,
            "coupon_id": coupon_id,
            "coupon_discount_amount": coupon_discount,
            "remaining_amount": final_amount,
        },
    ).mappings().first()

    order_id = order_row["id"]

    for item in cart_items:
        db.execute(
            text("""
                INSERT INTO order_items (
                    order_id,
                    variant_id,
                    quantity,
                    unit_price,
                    customization_total,
                    product_id,
                    product_name_snapshot,
                    created_at
                )
                VALUES (
                    :order_id,
                    :variant_id,
                    :quantity,
                    :unit_price,
                    :customization_total,
                    :product_id,
                    :product_name_snapshot,
                    CURRENT_TIMESTAMP
                )
            """),
            {
                "order_id": order_id,
                "variant_id": item["variant_id"],
                "quantity": item["quantity"],
                "unit_price": item["price"],
                "customization_total": item["customization_total"] or 0,
                "product_id": item["product_id"],
                "product_name_snapshot": item["product_name"],
            },
        )

    db.flush()

    final_row = db.execute(
        text("""
            SELECT id, final_amount, remaining_amount
            FROM orders
            WHERE id = :order_id
        """),
        {"order_id": order_id},
    ).mappings().first()

    payable_amount = final_row["remaining_amount"] or final_row["final_amount"]

    return order_id, round_money(payable_amount)


def create_razorpay_order_service(
    db: Session,
    user_id: int,
    address_id: int,
    coupon_code: str = None,
    currency: str = "INR",
):
    try:
        cart_id = get_user_cart(db, user_id)
        cart_items = get_cart_items(db, cart_id)

        gross_amount = calculate_cart_total(cart_items)

        coupon_id, coupon_discount = apply_coupon_if_any(
            db=db,
            coupon_code=coupon_code,
            user_id=user_id,
            gross_amount=gross_amount,
        )

        order_id, payable_amount = create_pending_order(
            db=db,
            user_id=user_id,
            address_id=address_id,
            cart_items=cart_items,
            gross_amount=gross_amount,
            coupon_id=coupon_id,
            coupon_discount=coupon_discount,
        )

        amount_paise = int(payable_amount * 100)

        client = get_razorpay_client()

        razorpay_order = client.order.create({
            "amount": amount_paise,
            "currency": currency,
            "receipt": f"order_{order_id}",
            "payment_capture": 1,
        })

        db.execute(
            text("""
                UPDATE orders
                SET razorpay_order_id = :razorpay_order_id,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = :order_id
            """),
            {
                "razorpay_order_id": razorpay_order["id"],
                "order_id": order_id,
            },
        )

        db.commit()

        return {
            "success": True,
            "key": RAZORPAY_KEY_ID,
            "key_id": RAZORPAY_KEY_ID,
            "order_id": order_id,
            "razorpay_order_id": razorpay_order["id"],
            "amount": float(payable_amount),
            "amount_paise": amount_paise,
            "gross_amount": float(gross_amount),
            "coupon_discount_amount": float(coupon_discount),
            "final_amount": float(payable_amount),
            "currency": currency,
            "receipt": f"order_{order_id}",
            "status": razorpay_order.get("status"),
        }

    except HTTPException:
        db.rollback()
        raise

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create Razorpay order: {str(e)}",
        )


def verify_razorpay_payment_service(
    db: Session,
    razorpay_order_id: str,
    razorpay_payment_id: str,
    razorpay_signature: str,
    user_id: int,
    address_id: int,
):
    order_id = None
    transaction_id = None
    payable_amount = Decimal("0.00")
    cart_id = None
    cart_items = []

    try:
        if not RAZORPAY_KEY_SECRET:
            raise HTTPException(status_code=500, detail="Razorpay secret missing")

        body = f"{razorpay_order_id}|{razorpay_payment_id}"

        generated_signature = hmac.new(
            RAZORPAY_KEY_SECRET.encode("utf-8"),
            body.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

        if not hmac.compare_digest(generated_signature, razorpay_signature):
            raise HTTPException(status_code=400, detail="Invalid Razorpay signature")

        order_row = db.execute(
            text("""
                SELECT id, final_amount, remaining_amount, payment_status
                FROM orders
                WHERE user_id = :user_id
                  AND address_id = :address_id
                  AND razorpay_order_id = :razorpay_order_id
                  AND status = 'PENDING'
                  AND payment_status = 'PENDING'
                LIMIT 1
                FOR UPDATE
            """),
            {
                "user_id": user_id,
                "address_id": address_id,
                "razorpay_order_id": razorpay_order_id,
            },
        ).mappings().first()

        if not order_row:
            raise HTTPException(
                status_code=400,
                detail="Pending order not found for this Razorpay order",
            )

        order_id = order_row["id"]

        payable_amount = round_money(
            order_row["remaining_amount"] or order_row["final_amount"]
        )

        if payable_amount <= 0:
            raise HTTPException(status_code=400, detail="Invalid payable amount")

        cart_id = get_user_cart(db, user_id)
        cart_items = get_cart_items(db, cart_id)

        existing_txn = db.execute(
            text("""
                SELECT id
                FROM transactions
                WHERE transaction_ref = :payment_id
                LIMIT 1
            """),
            {"payment_id": razorpay_payment_id},
        ).mappings().first()

        if existing_txn:
            transaction_id = existing_txn["id"]
        else:
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
                    "order_id": order_id,
                    "amount": payable_amount,
                    "transaction_ref": razorpay_payment_id,
                    "gateway_transaction_id": razorpay_order_id,
                    "gateway_response": json.dumps({
                        "razorpay_order_id": razorpay_order_id,
                        "razorpay_payment_id": razorpay_payment_id,
                        "razorpay_signature": razorpay_signature,
                    }),
                },
            ).mappings().first()

            transaction_id = transaction_row["id"]

        db.execute(
            text("""
                UPDATE orders
                SET transaction_id = :transaction_id,
                    razorpay_payment_id = :razorpay_payment_id,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = :order_id
            """),
            {
                "transaction_id": transaction_id,
                "razorpay_payment_id": razorpay_payment_id,
                "order_id": order_id,
            },
        )

        db.commit()

    except HTTPException:
        db.rollback()
        raise

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to verify payment: {str(e)}",
        )

    invoice_data = None
    invoice_error = None

    try:
        invoice_data = generate_invoice_after_successful_payment(
            db=db,
            order_id=order_id,
            user_id=user_id,
            address_id=address_id,
            cart_items=cart_items,
        )
        db.commit()

    except Exception as e:
        db.rollback()
        invoice_error = str(e)
        print("INVOICE GENERATION ERROR:", invoice_error)

    try:
        if cart_id:
            db.execute(
                text("DELETE FROM cart_item WHERE cart_id = :cart_id"),
                {"cart_id": cart_id},
            )
            db.commit()

    except Exception as e:
        db.rollback()
        print("CART CLEAR ERROR:", str(e))

    return {
        "success": True,
        "status": "success",
        "message": "Payment verified successfully",
        "payment_status": "SUCCESS",
        "order_id": order_id,
        "transaction_id": transaction_id,
        "transaction_ref": razorpay_payment_id,
        "razorpay_order_id": razorpay_order_id,
        "paid_amount": float(payable_amount),
        "invoice": invoice_data,
        "invoice_error": invoice_error,
    }


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
        db,
        user_id: int,
        address_id: int,
        coupon_code=None,
        currency: str = "INR",
    ):
        return create_razorpay_order_service(
            db=db,
            user_id=user_id,
            address_id=address_id,
            coupon_code=coupon_code,
            currency=currency,
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