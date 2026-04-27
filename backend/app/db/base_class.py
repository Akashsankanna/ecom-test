from app.db.base import Base  # 🔥 FIXED

from app.models.user import User
from app.models.product import Product
from app.models.product_variant import ProductVariant
from app.models.category import Category
from app.models.order import Order
from app.models.order_items import OrderItem
from app.models.payment_transaction import PaymentTransaction
from app.models.wishlist import Wishlist
from app.models.size_tax import TaxRate