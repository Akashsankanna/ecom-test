"""
Customization schemas — customization_type, customization_position,
product_customization, order_item_customization tables.
Uses: sp_add_customization_to_order_item, sp_approve_customization.
Import from: app.schemas.customization
"""
from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
from datetime import datetime
from enum import Enum


class ApprovalStatus(str, Enum):
    PENDING  = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


# ─── Customization Type ───────────────────────────────────────────────────────

class CustomizationTypeCreate(BaseModel):
    name: str
    description: Optional[str] = None
    is_active: Optional[bool] = True
    additional_price: Optional[Decimal] = Decimal("0")


class CustomizationTypeUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    additional_price: Optional[Decimal] = None


class CustomizationTypeOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    is_active: bool
    additional_price: Optional[Decimal] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ─── Customization Position ───────────────────────────────────────────────────

class CustomizationPositionCreate(BaseModel):
    name: str
    description: Optional[str] = None
    additional_price: Optional[Decimal] = Decimal("0")


class CustomizationPositionUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    additional_price: Optional[Decimal] = None


class CustomizationPositionOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    additional_price: Optional[Decimal] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ─── Product Customization ────────────────────────────────────────────────────

class ProductCustomizationCreate(BaseModel):
    product_id: int
    customization_type_id: int
    price: Optional[Decimal] = Decimal("0")
    is_required: Optional[bool] = False
    max_text_length: Optional[int] = None
    allowed_file_types: Optional[str] = None
    is_active: Optional[bool] = True


class ProductCustomizationOut(BaseModel):
    id: int
    product_id: int
    customization_type_id: int
    price: Optional[Decimal] = None
    is_required: bool
    max_text_length: Optional[int] = None
    allowed_file_types: Optional[str] = None
    is_active: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ─── Order Item Customization ─────────────────────────────────────────────────

class AddCustomizationToOrderItem(BaseModel):
    """Input for sp_add_customization_to_order_item stored procedure."""
    order_item_id: int
    customization_type_id: int
    position_id: Optional[int] = None
    customization_value: Optional[str] = None
    image_url: Optional[str] = None
    additional_price: Optional[Decimal] = Decimal("0")


class OrderItemCustomizationOut(BaseModel):
    id: int
    order_item_id: int
    customization_type_id: int
    position_id: Optional[int] = None
    text_value: Optional[str] = None
    customization_value: Optional[str] = None
    image_url: Optional[str] = None
    image_name: Optional[str] = None
    approved: bool
    approved_by: Optional[int] = None
    approval_status: str
    additional_price: Optional[Decimal] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True