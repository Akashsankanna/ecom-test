from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional, List

from app.models.coupon import Coupon
from app.models.coupon_usage import CouponUsage


class CouponRepository:

    @staticmethod
    def get_all_coupons(
        db: Session,
        is_active: Optional[bool] = None
    ) -> List[Coupon]:

        query = db.query(Coupon)

        if is_active is not None:
            query = query.filter(
                Coupon.is_active == is_active
            )

        return query.order_by(
            Coupon.created_at.desc()
        ).all()

    @staticmethod
    def get_coupon_by_id(
        db: Session,
        coupon_id: int
    ) -> Optional[Coupon]:

        return (
            db.query(Coupon)
            .filter(Coupon.id == coupon_id)
            .first()
        )

    @staticmethod
    def get_coupon_by_code(
        db: Session,
        code: str
    ) -> Optional[Coupon]:

        return (
            db.query(Coupon)
            .filter(Coupon.code == code.upper())
            .first()
        )

    @staticmethod
    def create_coupon(
        db: Session,
        data,
        user_id: int
    ) -> Coupon:

        coupon = Coupon(
            code=data.code.upper(),
            description=data.description,
            discount_type=data.discount_type.value,
            discount_value=data.discount_value,
            min_order_amount=data.min_order_amount or 0,
            max_discount_amount=data.max_discount_amount,
            usage_limit=data.usage_limit,
            valid_from=data.valid_from,
            valid_to=data.valid_to,
            is_active=(
                data.is_active
                if data.is_active is not None
                else True
            ),
            created_by=user_id,
        )

        db.add(coupon)
        db.commit()
        db.refresh(coupon)

        return coupon

    @staticmethod
    def update_coupon(
        db: Session,
        coupon_id: int,
        data,
        user_id: int
    ) -> Optional[Coupon]:

        coupon = (
            db.query(Coupon)
            .filter(Coupon.id == coupon_id)
            .first()
        )

        if not coupon:
            return None

        if data.description is not None:
            coupon.description = data.description

        if data.discount_type is not None:
            coupon.discount_type = data.discount_type.value

        if data.discount_value is not None:
            coupon.discount_value = data.discount_value

        if data.min_order_amount is not None:
            coupon.min_order_amount = data.min_order_amount

        if data.max_discount_amount is not None:
            coupon.max_discount_amount = data.max_discount_amount

        if data.usage_limit is not None:
            coupon.usage_limit = data.usage_limit

        if data.valid_from is not None:
            coupon.valid_from = data.valid_from

        if data.valid_to is not None:
            coupon.valid_to = data.valid_to

        if data.is_active is not None:
            coupon.is_active = data.is_active

        coupon.updated_by = user_id

        db.commit()
        db.refresh(coupon)

        return coupon

    @staticmethod
    def delete_coupon(
        db: Session,
        coupon_id: int
    ) -> Optional[Coupon]:

        coupon = (
            db.query(Coupon)
            .filter(Coupon.id == coupon_id)
            .first()
        )

        if not coupon:
            return None

        coupon.is_active = False

        db.commit()
        db.refresh(coupon)

        return coupon

    @staticmethod
    def get_coupon_performance_view(db: Session):
        """Uses coupon_performance DB view."""

        result = db.execute(
            text("SELECT * FROM coupon_performance")
        )

        return [
            dict(row)
            for row in result.mappings()
        ]

    @staticmethod
    def get_coupon_usage_view(
        db: Session,
        coupon_id: Optional[int] = None
    ):
        """Uses coupon_usage_view DB view."""

        if coupon_id:
            result = db.execute(
                text(
                    "SELECT * FROM coupon_usage_view "
                    "WHERE id = :cid"
                ),
                {"cid": coupon_id},
            )
        else:
            result = db.execute(
                text("SELECT * FROM coupon_usage_view")
            )

        return [
            dict(row)
            for row in result.mappings()
        ]

    @staticmethod
    def apply_coupon(
        db: Session,
        code: str,
        user_id: int,
        order_id: int,
        order_amount: float,
        additional_discount: float = 0
    ):
        """
        Uses 5-param procedure:
        sp_apply_coupon(
            code,
            user_id,
            order_id,
            order_amount,
            additional_discount
        )
        """

        db.execute(
            text(
                """
                CALL sp_apply_coupon(
                    :code,
                    :user_id,
                    :order_id,
                    :order_amount,
                    :additional_discount
                )
                """
            ),
            {
                "code": code.upper(),
                "user_id": user_id,
                "order_id": order_id,
                "order_amount": order_amount,
                "additional_discount": additional_discount
            }
        )

        db.commit()

        return {
            "message": "Coupon applied successfully"
        }