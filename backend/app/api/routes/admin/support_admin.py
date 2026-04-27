from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.db.session import get_db
from app.core.dependencies import require_admin
from app.repositories.support_repo import SupportRepository
from app.schemas.admin import (
    InvoiceCreate, InvoiceOut,
    TaxRateCreate, TaxRateUpdate, TaxRateOut,
    SizeCreate, SizeOut,
    AuditLogOut,
)

router = APIRouter(prefix="/admin/support", tags=["Admin - Support"])


# ════════════════════════════════════════════════════════════
# INVOICES
# ════════════════════════════════════════════════════════════

@router.get("/invoices", summary="List all invoices")
def get_all_invoices(
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    invoices = SupportRepository.get_all_invoices(db, limit)
    return [
        {
            "id": inv.id,
            "order_id": inv.order_id,
            "invoice_number": inv.invoice_number,
            "invoice_date": inv.invoice_date,
            "gst_number": inv.gst_number,
            "total_tax": float(inv.total_tax) if inv.total_tax else None,
            "created_at": inv.created_at,
        }
        for inv in invoices
    ]


@router.get("/invoices/{order_id}", summary="Get invoice for a specific order")
def get_invoice_by_order(
    order_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    invoice = SupportRepository.get_invoice_by_order(db, order_id)
    if not invoice:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Invoice not found for this order")
    return {
        "id": invoice.id,
        "order_id": invoice.order_id,
        "invoice_number": invoice.invoice_number,
        "invoice_date": invoice.invoice_date,
        "billing_address": invoice.billing_address,
        "gst_number": invoice.gst_number,
        "total_tax": float(invoice.total_tax) if invoice.total_tax else None,
        "created_at": invoice.created_at,
    }


@router.post("/invoices", summary="Create invoice for an order")
def create_invoice(
    data: InvoiceCreate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    existing = SupportRepository.get_invoice_by_order(db, data.order_id)
    if existing:
        from fastapi import HTTPException
        raise HTTPException(status_code=409, detail="Invoice already exists for this order")
    inv = SupportRepository.create_invoice(
        db,
        data.order_id,
        data.invoice_number,
        data.gst_number,
        data.total_tax,
        data.billing_address,
    )
    return {
        "message": "Invoice created",
        "invoice_id": inv.id,
        "invoice_number": inv.invoice_number,
        "order_id": inv.order_id,
    }


# ════════════════════════════════════════════════════════════
# AUDIT LOGS
# ════════════════════════════════════════════════════════════

@router.get("/audit-logs", summary="View audit logs (all admin actions)")
def get_audit_logs(
    entity_type: Optional[str] = Query(
        None, description="Filter: product | order | user | coupon etc."
    ),
    action: Optional[str] = Query(None, description="Filter by action"),
    user_id: Optional[int] = Query(None, description="Filter by user who performed action"),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    """
    audit_log table tracks: action, entity_type, entity_id, old_data, new_data.
    Used for compliance and debugging.
    """
    logs = SupportRepository.get_audit_logs(db, entity_type, action, user_id, limit)
    return [
        {
            "id": l.id,
            "user_id": l.user_id,
            "action": l.action,
            "entity_type": l.entity_type,
            "entity_id": l.entity_id,
            "old_data": l.old_data,
            "new_data": l.new_data,
            "created_at": l.created_at,
        }
        for l in logs
    ]


# ════════════════════════════════════════════════════════════
# ADDRESS VIEW
# ════════════════════════════════════════════════════════════

@router.get("/addresses", summary="Address view — all user addresses with user info")
def get_address_view(
    user_id: Optional[int] = Query(None, description="Filter by user"),
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    """Uses address_view DB view — joins address + user name/email."""
    return SupportRepository.get_address_view(db, user_id)


@router.get(
    "/addresses/user/{user_id}",
    summary="Get addresses for a specific user using fn_get_addresses()",
)
def get_user_addresses(
    user_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    """Uses fn_get_addresses(uid) DB function."""
    return SupportRepository.get_user_addresses(db, user_id)


# ════════════════════════════════════════════════════════════
# SHIPMENT TRACKING VIEW
# ════════════════════════════════════════════════════════════

@router.get(
    "/shipment-tracking",
    summary="Shipment tracking view — uses shipment_tracking_view",
)
def get_shipment_tracking(
    order_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    """Uses shipment_tracking_view DB view — joins shipment + order user_id."""
    return SupportRepository.get_shipment_tracking_view(db, order_id)


# ════════════════════════════════════════════════════════════
# TAX RATES
# ════════════════════════════════════════════════════════════

@router.get("/tax-rates", summary="List all active tax rates")
def get_tax_rates(
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    rates = SupportRepository.get_all_tax_rates(db)
    return [
        {"id": t.id, "name": t.name, "rate": float(t.rate) if t.rate else None, "is_active": t.is_active}
        for t in rates
    ]


@router.post("/tax-rates", summary="Create a new tax rate")
def create_tax_rate(
    data: TaxRateCreate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    tr = SupportRepository.create_tax_rate(db, data.name, data.rate)
    return {"message": "Tax rate created", "id": tr.id, "name": tr.name, "rate": float(tr.rate)}


@router.put("/tax-rates/{tax_id}", summary="Update a tax rate")
def update_tax_rate(
    tax_id: int,
    data: TaxRateUpdate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    tr = SupportRepository.update_tax_rate(db, tax_id, data.name, data.rate, data.is_active)
    if not tr:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Tax rate not found")
    return {"message": "Tax rate updated", "id": tr.id, "name": tr.name, "rate": float(tr.rate)}


# ════════════════════════════════════════════════════════════
# SIZE MASTER
# ════════════════════════════════════════════════════════════

@router.get("/sizes", summary="List all sizes from size_master table")
def get_all_sizes(
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    sizes = SupportRepository.get_all_sizes(db)
    return [{"id": s.id, "size_code": s.size_code, "sort_order": s.sort_order} for s in sizes]


@router.post("/sizes", summary="Add a new size to size_master")
def create_size(
    data: SizeCreate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    s = SupportRepository.create_size(db, data.size_code, data.sort_order)
    return {"message": "Size created", "id": s.id, "size_code": s.size_code}


@router.delete("/sizes/{size_id}", summary="Delete a size from size_master")
def delete_size(
    size_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    s = SupportRepository.delete_size(db, size_id)
    if not s:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Size not found")
    return {"message": f"Size {size_id} deleted"}


# ════════════════════════════════════════════════════════════
# CART / WISHLIST VIEW (read-only admin)
# ════════════════════════════════════════════════════════════

@router.get("/carts", summary="Cart view — uses cart_view DB view")
def get_cart_view(
    user_id: Optional[int] = Query(None, description="Filter by user"),
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    """Uses cart_view — shows cart_id, user_id, variant_id, qty, price, product_name."""
    return SupportRepository.get_cart_view(db, user_id)


@router.get("/wishlists", summary="Wishlist view — uses wishlist_view DB view")
def get_wishlist_view(
    user_id: Optional[int] = Query(None, description="Filter by user"),
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    """Uses wishlist_view — shows wishlist items with product name and image."""
    return SupportRepository.get_wishlist_view(db, user_id)