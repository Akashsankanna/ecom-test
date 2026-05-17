from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from uuid import uuid4
from xml.sax.saxutils import escape
import json

from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, KeepTogether
from num2words import num2words

from app.schemas.invoice_schema import InvoiceCreate


COMPANY = {
    "name": "Pushpa Textile",
    "address": "155-4-A AKKLAKOT NAKA GANDHINAGAR\nAKKALKOT ROAD\nSolapur 413006",
    "phone": "9923173456",
    "email": "info@pushpatextile.com",
    "gstin": "27AAYPR4273L1ZO",
    "state": "Maharashtra",
    "state_code": "27",
    "bank_name": "State Bank of India",
    "account_no": "36259243487",
    "branch_ifsc": "BALIVES BRANCH SOLAPUR & SBIN0000483",
}


def to_decimal(value) -> Decimal:
    try:
        return Decimal(str(value or 0)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    except Exception:
        return Decimal("0.00")


def safe(value) -> str:
    return escape(str(value or "")).replace("\n", "<br/>")


def amount_in_words(amount: Decimal) -> str:
    amount = to_decimal(amount)
    words = num2words(int(amount), lang="en_IN").title().replace(",", "")
    return f"INR {words} Only"


class InvoiceService:

    @staticmethod
    def get_order_totals(db: Session, order_id: int):
        order = db.execute(text("""
            SELECT
                id,
                total_amount,
                gst_amount,
                delivery_charge,
                platform_fee,
                customization_total,
                coupon_discount_amount,
                additional_discount_amount,
                final_amount,
                gst_percentage
            FROM orders
            WHERE id = :order_id
        """), {"order_id": order_id}).mappings().fetchone()

        if not order:
            raise Exception(f"Order not found: {order_id}")

        return {
            "subtotal": to_decimal(order["total_amount"]),
            "gst_amount": to_decimal(order["gst_amount"]),
            "delivery_charge": to_decimal(order["delivery_charge"]),
            "platform_fee": to_decimal(order["platform_fee"]),
            "customization_total": to_decimal(order["customization_total"]),
            "coupon_discount": to_decimal(order["coupon_discount_amount"]),
            "additional_discount": to_decimal(order["additional_discount_amount"]),
            "final_amount": to_decimal(order["final_amount"]),
            "gst_percentage": to_decimal(order["gst_percentage"] or 5),
        }

    @staticmethod
    def save_invoice_to_db(
        db: Session,
        invoice: InvoiceCreate,
        order_id: int | None = None,
        reference_type: str = "ORDER",
        reference_id: int | None = None,
    ):
        try:
            db_totals = None

            if order_id:
                existing = db.execute(text("""
                    SELECT id, invoice_number, total_amount, tax_amount, final_amount
                    FROM invoice
                    WHERE order_id = :order_id
                       OR (reference_type = 'ORDER' AND reference_id = :order_id)
                    LIMIT 1
                """), {"order_id": order_id}).mappings().fetchone()

                if existing:
                    return {
                        "invoice_id": existing["id"],
                        "invoice_number": existing["invoice_number"],
                        "total_amount": float(to_decimal(existing["total_amount"])),
                        "tax_amount": float(to_decimal(existing["tax_amount"])),
                        "final_amount": float(to_decimal(existing["final_amount"])),
                        "db_totals": InvoiceService.get_order_totals(db, order_id),
                    }

                db_totals = InvoiceService.get_order_totals(db, order_id)
                invoice_number = f"INV-ORDER-{order_id}"

                taxable_total = db_totals["subtotal"]
                tax_total = db_totals["gst_amount"]
                final_amount = db_totals["final_amount"]

            else:
                invoice_number = getattr(invoice, "invoice_no", None) or f"INV-MANUAL-{uuid4().hex[:8].upper()}"

                taxable_total = Decimal("0.00")
                tax_total = Decimal("0.00")

                for item in invoice.items:
                    qty = to_decimal(item.quantity)
                    rate = to_decimal(item.rate)
                    gst_rate = to_decimal(item.gst_rate)
                    taxable = to_decimal(qty * rate)
                    gst = to_decimal(taxable * gst_rate / Decimal("100"))
                    taxable_total += taxable
                    tax_total += gst

                final_amount = to_decimal(taxable_total + tax_total)

                db_totals = {
                    "subtotal": taxable_total,
                    "gst_amount": tax_total,
                    "delivery_charge": Decimal("0.00"),
                    "platform_fee": Decimal("0.00"),
                    "customization_total": Decimal("0.00"),
                    "coupon_discount": Decimal("0.00"),
                    "additional_discount": Decimal("0.00"),
                    "final_amount": final_amount,
                    "gst_percentage": Decimal("5.00"),
                }

            buyer_address = {
                "name": invoice.buyer.name,
                "address": invoice.buyer.address,
                "gstin": invoice.buyer.gstin,
                "state": invoice.buyer.state,
                "state_code": invoice.buyer.state_code,
                "contact": invoice.buyer.contact,
            }

            invoice_row = db.execute(text("""
                INSERT INTO invoice (
                    order_id,
                    invoice_number,
                    invoice_date,
                    billing_address,
                    gst_number,
                    total_tax,
                    reference_type,
                    reference_id,
                    total_amount,
                    tax_amount,
                    final_amount,
                    taxable_value,
                    gst_rate,
                    gst_amount,
                    total_amount_with_gst
                )
                VALUES (
                    :order_id,
                    :invoice_number,
                    NOW(),
                    CAST(:billing_address AS JSONB),
                    :gst_number,
                    :total_tax,
                    :reference_type,
                    :reference_id,
                    :total_amount,
                    :tax_amount,
                    :final_amount,
                    :taxable_value,
                    :gst_rate,
                    :gst_amount,
                    :total_amount_with_gst
                )
                RETURNING id
            """), {
                "order_id": order_id,
                "invoice_number": invoice_number,
                "billing_address": json.dumps(buyer_address),
                "gst_number": invoice.buyer.gstin,
                "total_tax": tax_total,
                "reference_type": reference_type,
                "reference_id": reference_id or order_id,
                "total_amount": taxable_total,
                "tax_amount": tax_total,
                "final_amount": final_amount,
                "taxable_value": taxable_total,
                "gst_rate": db_totals["gst_percentage"],
                "gst_amount": tax_total,
                "total_amount_with_gst": to_decimal(taxable_total + tax_total),
            }).mappings().fetchone()

            invoice_id = invoice_row["id"]

            for item in invoice.items:
                qty = to_decimal(item.quantity)
                rate = to_decimal(item.rate)
                gst_rate = to_decimal(item.gst_rate)
                taxable_value = to_decimal(qty * rate)
                gst_amount = to_decimal(taxable_value * gst_rate / Decimal("100"))
                total_price = to_decimal(taxable_value + gst_amount)

                db.execute(text("""
                    INSERT INTO invoice_item (
                        invoice_id,
                        product_name,
                        variant_id,
                        quantity,
                        price,
                        total_price,
                        product_id,
                        description,
                        hsn_code,
                        taxable_value,
                        gst_rate,
                        gst_amount
                    )
                    VALUES (
                        :invoice_id,
                        :product_name,
                        :variant_id,
                        :quantity,
                        :price,
                        :total_price,
                        :product_id,
                        :description,
                        :hsn_code,
                        :taxable_value,
                        :gst_rate,
                        :gst_amount
                    )
                """), {
                    "invoice_id": invoice_id,
                    "product_name": item.name,
                    "variant_id": getattr(item, "variant_id", None),
                    "quantity": int(qty),
                    "price": rate,
                    "total_price": total_price,
                    "product_id": getattr(item, "product_id", None),
                    "description": item.description,
                    "hsn_code": item.hsn,
                    "taxable_value": taxable_value,
                    "gst_rate": gst_rate,
                    "gst_amount": gst_amount,
                })

            db.commit()

            return {
                "invoice_id": invoice_id,
                "invoice_number": invoice_number,
                "total_amount": float(taxable_total),
                "tax_amount": float(tax_total),
                "final_amount": float(final_amount),
                "db_totals": db_totals,
            }

        except SQLAlchemyError as e:
            db.rollback()
            raise Exception(f"Invoice DB save error: {str(e.orig)}")
        except Exception:
            db.rollback()
            raise

    @staticmethod
    def generate_invoice_pdf(invoice: InvoiceCreate, db_totals: dict | None = None) -> str:
        output_dir = Path("generated_invoices")
        output_dir.mkdir(parents=True, exist_ok=True)

        invoice_no = getattr(invoice, "invoice_no", None) or "invoice"
        file_name = f"{str(invoice_no).replace('/', '_')}_{uuid4().hex[:8]}.pdf"
        pdf_path = output_dir / file_name

        doc = SimpleDocTemplate(
            str(pdf_path),
            pagesize=A4,
            rightMargin=18,
            leftMargin=18,
            topMargin=18,
            bottomMargin=18,
        )

        styles = getSampleStyleSheet()
        normal = ParagraphStyle("InvoiceNormal", parent=styles["Normal"], fontSize=8, leading=10)
        title_style = ParagraphStyle("InvoiceTitle", parent=styles["Title"], fontSize=16, leading=18, alignment=1)

        elements = [Paragraph("Tax Invoice", title_style)]

        seller_text = f"""
        <b>{safe(COMPANY['name'])}</b><br/>
        {safe(COMPANY['address'])}<br/>
        Phone : {safe(COMPANY['phone'])}<br/>
        E-Mail : {safe(COMPANY['email'])}<br/>
        GSTIN/UIN : {safe(COMPANY['gstin'])}<br/>
        State Name : {safe(COMPANY['state'])}, Code : {safe(COMPANY['state_code'])}
        """

        invoice_text = f"""
        <b>Invoice No.</b><br/>
        {safe(invoice_no)}<br/><br/>
        <b>Dated</b><br/>
        {safe(getattr(invoice, "invoice_date", ""))}<br/><br/>
        <b>Dispatched through</b><br/>
        {safe(getattr(invoice, "dispatch_through", ""))}<br/><br/>
        <b>Destination</b><br/>
        {safe(getattr(invoice, "destination", ""))}
        """

        header_table = Table([[Paragraph(seller_text, normal), Paragraph(invoice_text, normal)]], colWidths=[315, 244])
        header_table.setStyle(TableStyle([
            ("BOX", (0, 0), (-1, -1), 0.8, colors.black),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.black),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("PADDING", (0, 0), (-1, -1), 6),
        ]))
        elements.append(header_table)

        buyer = invoice.buyer
        buyer_text = f"""
        <b>Consignee (Ship to)</b><br/>
        <b>{safe(buyer.name)}</b><br/>
        {safe(buyer.address)}<br/>
        GSTIN/UIN : {safe(buyer.gstin)}<br/>
        State Name : {safe(buyer.state)}, Code : {safe(buyer.state_code)}<br/>
        Contact : {safe(buyer.contact)}<br/><br/>

        <b>Buyer (Bill to)</b><br/>
        <b>{safe(buyer.name)}</b><br/>
        {safe(buyer.address)}<br/>
        GSTIN/UIN : {safe(buyer.gstin)}<br/>
        State Name : {safe(buyer.state)}, Code : {safe(buyer.state_code)}<br/>
        Contact : {safe(buyer.contact)}
        """

        buyer_table = Table([[Paragraph(buyer_text, normal)]], colWidths=[559])
        buyer_table.setStyle(TableStyle([
            ("BOX", (0, 0), (-1, -1), 0.8, colors.black),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("PADDING", (0, 0), (-1, -1), 6),
        ]))
        elements.append(buyer_table)
        elements.append(Spacer(1, 6))

        item_rows = [[
            Paragraph("<b>Description of Goods and Services</b>", normal),
            Paragraph("<b>HSN/SAC</b>", normal),
            Paragraph("<b>Quantity</b>", normal),
            Paragraph("<b>Rate</b>", normal),
            Paragraph("<b>Per</b>", normal),
            Paragraph("<b>Amount</b>", normal),
        ]]

        total_qty = 0
        item_subtotal = Decimal("0.00")

        for item in invoice.items:
            qty = to_decimal(item.quantity)
            rate = to_decimal(item.rate)
            amount = to_decimal(qty * rate)
            item_subtotal += amount
            total_qty += int(qty)

            item_rows.append([
                Paragraph(f"<b>{safe(item.name)}</b><br/>{safe(item.description)}", normal),
                safe(item.hsn),
                f"{int(qty)} Nos.",
                f"{rate:.2f}",
                "Nos.",
                f"{amount:.2f}",
            ])

        if db_totals:
            taxable_total = db_totals["subtotal"]
            tax_total = db_totals["gst_amount"]
            delivery = db_totals["delivery_charge"]
            platform = db_totals["platform_fee"]
            customization = db_totals["customization_total"]
            coupon_discount = db_totals["coupon_discount"]
            additional_discount = db_totals["additional_discount"]
            grand_total = db_totals["final_amount"]
        else:
            taxable_total = item_subtotal
            tax_total = Decimal("0.00")
            delivery = platform = customization = coupon_discount = additional_discount = Decimal("0.00")
            grand_total = taxable_total

        buyer_state = str(buyer.state or "").strip().lower()
        tax_label = "CGST + SGST" if buyer_state == COMPANY["state"].lower() else "IGST"

        item_rows.append(["", "", "", "", "Taxable Total", f"{taxable_total:.2f}"])
        item_rows.append(["", "", "", "", tax_label, f"{tax_total:.2f}"])

        if delivery > 0:
            item_rows.append(["", "", "", "", "Delivery Charge", f"{delivery:.2f}"])
        if platform > 0:
            item_rows.append(["", "", "", "", "Platform Fee", f"{platform:.2f}"])
        if customization > 0:
            item_rows.append(["", "", "", "", "Customization", f"{customization:.2f}"])
        if coupon_discount > 0:
            item_rows.append(["", "", "", "", "Coupon Discount", f"-{coupon_discount:.2f}"])
        if additional_discount > 0:
            item_rows.append(["", "", "", "", "Additional Discount", f"-{additional_discount:.2f}"])

        item_rows.append([Paragraph("<b>Total</b>", normal), "", f"{total_qty} Nos.", "", "", f"{grand_total:.2f}"])

        item_table = Table(item_rows, colWidths=[270, 55, 65, 55, 45, 69], repeatRows=1)
        item_table.setStyle(TableStyle([
            ("BOX", (0, 0), (-1, -1), 0.8, colors.black),
            ("INNERGRID", (0, 0), (-1, -1), 0.45, colors.black),
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
            ("PADDING", (0, 0), (-1, -1), 5),
        ]))

        elements.append(item_table)
        elements.append(Spacer(1, 10))
        elements.append(Paragraph(f"<b>Amount Chargeable (in words)</b> : {amount_in_words(grand_total)}", normal))
        elements.append(Spacer(1, 8))

        footer_left = f"""
        <b>Declaration</b><br/>
        We declare that this invoice shows the actual price of the goods described and that all particulars are true and correct.<br/><br/>
        <b>Company's Bank Details</b><br/>
        Bank Name : {safe(COMPANY['bank_name'])}<br/>
        A/c No. : {safe(COMPANY['account_no'])}<br/>
        Branch &amp; IFS Code : {safe(COMPANY['branch_ifsc'])}
        """

        footer_right = f"""
        <b>for {safe(COMPANY['name'])}</b><br/><br/><br/><br/>
        Authorised Signatory
        """

        footer_table = Table([[Paragraph(footer_left, normal), Paragraph(footer_right, normal)]], colWidths=[380, 179])
        footer_table.setStyle(TableStyle([
            ("BOX", (0, 0), (-1, -1), 0.8, colors.black),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("ALIGN", (1, 0), (1, 0), "RIGHT"),
            ("PADDING", (0, 0), (-1, -1), 10),
        ]))

        elements.append(KeepTogether([footer_table]))
        elements.append(Spacer(1, 5))
        elements.append(Paragraph("This is a Computer Generated Invoice", normal))

        doc.build(elements)
        return str(pdf_path)

    @staticmethod
    def create_invoice(
        db: Session,
        invoice: InvoiceCreate,
        order_id: int | None = None,
        reference_type: str = "ORDER",
        reference_id: int | None = None,
    ):
        db_result = InvoiceService.save_invoice_to_db(
            db=db,
            invoice=invoice,
            order_id=order_id,
            reference_type=reference_type,
            reference_id=reference_id or order_id,
        )

        invoice.invoice_no = db_result.get("invoice_number")

        pdf_path = InvoiceService.generate_invoice_pdf(
            invoice=invoice,
            db_totals=db_result.get("db_totals"),
        )

        return {
            "success": True,
            "message": "Invoice generated successfully",
            "invoice_id": db_result.get("invoice_id"),
            "invoice_number": db_result.get("invoice_number"),
            "pdf_path": pdf_path,
            "total_amount": db_result.get("total_amount"),
            "tax_amount": db_result.get("tax_amount"),
            "final_amount": db_result.get("final_amount"),
        }