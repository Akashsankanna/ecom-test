# app/repositories/inventory_repo.py

from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional, List

from app.models.product_variant import ProductVariant
from app.models.inventory_log import InventoryLog


class InventoryRepository:

    # =====================================================
    # VARIANTS
    # =====================================================

    @staticmethod
    def get_all_variants(db: Session) -> List[ProductVariant]:
        return (
            db.query(ProductVariant)
            .filter(ProductVariant.is_deleted == False)
            .order_by(ProductVariant.product_id.asc(), ProductVariant.id.asc())
            .all()
        )

    @staticmethod
    def get_variant_by_id(db: Session, variant_id: int) -> Optional[ProductVariant]:
        return (
            db.query(ProductVariant)
            .filter(
                ProductVariant.id == variant_id,
                ProductVariant.is_deleted == False
            )
            .first()
        )

    @staticmethod
    def get_low_stock_variants(db: Session):
        return (
            db.query(ProductVariant)
            .filter(
                ProductVariant.is_deleted == False,
                ProductVariant.stock <= ProductVariant.low_stock_threshold
            )
            .order_by(ProductVariant.stock.asc())
            .all()
        )

    # =====================================================
    # LOGS
    # =====================================================

    @staticmethod
    def get_all_logs(
        db: Session,
        variant_id: Optional[int] = None,
        change_type: Optional[str] = None,
        limit: int = 100
    ):
        query = db.query(InventoryLog)

        if variant_id:
            query = query.filter(InventoryLog.variant_id == variant_id)

        if change_type:
            query = query.filter(
                InventoryLog.change_type == change_type.upper()
            )

        return (
            query.order_by(InventoryLog.created_at.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_logs_by_variant(db: Session, variant_id: int):
        return (
            db.query(InventoryLog)
            .filter(InventoryLog.variant_id == variant_id)
            .order_by(InventoryLog.created_at.desc())
            .all()
        )

    # =====================================================
    # COMMON LOGGER
    # =====================================================

    @staticmethod
    def create_log(
        db,
        variant,
        change_type,
        quantity,
        reference_id,
        reference_type,
        notes,
        user_id
    ):
        log = InventoryLog(
            variant_id=variant.id,
            change_type=change_type,
            quantity=quantity,
            reference_id=reference_id,
            reference_type=reference_type,
            notes=notes,
            created_by=user_id,
            updated_by=user_id
        )

        db.add(log)
        db.commit()
        db.refresh(log)
        return log

    # =====================================================
    # ADD STOCK
    # =====================================================

    @staticmethod
    def add_stock(db: Session, data, user_id: int):
        variant = InventoryRepository.get_variant_by_id(db, data.variant_id)

        if not variant:
            raise Exception("Variant not found")

        variant.stock += data.quantity
        variant.updated_by = user_id

        db.flush()

        ref_type = data.reference_type or (
            "RETURN" if data.change_type.value == "RETURN" else "RESTOCK"
        )

        return InventoryRepository.create_log(
            db=db,
            variant=variant,
            change_type=data.change_type.value,
            quantity=data.quantity,
            reference_id=data.reference_id,
            reference_type=ref_type,
            notes=data.notes,
            user_id=user_id
        )

    # =====================================================
    # REMOVE STOCK
    # =====================================================

    @staticmethod
    def remove_stock(db: Session, data, user_id: int):
        variant = InventoryRepository.get_variant_by_id(db, data.variant_id)

        if not variant:
            raise Exception("Variant not found")

        if variant.stock < data.quantity:
            raise Exception("Insufficient stock")

        variant.stock -= data.quantity
        variant.updated_by = user_id

        db.flush()

        ref_type = data.reference_type or (
            "EXCHANGE" if data.change_type.value == "EXCHANGE" else "MANUAL"
        )

        return InventoryRepository.create_log(
            db=db,
            variant=variant,
            change_type=data.change_type.value,
            quantity=data.quantity,
            reference_id=data.reference_id,
            reference_type=ref_type,
            notes=data.notes,
            user_id=user_id
        )

    # =====================================================
    # RESERVE STOCK
    # =====================================================

    @staticmethod
    def reserve_stock(db: Session, data, user_id: int):
        variant = InventoryRepository.get_variant_by_id(db, data.variant_id)

        if not variant:
            raise Exception("Variant not found")

        available = variant.stock - variant.reserved_stock

        if available < data.quantity:
            raise Exception("Not enough available stock")

        variant.reserved_stock += data.quantity
        variant.updated_by = user_id

        db.flush()

        return InventoryRepository.create_log(
            db=db,
            variant=variant,
            change_type="ORDER",
            quantity=data.quantity,
            reference_id=data.reference_id,
            reference_type="ORDER",
            notes=data.notes,
            user_id=user_id
        )

    # =====================================================
    # RELEASE RESERVED
    # =====================================================

    @staticmethod
    def release_stock(db: Session, data, user_id: int):
        variant = InventoryRepository.get_variant_by_id(db, data.variant_id)

        if not variant:
            raise Exception("Variant not found")

        if variant.reserved_stock < data.quantity:
            raise Exception("Reserved stock too low")

        variant.reserved_stock -= data.quantity
        variant.updated_by = user_id

        db.flush()

        return InventoryRepository.create_log(
            db=db,
            variant=variant,
            change_type="ORDER_CANCELLED",
            quantity=data.quantity,
            reference_id=data.reference_id,
            reference_type="ORDER",
            notes=data.notes,
            user_id=user_id
        )

    # =====================================================
    # UPDATE VARIANT SETTINGS
    # =====================================================

    @staticmethod
    def update_variant_stock(db: Session, variant_id: int, data):

        row = db.execute(
            text("""
                UPDATE product_variants
                SET
                    stock = COALESCE(:stock, stock),
                    reserved_stock = COALESCE(:reserved_stock, reserved_stock),
                    low_stock_threshold = COALESCE(:low_stock_threshold, low_stock_threshold),
                    updated_at = NOW()
                WHERE id = :variant_id
                RETURNING *
            """),
            {
                "variant_id": variant_id,
                "stock": data.stock,
                "reserved_stock": data.reserved_stock,
                "low_stock_threshold": data.low_stock_threshold
            }
        ).fetchone()

        db.commit()

        if not row:
            raise Exception("Variant not found")

        return row