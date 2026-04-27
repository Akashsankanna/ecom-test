from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from app.db.session import get_db

# ─── Auth ─────────────────────────────────────────────────────────────────────
from app.api.routes import auth
from app.api.routes import test_auth

# ─── Admin routers ────────────────────────────────────────────────────────────
from app.api.routes.admin import analytics_admin
from app.api.routes.admin import bulk_admin
from app.api.routes.admin import coupon_admin
from app.api.routes.admin import customization_admin
from app.api.routes.admin import exchange_admin
from app.api.routes.admin import inventory_admin
from app.api.routes.admin import notification_admin
from app.api.routes.admin import order_admin
from app.api.routes.admin import payment_admin
from app.api.routes.admin import product_admin
from app.api.routes.admin import return_admin
from app.api.routes.admin import review_admin
from app.api.routes.admin import shipment_admin
from app.api.routes.admin import support_admin
from app.api.routes.admin import user_admin

# ════════════════════════════════════════════════════════════
# APP INIT
# ════════════════════════════════════════════════════════════

app = FastAPI(
    title="Pushpa Textiles — Healthcare E-Commerce Admin API",
    description="""
## Pushpa Textiles — Complete Admin Backend (ecomdb21)

### Auth
All `/admin/*` endpoints require a Keycloak JWT Bearer token.
The token `sub` must match `keycloak_id` in `users` with `user_type='admin'`.

### Stored Procedures Used
`sp_update_order_status`, `sp_cancel_order`, `sp_create_shipment`,
`sp_update_shipment_status`, `sp_create_return_request`, `sp_approve_return_request`,
`sp_complete_refund`, `sp_create_exchange`, `sp_update_exchange_status`,
`sp_complete_exchange`, `sp_log_inventory`, `sp_process_payment`,
`sp_apply_coupon`, `sp_apply_additional_discount`, `sp_assign_role`,
`sp_delete_user`, `sp_update_user`, `sp_upsert_user_profile`,
`sp_create_notification`, `sp_convert_bulk_request_to_order`,
`sp_update_bulk_order_status`, `sp_add_customization_to_order_item`,
`sp_approve_customization`, `sp_add_product_image`

### DB Views Used
`order_view`, `order_tracking_view`, `exchange_view`, `return_request_view`,
`payment_view`, `low_stock_products`, `product_full_view`, `v_active_products`,
`coupon_performance`, `coupon_usage_view`, `customer_lifetime_value`,
`sales_summary`(materialized), `top_selling_products`, `product_rating_summary`,
`review_view`, `user_access_view`, `user_full_access`, `address_view`,
`bulk_order_view`, `shipment_tracking_view`, `cart_view`, `wishlist_view`
    """,
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ════════════════════════════════════════════════════════════
# CORS
# ════════════════════════════════════════════════════════════

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:9000",
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ════════════════════════════════════════════════════════════
# UTILITY
# ════════════════════════════════════════════════════════════

@app.get("/", tags=["Root"])
def root():
    return {
        "message": "Pushpa Textiles Healthcare API",
        "version": "3.0.0",
        "docs": "/docs",
    }


@app.get("/health", tags=["Root"])
def health():
    return {"status": "ok"}


@app.get("/test/db", tags=["Test"])
def test_db(db=Depends(get_db)):
    return {"message": "DB connected"}

# ════════════════════════════════════════════════════════════
# AUTH
# ════════════════════════════════════════════════════════════

app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(test_auth.router, prefix="/test", tags=["Test"])

# ════════════════════════════════════════════════════════════
# ADMIN — ANALYTICS & DASHBOARD
# GET /admin/dashboard
# GET /admin/analytics/sales      → sales_summary (materialized view)
# GET /admin/analytics/customers  → customer_lifetime_value view
# GET /admin/analytics/coupons    → coupon_performance view
# GET /admin/analytics/top-products → top_selling_products view
# GET /admin/analytics/ratings    → product_rating_summary view
# ════════════════════════════════════════════════════════════
app.include_router(analytics_admin.router)

# ════════════════════════════════════════════════════════════
# ADMIN — PRODUCTS
# GET/POST/PUT/DELETE /admin/products/categories
# GET/POST /admin/products/colors
# GET/POST/PUT/DELETE /admin/products/
# GET/POST/PUT/DELETE /admin/products/{id}/variants
# POST/DELETE /admin/products/{id}/images
# GET /admin/products/low-stock
# GET /admin/products/view/active  → v_active_products view (ecomdb21)
# POST /admin/products/{id}/bestseller → toggle bestseller (ecomdb21)
# ════════════════════════════════════════════════════════════
app.include_router(product_admin.router)

# ════════════════════════════════════════════════════════════
# ADMIN — CUSTOMIZATIONS (ecomdb21)
# GET/POST/PUT/DELETE /admin/customizations/types
# GET/POST/PUT/DELETE /admin/customizations/positions
# GET/POST/DELETE /admin/customizations/products
# GET/POST /admin/customizations/order-items
# GET /admin/customizations/order-items/pending
# POST /admin/customizations/order-items/{id}/approve → sp_approve_customization
# POST /admin/customizations/order-items/{id}/reject
# ════════════════════════════════════════════════════════════
app.include_router(customization_admin.router)

# ════════════════════════════════════════════════════════════
# ADMIN — ORDERS
# GET/GET /admin/orders/ + /{id}
# PUT /admin/orders/{id}/status      → sp_update_order_status
# POST /admin/orders/{id}/cancel     → sp_cancel_order
# GET /admin/orders/{id}/history
# POST /admin/orders/{id}/shipment   → sp_create_shipment
# GET /admin/orders/{id}/shipment
# POST /admin/orders/{id}/apply-discount → sp_apply_additional_discount (ecomdb21)
# POST /admin/orders/apply-coupon    → sp_apply_coupon 5-param (ecomdb21)
# GET /admin/orders/analytics/top-selling
# ════════════════════════════════════════════════════════════
app.include_router(order_admin.router)

# ════════════════════════════════════════════════════════════
# ADMIN — SHIPMENTS
# PUT /admin/shipments/{tracking}  → sp_update_shipment_status
# ════════════════════════════════════════════════════════════
app.include_router(shipment_admin.router)

# ════════════════════════════════════════════════════════════
# ADMIN — RETURNS  (mixed prefix)
# GET /admin/returns + /{id} + /view
# POST /admin/returns/{id}/approve → sp_approve_return_request
# POST /admin/returns/{id}/reject
# POST /admin/returns/{id}/refund  → sp_complete_refund
# POST /returns (user-facing)      → sp_create_return_request
# ════════════════════════════════════════════════════════════
app.include_router(return_admin.router)

# ════════════════════════════════════════════════════════════
# ADMIN — EXCHANGES
# GET/POST /admin/exchanges/
# GET /admin/exchanges/view
# GET /admin/exchanges/{id}
# PUT /admin/exchanges/{id}/status  → sp_update_exchange_status
# POST /admin/exchanges/{id}/complete → sp_complete_exchange
# ════════════════════════════════════════════════════════════
app.include_router(exchange_admin.router)

# ════════════════════════════════════════════════════════════
# ADMIN — INVENTORY
# GET /admin/inventory/            → all variants stock
# GET /admin/inventory/low-stock   → low_stock_products view
# GET /admin/inventory/full-view   → product_full_view
# GET /admin/inventory/{id}
# PUT /admin/inventory/{id}
# GET /admin/inventory/logs/all
# GET /admin/inventory/logs/{variant_id}
# POST /admin/inventory/add-stock  → sp_log_inventory
# POST /admin/inventory/remove-stock → sp_log_inventory
# ════════════════════════════════════════════════════════════
app.include_router(inventory_admin.router)

# ════════════════════════════════════════════════════════════
# ADMIN — USERS
# GET /admin/users/ + /{id} + /roles + /access-view + /full-access + /audit-logs
# PUT /admin/users/{id}            → sp_update_user
# PUT /admin/users/{id}/profile    → sp_upsert_user_profile
# DELETE /admin/users/{id}         → sp_delete_user (1-param, ecomdb21)
# POST /admin/users/{id}/assign-role → sp_assign_role (2-param)
# DELETE /admin/users/{id}/remove-role
# ════════════════════════════════════════════════════════════
app.include_router(user_admin.router)

# ════════════════════════════════════════════════════════════
# ADMIN — COUPONS
# GET/POST/PUT/DELETE /admin/coupons/
# GET /admin/coupons/performance   → coupon_performance view
# GET /admin/coupons/usage         → coupon_usage_view
# ════════════════════════════════════════════════════════════
app.include_router(coupon_admin.router)

# ════════════════════════════════════════════════════════════
# ADMIN — PAYMENTS
# GET /admin/payments/ + /view + /summary + /{order_id}
# POST /admin/payments/process     → sp_process_payment
# ════════════════════════════════════════════════════════════
app.include_router(payment_admin.router)

# ════════════════════════════════════════════════════════════
# ADMIN — BULK ORDERS  (prefix=/admin)
# GET /admin/organizations
# GET/POST /admin/bulk-requests + /{id} + approve + reject + convert
# GET /admin/bulk-orders + /view + /{id}
# PUT /admin/bulk-orders/{id}/status   → sp_update_bulk_order_status (ecomdb21)
# GET /admin/bulk-orders/{id}/history
# PATCH /admin/bulk-orders/{id}/urgent  (ecomdb21)
# ════════════════════════════════════════════════════════════
app.include_router(bulk_admin.router)

# ════════════════════════════════════════════════════════════
# ADMIN — NOTIFICATIONS
# GET /admin/notifications/ + /pending + /{id}
# POST /admin/notifications/send   → sp_create_notification
# PATCH /admin/notifications/{id}/mark-sent
# PATCH /admin/notifications/{id}/mark-failed
# ════════════════════════════════════════════════════════════
app.include_router(notification_admin.router)

# ════════════════════════════════════════════════════════════
# ADMIN — REVIEWS
# GET /admin/reviews/ + /view + /ratings + /{id}
# POST /admin/reviews/{id}/approve
# POST /admin/reviews/{id}/reject
# DELETE /admin/reviews/{id}
# ════════════════════════════════════════════════════════════
app.include_router(review_admin.router)

# ════════════════════════════════════════════════════════════
# ADMIN — SUPPORT
# GET/POST /admin/support/invoices + /{order_id}
# GET /admin/support/audit-logs
# GET /admin/support/addresses + /user/{id}
# GET /admin/support/shipment-tracking
# GET/POST/PUT /admin/support/tax-rates
# GET/POST/DELETE /admin/support/sizes
# GET /admin/support/carts + /wishlists
# ════════════════════════════════════════════════════════════
app.include_router(support_admin.router)

# ════════════════════════════════════════════════════════════
# KEYCLOAK JWT — loaded once at startup
# ════════════════════════════════════════════════════════════

from jose import jwt
from fastapi import HTTPException
import requests
from app.core.config import settings


def get_public_key() -> str:
    try:
        url = f"{settings.KEYCLOAK_SERVER_URL}/realms/{settings.KEYCLOAK_REALM}"
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        public_key = res.json()["public_key"]
        return f"-----BEGIN PUBLIC KEY-----\n{public_key}\n-----END PUBLIC KEY-----"
    except Exception as e:
        raise RuntimeError(f"Failed to fetch Keycloak public key: {e}")


PUBLIC_KEY = get_public_key()


def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            PUBLIC_KEY,
            algorithms=["RS256"],
            audience="account",
            options={"verify_exp": True},
        )
        return payload
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
    
from app.api.routes import tax_rate

app.include_router(tax_rate.router)