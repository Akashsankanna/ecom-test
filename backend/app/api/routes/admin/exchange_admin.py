from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.db.session import get_db
from app.core.dependencies import require_admin
from app.schemas.order import (
    ExchangeCreate,
    ExchangeStatusUpdate,
    ExchangeCompleteData,
)
from app.services.order_service import OrderService

router = APIRouter(prefix="/admin/exchanges", tags=["Admin - Exchanges"])


@router.get("/", summary="List all exchange requests")
def get_all_exchanges(
    status: Optional[str] = Query(
        None,
        description="REQUESTED | APPROVED | REJECTED | COMPLETED | CANCELLED",
    ),
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    exchanges = OrderService.get_all_exchanges(db, status)
    return [
        {
            "id": e.id,
            "order_id": e.order_id,
            "order_item_id": e.order_item_id,
            "reason": e.reason,
            "status": e.status,
            "created_at": e.created_at,
            "updated_at": e.updated_at,
        }
        for e in exchanges
    ]


@router.get("/view", summary="Exchange view — includes user_id via join")
def get_exchange_view(
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    """Uses exchange_view DB view which joins orders to get user_id."""
    return OrderService.get_exchange_view(db)


@router.get("/{exchange_id}", summary="Get exchange request by ID")
def get_exchange(
    exchange_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    e = OrderService.get_exchange(db, exchange_id)
    return {
        "id": e.id,
        "order_id": e.order_id,
        "order_item_id": e.order_item_id,
        "reason": e.reason,
        "status": e.status,
        "created_at": e.created_at,
        "updated_at": e.updated_at,
    }


@router.post(
    "/",
    summary="Create exchange request → uses sp_create_exchange (order must be DELIVERED)",
)
def create_exchange(
    data: ExchangeCreate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    """
    SP validates order is DELIVERED before allowing exchange.
    Raises exception if order not yet delivered.
    """
    e = OrderService.create_exchange(db, data)
    return {
        "message": "Exchange request created successfully",
        "exchange_id": e.id,
        "order_id": e.order_id,
        "order_item_id": e.order_item_id,
        "status": e.status,
    }


@router.put(
    "/{exchange_id}/status",
    summary="Update exchange status → uses sp_update_exchange_status",
)
def update_exchange_status(
    exchange_id: int,
    data: ExchangeStatusUpdate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    """
    Allowed transitions:
    REQUESTED → APPROVED / REJECTED
    APPROVED  → COMPLETED / CANCELLED
    """
    e = OrderService.update_exchange_status(db, exchange_id, data)
    return {
        "message": f"Exchange {exchange_id} status updated to {e.status}",
        "exchange_id": e.id,
        "status": e.status,
        "updated_at": e.updated_at,
    }


@router.post(
    "/{exchange_id}/complete",
    summary="Complete exchange → uses sp_complete_exchange (reduces new variant stock)",
)
def complete_exchange(
    exchange_id: int,
    data: ExchangeCompleteData,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    """
    Provide the new_variant_id to exchange to.
    SP reduces stock of the new variant automatically.
    """
    e = OrderService.complete_exchange(db, exchange_id, data)
    return {
        "message": f"Exchange {exchange_id} completed with new variant {data.new_variant_id}",
        "exchange_id": e.id,
        "status": e.status,
        "updated_at": e.updated_at,
    }