from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from uuid import uuid4
from xml.sax.saxutils import escape
from datetime import datetime
import json

from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
    KeepTogether,
)
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
        return Decimal(str(value or 0)).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP
        )
    except Exception:
        return Decimal("0.00")


def safe(value) -> str:
    return escape(str(value or "")).replace("\n", "<br/>")


def amount_in_words(amount: Decimal) -> str:
    amount = to_decimal(amount)
    rupees = int(amount)
    words = num2words(rupees, lang="en_IN").title().replace(",", "")
    return f"INR {words} Only"


def generate_invoice_number(db: Session) -> str:
    year = datetime.now().year
    prefix = f"PT/{year}/"

    last_invoice = db.execute(
        text("""
            SELECT invoice_number
            FROM invoice
            WHERE invoice_number LIKE :prefix
            ORDER BY id DESC
            LIMIT 1
        """),
        {"prefix": f"{prefix}%"}
    ).mappings().fetchone()

    if not last_invoice:
        next_no = 1
    else:
        last_no = str(last_invoice["invoice_number"]).split("/")[-1]
        next_no = int(last_no) + 1

    return f"{prefix}{str(next_no).zfill(6)}"


class InvoiceService:

    @staticmethod
    def save_invoice_to_db(
        db: Session,
        invoice: InvoiceCreate,
        order_id: int | None = None,
        reference_type: str = "ORDER",
        reference_id: int | None = None,
    ):
        taxable_total = Decimal("0.00")
        tax_total = Decimal("0.00")

        for item in invoice.items:
            qty = to_decimal(item.quantity)
            rate = to_decimal(item.rate)
            gst_rate = to_decimal(item.gst_rate)

            taxable_value = to_decimal(qty * rate)
            gst_amount = to_decimal(taxable_value * gst_rate / Decimal("100"))

            taxable_total += taxable_value
            tax_total += gst_amount

        final_amount = to_decimal(taxable_total + tax_total)

        try:
            if order_id:
                existing = db.execute(
                    text("""
                        SELECT id, invoice_number
                        FROM invoice
                        WHERE order_id = :order_id
                        LIMIT 1
                    """),
                    {"order_id": order_id}
                ).mappings().fetchone()

                if existing:
                    return {
                        "invoice_id": existing["id"],
                        "invoice_number": existing["invoice_number"],
                        "message": "Invoice already exists",
                        "total_amount": float(taxable_total),
                        "tax_amount": float(tax_total),
                        "final_amount": float(final_amount),
                    }

            invoice_number = generate_invoice_number(db)

            buyer_address = {
                "name": invoice.buyer.name,
                "address": invoice.buyer.address,
                "gstin": invoice.buyer.gstin,
                "state": invoice.buyer.state,
                "state_code": invoice.buyer.state_code,
                "contact": invoice.buyer.contact,
            }

            invoice_row = db.execute(
                text("""
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
                        final_amount
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
                        :final_amount
                    )
                    RETURNING id
                """),
                {
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
                }
            ).mappings().fetchone()

            invoice_id = invoice_row["id"]

            for item in invoice.items:
                qty = to_decimal(item.quantity)
                rate = to_decimal(item.rate)
                gst_rate = to_decimal(item.gst_rate)

                taxable_value = to_decimal(qty * rate)
                gst_amount = to_decimal(taxable_value * gst_rate / Decimal("100"))
                total_price = to_decimal(taxable_value + gst_amount)

                db.execute(
                    text("""
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
                    """),
                    {
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
                    }
                )

            db.commit()

            return {
                "invoice_id": invoice_id,
                "invoice_number": invoice_number,
                "total_amount": float(taxable_total),
                "tax_amount": float(tax_total),
                "final_amount": float(final_amount),
            }

        except SQLAlchemyError as e:
            db.rollback()
            raise Exception(f"Invoice DB save error: {str(e.orig)}")

    @staticmethod
    def generate_invoice_pdf(invoice: InvoiceCreate) -> str:
        output_dir = Path("generated_invoices")
        output_dir.mkdir(parents=True, exist_ok=True)

        invoice_no = getattr(invoice, "invoice_no", None) or "invoice"
        safe_invoice_no = str(invoice_no).replace("/", "_")
        file_name = f"{safe_invoice_no}_{uuid4().hex[:8]}.pdf"
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

        normal = ParagraphStyle(
            "InvoiceNormal",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=8,
            leading=10,
            spaceAfter=0,
        )

        title_style = ParagraphStyle(
            "InvoiceTitle",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=16,
            leading=18,
            alignment=1,
            spaceAfter=8,
        )

        elements = []
        elements.append(Paragraph("Tax Invoice", title_style))

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

        header_table = Table(
            [[Paragraph(seller_text, normal), Paragraph(invoice_text, normal)]],
            colWidths=[315, 244],
        )

        header_table.setStyle(TableStyle([
            ("BOX", (0, 0), (-1, -1), 0.8, colors.black),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.black),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
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
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
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

        taxable_total = Decimal("0.00")
        total_qty = 0
        hsn_summary = {}

        for item in invoice.items:
            qty = to_decimal(item.quantity)
            rate = to_decimal(item.rate)
            amount = to_decimal(qty * rate)

            taxable_total += amount
            total_qty += int(qty)

            gst_rate = to_decimal(item.gst_rate)
            tax_amount = to_decimal(amount * gst_rate / Decimal("100"))
            hsn = str(item.hsn or "NA")

            if hsn not in hsn_summary:
                hsn_summary[hsn] = {
                    "taxable": Decimal("0.00"),
                    "gst_rate": gst_rate,
                    "tax": Decimal("0.00"),
                }

            hsn_summary[hsn]["taxable"] += amount
            hsn_summary[hsn]["tax"] += tax_amount

            item_rows.append([
                Paragraph(f"<b>{safe(item.name)}</b><br/>{safe(item.description)}", normal),
                safe(hsn),
                f"{int(qty)} Nos.",
                f"{rate:.2f}",
                "Nos.",
                f"{amount:.2f}",
            ])

        tax_total = to_decimal(sum(data["tax"] for data in hsn_summary.values()))
        before_round_total = to_decimal(taxable_total + tax_total)
        grand_total = before_round_total.quantize(Decimal("1"), rounding=ROUND_HALF_UP)
        round_off = to_decimal(grand_total - before_round_total)

        buyer_state = str(buyer.state or "").strip().lower()
        is_same_state = buyer_state == COMPANY["state"].lower()
        tax_label = "CGST + SGST" if is_same_state else "IGST"

        item_rows.extend([
            ["", "", "", "", "Taxable Total", f"{taxable_total:.2f}"],
            ["", "", "", "", tax_label, f"{tax_total:.2f}"],
            ["", "", "", "", "Round Off", f"{round_off:.2f}"],
            [Paragraph("<b>Total</b>", normal), "", f"{total_qty} Nos.", "", "", f"{grand_total:.2f}"],
        ])

        item_table = Table(
            item_rows,
            colWidths=[270, 55, 65, 55, 45, 69],
            repeatRows=1,
            splitByRow=1,
        )

        item_table.setStyle(TableStyle([
            ("BOX", (0, 0), (-1, -1), 0.8, colors.black),
            ("INNERGRID", (0, 0), (-1, -5), 0.45, colors.black),
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
            ("ALIGN", (4, 1), (4, -1), "RIGHT"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
            ("SPAN", (0, -4), (3, -4)),
            ("SPAN", (0, -3), (3, -3)),
            ("SPAN", (0, -2), (3, -2)),
            ("LINEABOVE", (0, -4), (-1, -4), 0.8, colors.black),
            ("LINEABOVE", (0, -1), (-1, -1), 1, colors.black),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ]))

        elements.append(item_table)
        elements.append(Spacer(1, 10))

        elements.append(Paragraph(
            f"<b>Amount Chargeable (in words)</b> : {amount_in_words(grand_total)}",
            normal,
        ))

        elements.append(Spacer(1, 8))

        footer_left = f"""
        <b>Declaration</b><br/>
        We declare that this invoice shows the actual price of the goods
        described and that all particulars are true and correct.<br/><br/>
        <b>Company's Bank Details</b><br/>
        Bank Name : {safe(COMPANY['bank_name'])}<br/>
        A/c No. : {safe(COMPANY['account_no'])}<br/>
        Branch &amp; IFS Code : {safe(COMPANY['branch_ifsc'])}
        """

        footer_right = f"""
        <b>for {safe(COMPANY['name'])}</b><br/><br/><br/><br/>
        Authorised Signatory
        """

        footer_table = Table(
            [[Paragraph(footer_left, normal), Paragraph(footer_right, normal)]],
            colWidths=[380, 179],
        )

        footer_table.setStyle(TableStyle([
            ("BOX", (0, 0), (-1, -1), 0.8, colors.black),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("ALIGN", (1, 0), (1, 0), "RIGHT"),
            ("TOPPADDING", (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
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

        pdf_path = InvoiceService.generate_invoice_pdf(invoice)

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