from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os

from app.db.session import get_db
from app.db import base_class  # model registration side-effect

# =====================================================
# PUBLIC ROUTES
# =====================================================

from app.api.routes import auth, test_auth, payment_webhook
from app.api.routes.address import router as address_router
from app.api.routes.checkout_route import router as checkout_router
from app.api.routes.bulk_orders import router as bulk_router
from app.api.routes.cart import router as cart_router
from app.api.routes.products import router as products_router
from app.api.routes.payments import router as payment_router
from app.api.routes.wishlist import router as wishlist_router
from app.api.routes.orders import router as orders_router
from app.api.routes import tax_rate
from app.api.routes.admin import shipment_admin

from app.api.routes.reviews import router as review_router
from app.api.routes.invoice import router as invoice_router

# =====================================================
# ADMIN ROUTES
# =====================================================

from app.api.routes.admin import (
    analytics_admin,
    bulk_admin,
    coupon_admin,
    customization_admin,
    dashboard,
    exchange_admin,
    inventory_admin,
    notification_admin,
    order_admin,
    payment_admin,
    product_admin,
    return_admin,
    review_admin,
    shipment_admin,
    support_admin,
    user_admin,
)

# =====================================================
# APP INIT
# =====================================================

app = FastAPI(
    title="Pushpa Textiles Healthcare Backend API",
    description="""
Complete Ecommerce + Admin Backend

Includes:
- Auth
- Customer APIs
- Cart / Wishlist
- Checkout / Payments
- Orders / Returns / Exchanges
- Bulk Orders
- Admin Dashboard
- Products / Inventory
- Users / Roles
- Coupons
- Notifications
- Support
""",
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

print("MAIN.PY LOADED")

# =====================================================
# CORS
# =====================================================

cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:9000,http://localhost:9001,http://127.0.0.1:9000,http://127.0.0.1:9001").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================================
# RATE LIMITING
# =====================================================
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(Exception, lambda request, exc: {"detail": str(exc)})

# Global rate limit: 1000 requests per minute per IP
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse

@app.exception_handler(RateLimitExceeded)
async def rate_limit_exceeded_handler(request, exc):
    return JSONResponse(
        status_code=429,
        content={"detail": "Too many requests. Please try again later."},
    )

# =====================================================
# ROOT / HEALTH
# =====================================================

@app.get("/", tags=["Root"])
def root():
    return {
        "message": "Pushpa Textiles Healthcare API is running",
        "version": "3.0.0",
        "docs": "/docs",
    }


@app.get("/health", tags=["Root"])
def health():
    return {"status": "ok"}


@app.get("/test/db", tags=["Test"])
def test_db(db=Depends(get_db)):
    return {"message": "DB connected"}


# =====================================================
# AUTH ROUTERS
# =====================================================

app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(test_auth.router, prefix="/test", tags=["Test"])

# =====================================================
# CUSTOMER / PUBLIC ROUTERS
# =====================================================

app.include_router(cart_router)
app.include_router(products_router)
app.include_router(payment_router)
app.include_router(wishlist_router)
app.include_router(bulk_router)
app.include_router(address_router)
app.include_router(checkout_router)
app.include_router(orders_router)
app.include_router(payment_webhook.router)
app.include_router(tax_rate.router)
app.include_router(review_router)
app.include_router(invoice_router)

# =====================================================
# ADMIN ROUTERS
# =====================================================

# dashboard / analytics
app.include_router(dashboard.router)
app.include_router(analytics_admin.router)

# product management
app.include_router(product_admin.router)
app.include_router(customization_admin.router)

# order management
app.include_router(order_admin.router)
# app.include_router(shipment_admin.router)
app.include_router(return_admin.router)
app.include_router(exchange_admin.router)

# payments / coupons
app.include_router(payment_admin.router)
app.include_router(coupon_admin.router)

# inventory
app.include_router(inventory_admin.router)

# users / roles
app.include_router(user_admin.router)

# bulk orders
app.include_router(bulk_admin.router)

# notifications / reviews / support
app.include_router(notification_admin.router)
app.include_router(review_admin.router)
app.include_router(support_admin.router)


app.include_router(shipment_admin.shipments_router)
app.include_router(shipment_admin.orders_shipment_router)
# =====================================================
# KEYCLOAK JWT HELPERS
# =====================================================
from jose import jwt
import requests
from app.core.config import settings


_cached_public_key = None

def get_public_key() -> str:
    global _cached_public_key
    if _cached_public_key:
        return _cached_public_key

    try:
        url = (
            f"{settings.KEYCLOAK_SERVER_URL}"
            f"/realms/{settings.KEYCLOAK_REALM}"
        )

        res = requests.get(url, timeout=10)
        res.raise_for_status()

        public_key = res.json()["public_key"]

        _cached_public_key = (
            "-----BEGIN PUBLIC KEY-----\n"
            f"{public_key}\n"
            "-----END PUBLIC KEY-----"
        )
        return _cached_public_key

    except Exception as e:
        raise RuntimeError(
            f"Failed to fetch Keycloak public key: {e}"
        )


def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            get_public_key(),
            algorithms=["RS256"],
            audience="account",
            options={"verify_exp": True},
        )

        return payload

    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Invalid token: {str(e)}"
        )
    
