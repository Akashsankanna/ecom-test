from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.security import verify_token
from app.db.session import get_db
from app.models.user import User

security = HTTPBearer()


# 🔐 STEP 1: Extract + verify token
def get_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    return verify_token(token)


# 👤 STEP 2: Get user from DB
def get_current_user(
    db: Session = Depends(get_db),
    token: dict = Depends(get_token)   # ✅ correct chaining
):
    keycloak_id = token.get("sub")

    if not keycloak_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.keycloak_id == keycloak_id).first()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user


# 🛡️ STEP 3: Admin check (DB-based)
def require_admin(user: User = Depends(get_current_user)):
    if user.user_type != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin only"
        )
    return user


# 🎭 STEP 4: Role check (Keycloak roles)
def require_role(role: str):
    def checker(token: dict = Depends(get_token)):
        roles = token.get("realm_access", {}).get("roles", [])

        if role not in roles:
            raise HTTPException(
                status_code=403,
                detail=f"Access denied. Required role: '{role}'"
            )

        return token

    return checker


# 📧 STEP 5: Email verification
def require_email_verified(token: dict = Depends(get_token)):
    if not token.get("email_verified", False):
        raise HTTPException(
            status_code=403,
            detail="Email not verified"
        )

    return token