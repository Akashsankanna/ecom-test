from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, EmailStr
import requests
from sqlalchemy.orm import Session

from app.services.auth_service import (
    initiate_signup,
    verify_signup,
    complete_signup,
    initiate_forgot_password,
    verify_forgot_otp,
    reset_password_with_token,
)
from app.db.session import get_db
from app.core.config import settings
from app.services.user_service import (
    create_user_in_db,
    get_user_by_keycloak_id,
    get_user_by_phone,
)

router = APIRouter()

CALLBACK_URL = "http://localhost:8000/auth/callback"
FRONTEND_URL = "http://localhost:9000"


# =========================
# SCHEMAS
# =========================
class SignupInit(BaseModel):
    phone: str

class SignupVerify(BaseModel):
    phone: str
    otp: str

class SignupComplete(BaseModel):
    name: str
    email: EmailStr
    password: str
    phone: str

class PasswordLogin(BaseModel):
    identifier: str   # ← phone (10 digits) OR email. NOT "email" field.
    password: str

class ForgotPasswordInit(BaseModel):
    phone: str

class ForgotPasswordVerify(BaseModel):
    phone: str
    otp: str

class ForgotPasswordReset(BaseModel):
    phone: str
    reset_token: str
    new_password: str
    confirm_password: str


# =========================
# OTP SIGNUP FLOW
# =========================
@router.post("/signup/initiate")
def signup_init(data: SignupInit):
    phone = data.phone.strip()
    if not phone.isdigit() or len(phone) != 10:
        raise HTTPException(status_code=400, detail="Phone number must be exactly 10 digits")
    return initiate_signup(phone)


@router.post("/signup/verify")
def signup_verify(data: SignupVerify):
    phone = data.phone.strip()
    if not phone.isdigit() or len(phone) != 10:
        raise HTTPException(status_code=400, detail="Phone number must be exactly 10 digits")
    return verify_signup(phone, data.otp)


@router.post("/signup/complete")
def signup_complete(data: SignupComplete, db: Session = Depends(get_db)):
    phone = data.phone.strip()
    if not phone.isdigit() or len(phone) != 10:
        raise HTTPException(status_code=400, detail="Phone number must be exactly 10 digits")
    return complete_signup(data.name, data.email, data.password, phone, db)


# =========================
# PASSWORD LOGIN
# identifier = phone number OR email
# =========================
@router.post("/login/password")
def login_with_password(data: PasswordLogin, db: Session = Depends(get_db)):
    identifier = data.identifier.strip()

    # If it's a phone number, look up the email in DB first
    keycloak_username = identifier
    if identifier.isdigit() and len(identifier) == 10:
        user = get_user_by_phone(db, identifier)
        if not user:
            raise HTTPException(status_code=401, detail="No account found with this phone number")
        keycloak_username = user.email
    elif "@" not in identifier:
        raise HTTPException(
            status_code=400,
            detail="Enter a valid email address or 10-digit phone number"
        )

    token_url = (
        f"{settings.KEYCLOAK_SERVER_URL}/realms/{settings.KEYCLOAK_REALM}"
        f"/protocol/openid-connect/token"
    )

    # ✅ client_secret is REQUIRED for confidential clients
    res = requests.post(token_url, data={
        "grant_type":    "password",
        "client_id":     settings.KEYCLOAK_CLIENT_ID,
        "client_secret": settings.KEYCLOAK_CLIENT_SECRET,
        "username":      keycloak_username,
        "password":      data.password,
        "scope":         "openid email profile",
    }, timeout=10)

    if res.status_code != 200:
        try:
            err_msg = res.json().get("error_description", "Invalid credentials")
        except Exception:
            err_msg = "Invalid credentials"
        raise HTTPException(status_code=401, detail=err_msg)

    token_json   = res.json()
    access_token = token_json.get("access_token")

    # Get user info
    userinfo_url = (
        f"{settings.KEYCLOAK_SERVER_URL}/realms/{settings.KEYCLOAK_REALM}"
        f"/protocol/openid-connect/userinfo"
    )
    userinfo_res = requests.get(
        userinfo_url,
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=10,
    )
    if userinfo_res.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to fetch user info from Keycloak")

    userinfo       = userinfo_res.json()
    keycloak_id    = userinfo.get("sub")
    email          = userinfo.get("email")
    name           = userinfo.get("name") or (email.split("@")[0] if email else "User")
    email_verified = userinfo.get("email_verified", False)

    # Block if email not verified
    if not email_verified:
        raise HTTPException(status_code=403, detail="EMAIL_NOT_VERIFIED")

    # Upsert in DB
    user = get_user_by_keycloak_id(db, keycloak_id)
    if not user:
        create_user_in_db(
            db=db, name=name, email=email, phone=None,
            keycloak_id=keycloak_id, is_email_verified=True,
        )
    else:
        _mark_email_verified_in_db(db, keycloak_id)

    return {
        "access_token": access_token,
        "id_token":     token_json.get("id_token"),
        "user": {
            "email":       email,
            "id": user.id,
            "name":        name,
            "keycloak_id": keycloak_id,
        }
    }


# =========================
# FORGOT PASSWORD
# =========================
@router.post("/forgot-password/initiate")
def forgot_password_init(data: ForgotPasswordInit, db: Session = Depends(get_db)):
    phone = data.phone.strip()
    if not phone.isdigit() or len(phone) != 10:
        raise HTTPException(status_code=400, detail="Phone number must be exactly 10 digits")
    user = get_user_by_phone(db, phone)
    if not user:
        raise HTTPException(status_code=404, detail="No account found with this phone number")
    return initiate_forgot_password(phone)


@router.post("/forgot-password/verify")
def forgot_password_verify(data: ForgotPasswordVerify):
    phone = data.phone.strip()
    if not phone.isdigit() or len(phone) != 10:
        raise HTTPException(status_code=400, detail="Phone number must be exactly 10 digits")
    return verify_forgot_otp(phone, data.otp)


@router.post("/forgot-password/reset")
def forgot_password_reset(data: ForgotPasswordReset, db: Session = Depends(get_db)):
    if data.new_password != data.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    if len(data.new_password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
    phone = data.phone.strip()
    user  = get_user_by_phone(db, phone)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return reset_password_with_token(
        phone=phone,
        reset_token=data.reset_token,
        new_password=data.new_password,
        keycloak_id=user.keycloak_id,
    )


# =========================
# VERIFY TOKEN
# =========================
@router.get("/verify-token")
def verify_token_endpoint(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    token = auth_header.split(" ", 1)[1]
    userinfo_url = (
        f"{settings.KEYCLOAK_SERVER_URL}/realms/{settings.KEYCLOAK_REALM}"
        f"/protocol/openid-connect/userinfo"
    )
    res = requests.get(userinfo_url, headers={"Authorization": f"Bearer {token}"}, timeout=10)
    if res.status_code != 200:
        raise HTTPException(status_code=401, detail="Invalid token")

    userinfo = res.json()
    if not userinfo.get("email_verified", False):
        raise HTTPException(status_code=403, detail="EMAIL_NOT_VERIFIED")

    return {
        "valid":       True,
        "keycloak_id": userinfo.get("sub"),
        "email":       userinfo.get("email"),
        "name":        userinfo.get("name"),
    }


# =========================
# GOOGLE LOGIN
# =========================
@router.get("/login/google")
def login_google():
    auth_url = (
        f"{settings.KEYCLOAK_SERVER_URL}/realms/{settings.KEYCLOAK_REALM}"
        f"/protocol/openid-connect/auth"
        f"?client_id={settings.KEYCLOAK_CLIENT_ID}"
        f"&response_type=code"
        f"&scope=openid+email+profile"
        f"&redirect_uri={CALLBACK_URL}"
    )
    return RedirectResponse(url=auth_url)


# =========================
# GOOGLE CALLBACK
# ✅ client_secret added to token exchange (was the "unauthorized_client" error)
# ✅ redirect_uri in verification email points to frontend /login
# =========================
@router.get("/callback")
def auth_callback(code: str, db: Session = Depends(get_db)):
    token_url = (
        f"{settings.KEYCLOAK_SERVER_URL}/realms/{settings.KEYCLOAK_REALM}"
        f"/protocol/openid-connect/token"
    )

    # ✅ THIS IS WHAT WAS CAUSING "unauthorized_client" — client_secret was missing
    token_res = requests.post(token_url, data={
        "grant_type":    "authorization_code",
        "client_id":     settings.KEYCLOAK_CLIENT_ID,
        "client_secret": settings.KEYCLOAK_CLIENT_SECRET,
        "code":          code,
        "redirect_uri":  CALLBACK_URL,
    }, timeout=10)

    if token_res.status_code != 200:
        raise HTTPException(
            status_code=400,
            detail=f"Token exchange failed: {token_res.text}"
        )

    token_json   = token_res.json()
    access_token = token_json.get("access_token")
    id_token     = token_json.get("id_token")

    userinfo_res = requests.get(
        f"{settings.KEYCLOAK_SERVER_URL}/realms/{settings.KEYCLOAK_REALM}"
        f"/protocol/openid-connect/userinfo",
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=10,
    )
    if userinfo_res.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to fetch userinfo")

    userinfo       = userinfo_res.json()
    keycloak_id    = userinfo.get("sub")
    email          = userinfo.get("email")
    name           = userinfo.get("name") or (email.split("@")[0] if email else "User")
    email_verified = userinfo.get("email_verified", False)

    # Save to DB if new
    user = get_user_by_keycloak_id(db, keycloak_id)
    if not user:
        create_user_in_db(
            db=db, name=name, email=email, phone=None,
            keycloak_id=keycloak_id, is_email_verified=email_verified,
        )

    if not email_verified:
        # ✅ redirect_uri = frontend /login so after clicking verify, user lands on login page
        _send_verification_email(keycloak_id)
        return RedirectResponse(
            f"{FRONTEND_URL}/auth/callback?blocked=true&email={email}"
        )

    _mark_email_verified_in_db(db, keycloak_id)

    return RedirectResponse(
        f"{FRONTEND_URL}/auth/callback"
        f"?access_token={access_token}"
        f"&id_token={id_token}"
        f"&email={email}"
        f"&name={name}"
        f"&keycloak_id={keycloak_id}"
    )


# =========================
# LOGOUT
# =========================
@router.get("/logout")
def logout(id_token_hint: str = None):
    logout_url = (
        f"{settings.KEYCLOAK_SERVER_URL}/realms/{settings.KEYCLOAK_REALM}"
        f"/protocol/openid-connect/logout"
        f"?post_logout_redirect_uri={FRONTEND_URL}/login"
        f"&client_id={settings.KEYCLOAK_CLIENT_ID}"
    )
    if id_token_hint:
        logout_url += f"&id_token_hint={id_token_hint}"
    return RedirectResponse(url=logout_url)


# =========================
# HELPERS
# =========================
def _get_admin_token() -> str:
    res = requests.post(
        f"{settings.KEYCLOAK_SERVER_URL}/realms/master/protocol/openid-connect/token",
        data={
            "client_id":  "admin-cli",
            "grant_type": "password",
            "username":   settings.KEYCLOAK_ADMIN_USERNAME,
            "password":   settings.KEYCLOAK_ADMIN_PASSWORD,
        },
        timeout=10,
    )
    if res.status_code != 200:
        raise HTTPException(
            status_code=500,
            detail=f"Could not get Keycloak admin token: {res.text}"
        )
    return res.json().get("access_token")


def _send_verification_email(keycloak_id: str):
    """
    Sends Keycloak VERIFY_EMAIL action email.
    redirect_uri = frontend /login so user lands there after clicking the link.
    """
    try:
        admin_token = _get_admin_token()
        resp = requests.put(
            f"{settings.KEYCLOAK_SERVER_URL}/admin/realms/{settings.KEYCLOAK_REALM}"
            f"/users/{keycloak_id}/execute-actions-email"
            f"?client_id={settings.KEYCLOAK_CLIENT_ID}"
            f"&redirect_uri={FRONTEND_URL}/login",
            json=["VERIFY_EMAIL"],
            headers={
                "Authorization": f"Bearer {admin_token}",
                "Content-Type":  "application/json",
            },
            timeout=10,
        )
        print(f"📧 Verification email API response: {resp.status_code} | {resp.text}")
    except Exception as e:
        print(f"⚠️ Failed to send verification email: {e}")


def _mark_email_verified_in_db(db: Session, keycloak_id: str):
    try:
        from sqlalchemy import text
        db.execute(
            text("UPDATE public.users SET is_email_verified = TRUE WHERE keycloak_id = :kid"),
            {"kid": keycloak_id},
        )
        db.commit()
    except Exception as e:
        print(f"⚠️ Could not update is_email_verified in DB: {e}")
        db.rollback()