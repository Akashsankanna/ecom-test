from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.db.session import get_db
from app.core.dependencies import require_admin
from app.services.review_service import ReviewService

router = APIRouter(
    prefix="/admin/reviews",
    tags=["Admin - Reviews"]
)

# ════════════════════════════════════════════════════════════
# LIST ALL REVIEWS
# ════════════════════════════════════════════════════════════

@router.get(
    "/",
    summary="List all reviews"
)
def get_all_reviews(
    product_id: Optional[int] = Query(
        None,
        description="Filter by product ID"
    ),
    is_approved: Optional[bool] = Query(
        None,
        description="Filter by approval status"
    ),
    limit: int = Query(
        100,
        ge=1,
        le=500
    ),
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    reviews = ReviewService.get_all_reviews(
        db,
        product_id,
        is_approved,
        limit
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
        }
        for r in reviews
    ]


# ════════════════════════════════════════════════════════════
# STATIC ROUTES FIRST
# IMPORTANT:
# /view and /ratings MUST stay above /{review_id}
# ════════════════════════════════════════════════════════════

@router.get(
    "/view",
    summary="Admin review view (approved + unapproved)"
)
def get_review_view(
    product_id: Optional[int] = Query(None),
    is_approved: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    """
    Raw review table join.
    NOT review_view because review_view only shows approved rows.
    """

    return ReviewService.get_review_view(
        db,
        product_id,
        is_approved
    )


@router.get(
    "/ratings",
    summary="Product rating summary"
)
def get_rating_summary(
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    """
    Uses:
    product_rating_summary view
    """

    return ReviewService.get_rating_summary(db)


# ════════════════════════════════════════════════════════════
# DYNAMIC ROUTES LAST
# ════════════════════════════════════════════════════════════

@router.get(
    "/{review_id}",
    summary="Get review by ID"
)
def get_review(
    review_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    r = ReviewService.get_review(
        db,
        review_id
    )

    return {
        "id": r.id,
        "user_id": r.user_id,
        "product_id": r.product_id,
        "rating": r.rating,
        "title": r.title,
        "comment": r.comment,
        "is_verified_purchase": r.is_verified_purchase,
        "is_approved": r.is_approved,
        "created_at": r.created_at,
    }


@router.post(
    "/{review_id}/approve",
    summary="Approve review"
)
def approve_review(
    review_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    r = ReviewService.approve_review(
        db,
        review_id
    )

    return {
        "message": f"Review {review_id} approved",
        "review_id": r.id,
        "is_approved": r.is_approved,
    }


@router.post(
    "/{review_id}/reject",
    summary="Reject review"
)
def reject_review(
    review_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    r = ReviewService.reject_review(
        db,
        review_id
    )

    return {
        "message": f"Review {review_id} rejected",
        "review_id": r.id,
        "is_approved": r.is_approved,
    }


@router.delete(
    "/{review_id}",
    summary="Delete review permanently"
)
def delete_review(
    review_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    return ReviewService.delete_review(
        db,
        review_id
    )