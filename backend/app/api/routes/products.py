from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.db.session import get_db

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("/")
def get_products(db: Session = Depends(get_db)):
    result = db.execute(
        text("""
            SELECT
                p.id,
                p.name,
                p.description,
                COALESCE(pi.image_url, '') AS image_url,
                MIN(pv.price) AS price,

                CASE
                    WHEN LOWER(p.name) LIKE '%women%' THEN 'women'
                    WHEN LOWER(p.name) LIKE '%men%' THEN 'men'
                    ELSE 'unisex'
                END AS gender,

                CASE
                    WHEN LOWER(p.name) LIKE '%apron%' THEN 'Aprons'
                    ELSE 'Scrubs'
                END AS category_name,

                CASE
                    WHEN LOWER(p.name) LIKE '%ecoflex%' THEN 'Ecoflex'
                    ELSE 'Classic'
                END AS fabric

            FROM product p
            LEFT JOIN product_image pi
                ON pi.product_id = p.id
               AND pi.is_primary = TRUE
            LEFT JOIN product_variant pv
                ON pv.product_id = p.id
            GROUP BY p.id, p.name, p.description, pi.image_url
            ORDER BY p.id
        """)
    )

    rows = result.fetchall()

    return [
        {
            "id": row.id,
            "name": row.name,
            "description": row.description,
            "image_url": row.image_url,
            "price": float(row.price) if row.price is not None else 0,
            "gender": row.gender,
            "category_name": row.category_name,
            "fabric": row.fabric
        }
        for row in rows
    ]

@router.get("/{product_id}")
def get_product_details(product_id: int, db: Session = Depends(get_db)):
    product_row = db.execute(
        text("""
            SELECT
                p.id,
                p.name,
                p.description,
                COALESCE(pi.image_url, '') AS image_url
            FROM product p
            LEFT JOIN product_image pi
                ON pi.product_id = p.id
               AND pi.is_primary = TRUE
            WHERE p.id = :product_id
        """),
        {"product_id": product_id}
    ).fetchone()

    if not product_row:
        raise HTTPException(status_code=404, detail="Product not found")

    variant_rows = db.execute(
        text("""
            SELECT
                pv.id AS id,
                pv.product_id,
                pv.variant_name,
                pv.price,
                pv.stock
            FROM product_variant pv
            WHERE pv.product_id = :product_id
            ORDER BY pv.id
        """),
        {"product_id": product_id}
    ).fetchall()

    return {
        "id": product_row.id,
        "name": product_row.name,
        "description": product_row.description,
        "image_url": product_row.image_url,
        "variants": [
            {
                "id": row.id,   # IMPORTANT: real product_variant.id
                "product_id": row.product_id,
                "variant_name": row.variant_name,
                "price": float(row.price),
                "stock": row.stock
            }
            for row in variant_rows
        ]
    }