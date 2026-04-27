from sqlalchemy.orm import Session
from app.models.user import User
from app.models.product import Product
from app.models.product_variant import ProductVariant


class AdminRepository:

    @staticmethod
    def get_total_users(db: Session):
        return db.query(User).count()

    @staticmethod
    def get_total_products(db: Session):
        return db.query(Product).count()

    @staticmethod
    def get_total_variants(db: Session):
        return db.query(ProductVariant).count()

    @staticmethod
    def get_all_users(db: Session):
        return db.query(User).all()