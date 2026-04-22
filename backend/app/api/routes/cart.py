from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Body, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.cart_service import (
    get_or_create_guest,
    get_or_create_cart,
    add_to_cart as add_to_cart_service,
    get_cart as get_cart_service,
    get_cart_summary as get_cart_summary_service,
    update_cart_qty,
    remove_from_cart,
    clear_cart as clear_cart_service,
    merge_guest_cart,
)

router = APIRouter(prefix="/cart", tags=["Cart"])


# =========================================================
# REQUEST SCHEMAS
# =========================================================

class AddToCartRequest(BaseModel):
    variant_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0)
    user_id: Optional[int] = None
    guest_uuid: Optional[str] = None


class UpdateCartRequest(BaseModel):
    cart_item_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0)
    user_id: Optional[int] = None
    guest_uuid: Optional[str] = None


class RemoveCartRequest(BaseModel):
    cart_item_id: int = Field(..., gt=0)
    user_id: Optional[int] = None
    guest_uuid: Optional[str] = None


class MergeCartRequest(BaseModel):
    guest_uuid: str
    user_id: int = Field(..., gt=0)


class ClearCartRequest(BaseModel):
    user_id: Optional[int] = None
    guest_uuid: Optional[str] = None


# =========================================================
# HELPERS
# =========================================================

def validate_cart_owner(user_id: Optional[int], guest_uuid: Optional[str]):
    if user_id is None and guest_uuid is None:
        raise HTTPException(
            status_code=400,
            detail="user_id or guest_uuid is required"
        )


# =========================================================
# GUEST
# =========================================================

@router.post("/guest")
def create_guest(db: Session = Depends(get_db)):
    """
    Create guest UUID for guest cart flow.
    """
    try:
        guest_uuid = get_or_create_guest(db)
        return {
            "success": True,
            "guest_uuid": guest_uuid
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Guest creation error: {str(e)}")


# =========================================================
# GET CART
# =========================================================

@router.get("/")
def get_cart(
    user_id: Optional[int] = Query(default=None),
    guest_uuid: Optional[str] = Query(default=None),
    db: Session = Depends(get_db)
):
    """
    Get full cart items.
    """
    validate_cart_owner(user_id, guest_uuid)

    try:
        items = get_cart_service(db, user_id=user_id, guest_uuid=guest_uuid)

        return {
            "success": True,
            "items": items,
            "count": len(items)
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Fetch cart error: {str(e)}")


@router.get("/summary")
def get_cart_summary(
    user_id: Optional[int] = Query(default=None),
    guest_uuid: Optional[str] = Query(default=None),
    db: Session = Depends(get_db)
):
    """
    Get cart totals summary.
    """
    validate_cart_owner(user_id, guest_uuid)

    try:
        summary = get_cart_summary_service(db, user_id=user_id, guest_uuid=guest_uuid)

        return {
            "success": True,
            "summary": summary
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Cart summary error: {str(e)}")


# =========================================================
# ADD TO CART
# =========================================================

@router.post("/add")
def add_to_cart(data: AddToCartRequest, db: Session = Depends(get_db)):
    """
    Add item to cart.
    """
    validate_cart_owner(data.user_id, data.guest_uuid)

    try:
        cart_id = get_or_create_cart(
            db,
            user_id=data.user_id,
            guest_uuid=data.guest_uuid
        )

        if not cart_id:
            raise HTTPException(status_code=500, detail="Could not get or create cart")

        added_item = add_to_cart_service(
            db=db,
            cart_id=cart_id,
            variant_id=data.variant_id,
            quantity=data.quantity
        )

        return {
            "success": True,
            "message": "Added to cart successfully",
            "cart_id": cart_id,
            "item": added_item
        }

    except HTTPException:
        raise
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Cart error: {str(e)}")


# =========================================================
# UPDATE CART ITEM
# =========================================================

@router.put("/update")
def update_cart(data: UpdateCartRequest, db: Session = Depends(get_db)):
    """
    Update cart item quantity.
    """
    validate_cart_owner(data.user_id, data.guest_uuid)

    try:
        updated_item = update_cart_qty(db, data.cart_item_id, data.quantity)

        return {
            "success": True,
            "message": "Cart updated successfully",
            "item": updated_item
        }
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Update error: {str(e)}")


# =========================================================
# REMOVE CART ITEM
# =========================================================

@router.delete("/remove")
def remove_cart_item(
    data: RemoveCartRequest = Body(...),
    db: Session = Depends(get_db)
):
    """
    Remove one item from cart.
    """
    validate_cart_owner(data.user_id, data.guest_uuid)

    try:
        result = remove_from_cart(db, data.cart_item_id)

        return {
            "success": True,
            "message": result.get("message", "Item removed successfully")
        }
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Remove error: {str(e)}")


# =========================================================
# CLEAR CART
# =========================================================

@router.delete("/clear")
def clear_cart(
    data: ClearCartRequest = Body(...),
    db: Session = Depends(get_db)
):
    """
    Clear full cart.
    """
    validate_cart_owner(data.user_id, data.guest_uuid)

    try:
        result = clear_cart_service(
            db,
            user_id=data.user_id,
            guest_uuid=data.guest_uuid
        )

        return {
            "success": True,
            "message": result.get("message", "Cart cleared successfully")
        }
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Clear cart error: {str(e)}")


# =========================================================
# MERGE GUEST CART
# =========================================================

@router.post("/merge")
def merge_cart(data: MergeCartRequest, db: Session = Depends(get_db)):
    """
    Merge guest cart into user cart after login.
    """
    try:
        result = merge_guest_cart(db, data.guest_uuid, data.user_id)

        return {
            "success": True,
            "message": result.get("message", "Cart merged successfully"),
            "user_cart_id": result.get("user_cart_id")
        }
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Merge error: {str(e)}")