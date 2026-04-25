from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.repositories.product_repo import ProductRepository

from app.schemas.product import (
    ProductCreate, ProductUpdate,
    VariantCreate, VariantUpdate,
    CategoryCreate, CategoryUpdate,
    ColorCreate, ProductImageCreate
)


class ProductService:

    # =====================================================
    # CATEGORY
    # =====================================================

    @staticmethod
    def get_all_categories(db: Session):
        return ProductRepository.get_all_categories(db)

    @staticmethod
    def create_category(db: Session, data: CategoryCreate):
        return ProductRepository.create_category(db, data)

    @staticmethod
    def update_category(db: Session, category_id: int, data: CategoryUpdate):
        category = ProductRepository.update_category(db, category_id, data)

        if not category:
            raise HTTPException(status_code=404, detail="Category not found")

        return category

    @staticmethod
    def delete_category(db: Session, category_id: int):
        return ProductRepository.delete_category(db, category_id)

    # =====================================================
    # COLORS
    # =====================================================

    @staticmethod
    def get_all_colors(db: Session):
        return ProductRepository.get_all_colors(db)

    @staticmethod
    def create_color(db: Session, data: ColorCreate):
        return ProductRepository.create_color(db, data)

    # =====================================================
    # PRODUCTS
    # =====================================================

    @staticmethod
    def create_product(db: Session, data: ProductCreate, user_id: int):
        return ProductRepository.create_product(db, data, user_id)

    @staticmethod
    def get_products(db: Session, category_id=None, is_active=None):
        return ProductRepository.get_products(db, category_id, is_active)

    @staticmethod
    def get_product(db: Session, product_id: int):
        product, variants, images = ProductRepository.get_product(db, product_id)

        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        return product, variants, images

    @staticmethod
    def update_product(
        db: Session,
        product_id: int,
        data: ProductUpdate,
        user_id: int
    ):
        product = ProductRepository.update_product(
            db,
            product_id,
            data,
            user_id
        )

        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        return product

    @staticmethod
    def delete_product(db: Session, product_id: int):
        return ProductRepository.delete_product(db, product_id)

    # =====================================================
    # VARIANTS
    # =====================================================

    @staticmethod
    def create_variant(
        db: Session,
        product_id: int,
        data: VariantCreate,
        user_id: int
    ):
        product, _, _ = ProductRepository.get_product(db, product_id)

        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        return ProductRepository.create_variant(
            db,
            product_id,
            data,
            user_id
        )

    @staticmethod
    def get_variants(db: Session, product_id: int):
        return ProductRepository.get_variants(db, product_id)

    @staticmethod
    def update_variant(
        db: Session,
        variant_id: int,
        data: VariantUpdate,
        user_id: int
    ):
        variant = ProductRepository.update_variant(
            db,
            variant_id,
            data,
            user_id
        )

        if not variant:
            raise HTTPException(status_code=404, detail="Variant not found")

        return variant

    @staticmethod
    def delete_variant(db: Session, variant_id: int):
        return ProductRepository.delete_variant(db, variant_id)

    # =====================================================
    # IMAGES
    # =====================================================

    @staticmethod
    def add_image(
        db: Session,
        product_id: int,
        data: ProductImageCreate
    ):
        product, _, _ = ProductRepository.get_product(db, product_id)

        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        # DB33 variant image support
        if getattr(data, "variant_id", None):
            variants = ProductRepository.get_variants(db, product_id)
            valid_variant = any(v.id == data.variant_id for v in variants)

            if not valid_variant:
                raise HTTPException(
                    status_code=404,
                    detail="Variant not found for this product"
                )

        return ProductRepository.add_image(db, product_id, data)

    @staticmethod
    def delete_image(db: Session, image_id: int):
        return ProductRepository.delete_image(db, image_id)

    # =====================================================
    # LOW STOCK
    # =====================================================

    @staticmethod
    def get_low_stock(db: Session):
        return ProductRepository.get_low_stock(db)

    # =====================================================
    # BESTSELLER
    # =====================================================

    @staticmethod
    def toggle_bestseller(
        db: Session,
        product_id: int,
        is_bestseller: bool,
        user_id: int
    ):
        product = ProductRepository.toggle_bestseller(
            db,
            product_id,
            is_bestseller,
            user_id
        )

        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        return product

    # =====================================================
    # ACTIVE VIEW
    # =====================================================

    @staticmethod
    def get_active_products_view(db: Session):
        return ProductRepository.get_active_products_view(db)