import glob
import os
from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.db.session import get_db
from app.schemas.invoice_schema import InvoiceCreate, InvoiceResponse
from app.services.invoice_service import InvoiceService


router = APIRouter(
    prefix="/invoice",
    tags=["Invoice"]
)

INVOICE_DIR = "generated_invoices"


def round_money(value) -> Decimal:
    return Decimal(str(value or 0)).quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP
    )


def find_invoice_pdf(invoice_no: str):
    safe_invoice_no = invoice_no.replace("/", "_")
    files = glob.glob(os.path.join(INVOICE_DIR, f"{safe_invoice_no}_*.pdf"))
    if not files:
        return None
    return max(files, key=os.path.getctime)


@router.post("/generate", response_model=InvoiceResponse)
def generate_manual_invoice(
    payload: InvoiceCreate,
    db: Session = Depends(get_db),
):
    try:
        result = InvoiceService.create_invoice(
            db=db,
            invoice=payload,
            order_id=None,
            reference_type="MANUAL",
            reference_id=None,
        )

        return {
            "message": result["message"],
            "file_path": result["pdf_path"],
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Invoice generation failed: {str(e)}"
        )


@router.post("/generate/order/{order_id}")
def generate_invoice_by_order_id(
    order_id: int,
    db: Session = Depends(get_db),
):
    try:
        order = db.execute(text("""
            SELECT
                o.id,
                o.user_id,
                o.address_id,
                o.final_amount,
                o.status,
                o.payment_status,
                COALESCE(a.full_name, u.name, 'Customer') AS customer_name,
                COALESCE(a.phone, u.phone, '') AS phone,
                COALESCE(a.address_line1, '') AS address_line1,
                COALESCE(a.address_line2, '') AS address_line2,
                COALESCE(a.landmark, '') AS landmark,
                COALESCE(a.city, '') AS city,
                COALESCE(a.state, 'Maharashtra') AS state,
                COALESCE(a.postal_code, '') AS pincode
            FROM orders o
            LEFT JOIN users u ON u.id = o.user_id
            LEFT JOIN address a ON a.id = o.address_id
            WHERE o.id = :order_id
            LIMIT 1
        """), {"order_id": order_id}).mappings().fetchone()

        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        items = db.execute(text("""
            SELECT
                oi.product_id,
                oi.variant_id,
                oi.quantity,
                oi.unit_price AS price,
                COALESCE(oi.customization_total, 0) AS customization_total,
                COALESCE(oi.product_name_snapshot, p.name, 'Product') AS product_name,
                COALESCE(p.description, '') AS description,
                '6205' AS hsn_code,
                5 AS gst_rate
            FROM order_items oi
            LEFT JOIN product p ON p.id = oi.product_id
            WHERE oi.order_id = :order_id
            ORDER BY oi.id ASC
        """), {"order_id": order_id}).mappings().all()

        if not items:
            raise HTTPException(status_code=404, detail="Order items not found")

        address_text = ", ".join([
            str(order["address_line1"] or ""),
            str(order["address_line2"] or ""),
            str(order["landmark"] or ""),
            str(order["city"] or ""),
            str(order["state"] or ""),
            str(order["pincode"] or ""),
        ]).strip(", ")

        invoice_payload = InvoiceCreate(
            invoice_no=f"INV-ORDER-{order_id}",
            invoice_date=str(date.today()),
            dispatch_through="Courier",
            destination=order["state"] or "Maharashtra",
            buyer={
                "name": order["customer_name"] or "Customer",
                "address": address_text,
                "gstin": "",
                "state": order["state"] or "Maharashtra",
                "state_code": "27",
                "contact": order["phone"] or "",
            },
            items=[
                {
                    "name": item["product_name"],
                    "description": item["description"],
                    "hsn": item["hsn_code"],
                    "quantity": item["quantity"],
                    "rate": round_money(
                        Decimal(str(item["price"] or 0)) +
                        Decimal(str(item["customization_total"] or 0))
                    ),
                    "gst_rate": item["gst_rate"],
                    "product_id": item["product_id"],
                    "variant_id": item["variant_id"],
                }
                for item in items
            ],
        )

        result = InvoiceService.create_invoice(
            db=db,
            invoice=invoice_payload,
            order_id=order_id,
            reference_type="ORDER",
            reference_id=order_id,
        )

        return {
            "message": "Invoice generated successfully",
            "invoice_id": result["invoice_id"],
            "invoice_no": result["invoice_number"],
            "final_amount": result["final_amount"],
            "file_path": result["pdf_path"],
            "download_url": f"/invoice/download/{result['invoice_number']}",
        }

    except HTTPException:
        raise

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Invoice generation from order failed: {str(e)}"
        )


@router.get("/download/{invoice_no:path}")
def download_invoice(invoice_no: str):
    pdf_path = find_invoice_pdf(invoice_no)

    if not pdf_path:
        raise HTTPException(
            status_code=404,
            detail="Invoice PDF not found. Generate PDF first."
        )

    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=f"{invoice_no.replace('/', '_')}.pdf",
    )