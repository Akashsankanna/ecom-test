from decimal import Decimal, ROUND_HALF_UP
import glob
import os

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.db.session import get_db
from app.schemas.invoice_schema import InvoiceCreate, InvoiceResponse
from app.services.invoice_service import InvoiceService
from app.models.invoice_model import Invoice, InvoiceItem


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


def calculate_invoice_totals(items):
    taxable_amount = Decimal("0.00")
    tax_amount = Decimal("0.00")

    for item in items:
        item_amount = round_money(
            Decimal(str(item.quantity or 0)) * Decimal(str(item.rate or 0))
        )

        item_tax = round_money(
            item_amount * Decimal(str(item.gst_rate or 0)) / Decimal("100")
        )

        taxable_amount += item_amount
        tax_amount += item_tax

    final_amount = (taxable_amount + tax_amount).quantize(
        Decimal("1"),
        rounding=ROUND_HALF_UP
    )

    return taxable_amount, tax_amount, final_amount


def save_manual_invoice_to_db(
    db: Session,
    payload: InvoiceCreate,
    reference_type: str = "manual",
    reference_id=None,
    order_id=None,
):
    taxable_amount, tax_amount, final_amount = calculate_invoice_totals(payload.items)

    billing_address_json = {
        "buyer_name": payload.buyer.name or "Customer",
        "address": payload.buyer.address or "",
        "state": payload.buyer.state or "Maharashtra",
        "state_code": payload.buyer.state_code or "27",
        "contact": payload.buyer.contact or "",
        "gstin": payload.buyer.gstin or "",
    }

    invoice = Invoice(
        invoice_number=payload.invoice_no,
        billing_address=billing_address_json,
        gst_number=payload.buyer.gstin or "",
        total_tax=tax_amount,
        total_amount=taxable_amount,
        tax_amount=tax_amount,
        final_amount=final_amount,
        reference_type=reference_type,
        reference_id=reference_id,
        order_id=order_id,
    )

    db.add(invoice)
    db.flush()

    for item in payload.items:
        qty = int(item.quantity or 1)
        rate = round_money(item.rate or 0)
        taxable_value = round_money(Decimal(str(qty)) * rate)
        gst_rate = round_money(item.gst_rate or 0)
        gst_amount = round_money(taxable_value * gst_rate / Decimal("100"))
        total_price = taxable_value + gst_amount

        invoice_item = InvoiceItem(
            invoice_id=invoice.id,
            product_name=item.name,
            description=item.description or "",
            hsn_code=item.hsn or "6205",
            quantity=qty,
            price=rate,
            taxable_value=taxable_value,
            gst_rate=gst_rate,
            gst_amount=gst_amount,
            total_amount=total_price,
            total_price=total_price,
        )

        db.add(invoice_item)

    return invoice


@router.post("/generate", response_model=InvoiceResponse)
def generate_manual_invoice(
    payload: InvoiceCreate,
    db: Session = Depends(get_db),
):
    try:
        existing_invoice = (
            db.query(Invoice)
            .filter(Invoice.invoice_number == payload.invoice_no)
            .first()
        )

        existing_pdf = find_invoice_pdf(payload.invoice_no)

        if existing_invoice and existing_pdf:
            return {
                "message": "Invoice already exists",
                "file_path": existing_pdf,
            }

        os.makedirs(INVOICE_DIR, exist_ok=True)

        pdf_path = InvoiceService.generate_invoice_pdf(payload)

        if not existing_invoice:
            invoice = save_manual_invoice_to_db(
                db=db,
                payload=payload,
                reference_type="manual",
                reference_id=None,
                order_id=None,
            )
            db.commit()
            db.refresh(invoice)

        return {
            "message": "Invoice generated successfully",
            "file_path": pdf_path,
        }

    except Exception as e:
        db.rollback()
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
        # Check if invoice already generated for this order
        existing_invoice = db.execute(
            text("""
                SELECT id, invoice_number
                FROM invoice
                WHERE order_id = :order_id
                   OR reference_id = :order_id
                ORDER BY id DESC
                LIMIT 1
            """),
            {"order_id": order_id}
        ).mappings().first()

        if existing_invoice:
            invoice_id = existing_invoice["id"]
            invoice_no = existing_invoice["invoice_number"]
        else:
            # DB stored procedure/function generates invoice number
            invoice_id = db.execute(
                text("SELECT public.sp_generate_invoice(:order_id)"),
                {"order_id": order_id}
            ).scalar()

            invoice_row = db.execute(
                text("""
                    SELECT id, invoice_number
                    FROM invoice
                    WHERE id = :invoice_id
                    LIMIT 1
                """),
                {"invoice_id": invoice_id}
            ).mappings().first()

            if not invoice_row:
                raise HTTPException(
                    status_code=500,
                    detail="Invoice generated but not found in DB"
                )

            invoice_no = invoice_row["invoice_number"]

        db.commit()

        return {
            "message": "Invoice generated successfully from DB procedure",
            "invoice_id": invoice_id,
            "invoice_no": invoice_no,
            "download_url": f"/invoice/download/{invoice_no}",
        }

    except HTTPException:
        db.rollback()
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