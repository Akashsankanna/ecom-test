"""
Review schemas — strictly aligned with public.review DB table.
"""

from datetime import datetime
from typing import Optional

from pydantic import (
    BaseModel,
    field_validator
)


# =====================================================
# CREATE REVIEW
# =====================================================

class ReviewCreate(BaseModel):

    product_id: int

    rating: int

    title: Optional[str] = None

    comment: Optional[str] = None

    @field_validator("rating")
    @classmethod
    def rating_range(cls, v):

        if v < 1 or v > 5:
            raise ValueError(
                "Rating must be between 1 and 5"
            )

        return v


# =====================================================
# UPDATE REVIEW
# =====================================================

class ReviewUpdate(BaseModel):

    rating: Optional[int] = None

    title: Optional[str] = None

    comment: Optional[str] = None

    is_approved: Optional[bool] = None

    @field_validator("rating")
    @classmethod
    def rating_range(cls, v):

        if v is not None and (
            v < 1 or v > 5
        ):
            raise ValueError(
                "Rating must be between 1 and 5"
            )

        return v


# =====================================================
# RAW REVIEW OUTPUT
# =====================================================

class ReviewOut(BaseModel):

    id: int

    user_id: int

    product_id: int

    rating: int

    title: Optional[str] = None

    comment: Optional[str] = None

    is_verified_purchase: Optional[bool] = False

    is_approved: Optional[bool] = True

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# =====================================================
# PUBLIC REVIEW OUTPUT
# =====================================================

class ReviewPublicOut(BaseModel):

    id: int

    user_id: int

    product_id: int

    rating: int

    title: Optional[str] = None

    comment: Optional[str] = None

    is_verified_purchase: Optional[bool] = False

    is_approved: Optional[bool] = True

    created_at: Optional[datetime] = None

    # Joined fields from users table
    user_name: Optional[str] = None

    user_email: Optional[str] = None

    class Config:
        from_attributes = True


# =====================================================
# ADMIN REVIEW VIEW
# =====================================================

class ReviewViewOut(BaseModel):

    id: int

    product_id: int

    product_name: Optional[str] = None

    user_id: int

    user_email: Optional[str] = None

    user_name: Optional[str] = None

    rating: int

    title: Optional[str] = None

    comment: Optional[str] = None

    is_verified_purchase: Optional[bool] = False

    is_approved: Optional[bool] = True

    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# =====================================================
# PRODUCT RATING SUMMARY
# =====================================================

class ProductRatingSummaryOut(BaseModel):

    product_id: int

    product_name: str

    total_reviews: int

    average_rating: Optional[float] = None

    class Config:
        from_attributes = True
