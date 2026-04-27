"""
Cart & Wishlist schemas
Supports:
- cart
- cart_item
- wishlist
- wishlist_item

Stored Procedures:
- sp_add_to_cart
- sp_merge_guest_cart
- sp_add_to_wishlist
- sp_remove_from_wishlist
- sp_merge_wishlist
- sp_checkout
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from decimal import Decimal
from datetime import datetime


# =====================================================
# CART REQUEST SCHEMAS
# =====================================================

class CartItemCreate(BaseModel):
    variant_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0)

    # optional future customization pricing
    customization_total: Optional[float] = 0.0

    @field_validator("quantity")
    @classmethod
    def qty_positive(cls, v):
        if v <= 0:
            raise ValueError("Quantity must be > 0")
        return v


# alias kept for old code compatibility
class AddToCart(CartItemCreate):
    pass


class UpdateCartItem(BaseModel):
    cart_item_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0)


class RemoveCartItem(BaseModel):
    cart_item_id: int = Field(..., gt=0)


class CheckoutRequest(BaseModel):
    """
    Input for:
    sp_checkout(p_cart_id, p_address_id)
    """
    cart_id: int
    address_id: int


class MergeCartRequest(BaseModel):
    """
    Input for:
    sp_merge_guest_cart(p_guest_uuid, p_user_id)
    """
    guest_uuid: str


# alias kept for old code compatibility
class MergeCart(BaseModel):
    guest_uuid: str
    user_id: int


# =====================================================
# CART RESPONSE SCHEMAS
# =====================================================

class CartItemOut(BaseModel):
    id: int
    cart_id: int
    variant_id: int
    quantity: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CartOut(BaseModel):
    id: int
    user_id: Optional[int] = None
    guest_uuid: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CartViewOut(BaseModel):
    """
    Maps to cart_view DB view
    """
    cart_id: int
    user_id: Optional[int] = None
    guest_uuid: Optional[str] = None
    cart_item_id: Optional[int] = None

    product_id: Optional[int] = None
    variant_id: Optional[int] = None

    quantity: Optional[int] = None

    product_name: Optional[str] = None
    product_description: Optional[str] = None
    product_slug: Optional[str] = None

    variant_name: Optional[str] = None
    variant_sku: Optional[str] = None
    size: Optional[str] = None
    stock: Optional[int] = None

    image_url: Optional[str] = None

    price: Optional[Decimal] = None
    customization_total: Optional[Decimal] = None
    total_price: Optional[Decimal] = None
    line_total: Optional[Decimal] = None

    class Config:
        from_attributes = True


# richer response kept from second file
class CartItemResponse(BaseModel):
    id: int
    cart_item_id: int
    cart_id: int

    product_id: int
    variant_id: int

    quantity: int
    price: float
    customization_total: float
    line_total: float

    product_name: str
    product_description: Optional[str] = ""
    product_slug: Optional[str] = ""

    variant_name: Optional[str] = ""
    stock: Optional[int] = 0
    size: Optional[str] = ""
    variant_sku: Optional[str] = ""

    image_url: Optional[str] = ""


class CartSummary(BaseModel):
    total_items: int
    total_quantity: int
    subtotal: float


# =====================================================
# WISHLIST REQUEST SCHEMAS
# =====================================================

class WishlistItemCreate(BaseModel):
    variant_id: int = Field(..., gt=0)


# =====================================================
# WISHLIST RESPONSE SCHEMAS
# =====================================================

class WishlistItemOut(BaseModel):
    id: int
    wishlist_id: int
    variant_id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class WishlistViewOut(BaseModel):
    """
    Maps to wishlist_view DB view
    """
    wishlist_id: int
    user_id: Optional[int] = None
    guest_uuid: Optional[str] = None
    wishlist_item_id: Optional[int] = None

    product_id: Optional[int] = None
    product_name: Optional[str] = None

    variant_id: Optional[int] = None
    variant_name: Optional[str] = None

    price: Optional[Decimal] = None
    image_url: Optional[str] = None

    class Config:
        from_attributes = True