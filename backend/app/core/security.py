from jose import jwt
from fastapi import HTTPException
import requests
from app.core.config import settings


# 🔐 Fetch public key once
def get_public_key():
    url = f"{settings.KEYCLOAK_SERVER_URL}/realms/{settings.KEYCLOAK_REALM}"
    res = requests.get(url)
    if res.status_code != 200:
        raise HTTPException(status_code=500, detail="Failed to fetch public key")

    public_key = res.json()["public_key"]

    return f"-----BEGIN PUBLIC KEY-----\n{public_key}\n-----END PUBLIC KEY-----"


PUBLIC_KEY = get_public_key()


def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            PUBLIC_KEY,
            algorithms=["RS256"],
            audience="account",  # 🔥 IMPORTANT (matches your token)
            options={"verify_exp": True}
        )

        return payload

    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Invalid token: {str(e)}"
        )