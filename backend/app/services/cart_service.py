import uuid
from typing import Optional, List, Dict, Any

from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError


# =========================================================
# HELPERS
# =========================================================

def _normalize_uuid(value: Optional[str]) -> Optional[str]:
    if not value:
        return None

    try:
        return str(uuid.UUID(str(value)))
    except Exception:
        raise ValueError("Invalid guest_uuid format")


def _validate_owner(user_id: Optional[int], guest_uuid: Optional[str]):
    if user_id is None and guest_uuid is None:
        raise ValueError("Either user_id or guest_uuid is required")

    if user_id is not None and guest_uuid is not None:
        raise ValueError("Send only user_id or guest_uuid, not both")


def _cart_owner_condition(
    user_id: Optional[int] = None,
    guest_uuid: Optional[str] = None
):
    _validate_owner(user_id, guest_uuid)

    if user_id is not None:
        return "c.user_id = :user_id", {"user_id": user_id}

    guest_uuid = _normalize_uuid(guest_uuid)

    return (
        "c.guest_uuid = CAST(:guest_uuid AS UUID)",
        {"guest_uuid": guest_uuid}
    )


# =========================================================
# GUEST
# =========================================================

def get_or_create_guest(db: Session) -> str:
    guest_uuid = str(uuid.uuid4())

    try:
        db.execute(
            text("""
                INSERT INTO guest (uuid, created_at)
                VALUES (CAST(:guest_uuid AS UUID), NOW())
                ON CONFLICT (uuid) DO NOTHING
            """),
            {"guest_uuid": guest_uuid}
        )

        db.commit()
        return guest_uuid

    except SQLAlchemyError as e:
        db.rollback()
        raise ValueError(f"Guest creation failed: {str(e.orig)}")


# =========================================================
# CART
# =========================================================

def get_or_create_cart(
    db: Session,
    user_id: Optional[int] = None,
    guest_uuid: Optional[str] = None
) -> int:
    _validate_owner(user_id, guest_uuid)

    try:
        # USER CART
        if user_id is not None:
            row = db.execute(
                text("""
                    SELECT id
                    FROM cart
                    WHERE user_id = :user_id
                    ORDER BY id ASC
                    LIMIT 1
                """),
                {"user_id": user_id}
            ).fetchone()

            if row:
                return row[0]

            row = db.execute(
                text("""
                    INSERT INTO cart (
                        user_id,
                        guest_uuid,
                        created_at,
                        updated_at
                    )
                    VALUES (
                        :user_id,
                        NULL,
                        NOW(),
                        NOW()
                    )
                    RETURNING id
                """),
                {"user_id": user_id}
            ).fetchone()

            db.commit()
            return row[0]

        # GUEST CART
        guest_uuid = _normalize_uuid(guest_uuid)

        db.execute(
            text("""
                INSERT INTO guest (uuid, created_at)
                VALUES (CAST(:guest_uuid AS UUID), NOW())
                ON CONFLICT (uuid) DO NOTHING
            """),
            {"guest_uuid": guest_uuid}
        )

        row = db.execute(
            text("""
                SELECT id
                FROM cart
                WHERE guest_uuid = CAST(:guest_uuid AS UUID)
                ORDER BY id ASC
                LIMIT 1
            """),
            {"guest_uuid": guest_uuid}
        ).fetchone()

        if row:
            db.commit()
            return row[0]

        row = db.execute(
            text("""
                INSERT INTO cart (
                    user_id,
                    guest_uuid,
                    created_at,
                    updated_at
                )
                VALUES (
                    NULL,
                    CAST(:guest_uuid AS UUID),
                    NOW(),
                    NOW()
                )
                RETURNING id
            """),
            {"guest_uuid": guest_uuid}
        ).fetchone()

        db.commit()
        return row[0]

    except SQLAlchemyError as e:
        db.rollback()
        raise ValueError(f"Cart creation failed: {str(e.orig)}")


# =========================================================
# ADD TO CART
# =========================================================

def add_to_cart(
    db: Session,
    cart_id: int,
    variant_id: int,
    quantity: int
) -> Dict[str, Any]:

    if not cart_id:
        raise ValueError("cart_id is required")

    if not variant_id:
        raise ValueError("variant_id is required")

    if quantity <= 0:
        raise ValueError("quantity must be greater than 0")

    try:
        # Validate cart exists
        cart = db.execute(
            text("""
                SELECT id
                FROM cart
                WHERE id = :cart_id
                LIMIT 1
            """),
            {"cart_id": cart_id}
        ).fetchone()

        if not cart:
            raise ValueError("Cart not found")

        # Validate variant + product before procedure
        variant = db.execute(
            text("""
                SELECT
                    pv.id,
                    pv.product_id,
                    pv.price,
                    pv.stock,
                    pv.is_deleted,
                    p.is_active,
                    p.is_deleted AS product_deleted
                FROM product_variant pv
                JOIN product p ON p.id = pv.product_id
                WHERE pv.id = :variant_id
                LIMIT 1
            """),
            {"variant_id": variant_id}
        ).mappings().fetchone()

        if not variant:
            raise ValueError("Variant not found")

        if variant["is_deleted"]:
            raise ValueError("Variant is unavailable")

        if not variant["is_active"] or variant["product_deleted"]:
            raise ValueError("Product is unavailable")

        if int(variant["stock"] or 0) < quantity:
            raise ValueError("Insufficient stock")

        # DB procedure inserts product_id + price snapshot
        db.execute(
            text("""
                CALL sp_add_to_cart(
                    :cart_id,
                    :variant_id,
                    :quantity
                )
            """),
            {
                "cart_id": cart_id,
                "variant_id": variant_id,
                "quantity": quantity
            }
        )

        db.commit()

        row = db.execute(
            text("""
                SELECT
                    ci.id,
                    ci.cart_id,
                    ci.product_id,
                    ci.variant_id,
                    ci.quantity,
                    ci.price,
                    COALESCE(ci.customization_total, 0) AS customization_total,
                    p.name AS product_name,
                    COALESCE(pv.variant_name, '') AS variant_name,
                    pv.size,
                    pv.sku AS variant_sku
                FROM cart_item ci
                JOIN product p ON p.id = ci.product_id
                JOIN product_variant pv ON pv.id = ci.variant_id
                WHERE ci.cart_id = :cart_id
                  AND ci.variant_id = :variant_id
                LIMIT 1
            """),
            {
                "cart_id": cart_id,
                "variant_id": variant_id
            }
        ).mappings().fetchone()

        if not row:
            return {"message": "Item added to cart successfully"}

        return {
            "id": row["id"],
            "cart_id": row["cart_id"],
            "product_id": row["product_id"],
            "variant_id": row["variant_id"],
            "quantity": int(row["quantity"] or 0),
            "price": float(row["price"] or 0),
            "customization_total": float(row["customization_total"] or 0),
            "product_name": row["product_name"],
            "variant_name": row["variant_name"],
            "size": row["size"],
            "variant_sku": row["variant_sku"],
        }

    except ValueError:
        db.rollback()
        raise

    except SQLAlchemyError as e:
        db.rollback()
        raise ValueError(f"Add to cart DB error: {str(e.orig)}")


# =========================================================
# GET CART
# =========================================================

def get_cart(
    db: Session,
    user_id: Optional[int] = None,
    guest_uuid: Optional[str] = None
) -> List[Dict[str, Any]]:

    condition, params = _cart_owner_condition(user_id, guest_uuid)

    rows = db.execute(
        text(f"""
            SELECT
                ci.id AS id,
                ci.id AS cart_item_id,
                ci.cart_id AS cart_id,
                ci.product_id AS product_id,
                ci.variant_id AS variant_id,
                ci.quantity AS quantity,

                COALESCE(ci.price, pv.price, 0) AS price,
                COALESCE(ci.customization_total, 0) AS customization_total,

                (
                    (
                        COALESCE(ci.price, pv.price, 0)
                        + COALESCE(ci.customization_total, 0)
                    ) * ci.quantity
                ) AS line_total,

                p.name AS product_name,
                COALESCE(p.description, '') AS product_description,
                COALESCE(p.slug, '') AS product_slug,

                COALESCE(pv.variant_name, '') AS variant_name,
                COALESCE(pv.stock, 0) AS stock,
                COALESCE(pv.size, '') AS size,
                COALESCE(pv.sku, '') AS variant_sku,

                COALESCE(pi.image_url, '') AS image_url

            FROM cart c
            JOIN cart_item ci ON ci.cart_id = c.id
            JOIN product_variant pv
                ON pv.id = ci.variant_id
               AND pv.is_deleted = FALSE
            JOIN product p
                ON p.id = ci.product_id
               AND p.is_active = TRUE
               AND p.is_deleted = FALSE
            LEFT JOIN product_image pi
                ON pi.product_id = p.id
               AND pi.is_primary = TRUE

            WHERE {condition}
            ORDER BY ci.id DESC
        """),
        params
    ).mappings().fetchall()

    return [
        {
            "id": row["id"],
            "cart_item_id": row["cart_item_id"],
            "cart_id": row["cart_id"],
            "product_id": row["product_id"],
            "variant_id": row["variant_id"],
            "quantity": int(row["quantity"] or 0),
            "price": float(row["price"] or 0),
            "customization_total": float(row["customization_total"] or 0),
            "line_total": float(row["line_total"] or 0),
            "product_name": row["product_name"],
            "product_description": row["product_description"],
            "product_slug": row["product_slug"],
            "variant_name": row["variant_name"],
            "stock": int(row["stock"] or 0),
            "size": row["size"],
            "variant_sku": row["variant_sku"],
            "image_url": row["image_url"],
        }
        for row in rows
    ]


def get_cart_summary(
    db: Session,
    user_id: Optional[int] = None,
    guest_uuid: Optional[str] = None
) -> Dict[str, Any]:

    condition, params = _cart_owner_condition(user_id, guest_uuid)

    row = db.execute(
        text(f"""
            SELECT
                COUNT(ci.id) AS total_items,
                COALESCE(SUM(ci.quantity), 0) AS total_quantity,
                COALESCE(
                    SUM(
                        (
                            COALESCE(ci.price, 0)
                            + COALESCE(ci.customization_total, 0)
                        ) * ci.quantity
                    ),
                    0
                ) AS subtotal
            FROM cart c
            LEFT JOIN cart_item ci ON ci.cart_id = c.id
            WHERE {condition}
        """),
        params
    ).mappings().fetchone()

    return {
        "total_items": int(row["total_items"] or 0),
        "total_quantity": int(row["total_quantity"] or 0),
        "subtotal": float(row["subtotal"] or 0),
    }


# =========================================================
# UPDATE CART ITEM
# =========================================================

def update_cart_qty(
    db: Session,
    cart_item_id: int,
    quantity: int
) -> Dict[str, Any]:

    if not cart_item_id:
        raise ValueError("cart_item_id is required")

    if quantity <= 0:
        raise ValueError("quantity must be greater than 0")

    item = db.execute(
        text("""
            SELECT
                ci.id,
                ci.variant_id,
                pv.stock,
                pv.is_deleted,
                p.is_active,
                p.is_deleted AS product_deleted
            FROM cart_item ci
            JOIN product_variant pv ON pv.id = ci.variant_id
            JOIN product p ON p.id = ci.product_id
            WHERE ci.id = :cart_item_id
            LIMIT 1
        """),
        {"cart_item_id": cart_item_id}
    ).mappings().fetchone()

    if not item:
        raise ValueError("Cart item not found")

    if item["is_deleted"]:
        raise ValueError("Variant is unavailable")

    if not item["is_active"] or item["product_deleted"]:
        raise ValueError("Product is unavailable")

    if int(item["stock"] or 0) < quantity:
        raise ValueError("Insufficient stock")

    try:
        db.execute(
            text("""
                UPDATE cart_item
                SET quantity = :quantity,
                    updated_at = NOW()
                WHERE id = :cart_item_id
            """),
            {
                "quantity": quantity,
                "cart_item_id": cart_item_id
            }
        )

        db.commit()

        row = db.execute(
            text("""
                SELECT
                    id,
                    cart_id,
                    product_id,
                    variant_id,
                    quantity,
                    price,
                    COALESCE(customization_total, 0) AS customization_total
                FROM cart_item
                WHERE id = :cart_item_id
            """),
            {"cart_item_id": cart_item_id}
        ).mappings().fetchone()

        return dict(row)

    except SQLAlchemyError as e:
        db.rollback()
        raise ValueError(f"Update cart DB error: {str(e.orig)}")


# =========================================================
# REMOVE CART ITEM
# =========================================================

def remove_from_cart(db: Session, cart_item_id: int) -> Dict[str, Any]:
    if not cart_item_id:
        raise ValueError("cart_item_id is required")

    try:
        row = db.execute(
            text("""
                SELECT id
                FROM cart_item
                WHERE id = :cart_item_id
                LIMIT 1
            """),
            {"cart_item_id": cart_item_id}
        ).fetchone()

        if not row:
            raise ValueError("Cart item not found")

        db.execute(
            text("""
                DELETE FROM cart_item
                WHERE id = :cart_item_id
            """),
            {"cart_item_id": cart_item_id}
        )

        db.commit()

        return {"message": "Item removed from cart successfully"}

    except ValueError:
        db.rollback()
        raise

    except SQLAlchemyError as e:
        db.rollback()
        raise ValueError(f"Remove cart DB error: {str(e.orig)}")


# =========================================================
# CLEAR CART
# =========================================================

def clear_cart(
    db: Session,
    user_id: Optional[int] = None,
    guest_uuid: Optional[str] = None
) -> Dict[str, Any]:

    condition, params = _cart_owner_condition(user_id, guest_uuid)

    try:
        db.execute(
            text(f"""
                DELETE FROM cart_item
                WHERE cart_id IN (
                    SELECT c.id
                    FROM cart c
                    WHERE {condition}
                )
            """),
            params
        )

        db.commit()

        return {"message": "Cart cleared successfully"}

    except SQLAlchemyError as e:
        db.rollback()
        raise ValueError(f"Clear cart DB error: {str(e.orig)}")


# =========================================================
# MERGE GUEST CART INTO USER CART
# =========================================================

def merge_guest_cart(
    db: Session,
    guest_uuid: str,
    user_id: int
) -> Dict[str, Any]:

    if not user_id:
        raise ValueError("user_id is required")

    guest_uuid = _normalize_uuid(guest_uuid)

    if not guest_uuid:
        raise ValueError("guest_uuid is required")

    try:
        guest_cart = db.execute(
            text("""
                SELECT id
                FROM cart
                WHERE guest_uuid = CAST(:guest_uuid AS UUID)
                LIMIT 1
            """),
            {"guest_uuid": guest_uuid}
        ).fetchone()

        if not guest_cart:
            return {"message": "No guest cart found to merge"}

        guest_cart_id = guest_cart[0]
        user_cart_id = get_or_create_cart(db, user_id=user_id)

        if guest_cart_id == user_cart_id:
            return {
                "message": "Guest cart already linked to user cart",
                "user_cart_id": user_cart_id
            }

        db.execute(
            text("""
                INSERT INTO cart_item (
                    cart_id,
                    variant_id,
                    product_id,
                    quantity,
                    price,
                    customization_total,
                    created_at,
                    updated_at
                )
                SELECT
                    :user_cart_id,
                    ci.variant_id,
                    ci.product_id,
                    ci.quantity,
                    ci.price,
                    COALESCE(ci.customization_total, 0),
                    NOW(),
                    NOW()
                FROM cart_item ci
                JOIN product_variant pv
                    ON pv.id = ci.variant_id
                   AND pv.is_deleted = FALSE
                JOIN product p
                    ON p.id = ci.product_id
                   AND p.is_active = TRUE
                   AND p.is_deleted = FALSE
                WHERE ci.cart_id = :guest_cart_id
                ON CONFLICT (cart_id, variant_id)
                DO UPDATE SET
                    quantity = cart_item.quantity + EXCLUDED.quantity,
                    price = EXCLUDED.price,
                    customization_total =
                        COALESCE(cart_item.customization_total, 0)
                        + COALESCE(EXCLUDED.customization_total, 0),
                    updated_at = NOW()
            """),
            {
                "user_cart_id": user_cart_id,
                "guest_cart_id": guest_cart_id
            }
        )

        db.execute(
            text("""
                DELETE FROM cart_item
                WHERE cart_id = :guest_cart_id
            """),
            {"guest_cart_id": guest_cart_id}
        )

        db.execute(
            text("""
                DELETE FROM cart
                WHERE id = :guest_cart_id
            """),
            {"guest_cart_id": guest_cart_id}
        )

        db.commit()

        return {
            "message": "Guest cart merged successfully",
            "user_cart_id": user_cart_id
        }

    except SQLAlchemyError as e:
        db.rollback()
        raise ValueError(f"Merge cart DB error: {str(e.orig)}")


# =========================================================
# OPTIONAL HELPERS
# =========================================================

def get_cart_by_cart_id(
    db: Session,
    cart_id: int
) -> List[Dict[str, Any]]:

    rows = db.execute(
        text("""
            SELECT
                ci.id AS id,
                ci.cart_id AS cart_id,
                ci.product_id AS product_id,
                ci.variant_id AS variant_id,
                ci.quantity AS quantity,
                COALESCE(ci.price, pv.price, 0) AS price,
                COALESCE(ci.customization_total, 0) AS customization_total,
                (
                    (
                        COALESCE(ci.price, pv.price, 0)
                        + COALESCE(ci.customization_total, 0)
                    ) * ci.quantity
                ) AS line_total,
                p.name AS product_name,
                COALESCE(pv.variant_name, '') AS variant_name,
                COALESCE(pi.image_url, '') AS image_url
            FROM cart_item ci
            JOIN product_variant pv
                ON pv.id = ci.variant_id
               AND pv.is_deleted = FALSE
            JOIN product p
                ON p.id = ci.product_id
               AND p.is_active = TRUE
               AND p.is_deleted = FALSE
            LEFT JOIN product_image pi
                ON pi.product_id = p.id
               AND pi.is_primary = TRUE
            WHERE ci.cart_id = :cart_id
            ORDER BY ci.id DESC
        """),
        {"cart_id": cart_id}
    ).mappings().fetchall()

    return [
        {
            "id": row["id"],
            "cart_id": row["cart_id"],
            "product_id": row["product_id"],
            "variant_id": row["variant_id"],
            "quantity": int(row["quantity"] or 0),
            "price": float(row["price"] or 0),
            "customization_total": float(row["customization_total"] or 0),
            "line_total": float(row["line_total"] or 0),
            "product_name": row["product_name"],
            "variant_name": row["variant_name"],
            "image_url": row["image_url"],
        }
        for row in rows
    ]


def cart_item_exists(db: Session, cart_item_id: int) -> bool:
    row = db.execute(
        text("""
            SELECT 1
            FROM cart_item
            WHERE id = :cart_item_id
            LIMIT 1
        """),
        {"cart_item_id": cart_item_id}
    ).fetchone()

    return row is not None