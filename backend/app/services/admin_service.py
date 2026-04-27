from sqlalchemy.orm import Session
from app.repositories.admin_repo import AdminRepository


class AdminService:

    @staticmethod
    def get_dashboard_data(db: Session):
        return {
            "total_users": AdminRepository.get_total_users(db),
            "total_products": AdminRepository.get_total_products(db),
            "total_variants": AdminRepository.get_total_variants(db),
        }

    @staticmethod
    def get_users(db: Session):
        return AdminRepository.get_all_users(db)

    # ❌ REMOVE THIS (you don't have orders table yet)
    # @staticmethod
    # def get_orders(db: Session):
    #     return AdminRepository.get_all_orders(db)