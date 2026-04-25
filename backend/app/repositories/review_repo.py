from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models.review import Review, ProductReview
from typing import Optional, List


class ReviewRepository:

    @staticmethod
    def get_all_reviews(
        db: Session,
        product_id: Optional[int] = None,
        is_approved: Optional[bool] = None,
        limit: int = 100,
    ) -> List[Review]:
        query = db.query(Review)
        if product_id:
            query = query.filter(Review.product_id == product_id)
        if is_approved is not None:
            query = query.filter(Review.is_approved == is_approved)
        return query.order_by(Review.created_at.desc()).limit(limit).all()

    @staticmethod
    def get_review_by_id(db: Session, review_id: int) -> Optional[Review]:
        return db.query(Review).filter(Review.id == review_id).first()

    @staticmethod
    def approve_review(db: Session, review_id: int) -> Optional[Review]:
        review = db.query(Review).filter(Review.id == review_id).first()
        if not review:
            return None
        review.is_approved = True
        db.commit()
        db.refresh(review)
        return review

    @staticmethod
    def reject_review(db: Session, review_id: int) -> Optional[Review]:
        review = db.query(Review).filter(Review.id == review_id).first()
        if not review:
            return None
        review.is_approved = False
        db.commit()
        db.refresh(review)
        return review

    @staticmethod
    def delete_review(db: Session, review_id: int) -> Optional[Review]:
        review = db.query(Review).filter(Review.id == review_id).first()
        if not review:
            return None
        db.delete(review)
        db.commit()
        return review

    @staticmethod
    def get_review_view(
        db: Session,
        product_id: Optional[int] = None,
        is_approved: Optional[bool] = None,
    ):
        """
        Admin review view:
        Direct table query instead of review_view
        Shows approved + unapproved
        """

        sql = """
            SELECT
                r.id,
                r.user_id,
                u.email AS user_email,
                r.product_id,
                p.name AS product_name,
                r.rating,
                r.title,
                r.comment,
                r.is_verified_purchase,
                r.is_approved,
                r.created_at
            FROM review r
            JOIN users u ON u.id = r.user_id
            JOIN product p ON p.id = r.product_id
            WHERE 1=1
        """

        params = {}

        if product_id is not None:
            sql += " AND r.product_id = :pid"
            params["pid"] = product_id

        if is_approved is not None:
            sql += " AND r.is_approved = :approved"
            params["approved"] = is_approved

        sql += " ORDER BY r.created_at DESC"

        result = db.execute(text(sql), params)
        return [dict(row) for row in result.mappings()]

    @staticmethod
    def get_product_rating_summary(db: Session):
        """Uses product_rating_summary DB view."""
        result = db.execute(
            text("SELECT * FROM product_rating_summary ORDER BY average_rating DESC NULLS LAST")
        )
        return [dict(row) for row in result.mappings()]