from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.repositories.product_repo import ProductRepository
from app.schemas.product import (
    ProductCreate,
    ProductUpdate,
    VariantCreate,
    VariantUpdate,
    CategoryCreate,
    CategoryUpdate,
    ColorCreate,
    ProductImageCreate,
)


class ProductService:

    # =====================================================
    # CATEGORY
    # =====================================================

    @staticmethod
    def get_all_categories(db: Session):
        return ProductRepository.get_all_categories(db)

    @staticmethod
    def get_category(
        db: Session,
        category_id: int
    ):
        category = ProductRepository.get_category_by_id(
            db,
            category_id
        )

        if not category:
            raise HTTPException(
                status_code=404,
                detail="Category not found"
            )

        return category

    @staticmethod
    def create_category(
        db: Session,
        data: CategoryCreate
    ):
        return ProductRepository.create_category(
            db,
            data
        )

    @staticmethod
    def update_category(
        db: Session,
        category_id: int,
        data: CategoryUpdate
    ):
        category = ProductRepository.update_category(
            db,
            category_id,
            data
        )

        if not category:
            raise HTTPException(
                status_code=404,
                detail="Category not found"
            )

        return category

    @staticmethod
    def delete_category(
        db: Session,
        category_id: int
    ):
        category = ProductRepository.delete_category(
            db,
            category_id
        )

        if not category:
            raise HTTPException(
                status_code=404,
                detail="Category not found"
            )

        return {"message": "Category deleted"}

    # =====================================================
    # COLORS
    # =====================================================

    @staticmethod
    def get_all_colors(db: Session):
        return ProductRepository.get_all_colors(db)

    @staticmethod
    def create_color(
        db: Session,
        data: ColorCreate
    ):
        return ProductRepository.create_color(
            db,
            data
        )

    # =====================================================
    # PRODUCTS
    # =====================================================

    @staticmethod
    def create_product(
        db: Session,
        data: ProductCreate,
        user_id: int
    ):
        return ProductRepository.create_product(
            db,
            data,
            user_id
        )

    @staticmethod
    def get_products(
        db: Session,
        category_id=None,
        is_active=None
    ):
        # supports both repo names
        if hasattr(ProductRepository, "get_products"):
            return ProductRepository.get_products(
                db,
                category_id,
                is_active
            )

        return ProductRepository.get_all_products(
            db,
            category_id,
            is_active
        )

    @staticmethod
    def get_product(
        db: Session,
        product_id: int
    ):
        # supports merged repo helper
        if hasattr(ProductRepository, "get_product"):
            product, variants, images = (
                ProductRepository.get_product(
                    db,
                    product_id
                )
            )
        else:
            product = ProductRepository.get_product_by_id(
                db,
                product_id
            )

            variants = (
                ProductRepository.get_variants_by_product(
                    db,
                    product_id
                )
            )

            images = (
                ProductRepository.get_images_by_product(
                    db,
                    product_id
                )
            )

        if not product:
            raise HTTPException(
                status_code=404,
                detail="Product not found"
            )

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
            raise HTTPException(
                status_code=404,
                detail="Product not found"
            )

        return product

    @staticmethod
    def delete_product(
        db: Session,
        product_id: int
    ):
        product = ProductRepository.delete_product(
            db,
            product_id
        )

        if not product:
            raise HTTPException(
                status_code=404,
                detail="Product not found"
            )

        return {
            "message":
            "Product deleted successfully"
        }

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
        product = ProductRepository.get_product_by_id(
            db,
            product_id
        )

        if not product:
            raise HTTPException(
                status_code=404,
                detail="Product not found"
            )

        return ProductRepository.create_variant(
            db,
            product_id,
            data,
            user_id
        )

    @staticmethod
    def get_variants(
        db: Session,
        product_id: int
    ):
        if hasattr(ProductRepository, "get_variants"):
            return ProductRepository.get_variants(
                db,
                product_id
            )

        return ProductRepository.get_variants_by_product(
            db,
            product_id
        )

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
            raise HTTPException(
                status_code=404,
                detail="Variant not found"
            )

        return variant

    @staticmethod
    def delete_variant(
        db: Session,
        variant_id: int
    ):
        variant = ProductRepository.delete_variant(
            db,
            variant_id
        )

        if not variant:
            raise HTTPException(
                status_code=404,
                detail="Variant not found"
            )

        return {
            "message":
            "Variant deleted successfully"
        }

    # =====================================================
    # IMAGES
    # =====================================================

    @staticmethod
    def add_image(
        db: Session,
        product_id: int,
        data: ProductImageCreate
    ):
        product = ProductRepository.get_product_by_id(
            db,
            product_id
        )

        if not product:
            raise HTTPException(
                status_code=404,
                detail="Product not found"
            )

        # variant image validation
        if getattr(data, "variant_id", None):
            variants = ProductService.get_variants(
                db,
                product_id
            )

            valid_variant = any(
                v.id == data.variant_id
                for v in variants
            )

            if not valid_variant:
                raise HTTPException(
                    status_code=404,
                    detail=(
                        "Variant not found "
                        "for this product"
                    )
                )

        if hasattr(ProductRepository, "add_image"):
            return ProductRepository.add_image(
                db,
                product_id,
                data
            )

        return ProductRepository.add_product_image(
            db,
            product_id,
            data
        )

    @staticmethod
    def delete_image(
        db: Session,
        image_id: int
    ):
        if hasattr(ProductRepository, "delete_image"):
            img = ProductRepository.delete_image(
                db,
                image_id
            )
        else:
            img = (
                ProductRepository.delete_product_image(
                    db,
                    image_id
                )
            )

        if not img:
            raise HTTPException(
                status_code=404,
                detail="Image not found"
            )

        return {"message": "Image deleted"}

    # =====================================================
    # LOW STOCK
    # =====================================================

    @staticmethod
    def get_low_stock(db: Session):
        if hasattr(ProductRepository, "get_low_stock"):
            return ProductRepository.get_low_stock(db)

        return ProductRepository.get_low_stock_variants(
            db
        )

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
        if not hasattr(
            ProductRepository,
            "toggle_bestseller"
        ):
            raise HTTPException(
                status_code=400,
                detail=(
                    "Bestseller feature "
                    "not supported"
                )
            )

        product = ProductRepository.toggle_bestseller(
            db,
            product_id,
            is_bestseller,
            user_id
        )

        if not product:
            raise HTTPException(
                status_code=404,
                detail="Product not found"
            )

        return product

    # =====================================================
    # ACTIVE VIEW
    # =====================================================

    @staticmethod
    def get_active_products_view(
        db: Session
    ):
        if not hasattr(
            ProductRepository,
            "get_active_products_view"
        ):
            return []

        return ProductRepository.get_active_products_view(
            db
        )