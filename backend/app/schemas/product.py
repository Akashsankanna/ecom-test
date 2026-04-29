from pydantic import BaseModel, Field, validator
from typing import Optional, List, Literal
from decimal import Decimal


# =====================================================
# CATEGORY
# =====================================================

class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None
    is_active: Optional[bool] = True


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class CategoryOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True


# =====================================================
# COLOR
# =====================================================

class ColorCreate(BaseModel):
    name: str
    hex_code: Optional[str] = None
    is_active: Optional[bool] = True


class ColorOut(BaseModel):
    id: int
    name: str
    hex_code: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True


# =====================================================
# PRODUCT IMAGE
# =====================================================

class ProductImageCreate(BaseModel):
    image_url: str
    image_name: Optional[str] = None
    is_primary: Optional[bool] = False
    variant_id: Optional[int] = None


class ProductImageOut(BaseModel):
    id: int
    image_url: str
    is_primary: bool
    image_name: Optional[str] = None
    variant_id: Optional[int] = None

    class Config:
        from_attributes = True


# =====================================================
# PRODUCT VARIANT
# =====================================================

class VariantCreate(BaseModel):
    variant_name: Optional[str] = None
    price: Decimal
    stock: Optional[int] = 0
    sku: Optional[str] = None

    color: Optional[str] = None
    color_id: Optional[int] = None

    size: Optional[str] = None
    low_stock_threshold: Optional[int] = 5


class VariantUpdate(BaseModel):
    variant_name: Optional[str] = None
    price: Optional[Decimal] = None
    stock: Optional[int] = None
    sku: Optional[str] = None

    color: Optional[str] = None
    color_id: Optional[int] = None

    size: Optional[str] = None
    low_stock_threshold: Optional[int] = None

    is_deleted: Optional[bool] = None


class VariantOut(BaseModel):
    id: int
    product_id: int

    variant_name: Optional[str] = None

    price: Decimal
    stock: int

    sku: Optional[str] = None

    color: Optional[str] = None
    color_id: Optional[int] = None

    size: Optional[str] = None

    reserved_stock: int
    low_stock_threshold: int

    is_deleted: bool

    class Config:
        from_attributes = True


# =====================================================
# PRODUCT
# Allowed gender values mirror the DB CHECK constraint:
#   chk_gender: gender IN ('men', 'women', 'unisex')
# The admin UI also uses 'all' as a display alias for
# 'unisex', so we accept it and normalise on the way in.
# =====================================================

GenderType = Literal["men", "women", "unisex", "all"]

def _normalise_gender(v: Optional[str]) -> Optional[str]:
    """Map 'all' → 'unisex' and lowercase everything else."""
    if v is None:
        return "men"          # safe default matching DB constraint
    v = v.strip().lower()
    return "unisex" if v == "all" else v


class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    sku: str

    category_id: int

    # ── gender is now REQUIRED on create ──────────────
    # Accept 'men' | 'women' | 'unisex' | 'all'
    # 'all' is normalised to 'unisex' before hitting the DB.
    gender: Optional[GenderType] = "men"

    is_active: Optional[bool] = True

    details_and_fit: Optional[str] = None
    fabric_and_care: Optional[str] = None
    return_and_exchange: Optional[str] = None

    tax_rate_id: Optional[int] = None

    # slug auto-generated in DB
    # bestseller managed separately

    @validator("gender", pre=True, always=True)
    def normalise_gender(cls, v):
        return _normalise_gender(v)


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    sku: Optional[str] = None

    category_id: Optional[int] = None

    gender: Optional[GenderType] = None

    is_active: Optional[bool] = None

    details_and_fit: Optional[str] = None
    fabric_and_care: Optional[str] = None
    return_and_exchange: Optional[str] = None

    tax_rate_id: Optional[int] = None

    @validator("gender", pre=True, always=True)
    def normalise_gender(cls, v):
        if v is None:
            return None   # no-op on partial update
        return _normalise_gender(v)


class ProductOut(BaseModel):
    id: int

    name: str
    description: Optional[str] = None

    sku: str
    slug: Optional[str] = None

    category_id: Optional[int] = None

    # ── gender exposed in every response ──────────────
    gender: Optional[str] = "men"

    is_active: bool
    is_deleted: bool

    is_bestseller: bool = False

    details_and_fit: Optional[str] = None
    fabric_and_care: Optional[str] = None
    return_and_exchange: Optional[str] = None

    class Config:
        from_attributes = True


class ProductDetailOut(ProductOut):
    variants: List[VariantOut] = Field(default_factory=list)
    images: List[ProductImageOut] = Field(default_factory=list)