from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.order import ReturnRequestCreate
from app.services.order_service import OrderService

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.get("/", summary="Get orders for a user")
def get_orders(
    user_id: int = Query(..., description="The user's ID"),
    db: Session = Depends(get_db),
):
    """
    Returns all orders for the given user, each with:
    - Full order fields from DB
    - Items with product name, variant, color, size, image URL
    - Shipment details (status, tracking, courier)
    """
    return {
        "success": True,
        "orders":  OrderService.get_user_orders(db, user_id),
    }


@router.get("/{order_id}", summary="Get single order detail for user")
def get_order_detail(
    order_id: int,
    db: Session = Depends(get_db),
):
    """
    Full order detail for user-facing order confirmation / tracking page.
    Includes items, shipment, status history, and transaction.
    """
    return OrderService.get_order_detail(db, order_id)


@router.get(
    "/{order_id}/track",
    summary="Track an order (status history + shipment)",
)
def track_order(
    order_id: int,
    db: Session = Depends(get_db),
):
    detail = OrderService.get_order_detail(db, order_id)
    return {
        "order_id":      detail["order"]["id"],
        "status":        detail["order"]["status"],
        "shipment":      detail["shipment"],
        "status_history": detail["status_history"],
    }


@router.post(
    "/{order_id}/return",
    summary="Create a return request",
)
def create_return_request(
    order_id: int,
    data: ReturnRequestCreate,
    user_id: int = Query(...),
    db: Session = Depends(get_db),
):
    data.order_id = order_id
    rr = OrderService.create_return_request(db, user_id, data)
    return {
        "message":   "Return request submitted",
        "return_id": rr.id,
        "status":    rr.status,
    }