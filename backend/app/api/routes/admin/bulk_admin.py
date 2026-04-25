from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from typing import Optional

from app.db.session import get_db
from app.core.dependencies import require_admin

from app.schemas.bulk_order import (
    BulkOrderConvert,
    BulkOrderStatusUpdate,
    OrganizationCreate,
)

from app.services.bulk_order_service import BulkOrderService
from app.repositories.bulk_order_repo import BulkOrderRepository

router = APIRouter(
    prefix="/admin",
    tags=["Admin - Bulk Orders"]
)

# ════════════════════════════════════════════════════════════
# ORGANIZATIONS
# ════════════════════════════════════════════════════════════

@router.get(
    "/organizations",
    summary="List all active organizations"
)
def get_organizations(
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    orgs = BulkOrderService.get_all_organizations(db)

    return [
        {
            "id": o.id,
            "name": o.name,
            "contact_person": o.contact_person,
            "email": o.email,
            "phone": o.phone,
            "gst_number": o.gst_number,
            "city": o.city,
            "state": o.state,
            "is_active": o.is_active,
        }
        for o in orgs
    ]


@router.post(
    "/organizations",
    status_code=201,
    summary="Create organization"
)
def create_organization(
    data: OrganizationCreate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    """
    organization.email has UNIQUE constraint
    Return 409 on duplicate email
    """
    try:
        org = BulkOrderService.create_organization(
            db,
            data
        )

        return {
            "message": "Organization created successfully",
            "id": org.id,
            "name": org.name,
            "contact_person": org.contact_person,
            "email": org.email,
            "phone": org.phone,
            "gst_number": org.gst_number,
            "city": org.city,
            "state": org.state,
            "is_active": org.is_active,
        }

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Organization with this email already exists"
        )


# ════════════════════════════════════════════════════════════
# BULK REQUESTS
# ════════════════════════════════════════════════════════════

@router.get(
    "/bulk-requests",
    summary="List all bulk requests"
)
def get_all_bulk_requests(
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    requests = BulkOrderService.get_all_bulk_requests(
        db,
        status
    )

    return [
        {
            "id": r.id,
            "organization_id": r.organization_id,
            "user_id": r.user_id,
            "request_number": r.request_number,
            "status": r.status,
            "notes": r.notes,
            "expected_delivery_date": r.expected_delivery_date,
            "created_at": r.created_at,
        }
        for r in requests
    ]


@router.get(
    "/bulk-requests/{request_id}",
    summary="Get bulk request detail"
)
def get_bulk_request(
    request_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    req, items = BulkOrderService.get_bulk_request(
        db,
        request_id
    )

    return {
        "id": req.id,
        "organization_id": req.organization_id,
        "user_id": req.user_id,
        "request_number": req.request_number,
        "status": req.status,
        "notes": req.notes,
        "expected_delivery_date": req.expected_delivery_date,
        "created_at": req.created_at,
        "items": [
            {
                "id": i.id,
                "variant_id": i.variant_id,
                "quantity": i.quantity,
                "requested_price": float(i.requested_price)
                if i.requested_price else None,
                "quoted_price": float(i.quoted_price)
                if i.quoted_price else None,
                "notes": i.notes,
            }
            for i in items
        ],
    }


@router.post(
    "/bulk-requests/{request_id}/approve",
    summary="Approve bulk request"
)
def approve_bulk_request(
    request_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    req = BulkOrderService.approve_bulk_request(
        db,
        request_id
    )

    return {
        "message": f"Bulk request {request_id} approved",
        "request_id": req.id,
        "status": req.status,
    }


@router.post(
    "/bulk-requests/{request_id}/reject",
    summary="Reject bulk request"
)
def reject_bulk_request(
    request_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    req = BulkOrderService.reject_bulk_request(
        db,
        request_id
    )

    return {
        "message": f"Bulk request {request_id} rejected",
        "request_id": req.id,
        "status": req.status,
    }


@router.post(
    "/bulk-requests/{request_id}/convert",
    summary="Convert approved request to bulk order"
)
def convert_to_order(
    request_id: int,
    data: BulkOrderConvert,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    bulk_order = BulkOrderService.convert_to_order(
        db,
        request_id,
        data,
        admin.id
    )

    return {
        "message": f"Bulk request {request_id} converted",
        "bulk_order_id": bulk_order.id,
        "order_number": bulk_order.order_number,
        "total_amount": float(bulk_order.total_amount),
        "status": bulk_order.status,
        "payment_status": bulk_order.payment_status,
        "is_urgent": bulk_order.is_urgent,
        "expected_delivery_date": bulk_order.expected_delivery_date,
    }


# ════════════════════════════════════════════════════════════
# BULK ORDERS
# ════════════════════════════════════════════════════════════

@router.get(
    "/bulk-orders",
    summary="List all bulk orders"
)
def get_all_bulk_orders(
    status: Optional[str] = Query(None),
    is_urgent: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    orders = BulkOrderService.get_all_bulk_orders(
        db,
        status
    )

    result = [
        {
            "id": o.id,
            "order_number": o.order_number,
            "organization_id": o.organization_id,
            "total_amount": float(o.total_amount),
            "status": o.status,
            "payment_status": o.payment_status,
            "is_urgent": o.is_urgent,
            "expected_delivery_date": o.expected_delivery_date,
            "created_at": o.created_at,
        }
        for o in orders
    ]

    if is_urgent is not None:
        result = [
            x for x in result
            if x["is_urgent"] == is_urgent
        ]

    return result


# IMPORTANT FIX:
# must stay ABOVE /bulk-orders/{bulk_order_id}

@router.get(
    "/bulk-orders/view",
    summary="Bulk order view"
)
def get_bulk_order_view(
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    return BulkOrderService.get_bulk_order_view(db)


@router.get(
    "/bulk-orders/{bulk_order_id}",
    summary="Get bulk order detail"
)
def get_bulk_order(
    bulk_order_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    order, items = BulkOrderService.get_bulk_order(
        db,
        bulk_order_id
    )

    return {
        "id": order.id,
        "order_number": order.order_number,
        "organization_id": order.organization_id,
        "total_amount": float(order.total_amount),
        "status": order.status,
        "payment_status": order.payment_status,
        "is_urgent": order.is_urgent,
        "expected_delivery_date": order.expected_delivery_date,
        "created_at": order.created_at,
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
    "/bulk-orders/{bulk_order_id}/status",
    summary="Update bulk order status"
)
def update_bulk_order_status(
    bulk_order_id: int,
    data: BulkOrderStatusUpdate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    order = BulkOrderService.update_bulk_order_status(
        db,
        bulk_order_id,
        data.status.value,
        admin.id
    )

    return {
        "message": f"Bulk order {bulk_order_id} updated",
        "bulk_order_id": order.id,
        "status": order.status,
        "updated_at": order.updated_at,
    }


@router.get(
    "/bulk-orders/{bulk_order_id}/history",
    summary="Bulk order status history"
)
def get_bulk_order_history(
    bulk_order_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    history = BulkOrderService.get_bulk_order_status_history(
        db,
        bulk_order_id
    )

    return [
        {
            "id": h.id,
            "bulk_order_id": h.bulk_order_id,
            "status": h.status,
            "changed_by": h.changed_by,
            "notes": h.notes,
            "changed_at": h.changed_at,
        }
        for h in history
    ]


@router.patch(
    "/bulk-orders/{bulk_order_id}/urgent",
    summary="Toggle urgent flag"
)
def set_bulk_order_urgent(
    bulk_order_id: int,
    is_urgent: bool = Query(...),
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    order = BulkOrderRepository.get_bulk_order_by_id(
        db,
        bulk_order_id
    )

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Bulk order not found"
        )

    db.execute(
        text(
            """
            UPDATE bulk_order
            SET is_urgent = :urgent
            WHERE id = :bid
            """
        ),
        {
            "urgent": is_urgent,
            "bid": bulk_order_id
        }
    )

    db.commit()
    db.expire_all()

    order = BulkOrderRepository.get_bulk_order_by_id(
        db,
        bulk_order_id
    )

    return {
        "message": f"Bulk order {bulk_order_id} urgency updated",
        "bulk_order_id": order.id,
        "is_urgent": order.is_urgent,
    }