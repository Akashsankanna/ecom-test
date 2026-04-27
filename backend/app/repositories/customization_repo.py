from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional, List

from app.models.customization import (
    CustomizationType,
    CustomizationPosition,
    ProductCustomization,
    OrderItemCustomization,
)


class CustomizationRepository:

    # ════════════════════════════════════════════════════════════
    # CUSTOMIZATION TYPES
    # ════════════════════════════════════════════════════════════

    @staticmethod
    def get_all_types(
        db: Session,
        is_active: Optional[bool] = None
    ) -> List[CustomizationType]:

        query = db.query(CustomizationType)

        if is_active is not None:
            query = query.filter(
                CustomizationType.is_active == is_active
            )

        return query.order_by(
            CustomizationType.id
        ).all()

    @staticmethod
    def get_type_by_id(
        db: Session,
        type_id: int
    ) -> Optional[CustomizationType]:

        return (
            db.query(CustomizationType)
            .filter(CustomizationType.id == type_id)
            .first()
        )

    @staticmethod
    def create_type(
        db: Session,
        data
    ) -> CustomizationType:

        ct = CustomizationType(
            name=data.name,
            description=data.description,
            is_active=(
                data.is_active
                if data.is_active is not None
                else True
            ),
            additional_price=data.additional_price or 0,
        )

        db.add(ct)
        db.commit()
        db.refresh(ct)

        return ct

    @staticmethod
    def update_type(
        db: Session,
        type_id: int,
        data
    ) -> Optional[CustomizationType]:

        ct = (
            db.query(CustomizationType)
            .filter(CustomizationType.id == type_id)
            .first()
        )

        if not ct:
            return None

        if data.name is not None:
            ct.name = data.name

        if data.description is not None:
            ct.description = data.description

        if data.is_active is not None:
            ct.is_active = data.is_active

        if data.additional_price is not None:
            ct.additional_price = data.additional_price

        db.commit()
        db.refresh(ct)

        return ct

    @staticmethod
    def delete_type(
        db: Session,
        type_id: int
    ) -> Optional[CustomizationType]:

        ct = (
            db.query(CustomizationType)
            .filter(CustomizationType.id == type_id)
            .first()
        )

        if not ct:
            return None

        ct.is_active = False

        db.commit()
        db.refresh(ct)

        return ct

    # ════════════════════════════════════════════════════════════
    # CUSTOMIZATION POSITIONS
    # ════════════════════════════════════════════════════════════

    @staticmethod
    def get_all_positions(
        db: Session
    ) -> List[CustomizationPosition]:

        return (
            db.query(CustomizationPosition)
            .order_by(CustomizationPosition.id)
            .all()
        )

    @staticmethod
    def get_position_by_id(
        db: Session,
        pos_id: int
    ) -> Optional[CustomizationPosition]:

        return (
            db.query(CustomizationPosition)
            .filter(CustomizationPosition.id == pos_id)
            .first()
        )

    @staticmethod
    def create_position(
        db: Session,
        data
    ) -> CustomizationPosition:

        cp = CustomizationPosition(
            name=data.name,
            description=data.description,
            additional_price=data.additional_price or 0,
        )

        db.add(cp)
        db.commit()
        db.refresh(cp)

        return cp

    @staticmethod
    def update_position(
        db: Session,
        pos_id: int,
        data
    ) -> Optional[CustomizationPosition]:

        cp = (
            db.query(CustomizationPosition)
            .filter(CustomizationPosition.id == pos_id)
            .first()
        )

        if not cp:
            return None

        if data.name is not None:
            cp.name = data.name

        if data.description is not None:
            cp.description = data.description

        if data.additional_price is not None:
            cp.additional_price = data.additional_price

        db.commit()
        db.refresh(cp)

        return cp

    @staticmethod
    def delete_position(
        db: Session,
        pos_id: int
    ) -> Optional[CustomizationPosition]:

        cp = (
            db.query(CustomizationPosition)
            .filter(CustomizationPosition.id == pos_id)
            .first()
        )

        if not cp:
            return None

        db.delete(cp)
        db.commit()

        return cp

    # ════════════════════════════════════════════════════════════
    # PRODUCT CUSTOMIZATIONS
    # ════════════════════════════════════════════════════════════

    @staticmethod
    def get_product_customizations(
        db: Session,
        product_id: int
    ) -> List[ProductCustomization]:

        return (
            db.query(ProductCustomization)
            .filter(
                ProductCustomization.product_id == product_id
            )
            .all()
        )

    @staticmethod
    def create_product_customization(
        db: Session,
        data
    ) -> ProductCustomization:

        pc = ProductCustomization(
            product_id=data.product_id,
            customization_type_id=data.customization_type_id,
            price=data.price or 0,
            is_required=data.is_required or False,
            max_text_length=data.max_text_length,
            allowed_file_types=data.allowed_file_types,
            is_active=(
                data.is_active
                if data.is_active is not None
                else True
            ),
        )

        db.add(pc)
        db.commit()
        db.refresh(pc)

        return pc

    @staticmethod
    def delete_product_customization(
        db: Session,
        pc_id: int
    ) -> Optional[ProductCustomization]:

        pc = (
            db.query(ProductCustomization)
            .filter(ProductCustomization.id == pc_id)
            .first()
        )

        if not pc:
            return None

        db.delete(pc)
        db.commit()

        return pc

    # ════════════════════════════════════════════════════════════
    # ORDER ITEM CUSTOMIZATIONS
    # ════════════════════════════════════════════════════════════

    @staticmethod
    def get_order_item_customizations(
        db: Session,
        order_item_id: Optional[int] = None,
        approval_status: Optional[str] = None,
    ) -> List[OrderItemCustomization]:

        query = db.query(OrderItemCustomization)

        if order_item_id:
            query = query.filter(
                OrderItemCustomization.order_item_id == order_item_id
            )

        if approval_status:
            query = query.filter(
                OrderItemCustomization.approval_status
                == approval_status.upper()
            )

        return query.order_by(
            OrderItemCustomization.created_at.desc()
        ).all()

    @staticmethod
    def get_customization_by_id(
        db: Session,
        cust_id: int
    ) -> Optional[OrderItemCustomization]:

        return (
            db.query(OrderItemCustomization)
            .filter(OrderItemCustomization.id == cust_id)
            .first()
        )

    @staticmethod
    def add_customization_to_order_item(
        db: Session,
        data
    ) -> Optional[OrderItemCustomization]:
        """Uses sp_add_customization_to_order_item."""

        db.execute(
            text(
                """
                CALL sp_add_customization_to_order_item(
                    :order_item_id,
                    :type_id,
                    :position_id,
                    :cust_value,
                    :image_url,
                    :add_price
                )
                """
            ),
            {
                "order_item_id": data.order_item_id,
                "type_id": data.customization_type_id,
                "position_id": data.position_id,
                "cust_value": data.customization_value,
                "image_url": data.image_url,
                "add_price": float(data.additional_price or 0),
            },
        )

        db.commit()
        db.expire_all()

        return (
            db.query(OrderItemCustomization)
            .filter(
                OrderItemCustomization.order_item_id
                == data.order_item_id
            )
            .order_by(
                OrderItemCustomization.created_at.desc()
            )
            .first()
        )

    @staticmethod
    def approve_customization(
        db: Session,
        customization_id: int,
        approved_by: int
    ) -> Optional[OrderItemCustomization]:
        """Uses sp_approve_customization."""

        db.execute(
            text(
                "CALL sp_approve_customization("
                ":cust_id, :approver)"
            ),
            {
                "cust_id": customization_id,
                "approver": approved_by
            },
        )

        db.commit()
        db.expire_all()

        return (
            db.query(OrderItemCustomization)
            .filter(
                OrderItemCustomization.id
                == customization_id
            )
            .first()
        )

    @staticmethod
    def reject_customization(
        db: Session,
        customization_id: int,
        admin_id: int
    ) -> Optional[OrderItemCustomization]:

        oic = (
            db.query(OrderItemCustomization)
            .filter(
                OrderItemCustomization.id
                == customization_id
            )
            .first()
        )

        if not oic:
            return None

        oic.approval_status = "REJECTED"
        oic.approved = False
        oic.approved_by = admin_id

        db.commit()
        db.refresh(oic)

        return oic

    @staticmethod
    def get_pending_customizations(
        db: Session
    ) -> List[OrderItemCustomization]:

        return (
            db.query(OrderItemCustomization)
            .filter(
                OrderItemCustomization.approval_status
                == "PENDING"
            )
            .order_by(
                OrderItemCustomization.created_at.asc()
            )
            .all()
        )