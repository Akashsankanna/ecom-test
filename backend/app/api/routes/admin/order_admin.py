from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.db.session import get_db
from app.core.dependencies import require_admin
from app.schemas.order import (
    OrderStatusUpdate,
    ShipmentCreate,
    ShipmentStatusUpdate,
    ReturnApprove,
    ExchangeCreate,
    ExchangeStatusUpdate,
    ExchangeCompleteData,
    ApplyCouponRequest,
    ApplyAdditionalDiscount,
)
from app.services.order_service import OrderService

router = APIRouter(
    prefix="/admin/orders",
    tags=["Admin - Orders"],
)


# ════════════════════════════════════════════════════════════
# LIST ALL ORDERS
# ════════════════════════════════════════════════════════════

@router.get("/", summary="List all orders with optional filters")
def get_all_orders(
    status: Optional[str] = Query(
        None,
        description=(
            "PENDING | PAID | CONFIRMED | PROCESSING | "
            "SHIPPED | DELIVERED | CANCELLED | PAYMENT_FAILED"
        ),
    ),
    payment_status: Optional[str] = Query(
        None,
        description="PENDING | SUCCESS | FAILED | REFUNDED",
    ),
    user_id: Optional[int] = Query(None, description="Filter by user id"),
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    orders = OrderService.get_all_orders(db, status, payment_status, user_id)
    return [
        {
            "id":                         o.id,
            "user_id":                    o.user_id,
            "total_amount":               float(o.total_amount),
            "gross_amount":               float(o.gross_amount) if o.gross_amount else None,
            "final_amount":               float(o.final_amount) if o.final_amount else None,
            "coupon_discount_amount":     float(o.coupon_discount_amount) if o.coupon_discount_amount else 0,
            "additional_discount_amount": float(o.additional_discount_amount) if o.additional_discount_amount else 0,
            "status":                     o.status,
            "payment_status":             o.payment_status,
            "address_id":                 o.address_id,
            "coupon_id":                  o.coupon_id,
            "transaction_id":             o.transaction_id,
            "created_at":                 o.created_at,
            "updated_at":                 o.updated_at,
        }
        for o in orders
    ]


# ════════════════════════════════════════════════════════════
# ANALYTICS — must be ABOVE /{order_id}
# ════════════════════════════════════════════════════════════

@router.get(
    "/analytics/top-selling",
    summary="Top selling products",
)
def top_selling(
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    return OrderService.get_top_selling(db)


@router.get(
    "/analytics/returns",
    summary="Return requests view",
)
def returns_view(
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    return OrderService.get_return_requests_view(db)


@router.get(
    "/analytics/exchanges",
    summary="Exchange requests view",
)
def exchanges_view(
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    return OrderService.get_exchange_view(db)


# ════════════════════════════════════════════════════════════
# COUPON / DISCOUNT — static routes before /{order_id}
# ════════════════════════════════════════════════════════════

@router.post(
    "/apply-coupon",
    summary="Apply coupon to an order",
)
def apply_coupon_to_order(
    data: ApplyCouponRequest,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    order = OrderService.apply_coupon(db, data)
    return {
        "message":                f"Coupon '{data.coupon_code}' applied successfully",
        "order_id":               order.id,
        "coupon_id":              order.coupon_id,
        "coupon_discount_amount": float(order.coupon_discount_amount) if order.coupon_discount_amount else 0,
        "final_amount":           float(order.final_amount) if order.final_amount else None,
    }


# ════════════════════════════════════════════════════════════
# RETURN REQUESTS
# ════════════════════════════════════════════════════════════

@router.get(
    "/returns",
    summary="List all return requests",
)
def list_return_requests(
    status: Optional[str] = Query(
        None,
        description="REQUESTED | APPROVED | REJECTED | REFUNDED | COMPLETED",
    ),
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    returns = OrderService.get_all_return_requests(db, status)
    return [
        {
            "id":            r.id,
            "order_id":      r.order_id,
            "order_item_id": r.order_item_id,
            "user_id":       r.user_id,
            "quantity":      r.quantity,
            "reason":        r.reason,
            "status":        r.status,
            "refund_amount": float(r.refund_amount) if r.refund_amount else None,
            "refund_method": r.refund_method,
            "requested_at":  r.requested_at,
            "approved_at":   r.approved_at,
            "completed_at":  r.completed_at,
        }
        for r in returns
    ]


@router.get(
    "/returns/{return_id}",
    summary="Get a single return request",
)
def get_return(
    return_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    r = OrderService.get_return_request(db, return_id)
    return {
        "id":            r.id,
        "order_id":      r.order_id,
        "order_item_id": r.order_item_id,
        "user_id":       r.user_id,
        "quantity":      r.quantity,
        "reason":        r.reason,
        "status":        r.status,
        "refund_amount": float(r.refund_amount) if r.refund_amount else None,
        "refund_method": r.refund_method,
        "requested_at":  r.requested_at,
        "approved_at":   r.approved_at,
        "completed_at":  r.completed_at,
    }


@router.post(
    "/returns/{return_id}/approve",
    summary="Approve a return request",
)
def approve_return(
    return_id: int,
    data: ReturnApprove,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    r = OrderService.approve_return(db, return_id, data)
    return {
        "message": f"Return request {return_id} approved",
        "status":  r.status,
        "refund_method": r.refund_method,
    }


@router.post(
    "/returns/{return_id}/reject",
    summary="Reject a return request",
)
def reject_return(
    return_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    r = OrderService.reject_return(db, return_id)
    return {
        "message": f"Return request {return_id} rejected",
        "status":  r.status,
    }


@router.post(
    "/returns/{return_id}/complete-refund",
    summary="Mark refund as completed",
)
def complete_refund(
    return_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    r = OrderService.complete_refund(db, return_id)
    return {
        "message": f"Refund for return {return_id} completed",
        "status":  r.status,
    }


# ════════════════════════════════════════════════════════════
# EXCHANGE REQUESTS
# ════════════════════════════════════════════════════════════

@router.get(
    "/exchanges",
    summary="List all exchange requests",
)
def list_exchanges(
    status: Optional[str] = Query(
        None,
        description="REQUESTED | APPROVED | REJECTED | COMPLETED",
    ),
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    exchanges = OrderService.get_all_exchanges(db, status)
    return [
        {
            "id":            e.id,
            "order_id":      e.order_id,
            "order_item_id": e.order_item_id,
            "reason":        e.reason,
            "status":        e.status,
            "created_at":    e.created_at,
            "updated_at":    e.updated_at,
        }
        for e in exchanges
    ]


@router.post(
    "/exchanges",
    summary="Create an exchange request",
)
def create_exchange(
    data: ExchangeCreate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    ex = OrderService.create_exchange(db, data)
    return {
        "message":    "Exchange request created",
        "exchange_id": ex.id,
        "status":     ex.status,
    }


@router.get(
    "/exchanges/{exchange_id}",
    summary="Get a single exchange request",
)
def get_exchange(
    exchange_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    ex = OrderService.get_exchange(db, exchange_id)
    return {
        "id":            ex.id,
        "order_id":      ex.order_id,
        "order_item_id": ex.order_item_id,
        "reason":        ex.reason,
        "status":        ex.status,
        "created_at":    ex.created_at,
        "updated_at":    ex.updated_at,
    }


@router.put(
    "/exchanges/{exchange_id}/status",
    summary="Update exchange request status",
)
def update_exchange_status(
    exchange_id: int,
    data: ExchangeStatusUpdate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    ex = OrderService.update_exchange_status(db, exchange_id, data)
    return {
        "message": f"Exchange {exchange_id} status updated to {ex.status}",
        "status":  ex.status,
    }


@router.post(
    "/exchanges/{exchange_id}/complete",
    summary="Complete an exchange",
)
def complete_exchange(
    exchange_id: int,
    data: ExchangeCompleteData,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    ex = OrderService.complete_exchange(db, exchange_id, data)
    return {
        "message": f"Exchange {exchange_id} completed",
        "status":  ex.status,
    }


# ════════════════════════════════════════════════════════════
# SHIPMENT — global (update by tracking number)
# ════════════════════════════════════════════════════════════

@router.put(
    "/shipments/{tracking_number}/status",
    summary="Update shipment status by tracking number",
)
def update_shipment_status(
    tracking_number: str,
    data: ShipmentStatusUpdate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    shipment = OrderService.update_shipment_status(db, tracking_number, data)
    return {
        "message":         f"Shipment {tracking_number} updated to {shipment.shipment_status}",
        "tracking_number": shipment.tracking_number,
        "shipment_status": shipment.shipment_status,
        "order_id":        shipment.order_id,
        "delivered_at":    shipment.delivered_at,
    }


# ════════════════════════════════════════════════════════════
# SINGLE ORDER ROUTES — /{order_id} last to avoid conflicts
# ════════════════════════════════════════════════════════════

@router.get(
    "/{order_id}",
    summary="Get full order detail (order + items + shipment + history)",
)
def get_order_detail(
    order_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    """
    Returns a fully enriched order object with:
    - order fields (all DB columns)
    - items (with product name, variant, color, size, image)
    - shipment details
    - status history (with changed_by name)
    - transaction details
    """
    return OrderService.get_order_detail(db, order_id)


@router.put(
    "/{order_id}/status",
    summary="Update order status",
)
def update_order_status(
    order_id: int,
    data: OrderStatusUpdate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    order = OrderService.update_order_status(db, order_id, data)
    return {
        "message":    f"Order {order_id} updated to {order.status}",
        "order_id":   order.id,
        "status":     order.status,
        "updated_at": order.updated_at,
    }


@router.post(
    "/{order_id}/cancel",
    summary="Cancel an order",
)
def cancel_order(
    order_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    order = OrderService.cancel_order(db, order_id)
    return {
        "message":  f"Order {order_id} cancelled",
        "order_id": order.id,
        "status":   order.status,
    }


@router.get(
    "/{order_id}/history",
    summary="Get order status history",
)
def get_order_history(
    order_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    history = OrderService.get_status_history(db, order_id)
    return [
        {
            "id":         h.id,
            "order_id":   h.order_id,
            "status":     h.status,
            "changed_by": h.changed_by,
            "remarks":    h.remarks,
            "changed_at": h.changed_at,
        }
        for h in history
    ]


@router.post(
    "/{order_id}/shipment",
    summary="Create shipment for an order",
)
def create_shipment(
    order_id: int,
    data: ShipmentCreate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    shipment = OrderService.create_shipment(db, order_id, data)
    return {
        "message":          "Shipment created successfully",
        "shipment_id":      shipment.id,
        "order_id":         shipment.order_id,
        "courier_name":     shipment.courier_name,
        "tracking_number":  shipment.tracking_number,
        "shipment_status":  shipment.shipment_status,
        "tracking_url":     shipment.tracking_url,
        "estimated_delivery": str(shipment.estimated_delivery) if shipment.estimated_delivery else None,
    }


@router.get(
    "/{order_id}/shipment",
    summary="Get shipment for an order",
)
def get_shipment(
    order_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    shipment = OrderService.get_shipment(db, order_id)
    return {
        "id":                 shipment.id,
        "order_id":           shipment.order_id,
        "courier_name":       shipment.courier_name,
        "tracking_number":    shipment.tracking_number,
        "shipment_status":    shipment.shipment_status,
        "tracking_url":       shipment.tracking_url,
        "shipping_label_url": shipment.shipping_label_url,
        "shipped_at":         shipment.shipped_at,
        "estimated_delivery": str(shipment.estimated_delivery) if shipment.estimated_delivery else None,
        "delivered_at":       shipment.delivered_at,
    }


@router.post(
    "/{order_id}/apply-discount",
    summary="Apply additional discount to an order",
)
def apply_additional_discount(
    order_id: int,
    data: ApplyAdditionalDiscount,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    data.order_id = order_id
    order = OrderService.apply_additional_discount(db, data)
    return {
        "message":                    f"Discount applied to order {order_id}",
        "order_id":                   order.id,
        "total_amount":               float(order.total_amount),
        "additional_discount_amount": float(order.additional_discount_amount) if order.additional_discount_amount else 0,
        "final_amount":               float(order.final_amount) if order.final_amount else None,
        "discount_reason":            order.discount_reason,
    }