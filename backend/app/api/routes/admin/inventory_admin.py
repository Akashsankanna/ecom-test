# app/api/routes/admin/inventory_admin.py
# FULLY FIXED - LOW STOCK UPDATE + UI CONNECT + DB CONNECTED

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from app.db.session import get_db
from app.core.dependencies import require_admin

from app.services.inventory_service import InventoryService
from app.schemas.order import StockAdjust, VariantStockUpdate
from app.schemas.inventory import StockAdjust, VariantStockUpdate

router = APIRouter(
    prefix="/admin/inventory",
    tags=["Admin Inventory"]
)

# =====================================================
# SERIALIZERS
# =====================================================

def variant_payload(v):
    return {
        "id": v.id,
        "product_id": v.product_id,
        "variant_name": v.variant_name,
        "sku": v.sku,
        "price": float(v.price or 0),

        "stock": int(v.stock or 0),
        "reserved_stock": int(v.reserved_stock or 0),
        "available_stock": int(v.stock or 0) - int(v.reserved_stock or 0),

        "low_stock_threshold": int(v.low_stock_threshold or 5),

        "color_id": v.color_id,
        "size": v.size,

        "is_deleted": v.is_deleted
    }


def log_payload(log):
    return {
        "id": log.id,
        "variant_id": log.variant_id,
        "change_type": log.change_type,
        "quantity": log.quantity,

        "reference_id": log.reference_id,
        "reference_type": getattr(log, "reference_type", None),

        "notes": log.notes,

        "created_by": log.created_by,
        "updated_by": log.updated_by,
        "created_at": log.created_at
    }


# =====================================================
# GET ALL INVENTORY
# =====================================================

@router.get("/")
def get_inventory(
    search: Optional[str] = Query(None),
    low_stock_only: bool = Query(False),
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    rows = InventoryService.get_all_variants(db)
    data = [variant_payload(x) for x in rows]

    if search:
        q = search.lower().strip()

        data = [
            x for x in data
            if q in (x["variant_name"] or "").lower()
            or q in (x["sku"] or "").lower()
        ]

    if low_stock_only:
        data = [
            x for x in data
            if x["stock"] <= x["low_stock_threshold"]
        ]

    return {
        "count": len(data),
        "items": data
    }


# =====================================================
# LOW STOCK
# =====================================================

@router.get("/low-stock")
def get_low_stock(
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    rows = InventoryService.get_low_stock_variants(db)

    data = [variant_payload(x) for x in rows]

    return {
        "count": len(data),
        "items": data
    }


# =====================================================
# SINGLE VARIANT
# =====================================================

@router.get("/{variant_id}")
def get_variant(
    variant_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    row = InventoryService.get_variant_by_id(db, variant_id)

    if not row:
        raise HTTPException(status_code=404, detail="Variant not found")

    return variant_payload(row)


# =====================================================
# UPDATE VARIANT
# THIS FIXES LOW STOCK THRESHOLD UPDATE
# =====================================================

@router.put("/{variant_id}")
def update_variant(
    variant_id: int,
    payload: VariantStockUpdate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    row = InventoryService.update_variant_stock(
        db=db,
        variant_id=variant_id,
        payload=payload,
        user_id=admin.id
    )

    if not row:
        raise HTTPException(status_code=404, detail="Variant not found")

    return {
        "message": "Variant updated successfully",
        "item": variant_payload(row)
    }


# =====================================================
# UPDATE ONLY LOW STOCK THRESHOLD
# NEW ENDPOINT FOR UI BUTTON
# =====================================================

@router.put("/{variant_id}/threshold")
def update_threshold(
    variant_id: int,
    payload: VariantStockUpdate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    row = InventoryService.update_variant_stock(
        db=db,
        variant_id=variant_id,
        payload=VariantStockUpdate(
            stock=None,
            reserved_stock=None,
            low_stock_threshold=payload.low_stock_threshold
        ),
        user_id=admin.id
    )

    if not row:
        raise HTTPException(status_code=404, detail="Variant not found")

    return {
        "message": "Low stock threshold updated",
        "item": variant_payload(row)
    }


# =====================================================
# LOGS
# =====================================================

@router.get("/logs/all")
def get_logs(
    variant_id: Optional[int] = Query(None),
    change_type: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    rows = InventoryService.get_all_logs(
        db=db,
        variant_id=variant_id,
        change_type=change_type,
        limit=limit
    )

    return {
        "count": len(rows),
        "items": [log_payload(x) for x in rows]
    }


@router.get("/logs/{variant_id}")
def get_logs_by_variant(
    variant_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    rows = InventoryService.get_logs_by_variant(db, variant_id)

    return {
        "count": len(rows),
        "items": [log_payload(x) for x in rows]
    }


# =====================================================
# STOCK ACTIONS
# =====================================================

@router.post("/add-stock")
def add_stock(
    payload: StockAdjust,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    log = InventoryService.add_stock(
        db=db,
        payload=payload,
        user_id=admin.id
    )

    return {
        "message": "Stock added successfully",
        "log": log_payload(log)
    }


@router.post("/remove-stock")
def remove_stock(
    payload: StockAdjust,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    log = InventoryService.remove_stock(
        db=db,
        payload=payload,
        user_id=admin.id
    )

    return {
        "message": "Stock removed successfully",
        "log": log_payload(log)
    }


@router.post("/reserve-stock")
def reserve_stock(
    payload: StockAdjust,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    payload.change_type = "ORDER"

    log = InventoryService.reserve_stock(
        db=db,
        payload=payload,
        user_id=admin.id
    )

    return {
        "message": "Stock reserved successfully",
        "log": log_payload(log)
    }


@router.post("/release-stock")
def release_stock(
    payload: StockAdjust,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    payload.change_type = "ORDER_CANCELLED"

    log = InventoryService.release_stock(
        db=db,
        payload=payload,
        user_id=admin.id
    )

    return {
        "message": "Reserved stock released successfully",
        "log": log_payload(log)
    }