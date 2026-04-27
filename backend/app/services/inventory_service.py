# app/services/inventory_service.py
# UPDATED FOR NEW DB STRUCTURE

from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.repositories.inventory_repo import InventoryRepository


class InventoryService:

    # =====================================================
    # VARIANTS
    # =====================================================

    @staticmethod
    def get_all_variants(db: Session):
        return InventoryRepository.get_all_variants(db)

    @staticmethod
    def get_low_stock_variants(db: Session):
        return InventoryRepository.get_low_stock_variants(db)

    @staticmethod
    def get_variant_by_id(db: Session, variant_id: int):
        variant = InventoryRepository.get_variant_by_id(db, variant_id)

        if not variant:
            raise HTTPException(
                status_code=404,
                detail="Variant not found"
            )

        return variant

    # =====================================================
    # LOGS
    # =====================================================

    @staticmethod
    def get_all_logs(
        db: Session,
        variant_id=None,
        change_type=None,
        limit: int = 100
    ):
        return InventoryRepository.get_all_logs(
            db=db,
            variant_id=variant_id,
            change_type=change_type,
            limit=limit
        )

    @staticmethod
    def get_logs_by_variant(db: Session, variant_id: int):
        return InventoryRepository.get_logs_by_variant(db, variant_id)

    # =====================================================
    # STOCK ACTIONS
    # =====================================================

    @staticmethod
    def add_stock(db: Session, payload, user_id: int = 1):
        try:
            return InventoryRepository.add_stock(
                db=db,
                data=payload,
                user_id=user_id
            )
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=str(e)
            )

    @staticmethod
    def remove_stock(db: Session, payload, user_id: int = 1):
        try:
            return InventoryRepository.remove_stock(
                db=db,
                data=payload,
                user_id=user_id
            )
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=str(e)
            )

    @staticmethod
    def reserve_stock(db: Session, payload, user_id: int = 1):
        try:
            return InventoryRepository.reserve_stock(
                db=db,
                data=payload,
                user_id=user_id
            )
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=str(e)
            )

    @staticmethod
    def release_stock(db: Session, payload, user_id: int = 1):
        try:
            return InventoryRepository.release_stock(
                db=db,
                data=payload,
                user_id=user_id
            )
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=str(e)
            )

    # =====================================================
    # UPDATE VARIANT SETTINGS
    # =====================================================

    @staticmethod
    def update_variant_stock(
        db: Session,
        variant_id: int,
        payload,
        user_id: int = 1
    ):
        variant = InventoryRepository.update_variant_stock(
            db=db,
            variant_id=variant_id,
            data=payload
        )

        if not variant:
            raise HTTPException(
                status_code=404,
                detail="Variant not found"
            )

        return variant