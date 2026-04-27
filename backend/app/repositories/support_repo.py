from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models.invoice import Invoice
from app.models.audit_log import AuditLog
from app.models.address import Address
from app.models.size_tax import TaxRate, SizeMaster
from typing import Optional, List


class SupportRepository:

    # ════════════════════════════════════════════════════════════
    # INVOICE
    # ════════════════════════════════════════════════════════════

    @staticmethod
    def get_all_invoices(db: Session, limit: int = 100) -> List[Invoice]:
        return (
            db.query(Invoice)
            .order_by(Invoice.created_at.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_invoice_by_order(db: Session, order_id: int) -> Optional[Invoice]:
        return db.query(Invoice).filter(Invoice.order_id == order_id).first()

    @staticmethod
    def get_invoice_by_number(db: Session, invoice_number: str) -> Optional[Invoice]:
        return db.query(Invoice).filter(Invoice.invoice_number == invoice_number).first()

    @staticmethod
    def create_invoice(db: Session, order_id: int, invoice_number: str, gst_number: Optional[str], total_tax: Optional[float], billing_address: Optional[dict]) -> Invoice:
        invoice = Invoice(
            order_id=order_id,
            invoice_number=invoice_number,
            gst_number=gst_number,
            total_tax=total_tax,
            billing_address=billing_address,
        )
        db.add(invoice)
        db.commit()
        db.refresh(invoice)
        return invoice

    # ════════════════════════════════════════════════════════════
    # AUDIT LOG
    # ════════════════════════════════════════════════════════════

    @staticmethod
    def get_audit_logs(
        db: Session,
        entity_type: Optional[str] = None,
        action: Optional[str] = None,
        user_id: Optional[int] = None,
        limit: int = 100,
    ) -> List[AuditLog]:
        query = db.query(AuditLog)
        if entity_type:
            query = query.filter(AuditLog.entity_type == entity_type)
        if action:
            query = query.filter(AuditLog.action == action)
        if user_id:
            query = query.filter(AuditLog.user_id == user_id)
        return query.order_by(AuditLog.created_at.desc()).limit(limit).all()

    # ════════════════════════════════════════════════════════════
    # ADDRESS (admin view)
    # ════════════════════════════════════════════════════════════

    @staticmethod
    def get_address_view(db: Session, user_id: Optional[int] = None):
        """Uses address_view DB view — joins user name + email."""
        if user_id:
            result = db.execute(
                text("SELECT * FROM address_view WHERE user_id = :uid"),
                {"uid": user_id},
            )
        else:
            result = db.execute(text("SELECT * FROM address_view ORDER BY user_id"))
        return [dict(row) for row in result.mappings()]

    @staticmethod
    def get_user_addresses(db: Session, user_id: int):
        """Uses fn_get_addresses(uid) DB function."""
        result = db.execute(
            text("SELECT * FROM fn_get_addresses(:uid)"),
            {"uid": user_id},
        )
        return [dict(row) for row in result.mappings()]

    # ════════════════════════════════════════════════════════════
    # TAX RATES
    # ════════════════════════════════════════════════════════════

    @staticmethod
    def get_all_tax_rates(db: Session) -> List[TaxRate]:
        return db.query(TaxRate).filter(TaxRate.is_active == True).all()

    @staticmethod
    def create_tax_rate(db: Session, name: str, rate: float) -> TaxRate:
        tr = TaxRate(name=name, rate=rate)
        db.add(tr)
        db.commit()
        db.refresh(tr)
        return tr

    @staticmethod
    def update_tax_rate(db: Session, tax_id: int, name: Optional[str], rate: Optional[float], is_active: Optional[bool]) -> Optional[TaxRate]:
        tr = db.query(TaxRate).filter(TaxRate.id == tax_id).first()
        if not tr:
            return None
        if name is not None:
            tr.name = name
        if rate is not None:
            tr.rate = rate
        if is_active is not None:
            tr.is_active = is_active
        db.commit()
        db.refresh(tr)
        return tr

    # ════════════════════════════════════════════════════════════
    # SIZE MASTER
    # ════════════════════════════════════════════════════════════

    @staticmethod
    def get_all_sizes(db: Session) -> List[SizeMaster]:
        return db.query(SizeMaster).order_by(SizeMaster.sort_order).all()

    @staticmethod
    def create_size(db: Session, size_code: str, sort_order: Optional[int]) -> SizeMaster:
        s = SizeMaster(size_code=size_code.upper(), sort_order=sort_order)
        db.add(s)
        db.commit()
        db.refresh(s)
        return s

    @staticmethod
    def delete_size(db: Session, size_id: int) -> Optional[SizeMaster]:
        s = db.query(SizeMaster).filter(SizeMaster.id == size_id).first()
        if not s:
            return None
        db.delete(s)
        db.commit()
        return s

    # ════════════════════════════════════════════════════════════
    # SHIPMENT TRACKING VIEW
    # ════════════════════════════════════════════════════════════

    @staticmethod
    def get_shipment_tracking_view(db: Session, order_id: Optional[int] = None):
        """Uses shipment_tracking_view DB view."""
        if order_id:
            result = db.execute(
                text("SELECT * FROM shipment_tracking_view WHERE order_id = :oid"),
                {"oid": order_id},
            )
        else:
            result = db.execute(text("SELECT * FROM shipment_tracking_view ORDER BY created_at DESC"))
        return [dict(row) for row in result.mappings()]

    # ════════════════════════════════════════════════════════════
    # WISHLIST / CART (admin view only)
    # ════════════════════════════════════════════════════════════

    @staticmethod
    def get_cart_view(db: Session, user_id: Optional[int] = None):
        """Uses cart_view DB view."""
        if user_id:
            result = db.execute(
                text("SELECT * FROM cart_view WHERE user_id = :uid"),
                {"uid": user_id},
            )
        else:
            result = db.execute(text("SELECT * FROM cart_view"))
        return [dict(row) for row in result.mappings()]

    @staticmethod
    def get_wishlist_view(db: Session, user_id: Optional[int] = None):
        """Uses wishlist_view DB view."""
        if user_id:
            result = db.execute(
                text("SELECT * FROM wishlist_view WHERE user_id = :uid"),
                {"uid": user_id},
            )
        else:
            result = db.execute(text("SELECT * FROM wishlist_view"))
        return [dict(row) for row in result.mappings()]