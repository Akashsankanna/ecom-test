from passlib.context import CryptContext
from jose import jwt
from fastapi import HTTPException
import requests
import time

from app.core.config import settings

# =========================
# PASSWORD HASHING
# =========================
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

# =========================
# GLOBAL PUBLIC KEY CACHE
# =========================
PUBLIC_KEY = None


# =========================
# HASH PASSWORD
# =========================
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


# =========================
# FETCH KEYCLOAK PUBLIC KEY
# =========================
def get_public_key() -> str:
    url = f"{settings.KEYCLOAK_SERVER_URL}/realms/{settings.KEYCLOAK_REALM}"

    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch public key from Keycloak: {str(e)}"
        )

    public_key = res.json().get("public_key")

    if not public_key:
        raise HTTPException(
            status_code=500,
            detail="Public key not found in Keycloak response"
        )

    return f"-----BEGIN PUBLIC KEY-----\n{public_key}\n-----END PUBLIC KEY-----"


# =========================
# LOAD PUBLIC KEY WITH RETRY
# =========================
def load_public_key(retries: int = 5, delay: int = 3) -> str:
    global PUBLIC_KEY

    # Use cached key if already loaded
    if PUBLIC_KEY is not None:
        return PUBLIC_KEY

    last_error = None

    for _ in range(retries):
        try:
            PUBLIC_KEY = get_public_key()
            return PUBLIC_KEY
        except Exception as e:
            last_error = e
            time.sleep(delay)

    raise last_error


# =========================
# VERIFY JWT TOKEN
# =========================
def verify_token(token: str) -> dict:
    try:
        public_key = load_public_key()

        payload = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            audience="account",
            options={"verify_exp": True}
        )

        return payload

    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Invalid token: {str(e)}"
        )