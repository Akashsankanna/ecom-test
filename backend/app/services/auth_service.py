import uuid
import requests
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.config import settings
from app.utils.otp import generate_otp, verify_otp, store_reset_token, verify_reset_token
from app.integrations.sms_client import send_sms
from app.services.user_service import create_user_in_db


# =========================
# KEYCLOAK ADMIN TOKEN
# =========================
def get_admin_token() -> str:
    try:
        url = f"{settings.KEYCLOAK_SERVER_URL}/realms/master/protocol/openid-connect/token"
        res = requests.post(url, data={
            "client_id":  "admin-cli",
            "grant_type": "password",
            "username":   settings.KEYCLOAK_ADMIN_USERNAME,
            "password":   settings.KEYCLOAK_ADMIN_PASSWORD,
        }, timeout=10)

        if res.status_code != 200:
            raise HTTPException(status_code=500, detail=f"Failed to get admin token: {res.text}")

        token = res.json().get("access_token")
        if not token:
            raise HTTPException(status_code=500, detail="No access_token in admin response")
        return token

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Admin token error: {str(e)}")


# =========================
# OTP SIGNUP — INITIATE
# =========================
def initiate_signup(phone: str):
    try:
        print(f"📱 Initiating signup OTP for: {phone}")
        otp = generate_otp(phone)
        send_sms(phone, otp)
        print(f"✅ OTP sent to {phone}")
        return {"message": "OTP sent successfully", "phone": phone}
    except Exception as e:
        print(f"❌ Failed to send OTP: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to send OTP: {str(e)}")


# =========================
# OTP SIGNUP — VERIFY
# =========================
def verify_signup(phone: str, otp: str):
    try:
        result = verify_otp(phone, otp)
        if result == "expired":
            raise HTTPException(status_code=400, detail="OTP has expired. Please request a new one.")
        if not result:
            raise HTTPException(status_code=400, detail="Invalid OTP. Please try again.")
        return {"message": "OTP verified successfully", "phone": phone}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OTP verification failed: {str(e)}")


# =========================
# OTP SIGNUP — COMPLETE
# Creates Keycloak user with emailVerified=False,
# sends Keycloak verification email,
# saves to DB with is_email_verified=False.
# User must click the email link before logging in.
# =========================
def complete_signup(name: str, email: str, password: str, phone: str, db: Session):
    try:
        print(f"\n========== COMPLETE SIGNUP: {email} ==========")

        # 1. Create in Keycloak
        print("[1/3] Creating Keycloak user...")
        keycloak_id = _create_keycloak_user(name, email, password, phone)

        # 2. Send verification email via Keycloak
        print(f"[2/3] Sending email verification to {email}...")
        _send_keycloak_verification_email(keycloak_id)

        # 3. Save to DB
        print("[3/3] Saving to DB...")
        create_user_in_db(
            db=db,
            name=name,
            email=email,
            phone=phone,
            keycloak_id=keycloak_id,
            is_email_verified=False,
        )

        print(f"========== SIGNUP DONE — awaiting email verify ==========\n")
        return {
            "message":                     "Account created! Please verify your email before logging in.",
            "email":                       email,
            "keycloak_id":                 keycloak_id,
            "phone":                       phone,
            "requires_email_verification": True,
        }

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Signup failed: {str(e)}")


# =========================
# INTERNAL: Create Keycloak User
# emailVerified = False  ← Keycloak blocks login until user clicks the link
# =========================
def _create_keycloak_user(name: str, email: str, password: str, phone: str) -> str:
    """Returns keycloak_id (UUID string) of the created user."""
    try:
        token = get_admin_token()

        parts      = name.strip().split(" ", 1)
        first_name = parts[0]
        last_name  = parts[1] if len(parts) > 1 else ""

        payload = {
            "username":      email,
            "email":         email,
            "firstName":     first_name,
            "lastName":      last_name,
            "enabled":       True,
            "emailVerified": False,              # ← Must be False; Keycloak enforces verify
            "requiredActions": ["VERIFY_EMAIL"], # ← Keycloak will prompt/block until done
            "attributes": {"phone": [phone]},
            "credentials": [{
                "type":      "password",
                "value":     password,
                "temporary": False,
            }],
        }

        res = requests.post(
            f"{settings.KEYCLOAK_SERVER_URL}/admin/realms/{settings.KEYCLOAK_REALM}/users",
            json=payload,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type":  "application/json",
            },
            timeout=10,
        )

        if res.status_code == 409:
            raise HTTPException(status_code=409, detail="An account with this email already exists")
        if res.status_code != 201:
            raise HTTPException(status_code=400, detail=f"Keycloak create user error: {res.text}")

        print(f"✅ Keycloak user created: {email}")

        # Fetch the Keycloak ID
        res_get = requests.get(
            f"{settings.KEYCLOAK_SERVER_URL}/admin/realms/{settings.KEYCLOAK_REALM}"
            f"/users?username={email}",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10,
        )

        users = res_get.json()
        if not users:
            raise HTTPException(status_code=500, detail="User created but not found in Keycloak")

        keycloak_id = users[0]["id"]
        print(f"   Keycloak ID: {keycloak_id}")
        return keycloak_id

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create Keycloak user: {str(e)}"
        )


# =========================
# INTERNAL: Send Keycloak Verification Email
# ✅ redirect_uri = frontend /login so after clicking verify, user lands on login page
# =========================
def _send_keycloak_verification_email(keycloak_id: str):
    try:
        from app.core.config import settings as _s
        FRONTEND_URL = "http://localhost:9000"

        token = get_admin_token()
        resp  = requests.put(
            f"{_s.KEYCLOAK_SERVER_URL}/admin/realms/{_s.KEYCLOAK_REALM}"
            f"/users/{keycloak_id}/execute-actions-email"
            f"?client_id={_s.KEYCLOAK_CLIENT_ID}"
            f"&redirect_uri={FRONTEND_URL}/login",
            json=["VERIFY_EMAIL"],
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type":  "application/json",
            },
            timeout=10,
        )

        if resp.status_code in [200, 204]:
            print(f"✅ Verification email sent for keycloak_id={keycloak_id}")
        else:
            # Log but don't raise — user is created. Common reason: SMTP not configured in Keycloak.
            print(f"⚠️ execute-actions-email returned {resp.status_code}: {resp.text}")
            print("   → Check Realm Settings → Email tab in Keycloak Admin Console")

    except Exception as e:
        print(f"⚠️ _send_keycloak_verification_email failed: {e}")


# Public alias (used by auth.py routes)
def send_email_verification(email: str):
    """Lookup user by email and send verification email."""
    try:
        token = get_admin_token()
        res   = requests.get(
            f"{settings.KEYCLOAK_SERVER_URL}/admin/realms/{settings.KEYCLOAK_REALM}"
            f"/users?username={email}",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10,
        )
        users = res.json()
        if not users:
            raise HTTPException(status_code=404, detail="User not found in Keycloak")
        _send_keycloak_verification_email(users[0]["id"])
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send verification email: {str(e)}")


# =========================
# FORGOT PASSWORD — INITIATE
# =========================
def initiate_forgot_password(phone: str):
    try:
        otp = generate_otp(f"forgot:{phone}")   # separate namespace from signup
        send_sms(phone, otp)
        print(f"✅ Forgot-password OTP sent to {phone}")
        return {"message": "OTP sent to your registered phone number", "phone": phone}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send OTP: {str(e)}")


# =========================
# FORGOT PASSWORD — VERIFY OTP
# =========================
def verify_forgot_otp(phone: str, otp: str):
    result = verify_otp(f"forgot:{phone}", otp)

    if result == "expired":
        raise HTTPException(status_code=400, detail="OTP expired. Please request a new one.")
    if not result:
        raise HTTPException(status_code=400, detail="Invalid OTP.")

    reset_token = store_reset_token(phone)   # valid 10 min
    return {
        "message":     "OTP verified. Set your new password.",
        "reset_token": reset_token,
        "phone":       phone,
    }


# =========================
# FORGOT PASSWORD — RESET
# Uses Keycloak Admin API to reset password (no DB password stored)
# =========================
def reset_password_with_token(phone: str, reset_token: str, new_password: str, keycloak_id: str):
    # 1. Validate reset token
    if not verify_reset_token(phone, reset_token):
        raise HTTPException(
            status_code=400,
            detail="Reset link is invalid or expired. Please start again."
        )

    # 2. Update password via Keycloak Admin API
    try:
        admin_token = get_admin_token()

        reset_res = requests.put(
            f"{settings.KEYCLOAK_SERVER_URL}/admin/realms/{settings.KEYCLOAK_REALM}"
            f"/users/{keycloak_id}/reset-password",
            json={
                "type":      "password",
                "value":     new_password,
                "temporary": False,
            },
            headers={
                "Authorization": f"Bearer {admin_token}",
                "Content-Type":  "application/json",
            },
            timeout=10,
        )

        if reset_res.status_code not in [200, 204]:
            raise HTTPException(
                status_code=400,
                detail=f"Keycloak password reset failed: {reset_res.text}"
            )

        print(f"✅ Password reset for keycloak_id={keycloak_id}")
        return {"message": "Password reset successfully. You can now login."}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Password reset failed: {str(e)}")