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
def get_wishlist(
    db: Session = Depends(get_db),
    user_id: Optional[int] = None,
    guest_uuid: Optional[str] = Header(None, alias="guest-uuid")
):
    if not user_id and not guest_uuid:
        raise HTTPException(status_code=400, detail="Provide user_id or guest_uuid")

    return wishlist_service.get_wishlist(db, user_id, guest_uuid)


@router.post("/add")
def add_to_wishlist(
    data: WishlistItemIn,
    db: Session = Depends(get_db),
    user_id: Optional[int] = None,
    guest_uuid: Optional[str] = Header(None, alias="guest-uuid")
):
    if not user_id and not guest_uuid:
        raise HTTPException(status_code=400, detail="Provide user_id or guest_uuid")

    result = wishlist_service.add_to_wishlist(
        db=db,
        user_id=user_id,
        guest_uuid=guest_uuid,
        variant_id=data.variant_id
    )

    return {
        "message": "Added to wishlist",
        "data": result
    }


@router.delete("/remove")
def remove_from_wishlist(
    data: WishlistItemIn,
    db: Session = Depends(get_db),
    user_id: Optional[int] = None,
    guest_uuid: Optional[str] = Header(None, alias="guest-uuid")
):
    if not user_id and not guest_uuid:
        raise HTTPException(status_code=400, detail="Provide user_id or guest_uuid")

    items = wishlist_service.get_wishlist(db, user_id, guest_uuid)

    target = next(
        (item for item in items if int(item["variant_id"]) == int(data.variant_id)),
        None
    )

    if not target:
        raise HTTPException(status_code=404, detail="Wishlist item not found")

    wishlist_item_id = target.get("wishlist_item_id") or target.get("id")

    result = wishlist_service.remove_from_wishlist(db, wishlist_item_id)

    if not result:
        raise HTTPException(status_code=404, detail="Wishlist item not found")

    return {
        "message": "Removed from wishlist",
        "wishlist_item_id": wishlist_item_id,
        "variant_id": data.variant_id
    }


@router.delete("/{wishlist_item_id}")
def remove_from_wishlist_by_id(
    wishlist_item_id: int,
    db: Session = Depends(get_db)
):
    result = wishlist_service.remove_from_wishlist(db, wishlist_item_id)

    if not result:
        raise HTTPException(status_code=404, detail="Wishlist item not found")

    return {
        "message": "Removed from wishlist",
        "wishlist_item_id": wishlist_item_id
    }


@router.post("/merge")
def merge_wishlist(
    user_id: int,
    guest_uuid: str,
    db: Session = Depends(get_db)
):
    wishlist_service.merge_wishlist(db, guest_uuid, user_id)

    return {
        "message": "Wishlist merged"
    }