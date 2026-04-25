from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import Optional

from app.repositories.coupon_repo import CouponRepository
from app.schemas.coupon import CouponCreate, CouponUpdate


class CouponService:

    @staticmethod
    def get_all_coupons(db: Session, is_active: Optional[bool] = None):
        return CouponRepository.get_all_coupons(db, is_active)

    @staticmethod
    def get_coupon(db: Session, coupon_id: int):
        coupon = CouponRepository.get_coupon_by_id(db, coupon_id)

        if not coupon:
            raise HTTPException(404, "Coupon not found")

        return coupon

    @staticmethod
    def create_coupon(db: Session, data: CouponCreate, user_id: int):

        # validations
        if data.valid_from and data.valid_to:
            if data.valid_to <= data.valid_from:
                raise HTTPException(
                    status_code=400,
                    detail="valid_to must be after valid_from"
                )

        if data.discount_value <= 0:
            raise HTTPException(
                status_code=400,
                detail="Discount value must be greater than 0"
            )

        if data.discount_type.value == "PERCENTAGE":
            if data.discount_value > 100:
                raise HTTPException(
                    status_code=400,
                    detail="Percentage discount cannot exceed 100"
                )

        existing = CouponRepository.get_coupon_by_code(
            db,
            data.code
        )

        if existing:
            raise HTTPException(
                status_code=409,
                detail=f"Coupon code '{data.code}' already exists"
            )

        return CouponRepository.create_coupon(
            db,
            data,
            user_id
        )

    @staticmethod
    def update_coupon(
        db: Session,
        coupon_id: int,
        data: CouponUpdate,
        user_id: int
    ):
        coupon = CouponRepository.update_coupon(
            db,
            coupon_id,
            data,
            user_id
        )

        if not coupon:
            raise HTTPException(
                status_code=404,
                detail="Coupon not found"
            )

        return coupon

    @staticmethod
    def delete_coupon(db: Session, coupon_id: int):
        coupon = CouponRepository.delete_coupon(
            db,
            coupon_id
        )

        if not coupon:
            raise HTTPException(
                status_code=404,
                detail="Coupon not found"
            )

        return {
            "message": f"Coupon {coupon_id} deactivated successfully"
        }

    @staticmethod
    def get_performance(db: Session):
        return CouponRepository.get_coupon_performance_view(db)

    @staticmethod
    def get_usage(db: Session):
        return CouponRepository.get_coupon_usage_view(db)

    @staticmethod
    def apply_coupon(
        db: Session,
        code: str,
        user_id: int,
        order_id: int,
        order_amount: float,
        additional_discount: float = 0
    ):
        try:
            return CouponRepository.apply_coupon(
                db,
                code,
                user_id,
                order_id,
                order_amount,
                additional_discount
            )

        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=str(e)
            )