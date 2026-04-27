from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.schemas.coupon import (
    CouponCreate,
    CouponUpdate,
    ApplyCouponRequest,
)
from app.services.coupon_service import CouponService

router = APIRouter(
    prefix="/admin/coupons",
    tags=["Admin - Coupons"]
)

# ════════════════════════════════════════════════════════
# LIST ALL COUPONS
# GET /admin/coupons/
# ════════════════════════════════════════════════════════
@router.get("/", summary="List all coupons")
def get_all_coupons(
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    coupons = CouponService.get_all_coupons(db, is_active)

    return [
        {
            "id": c.id,
            "code": c.code,
            "description": c.description,
            "discount_type": c.discount_type,
            "discount_value": float(c.discount_value),
            "min_order_amount": float(c.min_order_amount or 0),
            "max_discount_amount": float(c.max_discount_amount)
            if c.max_discount_amount is not None else None,
            "usage_limit": c.usage_limit,
            "used_count": c.used_count,
            "remaining_usage": (
                c.usage_limit - c.used_count
                if c.usage_limit is not None else None
            ),
            "valid_from": c.valid_from,
            "valid_to": c.valid_to,
            "is_active": c.is_active,
            "created_by": c.created_by,
            "updated_by": c.updated_by,
            "created_at": c.created_at,
            "updated_at": c.updated_at,
        }
        for c in coupons
    ]


# ════════════════════════════════════════════════════════
# STATS
# GET /admin/coupons/stats
# ════════════════════════════════════════════════════════
@router.get("/stats", summary="Coupon stats")
def coupon_stats(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    coupons = CouponService.get_all_coupons(db)

    return {
        "total_coupons": len(coupons),
        "active_coupons": len([c for c in coupons if c.is_active]),
        "inactive_coupons": len([c for c in coupons if not c.is_active]),
    }


# ════════════════════════════════════════════════════════
# PERFORMANCE
# GET /admin/coupons/performance
# ════════════════════════════════════════════════════════
@router.get("/performance", summary="Coupon performance")
def get_coupon_performance(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    return CouponService.get_performance(db)


# ════════════════════════════════════════════════════════
# USAGE HISTORY
# GET /admin/coupons/usage
# ════════════════════════════════════════════════════════
@router.get("/usage", summary="Coupon usage history")
def get_coupon_usage(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    return CouponService.get_usage(db)


# ════════════════════════════════════════════════════════
# APPLY COUPON
# POST /admin/coupons/apply
# ════════════════════════════════════════════════════════
@router.post("/apply", summary="Apply coupon")
def apply_coupon(
    data: ApplyCouponRequest,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    return CouponService.apply_coupon(
        db,
        data.coupon_code,
        user.id,
        data.order_id,
        data.order_amount,
        data.additional_discount,
    )


# ════════════════════════════════════════════════════════
# CREATE COUPON
# POST /admin/coupons/
# ════════════════════════════════════════════════════════
@router.post("/", summary="Create coupon")
def create_coupon(
    data: CouponCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    c = CouponService.create_coupon(db, data, user.id)

    return {
        "message": f"Coupon '{c.code}' created successfully",
        "id": c.id,
        "code": c.code,
    }


# ════════════════════════════════════════════════════════
# GET SINGLE COUPON
# GET /admin/coupons/{coupon_id}
# ════════════════════════════════════════════════════════
@router.get("/{coupon_id}", summary="Get coupon")
def get_coupon(
    coupon_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    c = CouponService.get_coupon(db, coupon_id)

    return {
        "id": c.id,
        "code": c.code,
        "description": c.description,
        "discount_type": c.discount_type,
        "discount_value": float(c.discount_value),
        "min_order_amount": float(c.min_order_amount or 0),
        "max_discount_amount": float(c.max_discount_amount)
        if c.max_discount_amount is not None else None,
        "usage_limit": c.usage_limit,
        "used_count": c.used_count,
        "valid_from": c.valid_from,
        "valid_to": c.valid_to,
        "is_active": c.is_active,
        "created_by": c.created_by,
        "updated_by": c.updated_by,
        "created_at": c.created_at,
        "updated_at": c.updated_at,
    }


# ════════════════════════════════════════════════════════
# UPDATE COUPON
# PUT /admin/coupons/{coupon_id}
# ════════════════════════════════════════════════════════
@router.put("/{coupon_id}", summary="Update coupon")
def update_coupon(
    coupon_id: int,
    data: CouponUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    c = CouponService.update_coupon(
        db,
        coupon_id,
        data,
        user.id
    )

    return {
        "message": "Coupon updated successfully",
        "id": c.id,
        "code": c.code,
    }


# ════════════════════════════════════════════════════════
# DELETE / DEACTIVATE COUPON
# DELETE /admin/coupons/{coupon_id}
# ════════════════════════════════════════════════════════
@router.delete("/{coupon_id}", summary="Deactivate coupon")
def delete_coupon(
    coupon_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    return CouponService.delete_coupon(db, coupon_id)