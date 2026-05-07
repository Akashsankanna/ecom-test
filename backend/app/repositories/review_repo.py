from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models.review import Review, ProductReview
from app.models.user import User
from typing import Optional, List


class ReviewRepository:

    # ─────────────────────────────────────────
    # PUBLIC: fetch approved reviews with user JOIN
    # Returns user_name + user_email via join
    # NO reviewer_name column — joined from users
    # ─────────────────────────────────────────
    @staticmethod
    def get_public_reviews(
        db: Session,
        product_id: int,
    ):
        """
        Fetch approved reviews for a product.
        """
        reviews = (
            db.query(
                Review.id,
                Review.user_id,
                Review.product_id,
                Review.rating,
                Review.title,
                Review.comment,
                Review.is_verified_purchase,
                Review.is_approved,
                Review.created_at,
                User.name.label("user_name"),
                User.email.label("user_email"),
            )
            .join(
                User,
                User.id == Review.user_id
            )
            .filter(
                Review.product_id == product_id,
                Review.is_approved == True
            )
            .order_by(
                Review.created_at.desc()
            )
            .all()
        )

        return [
            {
                "id": r.id,
                "user_id": r.user_id,
                "product_id": r.product_id,
                "rating": r.rating,
                "title": r.title,
                "comment": r.comment,
                "is_verified_purchase": r.is_verified_purchase,
                "is_approved": r.is_approved,
                "created_at": r.created_at,
                "user_name": r.user_name,
                "user_email": r.user_email,
            }
            for r in reviews
        ]

    # ─────────────────────────────────────────
    # DUPLICATE CHECK
    # ─────────────────────────────────────────
    @staticmethod
    def check_duplicate(
        db: Session,
        user_id: int,
        product_id: int,
    ) -> bool:
        """Returns True if this user already reviewed this product."""
        existing = (
            db.query(Review)
            .filter(
                Review.user_id == user_id,
                Review.product_id == product_id,
            )
            .first()
        )
        return existing is not None

    # ─────────────────────────────────────────
    # CREATE REVIEW
    # user_id must be INTEGER DB id — NOT Keycloak sub
    # ─────────────────────────────────────────
    @staticmethod
    def create_review(
        db: Session,
        user_id: int,
        product_id: int,
        rating: int,
        title: Optional[str],
        comment: Optional[str],
    ) -> Review:
        review = Review(
            user_id=user_id,
            product_id=product_id,
            rating=rating,
            title=title,
            comment=comment,
            is_verified_purchase=False,
            is_approved=True,
        )
        db.add(review)
        db.commit()
        db.refresh(review)
        return review

    # ─────────────────────────────────────────
    # ADMIN: all reviews (with optional filters)
    # ─────────────────────────────────────────
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

    # ─────────────────────────────────────────
    # ADMIN VIEW (full join)
    # ─────────────────────────────────────────
    @staticmethod
    def get_review_view(
        db: Session,
        product_id: Optional[int] = None,
        is_approved: Optional[bool] = None,
    ):
        sql = """
            SELECT
                r.id,
                r.user_id,
                u.email   AS user_email,
                u.name    AS user_name,
                r.product_id,
                p.name    AS product_name,
                r.rating,
                r.title,
                r.comment,
                r.is_verified_purchase,
                r.is_approved,
                r.created_at
            FROM review r
            JOIN users u   ON u.id  = r.user_id
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
        result = db.execute(
            text("SELECT * FROM product_rating_summary ORDER BY average_rating DESC NULLS LAST")
        )
        return [dict(row) for row in result.mappings()]