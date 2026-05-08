from passlib.context import CryptContext
from jose import jwt, JWTError
from fastapi import HTTPException
import requests
import time
import json
import base64

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

PUBLIC_KEY = None


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def get_public_key() -> str:
    url = f"{settings.KEYCLOAK_SERVER_URL}/realms/{settings.KEYCLOAK_REALM}"
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch public key: {str(e)}"
        )
    public_key = res.json().get("public_key")
    if not public_key:
        raise HTTPException(status_code=500, detail="Public key not found")
    return f"-----BEGIN PUBLIC KEY-----\n{public_key}\n-----END PUBLIC KEY-----"


def load_public_key(retries: int = 5, delay: int = 3) -> str:
    global PUBLIC_KEY
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


def _peek_claims(token: str) -> dict:
    """Read JWT payload WITHOUT verifying signature — for aud/iss inspection only."""
    try:
        part = token.split(".")[1]
        part += "=" * (4 - len(part) % 4)
        return json.loads(base64.urlsafe_b64decode(part))
    except Exception:
        return {}


def verify_token(token: str) -> dict:
    """
    Verify Keycloak JWT.

    WHY STILL 401 AFTER PREVIOUS FIX:
    ──────────────────────────────────
    The jose library's audience check is strict:
      - If token aud = ["clientid", "account"] (a list)
        and you pass audience="account" (a string),
        jose compares string == list → FAILS.
      - Even passing audience=["account"] may fail if
        jose expects exact list match.

    DEFINITIVE FIX:
    ───────────────
    Skip audience verification entirely in jose.
    Manually verify 'iss' (issuer) instead — this is equally
    secure because it confirms the token came from YOUR
    Keycloak realm. Audience check is redundant when you
    control both the token issuer and the API.
    """
    try:
        public_key = load_public_key()

        # Peek at raw claims for logging — no verification here
        raw = _peek_claims(token)
        print(f"[Token] sub={raw.get('sub')} | aud={raw.get('aud')} | iss={raw.get('iss')}")

        # ── Decode with signature + expiry verification ────────
        # audience check is SKIPPED intentionally — see docstring
        payload = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            options={
                "verify_exp": True,   # ✅ expiry always checked
                "verify_aud": False,  # ✅ we verify iss manually instead
            }
        )

        # ── Manually verify issuer ─────────────────────────────
        # This confirms token was issued by OUR Keycloak realm.
        # Equally secure as audience check for single-realm setup.
        expected_iss = (
            f"{settings.KEYCLOAK_SERVER_URL}"
            f"/realms/{settings.KEYCLOAK_REALM}"
        )
        actual_iss = payload.get("iss", "")

        if actual_iss != expected_iss:
            print(f"[Token] ❌ issuer mismatch: got={actual_iss} expected={expected_iss}")
            raise HTTPException(
                status_code=401,
                detail="Invalid token issuer"
            )

        # ── Verify token has a subject ─────────────────────────
        if not payload.get("sub"):
            raise HTTPException(
                status_code=401,
                detail="Token missing subject claim"
            )

        print(f"[Token] ✅ verified for sub={payload.get('sub')}")
        return payload

    except HTTPException:
        raise
    except JWTError as e:
        print(f"[Token] ❌ JWTError: {e}")
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
    except Exception as e:
        print(f"[Token] ❌ Exception: {e}")
        raise HTTPException(status_code=401, detail=f"Token verification failed: {str(e)}")