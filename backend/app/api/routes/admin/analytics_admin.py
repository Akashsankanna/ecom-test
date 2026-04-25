from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.dependencies import require_admin
from app.repositories.analytics_repo import AnalyticsRepository

router = APIRouter(
    prefix="/admin",
    tags=["Admin - Analytics & Dashboard"]
)

# ════════════════════════════════════════════════════════════
# DASHBOARD
# ════════════════════════════════════════════════════════════

@router.get(
    "/dashboard",
    summary="Admin dashboard — total counts + revenue"
)
def get_dashboard(
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    """
    Returns:
    - total_users
    - total_products
    - total_orders
    - total_revenue
    - pending_orders
    - delivered_orders
    - cancelled_orders
    - pending_returns
    - low_stock_count
    - active_coupons
    """
    return AnalyticsRepository.get_dashboard_counts(db)


# ════════════════════════════════════════════════════════════
# SALES ANALYTICS
# ════════════════════════════════════════════════════════════

@router.get(
    "/analytics/sales",
    summary="Daily sales summary"
)
def get_sales_analytics(
    refresh: bool = Query(
        False,
        description=(
            "Pass true to refresh materialized view "
            "sales_summary before fetching"
        ),
    ),
    limit: int = Query(
        90,
        ge=1,
        le=365
    ),
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    """
    Uses sales_summary materialized view.
    If refresh=true, refreshes before fetching.
    """

    if refresh:
        AnalyticsRepository.refresh_sales_summary(db)

    return AnalyticsRepository.get_sales_summary(
        db,
        limit
    )


# ════════════════════════════════════════════════════════════
# CUSTOMER ANALYTICS
# ════════════════════════════════════════════════════════════

@router.get(
    "/analytics/customers",
    summary="Customer lifetime value"
)
def get_customer_analytics(
    limit: int = Query(
        100,
        ge=1,
        le=500
    ),
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    return AnalyticsRepository.get_customer_lifetime_value(
        db,
        limit
    )


# ════════════════════════════════════════════════════════════
# COUPON ANALYTICS
# ════════════════════════════════════════════════════════════

@router.get(
    "/analytics/coupons",
    summary="Coupon performance"
)
def get_coupon_analytics(
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    return AnalyticsRepository.get_coupon_performance(db)


# ════════════════════════════════════════════════════════════
# TOP PRODUCTS
# ════════════════════════════════════════════════════════════

@router.get(
    "/analytics/top-products",
    summary="Top selling products"
)
def get_top_products(
    limit: int = Query(
        20,
        ge=1,
        le=100
    ),
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    return AnalyticsRepository.get_top_selling_products(
        db,
        limit
    )


# ════════════════════════════════════════════════════════════
# RATINGS SUMMARY
# ════════════════════════════════════════════════════════════

@router.get(
    "/analytics/ratings",
    summary="Product rating summary"
)
def get_rating_summary(
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    return AnalyticsRepository.get_product_rating_summary(db)