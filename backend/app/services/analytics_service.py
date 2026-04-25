"""
Analytics Service
GAP 7 FIX: Passes force_refresh parameter through to repo layer.
"""
from sqlalchemy.orm import Session
from app.repositories import analytics_repo


def get_dashboard(db: Session) -> dict:
    return analytics_repo.get_dashboard_stats(db)


def get_sales_summary(db: Session, force_refresh: bool = False, limit: int = 90):
    """
    GAP 7 FIX: force_refresh=True triggers REFRESH MATERIALIZED VIEW sales_summary.
    Without this, the view returns empty data on a fresh DB.
    """
    return analytics_repo.get_sales_summary(db, force_refresh=force_refresh, limit=limit)


def get_customer_lifetime_value(db: Session, limit: int = 100):
    return analytics_repo.get_customer_lifetime_value(db, limit)


def get_coupon_performance(db: Session):
    return analytics_repo.get_coupon_performance(db)


def get_top_selling_products(db: Session, limit: int = 20):
    return analytics_repo.get_top_selling_products(db, limit)


def get_product_rating_summary(db: Session):
    return analytics_repo.get_product_rating_summary(db)