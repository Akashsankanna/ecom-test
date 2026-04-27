from sqlalchemy.orm import Session
from sqlalchemy import text


class AnalyticsRepository:

    # ───────────────── DASHBOARD ─────────────────

    @staticmethod
    def get_dashboard_counts(db: Session) -> dict:

        total_users = db.execute(text(
            "SELECT COUNT(*) FROM users WHERE is_deleted = false"
        )).scalar()

        total_products = db.execute(text(
            "SELECT COUNT(*) FROM product "
            "WHERE is_deleted = false AND is_active = true"
        )).scalar()

        total_orders = db.execute(text(
            "SELECT COUNT(*) FROM orders "
            "WHERE status != 'CANCELLED'"
        )).scalar()

        total_revenue = db.execute(text(
            "SELECT COALESCE(SUM(total_amount),0) "
            "FROM orders "
            "WHERE status NOT IN ('CANCELLED','PAYMENT_FAILED')"
        )).scalar()

        pending_orders = db.execute(text(
            "SELECT COUNT(*) FROM orders WHERE status = 'PENDING'"
        )).scalar()

        delivered_orders = db.execute(text(
            "SELECT COUNT(*) FROM orders WHERE status = 'DELIVERED'"
        )).scalar()

        cancelled_orders = db.execute(text(
            "SELECT COUNT(*) FROM orders WHERE status = 'CANCELLED'"
        )).scalar()

        pending_returns = db.execute(text(
            "SELECT COUNT(*) FROM return_request "
            "WHERE status = 'REQUESTED'"
        )).scalar()

        low_stock_count = db.execute(text(
            "SELECT COUNT(*) FROM low_stock_products"
        )).scalar()

        active_coupons = db.execute(text(
            "SELECT COUNT(*) FROM coupon WHERE is_active = true"
        )).scalar()

        return {
            "total_users": total_users,
            "total_products": total_products,
            "total_orders": total_orders,
            "total_revenue": float(total_revenue or 0),
            "pending_orders": pending_orders,
            "delivered_orders": delivered_orders,
            "cancelled_orders": cancelled_orders,
            "pending_returns": pending_returns,
            "low_stock_count": low_stock_count,
            "active_coupons": active_coupons
        }

    # ───────────────── SALES ─────────────────

    @staticmethod
    def refresh_sales_summary(db: Session):
        db.execute(text("SELECT refresh_analytics()"))
        db.commit()

    @staticmethod
    def get_sales_summary(
        db: Session,
        limit: int = 90
    ):

        rows = db.execute(text("""
            SELECT sale_date,
                   total_orders,
                   total_items_sold,
                   total_revenue
            FROM sales_summary
            ORDER BY sale_date DESC
            LIMIT :lim
        """), {"lim": limit}).mappings().all()

        if not rows:
            AnalyticsRepository.refresh_sales_summary(db)

            rows = db.execute(text("""
                SELECT sale_date,
                       total_orders,
                       total_items_sold,
                       total_revenue
                FROM sales_summary
                ORDER BY sale_date DESC
                LIMIT :lim
            """), {"lim": limit}).mappings().all()

        return [dict(r) for r in rows]

    # ───────────────── CUSTOMERS ─────────────────

    @staticmethod
    def get_customer_lifetime_value(
        db: Session,
        limit: int = 100
    ):
        rows = db.execute(text("""
            SELECT *
            FROM customer_lifetime_value
            ORDER BY lifetime_value DESC
            LIMIT :lim
        """), {"lim": limit}).mappings().all()

        return [dict(r) for r in rows]

    # ───────────────── COUPONS ─────────────────

    @staticmethod
    def get_coupon_performance(db: Session):
        rows = db.execute(text(
            "SELECT * FROM coupon_performance"
        )).mappings().all()

        return [dict(r) for r in rows]

    # ───────────────── TOP PRODUCTS ─────────────────

    @staticmethod
    def get_top_selling_products(
        db: Session,
        limit: int = 20
    ):
        rows = db.execute(text("""
            SELECT *
            FROM top_selling_products
            LIMIT :lim
        """), {"lim": min(limit, 100)}).mappings().all()

        return [dict(r) for r in rows]

    # ───────────────── RATINGS ─────────────────

    @staticmethod
    def get_product_rating_summary(db: Session):
        rows = db.execute(text("""
            SELECT *
            FROM product_rating_summary
            ORDER BY average_rating DESC NULLS LAST
        """)).mappings().all()

        return [dict(r) for r in rows]