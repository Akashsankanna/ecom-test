"""
Cart & Wishlist schemas — cart, cart_item, wishlist, wishlist_item tables.
Uses: sp_add_to_cart, sp_merge_guest_cart, sp_add_to_wishlist,
      sp_remove_from_wishlist, sp_merge_wishlist, sp_checkout.
Import from: app.schemas.cart
"""
from pydantic import BaseModel, field_validator
from typing import Optional, List
from decimal import Decimal
from datetime import datetime
import uuid


class CartItemCreate(BaseModel):
    variant_id: int
    quantity: int

    @field_validator("quantity")
    @classmethod
    def qty_positive(cls, v):
        if v <= 0:
            raise ValueError("Quantity must be > 0")
        return v


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
    """Maps to cart_view DB view."""
    cart_id: int
    user_id: Optional[int] = None
    guest_uuid: Optional[str] = None
    cart_item_id: Optional[int] = None
    variant_id: Optional[int] = None
    quantity: Optional[int] = None
    variant_name: Optional[str] = None
    price: Optional[Decimal] = None
    total_price: Optional[Decimal] = None
    product_name: Optional[str] = None

    class Config:
        from_attributes = True


class CheckoutRequest(BaseModel):
    """Input for sp_checkout(p_cart_id, p_address_id)."""
    cart_id: int
    address_id: int


class MergeCartRequest(BaseModel):
    """Input for sp_merge_guest_cart(p_guest_uuid, p_user_id)."""
    guest_uuid: str


# ─── Wishlist ─────────────────────────────────────────────────────────────────

class WishlistItemCreate(BaseModel):
    variant_id: int


class WishlistItemOut(BaseModel):
    id: int
    wishlist_id: int
    variant_id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class WishlistViewOut(BaseModel):
    """Maps to wishlist_view DB view."""
    wishlist_id: int
    user_id: Optional[int] = None
    guest_uuid: Optional[str] = None
    wishlist_item_id: Optional[int] = None
    variant_id: Optional[int] = None
    variant_name: Optional[str] = None
    price: Optional[Decimal] = None
    product_name: Optional[str] = None
    image_url: Optional[str] = None

    class Config:
        from_attributes = True