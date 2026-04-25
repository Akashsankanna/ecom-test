from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.db.session import get_db
from app.core.dependencies import get_current_user, require_admin
from app.schemas.order import ReturnRequestCreate, ReturnApprove
from app.services.order_service import OrderService

router = APIRouter(tags=["Admin - Returns"])


# ════════════════════════════════════════════════════════════
# ADMIN ENDPOINTS
# ════════════════════════════════════════════════════════════

@router.get("/admin/returns", summary="List all return requests")
def get_all_returns(
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
            "id": r.id,
            "order_id": r.order_id,
            "order_item_id": r.order_item_id,
            "user_id": r.user_id,
            "quantity": r.quantity,
            "reason": r.reason,
            "status": r.status,
            "refund_amount": float(r.refund_amount) if r.refund_amount else None,
            "refund_method": r.refund_method,
            "requested_at": r.requested_at,
            "approved_at": r.approved_at,
            "completed_at": r.completed_at,
        }
        for r in returns
    ]


@router.get(
    "/admin/returns/view",
    summary="Return requests view — includes user email (uses return_request_view)",
)
def get_returns_view(
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    return OrderService.get_returns_view(db)


@router.get("/admin/returns/{return_id}", summary="Get return request by ID")
def get_return_detail(
    return_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    r = OrderService.get_return_request(db, return_id)
    return {
        "id": r.id,
        "order_id": r.order_id,
        "order_item_id": r.order_item_id,
        "user_id": r.user_id,
        "quantity": r.quantity,
        "reason": r.reason,
        "status": r.status,
        "refund_amount": float(r.refund_amount) if r.refund_amount else None,
        "refund_method": r.refund_method,
        "requested_at": r.requested_at,
        "approved_at": r.approved_at,
        "completed_at": r.completed_at,
    }


@router.post(
    "/admin/returns/{return_id}/approve",
    summary="Approve return → uses sp_approve_return_request",
)
def approve_return(
    return_id: int,
    data: ReturnApprove,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    """
    refund_method: ORIGINAL_PAYMENT | STORE_CREDIT | BANK_TRANSFER

    SP automatically:
    - Sets status = APPROVED
    - Restores variant stock
    - Logs RETURN in inventory_log
    - Creates IN_APP notification for the user
    """
    r = OrderService.approve_return(db, return_id, data)
    return {
        "message": f"Return {return_id} approved",
        "return_id": r.id,
        "status": r.status,
        "refund_amount": float(r.refund_amount) if r.refund_amount else None,
        "refund_method": r.refund_method,
        "approved_at": r.approved_at,
    }


@router.post("/admin/returns/{return_id}/reject", summary="Reject a return request")
def reject_return(
    return_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    r = OrderService.reject_return(db, return_id)
    return {
        "message": f"Return {return_id} rejected",
        "return_id": r.id,
        "status": r.status,
    }


@router.post(
    "/admin/returns/{return_id}/refund",
    summary="Complete refund → uses sp_complete_refund",
)
def complete_refund(
    return_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    """
    Return must be APPROVED before refund can be completed.
    SP automatically:
    - Sets status = REFUNDED
    - Creates PAYMENT_SUCCESS IN_APP notification for user
    """
    r = OrderService.complete_refund(db, return_id)
    return {
        "message": f"Refund for return {return_id} completed",
        "return_id": r.id,
        "status": r.status,
        "completed_at": r.completed_at,
    }


# ════════════════════════════════════════════════════════════
# USER ENDPOINT — raise own return request
# ════════════════════════════════════════════════════════════

@router.post(
    "/returns",
    summary="User: Create return request → uses sp_create_return_request",
)
def create_return_request(
    data: ReturnRequestCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """
    SP validates:
    - Order must be DELIVERED
    - Order must belong to the requesting user
    - Calculates refund_amount = price × quantity automatically
    """
    r = OrderService.create_return_request(db, user.id, data)
    return {
        "message": "Return request submitted successfully",
        "return_id": r.id,
        "status": r.status,
        "refund_amount": float(r.refund_amount) if r.refund_amount else None,
    }