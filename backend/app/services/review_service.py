from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import Optional

from app.repositories.review_repo import ReviewRepository
from app.models.product import Product
from app.models.user import User


class ReviewService:

    # ─────────────────────────────────────────
    # CREATE REVIEW
    # ─────────────────────────────────────────
    @staticmethod
    def create_review(
        db: Session,
        keycloak_id: str,
        product_id: int,
        rating: int,
        title: Optional[str],
        comment: Optional[str],
    ):

        # Map Keycloak sub → DB user
        db_user = (
            db.query(User)
            .filter(User.keycloak_id == keycloak_id)
            .first()
        )

        if not db_user:
            raise HTTPException(
                status_code=401,
                detail="User not found in database. Please log in again."
            )

        user_id = db_user.id

        # Prevent duplicate reviews
        if ReviewRepository.check_duplicate(
            db,
            user_id,
            product_id
        ):
            raise HTTPException(
                status_code=409,
                detail="You have already reviewed this product."
            )

        # Check product exists
        product = (
            db.query(Product)
            .filter(Product.id == product_id)
            .first()
        )

        if not product:
            raise HTTPException(
                status_code=404,
                detail="Product not found."
            )

        # Save review
        review = ReviewRepository.create_review(
            db=db,
            user_id=user_id,
            product_id=product_id,
            rating=rating,
            title=title,
            comment=comment,
        )

        return review

    # ─────────────────────────────────────────
    # PUBLIC REVIEWS
    # ─────────────────────────────────────────
    @staticmethod
    def get_public_reviews(
        db: Session,
        product_id: int
    ):
        return ReviewRepository.get_public_reviews(
            db,
            product_id
        )

    # ─────────────────────────────────────────
    # ADMIN
    # ─────────────────────────────────────────
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
        return ReviewRepository.get_review_view(
            db,
            product_id,
            is_approved
        )

    @staticmethod
    def get_rating_summary(
        db: Session
    ):
        return ReviewRepository.get_product_rating_summary(
            db
        )
