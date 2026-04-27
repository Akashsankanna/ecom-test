"""
Review schemas — review table + product_review + review_view.
Import from: app.schemas.review
"""
from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime


class ReviewCreate(BaseModel):
    product_id: int
    rating: int
    title: Optional[str] = None
    comment: Optional[str] = None

    @field_validator("rating")
    @classmethod
    def rating_range(cls, v):
        if v < 1 or v > 5:
            raise ValueError("Rating must be between 1 and 5")
        return v


class ReviewUpdate(BaseModel):
    rating: Optional[int] = None
    title: Optional[str] = None
    comment: Optional[str] = None
    is_approved: Optional[bool] = None

    @field_validator("rating")
    @classmethod
    def rating_range(cls, v):
        if v is not None and (v < 1 or v > 5):
            raise ValueError("Rating must be between 1 and 5")
        return v


class ReviewOut(BaseModel):
    id: int
    user_id: int
    product_id: int
    rating: int
    title: Optional[str] = None
    comment: Optional[str] = None
    is_verified_purchase: bool
    is_approved: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ReviewViewOut(BaseModel):
    """Maps to review_view DB view — includes product_name and user_email."""
    id: int
    product_id: int
    product_name: Optional[str] = None
    user_id: int
    user_email: Optional[str] = None
    rating: int
    title: Optional[str] = None
    comment: Optional[str] = None
    is_verified_purchase: bool
    is_approved: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ProductRatingSummaryOut(BaseModel):
    """Maps to product_rating_summary DB view."""
    product_id: int
    product_name: str
    total_reviews: int
    average_rating: Optional[float] = None

    class Config:
        from_attributes = True