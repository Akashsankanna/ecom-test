from fastapi import APIRouter, Depends, HTTPException
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
    user_id: int,
    db: Session = Depends(get_db),
):
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required")

    return wishlist_service.get_wishlist(
        db=db,
        user_id=user_id,
        guest_uuid=None
    )


@router.post("/add")
def add_to_wishlist(
    data: WishlistItemIn,
    user_id: int,
    db: Session = Depends(get_db),
):
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required")

    result = wishlist_service.add_to_wishlist(
        db=db,
        user_id=user_id,
        guest_uuid=None,
        variant_id=data.variant_id
    )

    return {
        "message": "Added to wishlist",
        "data": result
    }


@router.delete("/remove")
def remove_from_wishlist(
    data: WishlistItemIn,
    user_id: int,
    db: Session = Depends(get_db),
):
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required")

    items = wishlist_service.get_wishlist(
        db=db,
        user_id=user_id,
        guest_uuid=None
    )

    target = next(
        (
            item for item in items
            if int(item.get("variant_id", 0)) == int(data.variant_id)
        ),
        None
    )

    if not target:
        raise HTTPException(status_code=404, detail="Wishlist item not found")

    wishlist_item_id = target.get("wishlist_item_id") or target.get("id")

    result = wishlist_service.remove_from_wishlist(
        db=db,
        wishlist_item_id=wishlist_item_id
    )

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
    user_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    result = wishlist_service.remove_from_wishlist(
        db=db,
        wishlist_item_id=wishlist_item_id
    )

    if not result:
        raise HTTPException(status_code=404, detail="Wishlist item not found")

    return {
        "message": "Removed from wishlist",
        "wishlist_item_id": wishlist_item_id
    }