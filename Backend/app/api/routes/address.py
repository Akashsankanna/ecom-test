from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.address import AddressCreate, AddressUpdate
from app.services.address_service import (
    list_user_addresses,
    create_user_address,
    update_user_address,
    delete_user_address,
)

router = APIRouter(prefix="/address", tags=["Address"])


@router.get("/")
def get_addresses(
    user_id: int = Query(...),
    db: Session = Depends(get_db)
):
    return list_user_addresses(db, user_id)


@router.post("/")
def create_address(
    payload: AddressCreate,
    db: Session = Depends(get_db)
):
    return create_user_address(db, payload)


@router.put("/{address_id}")
def update_address(
    address_id: int,
    payload: AddressUpdate,
    db: Session = Depends(get_db)
):
    return update_user_address(db, address_id, payload)


@router.delete("/{address_id}")
def delete_address(
    address_id: int,
    user_id: int = Query(...),
    db: Session = Depends(get_db)
):
    return delete_user_address(db, address_id, user_id)