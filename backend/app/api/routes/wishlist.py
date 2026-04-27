from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
from app.db.session import get_db
from app.services import wishlist_service

router = APIRouter(prefix="/wishlist", tags=["Wishlist"])

class WishlistItemIn(BaseModel):
    variant_id: int

@router.get("/")
def get_wishlist(db: Session = Depends(get_db),
                 user_id: Optional[int] = None,
                 guest_uuid: Optional[str] = Header(None, alias="guest-uuid")):
    if not user_id and not guest_uuid:
        raise HTTPException(400, "Provide user_id or guest_uuid")
    items = wishlist_service.get_wishlist(db, user_id, guest_uuid)
    return {"count": len(items), "items": items}

@router.post("/add")
def add_to_wishlist(data: WishlistItemIn, db: Session = Depends(get_db),
                    user_id: Optional[int] = None,
                    guest_uuid: Optional[str] = Header(None, alias="guest-uuid")):
    if not user_id and not guest_uuid:
        raise HTTPException(400, "Provide user_id or guest_uuid")
    wl_id = wishlist_service.get_or_create_wishlist(db, user_id, guest_uuid)
    wishlist_service.add_to_wishlist(db, wl_id, data.variant_id)
    return {"message": "Added to wishlist", "wishlist_id": wl_id}

@router.delete("/remove")
def remove_from_wishlist(data: WishlistItemIn, db: Session = Depends(get_db),
                         user_id: Optional[int] = None,
                         guest_uuid: Optional[str] = Header(None, alias="guest-uuid")):
    if not user_id and not guest_uuid:
        raise HTTPException(400, "Provide user_id or guest_uuid")
    wl_id = wishlist_service.get_or_create_wishlist(db, user_id, guest_uuid)
    wishlist_service.remove_from_wishlist(db, wl_id, data.variant_id)
    return {"message": "Removed from wishlist"}

@router.post("/merge")
def merge_wishlist(user_id: int, guest_uuid: str, db: Session = Depends(get_db)):
    wishlist_service.merge_wishlist(db, guest_uuid, user_id)
    return {"message": "Wishlist merged"}