from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import Optional

from app.repositories.customization_repo import CustomizationRepository
from app.schemas.customization import (
    CustomizationTypeCreate,
    CustomizationTypeUpdate,
    CustomizationPositionCreate,
    CustomizationPositionUpdate,
    ProductCustomizationCreate,
    AddCustomizationToOrderItem,
)


class CustomizationService:

    # ════════════════════════════════════════════════════════════
    # TYPES
    # ════════════════════════════════════════════════════════════

    @staticmethod
    def get_all_types(
        db: Session,
        is_active: Optional[bool] = None
    ):
        return CustomizationRepository.get_all_types(
            db,
            is_active
        )

    @staticmethod
    def get_type(
        db: Session,
        type_id: int
    ):
        ct = CustomizationRepository.get_type_by_id(
            db,
            type_id
        )

        if not ct:
            raise HTTPException(
                status_code=404,
                detail="Customization type not found"
            )

        return ct

    @staticmethod
    def create_type(
        db: Session,
        data: CustomizationTypeCreate
    ):
        return CustomizationRepository.create_type(
            db,
            data
        )

    @staticmethod
    def update_type(
        db: Session,
        type_id: int,
        data: CustomizationTypeUpdate
    ):
        ct = CustomizationRepository.update_type(
            db,
            type_id,
            data
        )

        if not ct:
            raise HTTPException(
                status_code=404,
                detail="Customization type not found"
            )

        return ct

    @staticmethod
    def delete_type(
        db: Session,
        type_id: int
    ):
        ct = CustomizationRepository.delete_type(
            db,
            type_id
        )

        if not ct:
            raise HTTPException(
                status_code=404,
                detail="Customization type not found"
            )

        return {
            "message": f"Customization type {type_id} deactivated"
        }

    # ════════════════════════════════════════════════════════════
    # POSITIONS
    # ════════════════════════════════════════════════════════════

    @staticmethod
    def get_all_positions(db: Session):
        return CustomizationRepository.get_all_positions(db)

    @staticmethod
    def get_position(
        db: Session,
        pos_id: int
    ):
        cp = CustomizationRepository.get_position_by_id(
            db,
            pos_id
        )

        if not cp:
            raise HTTPException(
                status_code=404,
                detail="Customization position not found"
            )

        return cp

    @staticmethod
    def create_position(
        db: Session,
        data: CustomizationPositionCreate
    ):
        return CustomizationRepository.create_position(
            db,
            data
        )

    @staticmethod
    def update_position(
        db: Session,
        pos_id: int,
        data: CustomizationPositionUpdate
    ):
        cp = CustomizationRepository.update_position(
            db,
            pos_id,
            data
        )

        if not cp:
            raise HTTPException(
                status_code=404,
                detail="Customization position not found"
            )

        return cp

    @staticmethod
    def delete_position(
        db: Session,
        pos_id: int
    ):
        cp = CustomizationRepository.delete_position(
            db,
            pos_id
        )

        if not cp:
            raise HTTPException(
                status_code=404,
                detail="Customization position not found"
            )

        return {
            "message": f"Position {pos_id} deleted"
        }

    # ════════════════════════════════════════════════════════════
    # PRODUCT CUSTOMIZATIONS
    # ════════════════════════════════════════════════════════════

    @staticmethod
    def get_product_customizations(
        db: Session,
        product_id: int
    ):
        return CustomizationRepository.get_product_customizations(
            db,
            product_id
        )

    @staticmethod
    def create_product_customization(
        db: Session,
        data: ProductCustomizationCreate
    ):
        return CustomizationRepository.create_product_customization(
            db,
            data
        )

    @staticmethod
    def delete_product_customization(
        db: Session,
        pc_id: int
    ):
        pc = CustomizationRepository.delete_product_customization(
            db,
            pc_id
        )

        if not pc:
            raise HTTPException(
                status_code=404,
                detail="Product customization not found"
            )

        return {
            "message": f"Product customization {pc_id} deleted"
        }

    # ════════════════════════════════════════════════════════════
    # ORDER ITEM CUSTOMIZATIONS
    # ════════════════════════════════════════════════════════════

    @staticmethod
    def get_order_item_customizations(
        db: Session,
        order_item_id: Optional[int] = None,
        approval_status: Optional[str] = None,
    ):
        return CustomizationRepository.get_order_item_customizations(
            db,
            order_item_id,
            approval_status
        )

    @staticmethod
    def get_pending_customizations(
        db: Session
    ):
        return CustomizationRepository.get_pending_customizations(
            db
        )

    @staticmethod
    def add_customization_to_order_item(
        db: Session,
        data: AddCustomizationToOrderItem
    ):
        try:
            return CustomizationRepository.add_customization_to_order_item(
                db,
                data
            )

        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=str(e)
            )

    @staticmethod
    def approve_customization(
        db: Session,
        customization_id: int,
        approved_by: int
    ):
        cust = CustomizationRepository.get_customization_by_id(
            db,
            customization_id
        )

        if not cust:
            raise HTTPException(
                status_code=404,
                detail="Customization not found"
            )

        if cust.approval_status == "APPROVED":
            raise HTTPException(
                status_code=400,
                detail="Already approved"
            )

        try:
            return CustomizationRepository.approve_customization(
                db,
                customization_id,
                approved_by
            )

        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=str(e)
            )

    @staticmethod
    def reject_customization(
        db: Session,
        customization_id: int,
        admin_id: int
    ):
        cust = CustomizationRepository.get_customization_by_id(
            db,
            customization_id
        )

        if not cust:
            raise HTTPException(
                status_code=404,
                detail="Customization not found"
            )

        if cust.approval_status != "PENDING":
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Cannot reject — "
                    f"status is '{cust.approval_status}'"
                )
            )

        return CustomizationRepository.reject_customization(
            db,
            customization_id,
            admin_id
        )