# app/schemas/inventory_schema.py

from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
from datetime import datetime


# ════════════════════════════════════════════════════════
# ENUMS
# ════════════════════════════════════════════════════════

class InventoryChangeType(str, Enum):
    ORDER = "ORDER"
    ORDER_CANCELLED = "ORDER_CANCELLED"
    EXCHANGE = "EXCHANGE"
    RESTOCK = "RESTOCK"
    ADJUSTMENT = "ADJUSTMENT"
    RETURN = "RETURN"
    DAMAGED = "DAMAGED"


# ════════════════════════════════════════════════════════
# STOCK OPERATIONS
# ════════════════════════════════════════════════════════

class StockAdjust(BaseModel):
    variant_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0)
    change_type: InventoryChangeType

    reference_id: Optional[int] = None
    reference_type: Optional[str] = None
    notes: Optional[str] = None


# ════════════════════════════════════════════════════════
# GENERIC REQUEST
# ════════════════════════════════════════════════════════

class StockChangeRequest(BaseModel):
    variant_id: int
    quantity: int
    change_type: str

    reference_id: Optional[int] = None
    reference_type: Optional[str] = None
    notes: Optional[str] = None


# ════════════════════════════════════════════════════════
# UPDATE STOCK / RESERVED / THRESHOLD
# ════════════════════════════════════════════════════════

class VariantStockUpdate(BaseModel):
    stock: Optional[int] = None
    reserved_stock: Optional[int] = None
    low_stock_threshold: Optional[int] = None


# ════════════════════════════════════════════════════════
# RESPONSE SCHEMA
# ════════════════════════════════════════════════════════

class InventoryVariantResponse(BaseModel):
    id: int
    product_id: int
    variant_name: str
    sku: Optional[str]
    price: float

    stock: int
    reserved_stock: int
    low_stock_threshold: int

    color: Optional[str]
    color_id: Optional[int]
    size: Optional[str]

    is_deleted: bool

    class Config:
        from_attributes = True


# ════════════════════════════════════════════════════════
# INVENTORY LOG RESPONSE
# ════════════════════════════════════════════════════════

class InventoryLogResponse(BaseModel):
    id: int
    variant_id: Optional[int]

    change_type: Optional[str]
    quantity: int

    previous_stock: Optional[int]
    new_stock: Optional[int]

    previous_reserved_stock: Optional[int]
    new_reserved_stock: Optional[int]

    reference_id: Optional[int]
    reference_type: Optional[str]

    notes: Optional[str]

    created_by: Optional[int]
    updated_by: Optional[int]

    created_at: datetime

    class Config:
        from_attributes = True


# ════════════════════════════════════════════════════════
# LOW STOCK RESPONSE
# ════════════════════════════════════════════════════════

class LowStockResponse(BaseModel):
    id: int
    product_id: int
    variant_name: str
    stock: int
    low_stock_threshold: int

    class Config:
        from_attributes = True


# ════════════════════════════════════════════════════════
# FULL PRODUCT INVENTORY VIEW
# ════════════════════════════════════════════════════════

class ProductInventoryFullView(BaseModel):
    product_id: int
    product_name: str
    product_sku: Optional[str]

    variant_id: int
    variant_name: str

    price: float
    stock: int
    reserved_stock: int

    size: Optional[str]
    color: Optional[str]
    color_id: Optional[int]

    class Config:
        from_attributes = True