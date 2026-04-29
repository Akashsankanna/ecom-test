from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import text

from app.db.session import get_db
from app.core.dependencies import get_current_user, require_admin
from app.schemas.product import (
    ProductCreate, ProductUpdate,
    VariantCreate, VariantUpdate,
    CategoryCreate, CategoryUpdate,
    ColorCreate, ProductImageCreate,
    ProductOut, ProductDetailOut, VariantOut,
    CategoryOut, ColorOut, ProductImageOut
)
from app.services.product_service import ProductService

router = APIRouter(prefix="/admin/products", tags=["Admin - Products"])


# ════════════════════════════════════════════════════════════
# CATEGORIES
# ════════════════════════════════════════════════════════════

@router.get("/categories", response_model=list[CategoryOut])
def get_categories(
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    return ProductService.get_all_categories(db)


@router.post("/categories", response_model=CategoryOut)
def create_category(
    data: CategoryCreate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    return ProductService.create_category(db, data)


@router.put("/categories/{category_id}", response_model=CategoryOut)
def update_category(
    category_id: int,
    data: CategoryUpdate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    return ProductService.update_category(db, category_id, data)


@router.delete("/categories/{category_id}")
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    return ProductService.delete_category(db, category_id)


# ════════════════════════════════════════════════════════════
# COLORS
# ════════════════════════════════════════════════════════════

@router.get("/colors", response_model=list[ColorOut])
def get_colors(db: Session = Depends(get_db)):
    return ProductService.get_all_colors(db)


@router.post("/colors", response_model=ColorOut)
def create_color(
    data: ColorCreate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    return ProductService.create_color(db, data)


# ════════════════════════════════════════════════════════════
# PRODUCTS
# ════════════════════════════════════════════════════════════

@router.post("/", response_model=ProductOut)
def create_product(
    data: ProductCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    return ProductService.create_product(db, data, user.id)


@router.get("/", response_model=list[ProductOut])
def get_products(
    category_id: Optional[int] = Query(None),
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    return ProductService.get_products(db, category_id, is_active)


@router.get("/low-stock")
def get_low_stock(
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    return ProductService.get_low_stock(db)


@router.get("/{product_id}")
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    product, variants, images = ProductService.get_product(db, product_id)

    return {
        "id": product.id,
        "name": product.name,
        "description": product.description,
        "sku": product.sku,
        "category_id": product.category_id,
        "is_active": product.is_active,
        "is_deleted": product.is_deleted,
        "gender": getattr(product, "gender", "men"),   # ← ADD THIS

        "details_and_fit": product.details_and_fit,
        "fabric_and_care": product.fabric_and_care,
        "return_and_exchange": product.return_and_exchange,

        "variants": [
            {
                "id": v.id,
                "variant_name": v.variant_name,
                "price": float(v.price),
                "stock": v.stock,
                "sku": v.sku,

                # UI compatibility kept
                "color": None,

                "color_id": v.color_id,
                "size": v.size,
                "reserved_stock": v.reserved_stock,
                "low_stock_threshold": v.low_stock_threshold,
            }
            for v in variants
        ],

        "images": [
            {
                "id": img.id,
                "image_url": img.image_url,
                "is_primary": img.is_primary,
                "image_name": img.image_name,

                # DB33 support
                "variant_id": getattr(img, "variant_id", None)
            }
            for img in images
        ]
    }


@router.put("/{product_id}", response_model=ProductOut)
def update_product(
    product_id: int,
    data: ProductUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    return ProductService.update_product(db, product_id, data, user.id)


@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    return ProductService.delete_product(db, product_id)


# ════════════════════════════════════════════════════════════
# VARIANTS
# ════════════════════════════════════════════════════════════

@router.post("/{product_id}/variants", response_model=VariantOut)
def create_variant(
    product_id: int,
    data: VariantCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    return ProductService.create_variant(db, product_id, data, user.id)


@router.get("/{product_id}/variants", response_model=list[VariantOut])
def get_variants(
    product_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    return ProductService.get_variants(db, product_id)


@router.put("/variants/{variant_id}", response_model=VariantOut)
def update_variant(
    variant_id: int,
    data: VariantUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    return ProductService.update_variant(db, variant_id, data, user.id)


@router.delete("/variants/{variant_id}")
def delete_variant(
    variant_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    return ProductService.delete_variant(db, variant_id)


# ════════════════════════════════════════════════════════════
# IMAGES
# ════════════════════════════════════════════════════════════

@router.post("/{product_id}/images")
def add_image(
    product_id: int,
    data: ProductImageCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    return ProductService.add_image(db, product_id, data)


@router.delete("/images/{image_id}")
def delete_image(
    image_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    return ProductService.delete_image(db, image_id)


# ════════════════════════════════════════════════════════════
# BESTSELLER
# ════════════════════════════════════════════════════════════

@router.post(
    "/{product_id}/bestseller",
    summary="Mark/unmark product as bestseller (new in ecomdb21)",
)
def toggle_bestseller(
    product_id: int,
    is_bestseller: bool = True,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """
    Sets is_bestseller flag on the product.
    Records bestseller_marked_at and bestseller_marked_by.
    """
    product = ProductService.toggle_bestseller(
        db,
        product_id,
        is_bestseller,
        user.id
    )

    return {
        "message": f"Product {product_id} bestseller={'enabled' if is_bestseller else 'disabled'}",
        "product_id": product.id,
        "name": product.name,
        "is_bestseller": product.is_bestseller,
        "bestseller_marked_at": product.bestseller_marked_at,
    }


# ════════════════════════════════════════════════════════════
# ACTIVE PRODUCTS VIEW
# ════════════════════════════════════════════════════════════

@router.get("/view/active", summary="Active products view — uses v_active_products DB view")
def get_active_products_view(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    return ProductService.get_active_products_view(db)