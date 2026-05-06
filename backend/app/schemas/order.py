from pydantic import BaseModel, field_validator
from typing import Optional, List
from decimal import Decimal
from datetime import date, datetime
from enum import Enum


# ════════════════════════════════════════════════════════════
# ENUMS — exactly matching DB CHECK constraints
# ════════════════════════════════════════════════════════════

class OrderStatus(str, Enum):
    PENDING    = "PENDING"
    PAID       = "PAID"
    CONFIRMED  = "CONFIRMED"
    PROCESSING = "PROCESSING"
    SHIPPED    = "SHIPPED"
    DELIVERED  = "DELIVERED"
    CANCELLED  = "CANCELLED"
    PAYMENT_FAILED = "PAYMENT_FAILED"


class PaymentStatus(str, Enum):
    PENDING  = "PENDING"
    SUCCESS  = "SUCCESS"
    FAILED   = "FAILED"
    REFUNDED = "REFUNDED"


class ShipmentStatus(str, Enum):
    PENDING          = "PENDING"
    SHIPPED          = "SHIPPED"
    OUT_FOR_DELIVERY = "OUT_FOR_DELIVERY"
    DELIVERED        = "DELIVERED"
    FAILED           = "FAILED"
    RETURNED         = "RETURNED"


class ReturnStatus(str, Enum):
    REQUESTED = "REQUESTED"
    APPROVED  = "APPROVED"
    REJECTED  = "REJECTED"
    REFUNDED  = "REFUNDED"
    COMPLETED = "COMPLETED"


class RefundMethod(str, Enum):
    ORIGINAL_PAYMENT = "ORIGINAL_PAYMENT"
    STORE_CREDIT     = "STORE_CREDIT"
    BANK_TRANSFER    = "BANK_TRANSFER"


class ExchangeStatus(str, Enum):
    REQUESTED = "REQUESTED"
    APPROVED  = "APPROVED"
    REJECTED  = "REJECTED"
    COMPLETED = "COMPLETED"


class InventoryChangeType(str, Enum):
    ORDER           = "ORDER"
    ORDER_PLACED    = "ORDER_PLACED"
    ORDER_CANCELLED = "ORDER_CANCELLED"
    EXCHANGE        = "EXCHANGE"
    RESTOCK         = "RESTOCK"
    ADJUSTMENT      = "ADJUSTMENT"
    RETURN          = "RETURN"


# ════════════════════════════════════════════════════════════
# ORDER SCHEMAS
# ════════════════════════════════════════════════════════════

class OrderStatusUpdate(BaseModel):
    status: OrderStatus


class OrderItemOut(BaseModel):
    id: int
    order_id: int
    variant_id: int
    product_id: Optional[int] = None
    quantity: int
    price: Decimal
    customization_total: Optional[Decimal] = Decimal("0")

    class Config:
        from_attributes = True


class OrderOut(BaseModel):
    id: int
    user_id: Optional[int] = None
    total_amount: Decimal
    gross_amount: Optional[Decimal] = None
    status: str
    payment_status: str
    address_id: Optional[int] = None
    coupon_id: Optional[int] = None
    coupon_discount_amount: Optional[Decimal] = None
    additional_discount_amount: Optional[Decimal] = None
    final_amount: Optional[Decimal] = None
    discount_reason: Optional[str] = None
    transaction_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class OrderDetailOut(BaseModel):
    id: int
    user_id: Optional[int] = None
    total_amount: Decimal
    gross_amount: Optional[Decimal] = None
    status: str
    payment_status: str
    address_id: Optional[int] = None
    coupon_id: Optional[int] = None
    coupon_discount_amount: Optional[Decimal] = None
    additional_discount_amount: Optional[Decimal] = None
    final_amount: Optional[Decimal] = None
    discount_reason: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    items: List[OrderItemOut] = []

    class Config:
        from_attributes = True


class OrderStatusHistoryOut(BaseModel):
    id: int
    order_id: int
    status: str
    changed_by: Optional[int] = None
    remarks: Optional[str] = None
    changed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ════════════════════════════════════════════════════════════
# SHIPMENT SCHEMAS
# ════════════════════════════════════════════════════════════

class ShipmentCreate(BaseModel):
    courier_name: str
    tracking_number: str
    estimated_delivery: Optional[date] = None
    tracking_url: Optional[str] = None


class ShipmentStatusUpdate(BaseModel):
    status: ShipmentStatus


class ShipmentOut(BaseModel):
    id: int
    order_id: int
    courier_name: str
    tracking_number: str
    shipment_status: str
    tracking_url: Optional[str] = None
    shipping_label_url: Optional[str] = None
    estimated_delivery: Optional[date] = None
    shipped_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ════════════════════════════════════════════════════════════
# RETURN REQUEST SCHEMAS
# ════════════════════════════════════════════════════════════

class ReturnRequestCreate(BaseModel):
    order_id: int
    order_item_id: int
    quantity: int
    reason: str

    @field_validator("quantity")
    @classmethod
    def qty_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Quantity must be greater than 0")
        return v


class ReturnApprove(BaseModel):
    refund_method: RefundMethod


class ReturnRequestOut(BaseModel):
    id: int
    order_id: int
    order_item_id: int
    user_id: int
    quantity: int
    reason: str
    status: str
    refund_amount: Optional[Decimal] = None
    refund_method: Optional[str] = None
    requested_at: Optional[datetime] = None
    approved_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ════════════════════════════════════════════════════════════
# EXCHANGE SCHEMAS
# ════════════════════════════════════════════════════════════

class ExchangeCreate(BaseModel):
    order_id: int
    order_item_id: int
    reason: str


class ExchangeStatusUpdate(BaseModel):
    status: ExchangeStatus


class ExchangeCompleteData(BaseModel):
    new_variant_id: int


class ExchangeOut(BaseModel):
    id: int
    order_id: int
    order_item_id: int
    reason: Optional[str] = None
    status: str
    return_request_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ════════════════════════════════════════════════════════════
# INVENTORY SCHEMAS
# ════════════════════════════════════════════════════════════

class StockAdjust(BaseModel):
    variant_id: int
    quantity: int
    change_type: InventoryChangeType
    reference_id: Optional[int] = None
    notes: Optional[str] = None

    @field_validator("quantity")
    @classmethod
    def qty_positive(cls, v):
        if v <= 0:
            raise ValueError("Quantity must be greater than 0")
        return v


class VariantStockUpdate(BaseModel):
    stock: int
    low_stock_threshold: Optional[int] = None

    @field_validator("stock")
    @classmethod
    def stock_non_negative(cls, v):
        if v < 0:
            raise ValueError("Stock cannot be negative")
        return v


class InventoryLogOut(BaseModel):
    id: int
    variant_id: Optional[int] = None
    change_type: Optional[str] = None
    quantity: int
    reference_id: Optional[int] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class VariantInventoryOut(BaseModel):
    id: int
    product_id: int
    variant_name: Optional[str] = None
    sku: Optional[str] = None
    price: Decimal
    stock: int
    reserved_stock: int
    low_stock_threshold: int
    color_id: Optional[int] = None
    size: Optional[str] = None
    is_deleted: bool

    class Config:
        from_attributes = True


# ════════════════════════════════════════════════════════════
# COUPON SCHEMAS (for order discount endpoints)
# ════════════════════════════════════════════════════════════

class ApplyAdditionalDiscount(BaseModel):
    order_id: int
    discount_amount: Decimal
    reason: Optional[str] = "Manual discount"

    @field_validator("discount_amount")
    @classmethod
    def discount_positive(cls, v):
        if v <= 0:
            raise ValueError("Discount amount must be greater than 0")
        return v


class ApplyCouponRequest(BaseModel):
    order_id: int
    coupon_code: str
    user_id: int
    order_amount: Decimal
    additional_discount: Optional[Decimal] = Decimal("0")