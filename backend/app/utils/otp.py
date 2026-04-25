import random
import uuid
import redis
from app.core.config import settings

r = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=0,
    decode_responses=True,
)


def generate_otp(key: str) -> str:
    """Store a 6-digit OTP in Redis for 5 minutes. key = phone or 'forgot:phone'"""
    otp = str(random.randint(100000, 999999))
    r.setex(f"otp:{key}", 300, otp)
    return otp


def verify_otp(key: str, otp: str):
    """
    True      → correct, consumed
    "expired" → key missing from Redis
    False     → wrong OTP
    """
    stored = r.get(f"otp:{key}")
    if stored is None:
        return "expired"
    if stored == otp:
        r.delete(f"otp:{key}")
        return True
    return False


def store_reset_token(phone: str) -> str:
    """Generate and store a one-time password-reset token (10 min TTL)."""
    token = str(uuid.uuid4())
    r.setex(f"reset_token:{phone}", 600, token)
    return token


def verify_reset_token(phone: str, token: str) -> bool:
    """Validate and consume a reset token. Returns False if expired or wrong."""
    stored = r.get(f"reset_token:{phone}")
    if stored is None:
        return False
    if stored == token:
        r.delete(f"reset_token:{phone}")
        return True
    return False