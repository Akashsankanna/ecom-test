from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.db.session import get_db
from app.core.dependencies import require_admin
from app.schemas.order import (
    OrderStatusUpdate,
    ShipmentCreate,
)
from app.schemas.coupon import ApplyCouponRequest, ApplyAdditionalDiscount
from app.services.order_service import OrderService

router = APIRouter(
    prefix="/admin/orders",
    tags=["Admin - Orders"]
)

# ════════════════════════════════════════════════════════════
# ORDERS
# ════════════════════════════════════════════════════════════

@router.get("/", summary="List all orders with optional filters")
def get_all_orders(
    status: Optional[str] = Query(
        None,
        description="PENDING | PAID | PROCESSING | SHIPPED | DELIVERED | CANCELLED",
    ),
    payment_status: Optional[str] = Query(
        None,
        description="PENDING | SUCCESS | FAILED",
    ),
    user_id: Optional[int] = Query(
        None,
        description="Filter by user id",
    ),
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    orders = OrderService.get_all_orders(
        db,
        status,
        payment_status,
        user_id
    )

    return [
        {
            "id": o.id,
            "user_id": o.user_id,
            "total_amount": float(o.total_amount),
            "status": o.status,
            "payment_status": o.payment_status,
            "address_id": o.address_id,
            "created_at": o.created_at,
            "updated_at": o.updated_at,
        }
        for o in orders
    ]


# ════════════════════════════════════════════════════════════
# ANALYTICS
# IMPORTANT:
# Must be ABOVE /{order_id} route
# ════════════════════════════════════════════════════════════

@router.get(
    "/analytics/top-selling",
    summary="Top selling products from DB view"
)
def top_selling(
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    return OrderService.get_top_selling(db)


# ════════════════════════════════════════════════════════════
# COUPON / GLOBAL ORDER ACTIONS
# IMPORTANT:
# Static route before /{order_id}
# ════════════════════════════════════════════════════════════

@router.post(
    "/apply-coupon",
    summary="Apply coupon to order → uses sp_apply_coupon (5-param)"
)
def apply_coupon_to_order(
    data: ApplyCouponRequest,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    order = OrderService.apply_coupon(db, data)

    return {
        "message": f"Coupon '{data.coupon_code}' applied successfully",
        "order_id": order.id,
        "coupon_id": order.coupon_id,
        "coupon_discount_amount": float(order.coupon_discount_amount)
        if order.coupon_discount_amount else 0,
        "final_amount": float(order.final_amount)
        if order.final_amount else None,
    }


# ════════════════════════════════════════════════════════════
# SINGLE ORDER ROUTES
# ════════════════════════════════════════════════════════════

@router.get(
    "/{order_id}",
    summary="Get order detail with items"
)
def get_order_detail(
    order_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    order, items = OrderService.get_order_detail(
        db,
        order_id
    )

    return {
        "id": order.id,
        "user_id": order.user_id,
        "total_amount": float(order.total_amount),
        "status": order.status,
        "payment_status": order.payment_status,
        "address_id": order.address_id,
        "created_at": order.created_at,
        "updated_at": order.updated_at,
        "items": [
            {
                "id": i.id,
                "variant_id": i.variant_id,
                "quantity": i.quantity,
                "price": float(i.price),
            }
            for i in items
        ],
    }


@router.put(
    "/{order_id}/status",
    summary="Update order status"
)
def update_order_status(
    order_id: int,
    data: OrderStatusUpdate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    order = OrderService.update_order_status(
        db,
        order_id,
        data
    )

    return {
        "message": f"Order {order_id} updated to {order.status}",
        "order_id": order.id,
        "status": order.status,
        "updated_at": order.updated_at,
    }


@router.post(
    "/{order_id}/cancel",
    summary="Cancel order"
)
def cancel_order(
    order_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    order = OrderService.cancel_order(
        db,
        order_id
    )

    return {
        "message": f"Order {order_id} cancelled",
        "order_id": order.id,
        "status": order.status,
    }


@router.get(
    "/{order_id}/history",
    summary="Get order status history"
)
def get_order_history(
    order_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    history = OrderService.get_status_history(
        db,
        order_id
    )

    return [
        {
            "id": h.id,
            "order_id": h.order_id,
            "status": h.status,
            "changed_by": h.changed_by,
            "remarks": h.remarks,
            "changed_at": h.changed_at,
        }
        for h in history
    ]


# ════════════════════════════════════════════════════════════
# SHIPMENT
# ════════════════════════════════════════════════════════════

@router.post(
    "/{order_id}/shipment",
    summary="Create shipment"
)
def create_shipment(
    order_id: int,
    data: ShipmentCreate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    shipment = OrderService.create_shipment(
        db,
        order_id,
        data
    )

    return {
        "message": "Shipment created successfully",
        "shipment_id": shipment.id,
        "order_id": shipment.order_id,
        "courier_name": shipment.courier_name,
        "tracking_number": shipment.tracking_number,
        "shipment_status": shipment.shipment_status,
        "estimated_delivery": shipment.estimated_delivery,
    }


@router.get(
    "/{order_id}/shipment",
    summary="Get shipment details"
)
def get_shipment(
    order_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    shipment = OrderService.get_shipment(
        db,
        order_id
    )

    return {
        "id": shipment.id,
        "order_id": shipment.order_id,
        "courier_name": shipment.courier_name,
        "tracking_number": shipment.tracking_number,
        "shipment_status": shipment.shipment_status,
        "tracking_url": shipment.tracking_url,
        "shipped_at": shipment.shipped_at,
        "estimated_delivery": shipment.estimated_delivery,
        "delivered_at": shipment.delivered_at,
    }


# ════════════════════════════════════════════════════════════
# DISCOUNTS
# ════════════════════════════════════════════════════════════

@router.post(
    "/{order_id}/apply-discount",
    summary="Apply additional discount"
)
def apply_additional_discount(
    order_id: int,
    data: ApplyAdditionalDiscount,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    data.order_id = order_id

    order = OrderService.apply_additional_discount(
        db,
        data
    )

    return {
        "message": f"Discount applied to order {order_id}",
        "order_id": order.id,
        "total_amount": float(order.total_amount),
        "additional_discount_amount": float(order.additional_discount_amount)
        if order.additional_discount_amount else 0,
        "final_amount": float(order.final_amount)
        if order.final_amount else None,
        "discount_reason": order.discount_reason,
    }