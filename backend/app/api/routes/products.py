from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional

from app.db.session import get_db

router = APIRouter(prefix="/products", tags=["Products"])


def to_float(value):
    return float(value) if value is not None else 0


@router.get("/")
def get_products(
    gender: Optional[str] = Query(None),   # men / women / unisex
    db: Session = Depends(get_db)
):
    products_sql = """
        SELECT
            p.id AS product_id,
            p.name,
            p.description,
            p.sku,
            p.slug,
            p.gender,
            p.is_bestseller,
            cat.name AS category_name,
            COALESCE(primary_img.image_url, '') AS image_url
        FROM product p
        LEFT JOIN category cat ON cat.id = p.category_id
        LEFT JOIN LATERAL (
            SELECT pi.image_url
            FROM product_image pi
            WHERE pi.product_id = p.id
            ORDER BY pi.is_primary DESC, pi.id ASC
            LIMIT 1
        ) primary_img ON TRUE
        WHERE p.is_deleted = FALSE
          AND p.is_active = TRUE
          AND (:gender IS NULL OR LOWER(p.gender) = LOWER(:gender))
        ORDER BY p.id
    """

    product_rows = db.execute(text(products_sql), {"gender": gender}).fetchall()

    product_ids = [r.product_id for r in product_rows]
    if not product_ids:
        return []

    variants_sql = """
        SELECT
            pv.id AS variant_id,
            pv.product_id,
            pv.variant_name,
            pv.sku,
            pv.size,
            pv.price,
            pv.stock,
            pv.reserved_stock,
            pv.low_stock_threshold,
            c.id AS color_id,
            c.name AS color_name,
            c.hex_code,
            COALESCE(variant_img.image_url, product_img.image_url, '') AS image_url
        FROM product_variant pv
        LEFT JOIN color c ON c.id = pv.color_id
        LEFT JOIN LATERAL (
            SELECT pi.image_url
            FROM product_image pi
            WHERE pi.variant_id = pv.id
            ORDER BY pi.is_primary DESC, pi.id ASC
            LIMIT 1
        ) variant_img ON TRUE
        LEFT JOIN LATERAL (
            SELECT pi.image_url
            FROM product_image pi
            WHERE pi.product_id = pv.product_id
            ORDER BY pi.is_primary DESC, pi.id ASC
            LIMIT 1
        ) product_img ON TRUE
        WHERE pv.product_id = ANY(:product_ids)
          AND pv.is_deleted = FALSE
        ORDER BY pv.product_id, pv.id
    """

    variant_rows = db.execute(
        text(variants_sql),
        {"product_ids": product_ids}
    ).fetchall()

    variants_by_product = {}
    for v in variant_rows:
        variant_obj = {
            "id": v.variant_id,
            "variant_id": v.variant_id,
            "product_id": v.product_id,
            "variant_name": v.variant_name,
            "sku": v.sku,

            "size": v.size,
            "color_id": v.color_id,
            "color": v.color_name,
            "color_name": v.color_name,
            "hex_code": v.hex_code,

            "price": to_float(v.price),
            "stock": v.stock,
            "reserved_stock": v.reserved_stock,
            "low_stock_threshold": v.low_stock_threshold,

            "image_url": v.image_url,
            "image": v.image_url,
        }

        variants_by_product.setdefault(v.product_id, []).append(variant_obj)

    result = []

    for r in product_rows:
        variants = variants_by_product.get(r.product_id, [])
        default_variant = variants[0] if variants else None

        sizes = sorted({
            v["size"] for v in variants
            if v["size"] is not None
        })

        colors_map = {}
        for v in variants:
            if v["color_id"]:
                colors_map[v["color_id"]] = {
                    "color_id": v["color_id"],
                    "color": v["color"],
                    "color_name": v["color_name"],
                    "hex_code": v["hex_code"],
                }

        result.append({
            "id": r.product_id,
            "product_id": r.product_id,
            "db_product_id": r.product_id,

            "variant_id": default_variant["variant_id"] if default_variant else None,
            "default_variant_id": default_variant["variant_id"] if default_variant else None,

            "color_id": default_variant["color_id"] if default_variant else None,
            "color": default_variant["color"] if default_variant else None,
            "color_name": default_variant["color_name"] if default_variant else None,
            "size": default_variant["size"] if default_variant else None,

            "name": r.name,
            "title": r.name,
            "description": r.description,
            "sku": r.sku,
            "slug": r.slug,

            "image_url": default_variant["image_url"] if default_variant and default_variant["image_url"] else r.image_url,
            "image": default_variant["image_url"] if default_variant and default_variant["image_url"] else r.image_url,

            "price": default_variant["price"] if default_variant else 0,
            "category_name": r.category_name,
            "gender": r.gender or "unisex",

            "fabric": "Ecoflex" if "ecoflex" in (r.name or "").lower() else "Classic",
            "is_bestseller": r.is_bestseller,

            "variant_count": len(variants),
            "sizes": sizes,
            "colors": list(colors_map.values()),
            "variants": variants,
        })

    return result


@router.get("/{product_id}")
def get_product_details(product_id: int, db: Session = Depends(get_db)):
    product = db.execute(text("""
        SELECT
            p.id,
            p.name,
            p.description,
            p.sku,
            p.slug,
            p.gender,
            p.details_and_fit,
            p.fabric_and_care,
            p.return_and_exchange,
            p.is_bestseller,
            cat.name AS category_name,
            COALESCE(primary_img.image_url, '') AS image_url
        FROM product p
        LEFT JOIN category cat ON cat.id = p.category_id
        LEFT JOIN LATERAL (
            SELECT pi.image_url
            FROM product_image pi
            WHERE pi.product_id = p.id
            ORDER BY pi.is_primary DESC, pi.id ASC
            LIMIT 1
        ) primary_img ON TRUE
        WHERE p.id = :product_id
          AND p.is_deleted = FALSE
          AND p.is_active = TRUE
    """), {"product_id": product_id}).fetchone()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    variants = db.execute(text("""
        SELECT
            pv.id AS variant_id,
            pv.product_id,
            pv.variant_name,
            pv.sku,
            pv.size,
            pv.price,
            pv.stock,
            pv.reserved_stock,
            pv.low_stock_threshold,
            c.id AS color_id,
            c.name AS color_name,
            c.hex_code,
            COALESCE(variant_img.image_url, product_img.image_url, '') AS image_url
        FROM product_variant pv
        LEFT JOIN color c ON c.id = pv.color_id
        LEFT JOIN LATERAL (
            SELECT pi.image_url
            FROM product_image pi
            WHERE pi.variant_id = pv.id
            ORDER BY pi.is_primary DESC, pi.id ASC
            LIMIT 1
        ) variant_img ON TRUE
        LEFT JOIN LATERAL (
            SELECT pi.image_url
            FROM product_image pi
            WHERE pi.product_id = pv.product_id
            ORDER BY pi.is_primary DESC, pi.id ASC
            LIMIT 1
        ) product_img ON TRUE
        WHERE pv.product_id = :product_id
          AND pv.is_deleted = FALSE
        ORDER BY pv.id
    """), {"product_id": product_id}).fetchall()

    images = db.execute(text("""
        SELECT
            id,
            product_id,
            variant_id,
            image_url,
            is_primary,
            image_name,
            alt_text
        FROM product_image
        WHERE product_id = :product_id
        ORDER BY is_primary DESC, id ASC
    """), {"product_id": product_id}).fetchall()

    variant_list = [
        {
            "id": v.variant_id,
            "variant_id": v.variant_id,
            "product_id": v.product_id,
            "variant_name": v.variant_name,
            "sku": v.sku,

            "size": v.size,
            "color_id": v.color_id,
            "color": v.color_name,
            "color_name": v.color_name,
            "hex_code": v.hex_code,

            "price": to_float(v.price),
            "stock": v.stock,
            "reserved_stock": v.reserved_stock,
            "low_stock_threshold": v.low_stock_threshold,

            "image_url": v.image_url,
            "image": v.image_url,
        }
        for v in variants
    ]

    default_variant = variant_list[0] if variant_list else None

    return {
        "id": product.id,
        "product_id": product.id,
        "db_product_id": product.id,

        "variant_id": default_variant["variant_id"] if default_variant else None,
        "default_variant_id": default_variant["variant_id"] if default_variant else None,

        "color_id": default_variant["color_id"] if default_variant else None,
        "color": default_variant["color"] if default_variant else None,
        "size": default_variant["size"] if default_variant else None,

        "name": product.name,
        "title": product.name,
        "description": product.description,
        "sku": product.sku,
        "slug": product.slug,
        "gender": product.gender or "unisex",

        "image_url": product.image_url,
        "image": product.image_url,

        "category_name": product.category_name,
        "fabric": "Ecoflex" if "ecoflex" in (product.name or "").lower() else "Classic",

        "details_and_fit": product.details_and_fit,
        "fabric_and_care": product.fabric_and_care,
        "return_and_exchange": product.return_and_exchange,
        "is_bestseller": product.is_bestseller,

        "images": [
            {
                "id": img.id,
                "product_id": img.product_id,
                "variant_id": img.variant_id,
                "image_url": img.image_url,
                "image": img.image_url,
                "is_primary": img.is_primary,
                "image_name": img.image_name,
                "alt_text": img.alt_text,
            }
            for img in images
        ],

        "sizes": sorted({
            v["size"] for v in variant_list
            if v["size"] is not None
        }),

        "colors": list({
            v["color_id"]: {
                "color_id": v["color_id"],
                "color": v["color"],
                "color_name": v["color_name"],
                "hex_code": v["hex_code"],
            }
            for v in variant_list
            if v["color_id"]
        }.values()),

        "variants": variant_list,
    }