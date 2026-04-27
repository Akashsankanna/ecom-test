from fastapi import APIRouter, Depends
from app.core.dependencies import get_current_user, require_role

router = APIRouter()


@router.get("/public")
def public():
    return {"message": "Public endpoint"}


@router.get("/protected")
def protected(user=Depends(get_current_user)):
    return {
        "message": "You are authenticated",
        "user": user
    }


@router.get("/admin")
def admin(user=Depends(require_role("admin"))):
    return {"message": "Welcome Admin"}