from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from app.db.session import get_db
from app.db import base_class  # keep this for model registration
from app.api.routes.address import router as address_router
from app.api.routes.checkout_route import router as checkout_router
from app.api.routes.bulk_orders import router as bulk_routers

from app.api.routes import auth, test_auth
from app.api.routes.cart import router as cart_router
from app.api.routes.products import router as products_router
from app.api.routes.payments import router as payment_router
from app.api.routes.wishlist import router as wishlist_router
from app.api.routes.orders import router as orders_router 
from app.api.routes import payment_webhook

from app.api.routes.admin import (
    dashboard,
    product_admin,
    order_admin,
    payment_admin,
    support_admin,
    inventory_admin
)

app = FastAPI(title="Healthcare Backend")

print("MAIN.PY LOADED")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:9000",
        "http://localhost:9001",
        "http://127.0.0.1:9000",
        "http://127.0.0.1:9001",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://192.168.1.11:9001",
        "https://gttw6tjg-9000.inc1.devtunnels.ms",
        "http://192.168.100.55:9000",
        "http://localhost:8081",
        "http://127.0.0.1:8081",
        "http://192.168.100.50:8081",
        "http://192.168.1.30:8081",
        "https://bureau-agenda-packets-from.trycloudflare.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Root
@app.get("/", tags=["Root"])
def root():
    return {"message": "Healthcare API is running"}

# DB health check
@app.get("/test/db", tags=["Test"])
def test_db(db=Depends(get_db)):
    return {"message": "DB connected"}

# Auth/Test routers
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(test_auth.router, prefix="/test", tags=["Test"])

# Main routers
app.include_router(cart_router)
app.include_router(products_router)
app.include_router(payment_router)
app.include_router(wishlist_router)
app.include_router(bulk_routers)

# Admin routers
app.include_router(dashboard.router)
app.include_router(product_admin.router)
app.include_router(order_admin.router)
app.include_router(payment_admin.router)
app.include_router(support_admin.router)
app.include_router(inventory_admin.router)
app.include_router(address_router)
app.include_router(checkout_router)
app. include_router(orders_router)
app.include_router(payment_webhook.router)