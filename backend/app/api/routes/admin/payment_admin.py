from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel

from app.db.session import get_db
from app.core.dependencies import require_admin
from app.services.payment_service import PaymentService

router = APIRouter(prefix="/admin/payments", tags=["Admin - Payments"])


class ProcessPaymentRequest(BaseModel):
    order_id: int
    payment_method: str  # UPI | CARD | NET_BANKING | NEFT | RTGS | COD | BANK_TRANSFER
    status: str          # PENDING | SUCCESS | FAILED
    transaction_ref: str


@router.get("/", summary="List all transactions")
def get_all_payments(
    status: Optional[str] = Query(
        None,
        description="Filter by status: PENDING | SUCCESS | FAILED | REFUNDED",
    ),
    payment_method: Optional[str] = Query(
        None,
        description="Filter by payment method: UPI | CARD | NET_BANKING | NEFT | COD etc.",
    ),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    txns = PaymentService.get_all_payments(db, status, payment_method, limit)
    return [
        {
            "id": t.id,
            "order_id": t.order_id,
            "amount": float(t.amount),
            "payment_method": t.payment_method,
            "status": t.status,
            "transaction_ref": t.transaction_ref,
            "payment_gateway": t.payment_gateway,
            "gateway_transaction_id": t.gateway_transaction_id,
            "currency": t.currency,
            "created_at": t.created_at,
        }
        for t in txns
    ]


@router.get("/view", summary="Payment view — transactions joined with orders")
def get_payment_view(
    order_id: Optional[int] = Query(None, description="Filter by order ID"),
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    """Uses payment_view DB view."""
    return PaymentService.get_payment_view(db, order_id)


@router.get("/summary", summary="Revenue summary across all transactions")
def get_revenue_summary(
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    return PaymentService.get_revenue_summary(db)


@router.get("/{order_id}", summary="Get all transactions for a specific order")
def get_payments_by_order(
    order_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    txns = PaymentService.get_payments_by_order(db, order_id)
    return [
        {
            "id": t.id,
            "order_id": t.order_id,
            "amount": float(t.amount),
            "payment_method": t.payment_method,
            "status": t.status,
            "transaction_ref": t.transaction_ref,
            "payment_gateway": t.payment_gateway,
            "gateway_transaction_id": t.gateway_transaction_id,
            "currency": t.currency,
            "created_at": t.created_at,
        }
        for t in txns
    ]


@router.post(
    "/process",
    summary="Process payment for an order → uses sp_process_payment",
)
def process_payment(
    data: ProcessPaymentRequest,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    """
    Uses sp_process_payment which:
    - Inserts into transactions table
    - Updates orders.payment_status
    - If SUCCESS → sets order.status = PAID
    - Triggers trg_payment_success → sp_reduce_stock automatically
    """
    txn = PaymentService.process_payment(
        db,
        data.order_id,
        data.payment_method,
        data.status,
        data.transaction_ref,
    )
    return {
        "message": "Payment processed successfully",
        "transaction_id": txn.id,
        "order_id": txn.order_id,
        "amount": float(txn.amount),
        "payment_method": txn.payment_method,
        "status": txn.status,
        "transaction_ref": txn.transaction_ref,
    }