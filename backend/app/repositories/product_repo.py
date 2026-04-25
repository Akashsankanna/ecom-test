from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional
import os


class ProductRepository:

    # ───────────── CATEGORIES ─────────────

    @staticmethod
    def get_all_categories(db: Session):
        return db.execute(text("""
            SELECT id, name, description, is_active, created_at
            FROM category
            WHERE is_deleted = false
            ORDER BY name
        """)).mappings().all()

    @staticmethod
    def create_category(db: Session, data):
        result = db.execute(text("""
            INSERT INTO category
            (name, description, is_active, created_at, updated_at)
            VALUES (:name, :desc, true, NOW(), NOW())
            RETURNING *
        """), {
            "name": data.name,
            "desc": data.description
        })
        db.commit()
        return result.mappings().first()

    @staticmethod
    def update_category(db: Session, category_id: int, data):
        result = db.execute(text("""
            UPDATE category
            SET name = COALESCE(:name,name),
                description = COALESCE(:desc,description),
                is_active = COALESCE(:active,is_active),
                updated_at = NOW()
            WHERE id = :id
            RETURNING *
        """), {
            "id": category_id,
            "name": data.name,
            "desc": data.description,
            "active": data.is_active
        })
        db.commit()
        return result.mappings().first()

    @staticmethod
    def delete_category(db: Session, category_id: int):
        db.execute(text("""
            UPDATE category
            SET is_deleted = true,
                updated_at = NOW()
            WHERE id = :id
        """), {"id": category_id})
        db.commit()
        return {"message": "Category deleted"}

    # ───────────── COLORS ─────────────

    @staticmethod
    def get_all_colors(db: Session):
        return db.execute(text("""
            SELECT *
            FROM color
            ORDER BY name
        """)).mappings().all()

    @staticmethod
    def create_color(db: Session, data):
        result = db.execute(text("""
            INSERT INTO color
            (name, hex_code, is_active, created_at)
            VALUES (:name,:hex,true,NOW())
            RETURNING *
        """), {
            "name": data.name,
            "hex": data.hex_code
        })
        db.commit()
        return result.mappings().first()

    # ───────────── PRODUCTS ─────────────

    @staticmethod
    def get_products(
        db: Session,
        category_id=None,
        is_active=None
    ):
        sql = """
            SELECT *
            FROM product
            WHERE is_deleted = false
        """

        params = {}

        if category_id is not None:
            sql += " AND category_id = :cat"
            params["cat"] = category_id

        if is_active is not None:
            sql += " AND is_active = :active"
            params["active"] = is_active

        sql += " ORDER BY created_at DESC"

        return db.execute(
            text(sql),
            params
        ).mappings().all()

    @staticmethod
    def get_product(db: Session, product_id: int):

        product = db.execute(text("""
            SELECT *
            FROM product
            WHERE id = :id
              AND is_deleted = false
        """), {"id": product_id}).mappings().first()

        if not product:
            return None, [], []

        variants = db.execute(text("""
            SELECT *
            FROM product_variant
            WHERE product_id = :id
              AND is_deleted = false
            ORDER BY id
        """), {"id": product_id}).mappings().all()

        images = db.execute(text("""
            SELECT *
            FROM product_image
            WHERE product_id = :id
            ORDER BY is_primary DESC, id
        """), {"id": product_id}).mappings().all()

        return product, variants, images

    @staticmethod
    def create_product(
        db: Session,
        data,
        user_id: int
    ):
        db.execute(text("""
            CALL sp_add_product(
                :name,
                :sku,
                :cat,
                :desc,
                :daf,
                :fac,
                :rae,
                :tax,
                :active,
                :uid,
                NULL
            )
        """), {
            "name": data.name,
            "sku": data.sku,
            "cat": data.category_id,
            "desc": data.description,
            "daf": data.details_and_fit,
            "fac": data.fabric_and_care,
            "rae": data.return_and_exchange,
            "tax": getattr(data, "tax_rate_id", None),
            "active": data.is_active,
            "uid": user_id
        })

        db.commit()

        row = db.execute(text("""
            SELECT *
            FROM product
            WHERE sku = :sku
        """), {"sku": data.sku}).mappings().first()

        return row

    @staticmethod
    def update_product(db: Session, product_id: int, data, user_id: int):
        db.execute(text("""
            UPDATE product
            SET
                name = COALESCE(:name, name),
                sku = COALESCE(:sku, sku),
                description = COALESCE(:desc, description),
                category_id = COALESCE(:cat, category_id),
                details_and_fit = COALESCE(:daf, details_and_fit),
                fabric_and_care = COALESCE(:fac, fabric_and_care),
                return_and_exchange = COALESCE(:rae, return_and_exchange),
                tax_rate_id = :tax,
                is_active = COALESCE(:active, is_active),
                updated_by = :uid,
                updated_at = NOW()
            WHERE id = :id
        """), {
            "id": product_id,
            "name": data.name,
            "sku": data.sku,
            "desc": data.description,
            "cat": data.category_id,
            "daf": data.details_and_fit,
            "fac": data.fabric_and_care,
            "rae": data.return_and_exchange,
            "tax": data.tax_rate_id,
            "active": data.is_active,
            "uid": user_id
        })

        db.commit()

        return db.execute(text("""
            SELECT *
            FROM product
            WHERE id = :id
        """), {"id": product_id}).mappings().first()

    @staticmethod
    def delete_product(
        db: Session,
        product_id: int
    ):
        db.execute(text("""
            UPDATE product
            SET is_deleted = true,
                updated_at = NOW()
            WHERE id = :id
        """), {"id": product_id})

        db.commit()

        return {"message": "Product deleted"}

    @staticmethod
    def toggle_bestseller(
        db: Session,
        product_id: int,
        is_bestseller: bool,
        user_id: int
    ):
        db.execute(text("""
            UPDATE product
            SET is_bestseller = :flag,
                bestseller_marked_at = NOW(),
                bestseller_marked_by = :uid,
                updated_by = :uid,
                updated_at = NOW()
            WHERE id = :id
        """), {
            "flag": is_bestseller,
            "uid": user_id,
            "id": product_id
        })

        db.commit()

        return db.execute(text("""
            SELECT *
            FROM product
            WHERE id = :id
        """), {"id": product_id}).mappings().first()

    # ───────────── VARIANTS ─────────────

    @staticmethod
    def get_variants(db: Session, product_id: int):
        return db.execute(text("""
            SELECT *
            FROM product_variant
            WHERE product_id = :id
              AND is_deleted = false
            ORDER BY id
        """), {"id": product_id}).mappings().all()

    @staticmethod
    def create_variant(db: Session, product_id: int, data, user_id: int):
        result = db.execute(text("""
            INSERT INTO product_variant
            (product_id, variant_name, price, stock, sku,
             color_id, size, low_stock_threshold,
             created_by, created_at, updated_at)
            VALUES
            (:pid,:name,:price,:stock,:sku,
             :color,:size,:low,
             :uid,NOW(),NOW())
            RETURNING *
        """), {
            "pid": product_id,
            "name": data.variant_name,
            "price": data.price,
            "stock": data.stock,
            "sku": data.sku,
            "color": data.color_id,
            "size": data.size,
            "low": data.low_stock_threshold,
            "uid": user_id
        })
        db.commit()
        return result.mappings().first()

    @staticmethod
    def update_variant(db: Session, variant_id: int, data, user_id: int):
        result = db.execute(text("""
            UPDATE product_variant
            SET variant_name = COALESCE(:name,variant_name),
                price = COALESCE(:price,price),
                stock = COALESCE(:stock,stock),
                sku = COALESCE(:sku,sku),
                color_id = COALESCE(:color_id,color_id),
                size = COALESCE(:size,size),
                low_stock_threshold = COALESCE(:low,low_stock_threshold),
                updated_by = :uid,
                updated_at = NOW()
            WHERE id = :id
            RETURNING *
        """), {
            "id": variant_id,
            "name": data.variant_name,
            "price": data.price,
            "stock": data.stock,
            "sku": data.sku,
            "color_id": data.color_id,
            "size": data.size,
            "low": data.low_stock_threshold,
            "uid": user_id
        })
        db.commit()
        return result.mappings().first()

    @staticmethod
    def delete_variant(db: Session, variant_id: int):
        db.execute(text("""
            UPDATE product_variant
            SET is_deleted = true,
                updated_at = NOW()
            WHERE id = :id
        """), {"id": variant_id})
        db.commit()
        return {"message": "Variant deleted"}

    # ───────────── IMAGES ─────────────

    @staticmethod
    def add_image(db: Session, product_id: int, data):

        image_name = data.image_name or os.path.basename(data.image_url)

        db.execute(text("""
            INSERT INTO product_image
            (product_id, variant_id, image_url, image_name, is_primary, created_at)
            VALUES
            (:pid, :vid, :url, :name, :primary, NOW())
        """), {
            "pid": product_id,
            "vid": getattr(data, "variant_id", None),
            "url": data.image_url,
            "name": image_name,
            "primary": data.is_primary
        })

        db.commit()

        return {"message": "Image added"}

    @staticmethod
    def delete_image(db: Session, image_id: int):
        db.execute(text("""
            DELETE FROM product_image
            WHERE id = :id
        """), {"id": image_id})
        db.commit()
        return {"message": "Image deleted"}

    # ───────────── EXTRA ─────────────

    @staticmethod
    def get_low_stock(db: Session):
        return db.execute(text("""
            SELECT *
            FROM low_stock_products
        """)).mappings().all()

    @staticmethod
    def get_active_products_view(db: Session):
        return db.execute(text("""
            SELECT *
            FROM v_active_products
        """)).mappings().all()