from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional
import os

from app.models.product import Product
from app.models.product_variant import ProductVariant
from app.models.product_image import ProductImage
from app.models.category import Category
from app.models.color import Color


class ProductRepository:

    # =====================================================
    # CATEGORY
    # =====================================================

    @staticmethod
    def get_all_categories(db: Session):
        return db.query(Category).filter(
            Category.is_deleted == False
        ).order_by(Category.name.asc()).all()

    @staticmethod
    def get_category_by_id(db: Session, category_id: int):
        return db.query(Category).filter(
            Category.id == category_id,
            Category.is_deleted == False
        ).first()

    @staticmethod
    def create_category(db: Session, data):
        result = db.execute(text("""
            INSERT INTO category
            (name, description, is_active, created_at, updated_at)
            VALUES (:name, :description, :is_active, NOW(), NOW())
            RETURNING *
        """), {
            "name": data.name,
            "description": data.description,
            "is_active": data.is_active if data.is_active is not None else True
        })

        db.commit()
        return result.mappings().first()

    @staticmethod
    def update_category(db: Session, category_id: int, data):
        result = db.execute(text("""
            UPDATE category
            SET
                name = COALESCE(:name, name),
                description = COALESCE(:description, description),
                is_active = COALESCE(:is_active, is_active),
                updated_at = NOW()
            WHERE id = :id
            RETURNING *
        """), {
            "id": category_id,
            "name": data.name,
            "description": data.description,
            "is_active": data.is_active
        })

        db.commit()
        return result.mappings().first()

    @staticmethod
    def delete_category(db: Session, category_id: int):
        result = db.execute(text("""
            UPDATE category
            SET is_deleted = TRUE,
                updated_at = NOW()
            WHERE id = :id
            RETURNING *
        """), {"id": category_id})

        db.commit()
        return result.mappings().first()

    # =====================================================
    # COLORS
    # =====================================================

    @staticmethod
    def get_all_colors(db: Session):
        return db.query(Color).filter(
            Color.is_active == True
        ).order_by(Color.name.asc()).all()

    @staticmethod
    def create_color(db: Session, data):
        result = db.execute(text("""
            INSERT INTO color
            (name, hex_code, is_active, created_at)
            VALUES (:name, :hex_code, TRUE, NOW())
            RETURNING *
        """), {
            "name": data.name,
            "hex_code": data.hex_code
        })

        db.commit()
        return result.mappings().first()

    # =====================================================
    # PRODUCTS
    # =====================================================

    @staticmethod
    def get_all_products(
        db: Session,
        category_id: Optional[int] = None,
        is_active: Optional[bool] = None
    ):
        query = db.query(Product).filter(Product.is_deleted == False)

        if category_id is not None:
            query = query.filter(Product.category_id == category_id)

        if is_active is not None:
            query = query.filter(Product.is_active == is_active)

        return query.order_by(Product.created_at.desc()).all()

    @staticmethod
    def get_products(
        db: Session,
        category_id: Optional[int] = None,
        is_active: Optional[bool] = None
    ):
        return ProductRepository.get_all_products(
            db=db,
            category_id=category_id,
            is_active=is_active
        )

    @staticmethod
    def get_product_by_id(db: Session, product_id: int):
        return db.query(Product).filter(
            Product.id == product_id,
            Product.is_deleted == False
        ).first()

    @staticmethod
    def get_product(db: Session, product_id: int):
        product = ProductRepository.get_product_by_id(db, product_id)

        if not product:
            return None, [], []

        variants = ProductRepository.get_variants_by_product(db, product_id)
        images = ProductRepository.get_images_by_product(db, product_id)

        return product, variants, images

    @staticmethod
    def create_product(db: Session, data, user_id: int):
        db.execute(text("""
            CALL sp_add_product(
                :name,
                :sku,
                :category_id,
                :description,
                :details_and_fit,
                :fabric_and_care,
                :return_and_exchange,
                :tax_rate_id,
                :is_active,
                :created_by,
                NULL
            )
        """), {
            "name": data.name,
            "sku": data.sku,
            "category_id": data.category_id,
            "description": data.description,
            "details_and_fit": data.details_and_fit,
            "fabric_and_care": data.fabric_and_care,
            "return_and_exchange": data.return_and_exchange,
            "tax_rate_id": getattr(data, "tax_rate_id", None),
            "is_active": data.is_active if data.is_active is not None else True,
            "created_by": user_id
        })

        db.commit()

        return db.query(Product).filter(
            Product.sku == data.sku
        ).first()

    @staticmethod
    def update_product(db: Session, product_id: int, data, user_id: int):
        product = db.query(Product).filter(Product.id == product_id).first()

        if not product:
            return None

        if data.name is not None:
            product.name = data.name
        if data.description is not None:
            product.description = data.description
        if data.category_id is not None:
            product.category_id = data.category_id
        if data.sku is not None:
            product.sku = data.sku
        if data.is_active is not None:
            product.is_active = data.is_active
        if data.details_and_fit is not None:
            product.details_and_fit = data.details_and_fit
        if data.fabric_and_care is not None:
            product.fabric_and_care = data.fabric_and_care
        if data.return_and_exchange is not None:
            product.return_and_exchange = data.return_and_exchange
        if hasattr(data, "tax_rate_id") and data.tax_rate_id is not None:
            product.tax_rate_id = data.tax_rate_id

        product.updated_by = user_id

        db.commit()
        db.refresh(product)

        return product

    @staticmethod
    def delete_product(db: Session, product_id: int):
        product = db.query(Product).filter(Product.id == product_id).first()

        if not product:
            return None

        product.is_deleted = True

        db.commit()
        db.refresh(product)

        return product

    @staticmethod
    def toggle_bestseller(
        db: Session,
        product_id: int,
        is_bestseller: bool,
        user_id: int
    ):
        result = db.execute(text("""
            UPDATE product
            SET
                is_bestseller = :flag,
                bestseller_marked_at = NOW(),
                bestseller_marked_by = :uid,
                updated_by = :uid,
                updated_at = NOW()
            WHERE id = :id
            RETURNING *
        """), {
            "flag": is_bestseller,
            "uid": user_id,
            "id": product_id
        })

        db.commit()
        return result.mappings().first()

    # =====================================================
    # VARIANTS
    # =====================================================

    @staticmethod
    def get_variants_by_product(db: Session, product_id: int):
        return db.query(ProductVariant).filter(
            ProductVariant.product_id == product_id,
            ProductVariant.is_deleted == False
        ).order_by(ProductVariant.id.asc()).all()

    @staticmethod
    def get_variants(db: Session, product_id: int):
        return ProductRepository.get_variants_by_product(db, product_id)

    @staticmethod
    def get_variant_by_id(db: Session, variant_id: int):
        return db.query(ProductVariant).filter(
            ProductVariant.id == variant_id,
            ProductVariant.is_deleted == False
        ).first()

    @staticmethod
    def create_variant(db: Session, product_id: int, data, user_id: int):
        variant = ProductVariant(
            product_id=product_id,
            variant_name=data.variant_name,
            price=data.price,
            stock=data.stock if data.stock is not None else 0,
            sku=data.sku,
            color=getattr(data, "color", None),
            color_id=data.color_id,
            size=data.size,
            low_stock_threshold=data.low_stock_threshold if data.low_stock_threshold is not None else 5,
            created_by=user_id
        )

        db.add(variant)
        db.commit()
        db.refresh(variant)

        return variant

    @staticmethod
    def update_variant(db: Session, variant_id: int, data, user_id: int):
        variant = db.query(ProductVariant).filter(
            ProductVariant.id == variant_id
        ).first()

        if not variant:
            return None

        if data.variant_name is not None:
            variant.variant_name = data.variant_name
        if data.price is not None:
            variant.price = data.price
        if data.stock is not None:
            variant.stock = data.stock
        if data.sku is not None:
            variant.sku = data.sku
        if hasattr(data, "color") and data.color is not None:
            variant.color = data.color
        if data.color_id is not None:
            variant.color_id = data.color_id
        if data.size is not None:
            variant.size = data.size
        if data.low_stock_threshold is not None:
            variant.low_stock_threshold = data.low_stock_threshold
        if hasattr(data, "is_deleted") and data.is_deleted is not None:
            variant.is_deleted = data.is_deleted

        variant.updated_by = user_id

        db.commit()
        db.refresh(variant)

        return variant

    @staticmethod
    def delete_variant(db: Session, variant_id: int):
        variant = db.query(ProductVariant).filter(
            ProductVariant.id == variant_id
        ).first()

        if not variant:
            return None

        variant.is_deleted = True

        db.commit()
        db.refresh(variant)

        return variant

    # =====================================================
    # IMAGES
    # =====================================================

    @staticmethod
    def get_images_by_product(db: Session, product_id: int):
        return db.query(ProductImage).filter(
            ProductImage.product_id == product_id
        ).order_by(
            ProductImage.is_primary.desc(),
            ProductImage.id.asc()
        ).all()

    @staticmethod
    def add_product_image(db: Session, product_id: int, data):
        return ProductRepository.add_image(db, product_id, data)

    @staticmethod
    def add_image(db: Session, product_id: int, data):
        image_name = data.image_name or os.path.basename(data.image_url)

        if data.is_primary:
            db.execute(text("""
                CALL sp_add_product_image(
                    :pid,
                    :url,
                    :name,
                    TRUE
                )
            """), {
                "pid": product_id,
                "url": data.image_url,
                "name": image_name
            })

            db.commit()

            return db.query(ProductImage).filter(
                ProductImage.product_id == product_id,
                ProductImage.is_primary == True
            ).first()

        image = ProductImage(
            product_id=product_id,
            variant_id=getattr(data, "variant_id", None),
            image_url=data.image_url,
            image_name=image_name,
            is_primary=False
        )

        db.add(image)
        db.commit()
        db.refresh(image)

        return image

    @staticmethod
    def delete_product_image(db: Session, image_id: int):
        return ProductRepository.delete_image(db, image_id)

    @staticmethod
    def delete_image(db: Session, image_id: int):
        image = db.query(ProductImage).filter(
            ProductImage.id == image_id
        ).first()

        if not image:
            return None

        db.delete(image)
        db.commit()

        return image

    # =====================================================
    # EXTRA / REPORTS
    # =====================================================

    @staticmethod
    def get_low_stock_variants(db: Session):
        result = db.execute(text("SELECT * FROM low_stock_products"))
        return result.mappings().all()

    @staticmethod
    def get_low_stock(db: Session):
        return ProductRepository.get_low_stock_variants(db)

    @staticmethod
    def get_active_products_view(db: Session):
        result = db.execute(text("SELECT * FROM v_active_products"))
        return result.mappings().all()