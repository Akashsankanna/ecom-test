"""
Review routes.

POST /api/v1/reviews              → Auth required
GET  /api/v1/reviews/{product_id} → Public

Admin routes:
GET    /api/v1/reviews/admin/all
PATCH  /api/v1/reviews/admin/{id}/approve
PATCH  /api/v1/reviews/admin/{id}/reject
DELETE /api/v1/reviews/admin/{id}
GET    /api/v1/reviews/admin/view
GET    /api/v1/reviews/admin/rating-summary
"""

from typing import List, Optional

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)

from sqlalchemy.orm import Session

from app.core.dependencies import (
    get_current_user,
    require_admin,
)

from app.db.session import get_db

from app.models.user import User

from app.schemas.review import (
    ProductRatingSummaryOut,
    ReviewCreate,
    ReviewOut,
    ReviewPublicOut,
    ReviewViewOut,
)

from app.services.review_service import (
    ReviewService,
)

# =====================================================
# ROUTER
# =====================================================

router = APIRouter(
    prefix="/api/v1/reviews",
    tags=["Reviews"],
)


# =====================================================
# CREATE REVIEW
# =====================================================
@router.post("", response_model=ReviewOut, status_code=201)
def submit_review(
    data: ReviewCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):

    print("CURRENT USER TYPE:", type(current_user))
    print("CURRENT USER:", current_user)

    # CASE 1 → dict from Keycloak token
    if isinstance(current_user, dict):
        keycloak_id = current_user.get("sub")

    # CASE 2 → SQLAlchemy User model
    else:
        keycloak_id = getattr(current_user, "keycloak_id", None)

    if not keycloak_id:
        raise HTTPException(
            status_code=401,
            detail="Invalid Keycloak token."
        )

    review = ReviewService.create_review(
        db=db,
        keycloak_id=keycloak_id,
        product_id=data.product_id,
        rating=data.rating,
        title=data.title,
        comment=data.comment,
    )

    return review
# =====================================================
# PUBLIC PRODUCT REVIEWS
# =====================================================

@router.get(
    "/{product_id}",
    response_model=List[ReviewPublicOut],
)
def get_product_reviews(
    product_id: int,
    db: Session = Depends(get_db),
):
    """
    Public reviews for product.
    """

    return ReviewService.get_public_reviews(
        db=db,
        product_id=product_id,
    )


# =====================================================
# ADMIN: GET ALL REVIEWS
# =====================================================

@router.get(
    "/admin/all",
    response_model=List[ReviewOut],
)
def admin_get_all_reviews(
    product_id: Optional[int] = Query(None),
    is_approved: Optional[bool] = Query(None),
    limit: int = Query(100, ge=1, le=500),

    db: Session = Depends(get_db),

    _: User = Depends(require_admin),
):

    return ReviewService.get_all_reviews(
        db=db,
        product_id=product_id,
        is_approved=is_approved,
        limit=limit,
    )


# =====================================================
# ADMIN: APPROVE REVIEW
# =====================================================

@router.patch(
    "/admin/{review_id}/approve",
    response_model=ReviewOut,
)
def admin_approve_review(
    review_id: int,

    db: Session = Depends(get_db),

    _: User = Depends(require_admin),
):

    return ReviewService.approve_review(
        db=db,
        review_id=review_id,
    )


# =====================================================
# ADMIN: REJECT REVIEW
# =====================================================

@router.patch(
    "/admin/{review_id}/reject",
    response_model=ReviewOut,
)
def admin_reject_review(
    review_id: int,

    db: Session = Depends(get_db),

    _: User = Depends(require_admin),
):

    return ReviewService.reject_review(
        db=db,
        review_id=review_id,
    )


# =====================================================
# ADMIN: DELETE REVIEW
# =====================================================

@router.delete(
    "/admin/{review_id}",
)
def admin_delete_review(
    review_id: int,

    db: Session = Depends(get_db),

    _: User = Depends(require_admin),
):

    return ReviewService.delete_review(
        db=db,
        review_id=review_id,
    )


# =====================================================
# ADMIN: REVIEW VIEW
# =====================================================

@router.get(
    "/admin/view",
    response_model=List[ReviewViewOut],
)
def admin_review_view(
    product_id: Optional[int] = Query(None),

    is_approved: Optional[bool] = Query(None),

    db: Session = Depends(get_db),

    _: User = Depends(require_admin),
):

    return ReviewService.get_review_view(
        db=db,
        product_id=product_id,
        is_approved=is_approved,
    )


# =====================================================
# ADMIN: RATING SUMMARY
# =====================================================

@router.get(
    "/admin/rating-summary",
    response_model=List[ProductRatingSummaryOut],
)
def admin_rating_summary(
    db: Session = Depends(get_db),

    _: User = Depends(require_admin),
):

    return ReviewService.get_rating_summary(
        db=db,
    )
# ADD these two routes after the existing submit_review POST route
# and before the GET /{product_id} route

# =====================================================
# GET CURRENT USER'S REVIEW FOR A PRODUCT
# Used by frontend to detect existing review + prefill
# =====================================================
@router.get(
    "/my/{product_id}",
    response_model=Optional[ReviewOut],
)
def get_my_review(
    product_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Returns the authenticated user's review for this product.
    Returns null (HTTP 200 with null body) if no review exists yet.
    Frontend uses this to decide Write vs Edit mode.
    """
    if isinstance(current_user, dict):
        keycloak_id = current_user.get("sub")
    else:
        keycloak_id = getattr(current_user, "keycloak_id", None)

    if not keycloak_id:
        raise HTTPException(status_code=401, detail="Invalid token.")

    review = ReviewService.get_user_review(
        db=db,
        keycloak_id=keycloak_id,
        product_id=product_id,
    )

    return review  # None serializes to null in JSON — frontend handles this


# =====================================================
# UPDATE EXISTING REVIEW
# =====================================================
@router.put(
    "/{review_id}",
    response_model=ReviewOut,
)
def update_review(
    review_id: int,
    data: ReviewCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Update an existing review. Only the owner can update.
    Uses ReviewCreate schema — same fields as create.
    """
    if isinstance(current_user, dict):
        keycloak_id = current_user.get("sub")
    else:
        keycloak_id = getattr(current_user, "keycloak_id", None)

    if not keycloak_id:
        raise HTTPException(status_code=401, detail="Invalid token.")

    return ReviewService.update_review(
        db=db,
        keycloak_id=keycloak_id,
        review_id=review_id,
        rating=data.rating,
        title=data.title,
        comment=data.comment,
    )
