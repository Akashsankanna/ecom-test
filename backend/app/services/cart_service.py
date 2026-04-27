import uuid
from typing import Optional, List, Dict, Any

from sqlalchemy.orm import Session
from sqlalchemy import text


# =========================================================
# HELPERS
# =========================================================

def _normalize_uuid(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    try:
        return str(uuid.UUID(str(value)))
    except (ValueError, TypeError):
        raise ValueError("Invalid guest_uuid format")


def _cart_owner_condition(user_id: Optional[int] = None, guest_uuid: Optional[str] = None):
    if user_id:
        return "c.user_id = :identifier", {"identifier": user_id}

    guest_uuid = _normalize_uuid(guest_uuid)
    if guest_uuid:
        return "c.guest_uuid = CAST(:identifier AS UUID)", {"identifier": guest_uuid}

    raise ValueError("Either user_id or guest_uuid is required")


# =========================================================
# GUEST
# =========================================================

def get_or_create_guest(db: Session) -> str:
    """
    Creates a new guest UUID in guest table and returns it.
    guest.uuid is UUID type in new DB.
    """
    new_uuid = str(uuid.uuid4())

    db.execute(
        text("""
            INSERT INTO guest (uuid)
            VALUES (CAST(:uuid AS UUID))
            ON CONFLICT (uuid) DO NOTHING
        """),
        {"uuid": new_uuid}
    )
    db.commit()
    return new_uuid


# =========================================================
# CART
# =========================================================

def get_or_create_cart(
    db: Session,
    user_id: Optional[int] = None,
    guest_uuid: Optional[str] = None
) -> int:
    """
    Get existing cart or create a new one.
    Supports logged-in user cart and guest cart.
    """
    if user_id:
        row = db.execute(
            text("""
                SELECT id
                FROM cart
                WHERE user_id = :uid
                ORDER BY id ASC
                LIMIT 1
            """),
            {"uid": user_id}
        ).fetchone()

        if row:
            return row[0]

        row = db.execute(
            text("""
                INSERT INTO cart (user_id, created_at)
                VALUES (:uid, CURRENT_TIMESTAMP)
                RETURNING id
            """),
            {"uid": user_id}
        ).fetchone()
        db.commit()
        return row[0]

    guest_uuid = _normalize_uuid(guest_uuid)
    if guest_uuid:
        # ensure guest exists
        db.execute(
            text("""
                INSERT INTO guest (uuid)
                VALUES (CAST(:uuid AS UUID))
                ON CONFLICT (uuid) DO NOTHING
            """),
            {"uuid": guest_uuid}
        )

        row = db.execute(
            text("""
                SELECT id
                FROM cart
                WHERE guest_uuid = CAST(:guuid AS UUID)
                ORDER BY id ASC
                LIMIT 1
            """),
            {"guuid": guest_uuid}
        ).fetchone()

        if row:
            db.commit()
            return row[0]

        row = db.execute(
            text("""
                INSERT INTO cart (guest_uuid, created_at)
                VALUES (CAST(:guuid AS UUID), CURRENT_TIMESTAMP)
                RETURNING id
            """),
            {"guuid": guest_uuid}
        ).fetchone()
        db.commit()
        return row[0]

    raise ValueError("Either user_id or guest_uuid is required")


# =========================================================
# ADD TO CART
# =========================================================

def add_to_cart(db: Session, cart_id: int, variant_id: int, quantity: int) -> Dict[str, Any]:
    """
    Add item to cart using DB procedure sp_add_to_cart.
    New DB procedure already:
    - validates quantity
    - validates variant
    - validates product active/deleted
    - stores product_id and price snapshot
    - upserts on (cart_id, variant_id)
    """
    if not cart_id:
        raise ValueError("cart_id is required")
    if not variant_id:
        raise ValueError("variant_id is required")
    if not quantity or quantity <= 0:
        raise ValueError("quantity must be greater than 0")

    db.execute(
        text("CALL sp_add_to_cart(:cart_id, :variant_id, :quantity)"),
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
                ci.customization_total
            FROM cart_item ci
            WHERE ci.cart_id = :cart_id
              AND ci.variant_id = :variant_id
            LIMIT 1
        """),
        {"cart_id": cart_id, "variant_id": variant_id}
    ).mappings().fetchone()

    return dict(row) if row else {
        "message": "Item added to cart successfully"
    }


# =========================================================
# GET CART
# =========================================================

def get_cart(
    db: Session,
    user_id: Optional[int] = None,
    guest_uuid: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Returns cart items with product + variant details.
    Uses cart_item.price as snapshot price from cart table,
    not always live product_variant price.
    """
    condition, params = _cart_owner_condition(user_id=user_id, guest_uuid=guest_uuid)

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
                    (COALESCE(ci.price, pv.price, 0) + COALESCE(ci.customization_total, 0))
                    * ci.quantity
                ) AS line_total,

                p.name AS product_name,
                p.description AS product_description,
                p.slug AS product_slug,

                COALESCE(pv.variant_name, '') AS variant_name,
                pv.stock AS stock,
                pv.size AS size,
                pv.sku AS variant_sku,

                COALESCE(pi.image_url, '') AS image_url

            FROM cart c
            JOIN cart_item ci
              ON ci.cart_id = c.id

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

            "product_name": row["product_name"] or "Product",
            "product_description": row["product_description"] or "",
            "product_slug": row["product_slug"] or "",

            "variant_name": row["variant_name"] or "",
            "stock": int(row["stock"] or 0) if row["stock"] is not None else 0,
            "size": row["size"] or "",
            "variant_sku": row["variant_sku"] or "",

            "image_url": row["image_url"] or "",
        }
        for row in rows
    ]


def get_cart_summary(
    db: Session,
    user_id: Optional[int] = None,
    guest_uuid: Optional[str] = None
) -> Dict[str, Any]:
    """
    Cart totals summary.
    """
    condition, params = _cart_owner_condition(user_id=user_id, guest_uuid=guest_uuid)

    row = db.execute(
        text(f"""
            SELECT
                COUNT(ci.id) AS total_items,
                COALESCE(SUM(ci.quantity), 0) AS total_quantity,
                COALESCE(SUM((COALESCE(ci.price, 0) + COALESCE(ci.customization_total, 0)) * ci.quantity), 0) AS subtotal
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
# UPDATE CART ITEM QUANTITY
# =========================================================

def update_cart_qty(db: Session, cart_item_id: int, quantity: int) -> Dict[str, Any]:
    """
    Update quantity of a cart item.
    Keeps price snapshot as-is.
    """
    if not cart_item_id:
        raise ValueError("cart_item_id is required")

    if quantity <= 0:
        raise ValueError("quantity must be greater than 0")

    # validate item + variant availability
    item = db.execute(
        text("""
            SELECT
                ci.id,
                ci.variant_id,
                pv.stock,
                pv.is_deleted,
                p.is_active,
                p.is_deleted AS product_is_deleted
            FROM cart_item ci
            JOIN product_variant pv ON pv.id = ci.variant_id
            JOIN product p ON p.id = ci.product_id
            WHERE ci.id = :id
            LIMIT 1
        """),
        {"id": cart_item_id}
    ).mappings().fetchone()

    if not item:
        raise ValueError("Cart item not found")

    if item["is_deleted"]:
        raise ValueError("Variant is unavailable")

    if not item["is_active"] or item["product_is_deleted"]:
        raise ValueError("Product is unavailable")

    db.execute(
        text("""
            UPDATE cart_item
            SET quantity = :qty,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = :id
        """),
        {"qty": quantity, "id": cart_item_id}
    )
    db.commit()

    updated = db.execute(
        text("""
            SELECT
                id,
                cart_id,
                product_id,
                variant_id,
                quantity,
                price,
                customization_total
            FROM cart_item
            WHERE id = :id
        """),
        {"id": cart_item_id}
    ).mappings().fetchone()

    return dict(updated) if updated else {"message": "Cart updated successfully"}


# =========================================================
# REMOVE CART ITEM
# =========================================================

def remove_from_cart(db: Session, cart_item_id: int) -> Dict[str, Any]:
    """
    Remove item from cart.
    """
    if not cart_item_id:
        raise ValueError("cart_item_id is required")

    row = db.execute(
        text("""
            SELECT id
            FROM cart_item
            WHERE id = :id
        """),
        {"id": cart_item_id}
    ).fetchone()

    if not row:
        raise ValueError("Cart item not found")

    db.execute(
        text("DELETE FROM cart_item WHERE id = :id"),
        {"id": cart_item_id}
    )
    db.commit()

    return {"message": "Item removed from cart successfully"}


def clear_cart(
    db: Session,
    user_id: Optional[int] = None,
    guest_uuid: Optional[str] = None
) -> Dict[str, Any]:
    """
    Remove all items from a user's or guest's cart.
    """
    condition, params = _cart_owner_condition(user_id=user_id, guest_uuid=guest_uuid)

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


# =========================================================
# MERGE GUEST CART INTO USER CART
# =========================================================

def merge_guest_cart(db: Session, guest_uuid: str, user_id: int) -> Dict[str, Any]:
    """
    Merge guest cart into user cart after login.

    New DB wise:
    - guest_uuid is UUID
    - cart_item contains product_id, price, customization_total
    - active/deleted product and variant are respected
    """
    if not user_id:
        raise ValueError("user_id is required")

    guest_uuid = _normalize_uuid(guest_uuid)
    if not guest_uuid:
        raise ValueError("guest_uuid is required")

    guest_cart = db.execute(
        text("""
            SELECT id
            FROM cart
            WHERE guest_uuid = CAST(:guuid AS UUID)
            LIMIT 1
        """),
        {"guuid": guest_uuid}
    ).fetchone()

    if not guest_cart:
        return {"message": "No guest cart found to merge"}

    guest_cart_id = guest_cart[0]
    user_cart_id = get_or_create_cart(db, user_id=user_id)

    if guest_cart_id == user_cart_id:
        return {"message": "Guest cart already linked to user cart"}

    # merge cart items
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
                CURRENT_TIMESTAMP,
                CURRENT_TIMESTAMP
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
                customization_total = cart_item.customization_total + EXCLUDED.customization_total,
                updated_at = CURRENT_TIMESTAMP
        """),
        {
            "user_cart_id": user_cart_id,
            "guest_cart_id": guest_cart_id
        }
    )

    # delete guest cart items
    db.execute(
        text("DELETE FROM cart_item WHERE cart_id = :guest_cart_id"),
        {"guest_cart_id": guest_cart_id}
    )

    # delete guest cart
    db.execute(
        text("DELETE FROM cart WHERE id = :guest_cart_id"),
        {"guest_cart_id": guest_cart_id}
    )

    db.commit()

    return {
        "message": "Guest cart merged successfully",
        "user_cart_id": user_cart_id
    }


# =========================================================
# OPTIONAL HELPERS
# =========================================================

def get_cart_by_cart_id(db: Session, cart_id: int) -> List[Dict[str, Any]]:
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
                    (COALESCE(ci.price, pv.price, 0) + COALESCE(ci.customization_total, 0))
                    * ci.quantity
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
            "product_name": row["product_name"] or "Product",
            "variant_name": row["variant_name"] or "",
            "image_url": row["image_url"] or "",
        }
        for row in rows
    ]


def cart_item_exists(db: Session, cart_item_id: int) -> bool:
    row = db.execute(
        text("SELECT 1 FROM cart_item WHERE id = :id LIMIT 1"),
        {"id": cart_item_id}
    ).fetchone()
    return row is not None