from sqlalchemy.orm import Session
from sqlalchemy import text


def get_wishlist(db: Session, user_id=None, guest_uuid=None):
    if not user_id and not guest_uuid:
        return []

    rows = db.execute(
        text("""
            SELECT
                wi.id AS wishlist_item_id,
                wi.variant_id,

                p.id AS product_id,
                p.name AS product_name,
                p.description,

                pv.price,
                pv.size,
                pv.stock,

                c.name AS color,
                c.hex_code,

                COALESCE(pi.image_url, '') AS image_url

            FROM wishlist w
            JOIN wishlist_item wi ON wi.wishlist_id = w.id
            JOIN product_variant pv ON pv.id = wi.variant_id
            JOIN product p ON p.id = pv.product_id
            LEFT JOIN color c ON c.id = pv.color_id
            LEFT JOIN product_image pi
                ON pi.product_id = p.id
               AND pi.is_primary = TRUE

            WHERE
                (:user_id IS NOT NULL AND w.user_id = :user_id)
                OR
                (:guest_uuid IS NOT NULL AND w.guest_uuid = :guest_uuid)

            ORDER BY wi.id DESC
        """),
        {
            "user_id": user_id,
            "guest_uuid": guest_uuid
        }
    ).mappings().all()

    return [
        {
            "id": row["wishlist_item_id"],
            "wishlist_item_id": row["wishlist_item_id"],

            "product_id": row["product_id"],
            "db_product_id": row["product_id"],

            "variant_id": row["variant_id"],

            "name": row["product_name"],
            "title": row["product_name"],
            "product_name": row["product_name"],

            "description": row["description"],

            "price": float(row["price"] or 0),
            "size": row["size"],
            "color": row["color"],
            "hex_code": row["hex_code"],
            "stock": row["stock"],

            "image_url": row["image_url"],
            "image": row["image_url"],
        }
        for row in rows
    ]


def add_to_wishlist(
    db: Session,
    user_id=None,
    guest_uuid=None,
    product_id=None,
    variant_id=None
):
    if not user_id and not guest_uuid:
        raise ValueError("user_id or guest_uuid is required")

    if not variant_id:
        raise ValueError("variant_id is required")

    variant = db.execute(
        text("""
            SELECT id, product_id
            FROM product_variant
            WHERE id = :variant_id
              AND is_deleted = FALSE
            LIMIT 1
        """),
        {"variant_id": variant_id}
    ).mappings().first()

    if not variant:
        raise ValueError("Invalid variant_id")

    product_id = variant["product_id"]

    wishlist = db.execute(
        text("""
            SELECT id
            FROM wishlist
            WHERE
                (:user_id IS NOT NULL AND user_id = :user_id)
                OR
                (:guest_uuid IS NOT NULL AND guest_uuid = :guest_uuid)
            LIMIT 1
        """),
        {
            "user_id": user_id,
            "guest_uuid": guest_uuid
        }
    ).mappings().first()

    if not wishlist:
        wishlist = db.execute(
            text("""
                INSERT INTO wishlist (user_id, guest_uuid)
                VALUES (:user_id, :guest_uuid)
                RETURNING id
            """),
            {
                "user_id": user_id,
                "guest_uuid": guest_uuid
            }
        ).mappings().first()

    wishlist_id = wishlist["id"]

    wishlist_item = db.execute(
        text("""
            INSERT INTO wishlist_item (wishlist_id, variant_id)
            VALUES (:wishlist_id, :variant_id)
            ON CONFLICT (wishlist_id, variant_id) DO NOTHING
            RETURNING id
        """),
        {
            "wishlist_id": wishlist_id,
            "variant_id": variant_id
        }
    ).mappings().first()

    db.commit()

    return {
        "wishlist_id": wishlist_id,
        "wishlist_item_id": wishlist_item["id"] if wishlist_item else None,
        "product_id": product_id,
        "variant_id": variant_id
    }


def remove_from_wishlist(db: Session, wishlist_item_id: int):
    result = db.execute(
        text("""
            DELETE FROM wishlist_item
            WHERE id = :wishlist_item_id
            RETURNING id
        """),
        {"wishlist_item_id": wishlist_item_id}
    ).mappings().first()

    db.commit()
    return result


def remove_by_variant(db: Session, user_id=None, guest_uuid=None, variant_id=None):
    if not variant_id:
        return None

    result = db.execute(
        text("""
            DELETE FROM wishlist_item wi
            USING wishlist w
            WHERE wi.wishlist_id = w.id
              AND wi.variant_id = :variant_id
              AND (
                    (:user_id IS NOT NULL AND w.user_id = :user_id)
                    OR
                    (:guest_uuid IS NOT NULL AND w.guest_uuid = :guest_uuid)
                  )
            RETURNING wi.id
        """),
        {
            "variant_id": variant_id,
            "user_id": user_id,
            "guest_uuid": guest_uuid
        }
    ).mappings().first()

    db.commit()
    return result


def merge_wishlist(db: Session, guest_uuid: str, user_id: int):
    guest_wishlist = db.execute(
        text("SELECT id FROM wishlist WHERE guest_uuid = :guest_uuid LIMIT 1"),
        {"guest_uuid": guest_uuid}
    ).mappings().first()

    if not guest_wishlist:
        return {"message": "No guest wishlist found"}

    user_wishlist = db.execute(
        text("SELECT id FROM wishlist WHERE user_id = :user_id LIMIT 1"),
        {"user_id": user_id}
    ).mappings().first()

    if not user_wishlist:
        user_wishlist = db.execute(
            text("""
                INSERT INTO wishlist (user_id)
                VALUES (:user_id)
                RETURNING id
            """),
            {"user_id": user_id}
        ).mappings().first()

    db.execute(
        text("""
            INSERT INTO wishlist_item (wishlist_id, variant_id)
            SELECT :user_wishlist_id, variant_id
            FROM wishlist_item
            WHERE wishlist_id = :guest_wishlist_id
            ON CONFLICT (wishlist_id, variant_id) DO NOTHING
        """),
        {
            "user_wishlist_id": user_wishlist["id"],
            "guest_wishlist_id": guest_wishlist["id"]
        }
    )

    db.execute(
        text("DELETE FROM wishlist_item WHERE wishlist_id = :guest_wishlist_id"),
        {"guest_wishlist_id": guest_wishlist["id"]}
    )

    db.execute(
        text("DELETE FROM wishlist WHERE id = :guest_wishlist_id"),
        {"guest_wishlist_id": guest_wishlist["id"]}
    )

    db.commit()

    return {"message": "Wishlist merged"}