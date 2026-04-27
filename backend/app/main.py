from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware

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

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        # local frontend
        "http://localhost:9000",
        "http://localhost:9001",
        "http://127.0.0.1:9000",
        "http://127.0.0.1:9001",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://localhost:8080",
        "http://localhost:8081",
        "http://127.0.0.1:8081",

        # LAN devices
        "http://192.168.1.11:9001",
        "http://192.168.100.55:9000",
        "http://192.168.100.50:8081",
        "http://192.168.1.30:8081",

        # tunnels
        "https://gttw6tjg-9000.inc1.devtunnels.ms",
        "https://bureau-agenda-packets-from.trycloudflare.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
app.include_router(shipment_admin.router)
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

# =====================================================
# KEYCLOAK JWT HELPERS
# =====================================================

from jose import jwt
import requests
from app.core.config import settings


def get_public_key() -> str:
    try:
        url = (
            f"{settings.KEYCLOAK_SERVER_URL}"
            f"/realms/{settings.KEYCLOAK_REALM}"
        )

        res = requests.get(url, timeout=10)
        res.raise_for_status()

        public_key = res.json()["public_key"]

        return (
            "-----BEGIN PUBLIC KEY-----\n"
            f"{public_key}\n"
            "-----END PUBLIC KEY-----"
        )

    except Exception as e:
        raise RuntimeError(
            f"Failed to fetch Keycloak public key: {e}"
        )


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
        raise HTTPException(
            status_code=401,
            detail=f"Invalid token: {str(e)}"
        )