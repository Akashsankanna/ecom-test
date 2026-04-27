from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.db.session import get_db
from app.core.dependencies import require_admin
from app.schemas.customization import (
    CustomizationTypeCreate, CustomizationTypeUpdate, CustomizationTypeOut,
    CustomizationPositionCreate, CustomizationPositionUpdate, CustomizationPositionOut,
    ProductCustomizationCreate, ProductCustomizationOut,
    AddCustomizationToOrderItem, OrderItemCustomizationOut,
)
from app.services.customization_service import CustomizationService

router = APIRouter(prefix="/admin/customizations", tags=["Admin - Customizations"])


# ════════════════════════════════════════════════════════════
# CUSTOMIZATION TYPES
# ════════════════════════════════════════════════════════════

@router.get("/types", summary="List all customization types")
def get_all_types(
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    """e.g. Embroidery, Screen Print, Monogram — each has additional_price."""
    types = CustomizationService.get_all_types(db, is_active)
    return [
        {
            "id": t.id,
            "name": t.name,
            "description": t.description,
            "is_active": t.is_active,
            "additional_price": float(t.additional_price) if t.additional_price else 0,
        }
        for t in types
    ]


@router.get("/types/{type_id}", summary="Get customization type by ID")
def get_type(
    type_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    t = CustomizationService.get_type(db, type_id)
    return {
        "id": t.id,
        "name": t.name,
        "description": t.description,
        "is_active": t.is_active,
        "additional_price": float(t.additional_price) if t.additional_price else 0,
    }


@router.post("/types", summary="Create customization type")
def create_type(
    data: CustomizationTypeCreate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    t = CustomizationService.create_type(db, data)
    return {
        "message": f"Customization type '{t.name}' created",
        "id": t.id,
        "name": t.name,
        "additional_price": float(t.additional_price) if t.additional_price else 0,
    }


@router.put("/types/{type_id}", summary="Update customization type")
def update_type(
    type_id: int,
    data: CustomizationTypeUpdate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    t = CustomizationService.update_type(db, type_id, data)
    return {
        "message": f"Type {type_id} updated",
        "id": t.id,
        "name": t.name,
        "is_active": t.is_active,
        "additional_price": float(t.additional_price) if t.additional_price else 0,
    }


@router.delete("/types/{type_id}", summary="Deactivate customization type")
def delete_type(
    type_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    return CustomizationService.delete_type(db, type_id)


# ════════════════════════════════════════════════════════════
# CUSTOMIZATION POSITIONS
# ════════════════════════════════════════════════════════════

@router.get("/positions", summary="List all customization positions")
def get_all_positions(
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    """e.g. Chest Left, Chest Right, Back, Sleeve — each has additional_price."""
    positions = CustomizationService.get_all_positions(db)
    return [
        {
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "additional_price": float(p.additional_price) if p.additional_price else 0,
        }
        for p in positions
    ]


@router.get("/positions/{pos_id}", summary="Get position by ID")
def get_position(
    pos_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    p = CustomizationService.get_position(db, pos_id)
    return {
        "id": p.id,
        "name": p.name,
        "description": p.description,
        "additional_price": float(p.additional_price) if p.additional_price else 0,
    }


@router.post("/positions", summary="Create customization position")
def create_position(
    data: CustomizationPositionCreate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    p = CustomizationService.create_position(db, data)
    return {
        "message": f"Position '{p.name}' created",
        "id": p.id,
        "name": p.name,
        "additional_price": float(p.additional_price) if p.additional_price else 0,
    }


@router.put("/positions/{pos_id}", summary="Update customization position")
def update_position(
    pos_id: int,
    data: CustomizationPositionUpdate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    p = CustomizationService.update_position(db, pos_id, data)
    return {
        "message": f"Position {pos_id} updated",
        "id": p.id,
        "name": p.name,
        "additional_price": float(p.additional_price) if p.additional_price else 0,
    }


@router.delete("/positions/{pos_id}", summary="Delete customization position")
def delete_position(
    pos_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    return CustomizationService.delete_position(db, pos_id)


# ════════════════════════════════════════════════════════════
# PRODUCT CUSTOMIZATIONS (which types allowed per product)
# ════════════════════════════════════════════════════════════

@router.get(
    "/products/{product_id}",
    summary="Get all customization options for a product",
)
def get_product_customizations(
    product_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    pcs = CustomizationService.get_product_customizations(db, product_id)
    return [
        {
            "id": pc.id,
            "product_id": pc.product_id,
            "customization_type_id": pc.customization_type_id,
            "price": float(pc.price) if pc.price else 0,
            "is_required": pc.is_required,
            "max_text_length": pc.max_text_length,
            "allowed_file_types": pc.allowed_file_types,
            "is_active": pc.is_active,
        }
        for pc in pcs
    ]


@router.post(
    "/products",
    summary="Add a customization type to a product",
)
def create_product_customization(
    data: ProductCustomizationCreate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    pc = CustomizationService.create_product_customization(db, data)
    return {
        "message": f"Customization type {data.customization_type_id} added to product {data.product_id}",
        "id": pc.id,
        "product_id": pc.product_id,
        "customization_type_id": pc.customization_type_id,
        "is_active": pc.is_active,
    }


@router.delete(
    "/products/{pc_id}",
    summary="Remove a customization option from a product",
)
def delete_product_customization(
    pc_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    return CustomizationService.delete_product_customization(db, pc_id)


# ════════════════════════════════════════════════════════════
# ORDER ITEM CUSTOMIZATIONS
# ════════════════════════════════════════════════════════════

@router.get(
    "/order-items",
    summary="List all order item customizations",
)
def get_order_item_customizations(
    order_item_id: Optional[int] = Query(None, description="Filter by order item"),
    approval_status: Optional[str] = Query(
        None, description="PENDING | APPROVED | REJECTED"
    ),
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    items = CustomizationService.get_order_item_customizations(
        db, order_item_id, approval_status
    )
    return [
        {
            "id": i.id,
            "order_item_id": i.order_item_id,
            "customization_type_id": i.customization_type_id,
            "position_id": i.position_id,
            "text_value": i.text_value,
            "customization_value": i.customization_value,
            "image_url": i.image_url,
            "image_name": i.image_name,
            "approved": i.approved,
            "approved_by": i.approved_by,
            "approval_status": i.approval_status,
            "additional_price": float(i.additional_price) if i.additional_price else 0,
            "created_at": i.created_at,
        }
        for i in items
    ]


@router.get(
    "/order-items/pending",
    summary="List all PENDING customization approvals",
)
def get_pending_customizations(
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    items = CustomizationService.get_pending_customizations(db)
    return [
        {
            "id": i.id,
            "order_item_id": i.order_item_id,
            "customization_type_id": i.customization_type_id,
            "position_id": i.position_id,
            "customization_value": i.customization_value,
            "image_url": i.image_url,
            "additional_price": float(i.additional_price) if i.additional_price else 0,
            "created_at": i.created_at,
        }
        for i in items
    ]


@router.post(
    "/order-items",
    summary="Add customization to an order item → uses sp_add_customization_to_order_item",
)
def add_customization_to_order_item(
    data: AddCustomizationToOrderItem,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    """
    SP automatically:
    - Inserts into order_item_customization
    - Adds additional_price to the order total
    - Sets approved=FALSE (pending approval)
    """
    item = CustomizationService.add_customization_to_order_item(db, data)
    return {
        "message": "Customization added to order item",
        "id": item.id,
        "order_item_id": item.order_item_id,
        "customization_type_id": item.customization_type_id,
        "approval_status": item.approval_status,
        "additional_price": float(item.additional_price) if item.additional_price else 0,
    }


@router.post(
    "/order-items/{customization_id}/approve",
    summary="Approve order item customization → uses sp_approve_customization",
)
def approve_customization(
    customization_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    """SP sets approved=TRUE and records approved_by."""
    item = CustomizationService.approve_customization(db, customization_id, admin.id)
    return {
        "message": f"Customization {customization_id} approved",
        "id": item.id,
        "approved": item.approved,
        "approved_by": item.approved_by,
        "approval_status": item.approval_status,
    }


@router.post(
    "/order-items/{customization_id}/reject",
    summary="Reject order item customization",
)
def reject_customization(
    customization_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    item = CustomizationService.reject_customization(
        db,
        customization_id,
        admin.id
    )

    return {
        "message": f"Customization {customization_id} rejected",
        "id": item.id,
        "approved": item.approved,
        "approved_by": item.approved_by,
        "approval_status": item.approval_status,
    }