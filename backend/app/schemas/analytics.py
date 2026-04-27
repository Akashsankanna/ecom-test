"""
Analytics schemas — dashboard, sales_summary, customer_lifetime_value,
coupon_performance, top_selling_products, product_rating_summary views.
Import from: app.schemas.analytics
"""
from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
from datetime import date, datetime


class DashboardOut(BaseModel):
    total_users: int
    total_products: int
    total_orders: int
    total_revenue: float
    pending_orders: int
    delivered_orders: int
    cancelled_orders: int
    pending_returns: int
    low_stock_count: int
    active_coupons: int


class SalesSummaryOut(BaseModel):
    """Maps to sales_summary materialized view."""
    sale_date: Optional[date] = None
    total_orders: Optional[int] = None
    total_items_sold: Optional[int] = None
    total_revenue: Optional[Decimal] = None

    class Config:
        from_attributes = True


class CustomerLifetimeValueOut(BaseModel):
    """Maps to customer_lifetime_value DB view."""
    user_id: int
    email: Optional[str] = None
    total_orders: Optional[int] = None
    lifetime_value: Optional[Decimal] = None
    last_order_date: Optional[datetime] = None

    class Config:
        from_attributes = True


class CouponPerformanceOut(BaseModel):
    """Maps to coupon_performance DB view."""
    coupon_id: int
    code: str
    discount_type: str
    discount_value: Decimal
    used_count: int
    total_usages: Optional[int] = None
    total_revenue_generated: Optional[Decimal] = None

    class Config:
        from_attributes = True


class TopSellingProductOut(BaseModel):
    """Maps to top_selling_products DB view."""
    product_id: int
    product_name: str
    total_quantity_sold: Optional[int] = None
    total_revenue: Optional[Decimal] = None

    class Config:
        from_attributes = True


class ProductRatingSummaryOut(BaseModel):
    """Maps to product_rating_summary DB view."""
    product_id: int
    product_name: str
    total_reviews: int
    average_rating: Optional[Decimal] = None

    class Config:
        from_attributes = True