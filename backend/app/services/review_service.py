from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import Optional

from app.repositories.review_repo import ReviewRepository
from app.models.review import Review
from app.models.product import Product
from app.models.user import User


class ReviewService:

    @staticmethod
    def get_all_reviews(
        db: Session,
        product_id: Optional[int] = None,
        is_approved: Optional[bool] = None,
        limit: int = 100,
    ):
        return ReviewRepository.get_all_reviews(
            db,
            product_id,
            is_approved,
            limit
        )

    @staticmethod
    def get_review(
        db: Session,
        review_id: int
    ):
        review = ReviewRepository.get_review_by_id(
            db,
            review_id
        )

        if not review:
            raise HTTPException(
                status_code=404,
                detail="Review not found"
            )

        return review

    @staticmethod
    def approve_review(
        db: Session,
        review_id: int
    ):
        review = ReviewRepository.approve_review(
            db,
            review_id
        )

        if not review:
            raise HTTPException(
                status_code=404,
                detail="Review not found"
            )

        return review

    @staticmethod
    def reject_review(
        db: Session,
        review_id: int
    ):
        review = ReviewRepository.reject_review(
            db,
            review_id
        )

        if not review:
            raise HTTPException(
                status_code=404,
                detail="Review not found"
            )

        return review

    @staticmethod
    def delete_review(
        db: Session,
        review_id: int
    ):
        review = ReviewRepository.delete_review(
            db,
            review_id
        )

        if not review:
            raise HTTPException(
                status_code=404,
                detail="Review not found"
            )

        return {
            "message": f"Review {review_id} deleted"
        }

    @staticmethod
    def get_review_view(
        db: Session,
        product_id: Optional[int] = None,
        is_approved: Optional[bool] = None,
    ):
        """
        Admin view:
        Queries raw review table joined
        with product + user.
        """

        query = (
            db.query(
                Review.id,
                Review.product_id,
                Product.name.label("product_name"),
                Review.user_id,
                User.email.label("user_email"),
                Review.rating,
                Review.title,
                Review.comment,
                Review.is_verified_purchase,
                Review.is_approved,
                Review.created_at,
            )
            .join(
                Product,
                Review.product_id == Product.id
            )
            .join(
                User,
                Review.user_id == User.id
            )
        )

        if product_id is not None:
            query = query.filter(
                Review.product_id == product_id
            )

        if is_approved is not None:
            query = query.filter(
                Review.is_approved == is_approved
            )

        rows = query.order_by(
            Review.created_at.desc()
        ).all()

        return [
            {
                "id": r.id,
                "product_id": r.product_id,
                "product_name": r.product_name,
                "user_id": r.user_id,
                "user_email": r.user_email,
                "rating": r.rating,
                "title": r.title,
                "comment": r.comment,
                "is_verified_purchase":
                    r.is_verified_purchase,
                "is_approved":
                    r.is_approved,
                "created_at":
                    r.created_at,
            }
            for r in rows
        ]

    @staticmethod
    def get_rating_summary(
        db: Session
    ):
        return ReviewRepository.get_product_rating_summary(
            db
        )