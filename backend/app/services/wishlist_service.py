from sqlalchemy.orm import Session
from sqlalchemy import text


def get_wishlist(db: Session, user_id=None, guest_uuid=None):
    if not user_id and not guest_uuid:
        return []

    if user_id:
        query = text("""
            SELECT
                wi.id AS id,
                pv.product_id AS product_id,
                wi.variant_id AS variant_id,
                p.name AS product_name,
                pv.price AS price,
                pi.image_url AS image_url
            FROM wishlist w
            JOIN wishlist_item wi ON wi.wishlist_id = w.id
            JOIN product_variant pv ON pv.id = wi.variant_id
            JOIN product p ON p.id = pv.product_id
            LEFT JOIN product_image pi 
                ON pi.product_id = p.id AND pi.is_primary = true
            WHERE w.user_id = :user_id
        """)

        rows = db.execute(query, {"user_id": user_id}).mappings().all()

    else:
        query = text("""
            SELECT
                wi.id AS id,
                pv.product_id AS product_id,
                wi.variant_id AS variant_id,
                p.name AS product_name,
                pv.price AS price,
                pi.image_url AS image_url
            FROM wishlist w
            JOIN wishlist_item wi ON wi.wishlist_id = w.id
            JOIN product_variant pv ON pv.id = wi.variant_id
            JOIN product p ON p.id = pv.product_id
            LEFT JOIN product_image pi 
                ON pi.product_id = p.id AND pi.is_primary = true
            WHERE w.guest_uuid = :guest_uuid
        """)

        rows = db.execute(query, {"guest_uuid": guest_uuid}).mappings().all()

    return [
        {
            "id": row["id"],
            "product_id": row["product_id"],
            "variant_id": row["variant_id"],
            "product_name": row["product_name"],
            "price": float(row["price"] or 0),
            "image_url": row["image_url"],
        }
        for row in rows
    ]

def add_to_wishlist(db: Session, user_id=None, guest_uuid=None, product_id=None, variant_id=None):
    if not user_id and not guest_uuid:
        raise ValueError("user_id or guest_uuid is required")

    if not variant_id:
        raise ValueError("variant_id is required")

    if user_id:
        wishlist = db.execute(
            text("SELECT id FROM wishlist WHERE user_id = :user_id LIMIT 1"),
            {"user_id": user_id}
        ).mappings().first()

        if not wishlist:
            wishlist = db.execute(
                text("""
                    INSERT INTO wishlist (user_id)
                    VALUES (:user_id)
                    RETURNING id
                """),
                {"user_id": user_id}
            ).mappings().first()

    else:
        wishlist = db.execute(
            text("SELECT id FROM wishlist WHERE guest_uuid = :guest_uuid LIMIT 1"),
            {"guest_uuid": guest_uuid}
        ).mappings().first()

        if not wishlist:
            wishlist = db.execute(
                text("""
                    INSERT INTO wishlist (guest_uuid)
                    VALUES (:guest_uuid)
                    RETURNING id
                """),
                {"guest_uuid": guest_uuid}
            ).mappings().first()

    wishlist_id = wishlist["id"]

    db.execute(
        text("""
            INSERT INTO wishlist_item (wishlist_id, variant_id)
            VALUES (:wishlist_id, :variant_id)
            ON CONFLICT (wishlist_id, variant_id) DO NOTHING
        """),
        {
            "wishlist_id": wishlist_id,
            "variant_id": variant_id
        }
    )

    db.commit()

    return {
        "wishlist_id": wishlist_id,
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