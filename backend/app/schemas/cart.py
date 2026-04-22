from pydantic import BaseModel, Field
from typing import Optional


# ==========================
# ADD TO CART
# ==========================
class AddToCart(BaseModel):
    variant_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0)

    # optional (future use if customization added)
    customization_total: Optional[float] = 0.0


# ==========================
# UPDATE CART
# ==========================
class UpdateCartItem(BaseModel):
    cart_item_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0)


# ==========================
# REMOVE CART ITEM
# ==========================
class RemoveCartItem(BaseModel):
    cart_item_id: int = Field(..., gt=0)


# ==========================
# CART RESPONSE ITEM
# ==========================
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


# ==========================
# CART SUMMARY
# ==========================
class CartSummary(BaseModel):
    total_items: int
    total_quantity: int
    subtotal: float



# MERGE CART

class MergeCart(BaseModel):
    guest_uuid: str
    user_id: int