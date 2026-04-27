from typing import Dict, Any, List
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.repositories.address_repo import (
    get_user_by_id,
    get_addresses_by_user_id,
    get_address_by_id_and_user_id,
    clear_default_addresses,
    create_address as repo_create_address,
    update_address as repo_update_address,
    delete_address as repo_delete_address,
)


def list_user_addresses(db: Session, user_id: int) -> List[Dict[str, Any]]:
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return get_addresses_by_user_id(db, user_id)


def create_user_address(db: Session, payload) -> Dict[str, Any]:
    user = get_user_by_id(db, payload.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    data = payload.model_dump()

    if data.get("address_type"):
        data["address_type"] = data["address_type"].upper()

    if data.get("is_default") is True:
        clear_default_addresses(db, payload.user_id)

    new_address = repo_create_address(db, data)
    db.commit()
    return new_address


def update_user_address(db: Session, address_id: int, payload) -> Dict[str, Any]:
    existing = get_address_by_id_and_user_id(db, address_id, payload.user_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Address not found")

    data = payload.model_dump(exclude_unset=True)

    if data.get("address_type"):
        data["address_type"] = data["address_type"].upper()

    if data.get("is_default") is True:
        clear_default_addresses(db, payload.user_id, exclude_address_id=address_id)

    updated = repo_update_address(db, address_id, payload.user_id, data)
    db.commit()

    if not updated:
        raise HTTPException(status_code=404, detail="Address not found")

    return updated


def delete_user_address(db: Session, address_id: int, user_id: int) -> Dict[str, Any]:
    existing = get_address_by_id_and_user_id(db, address_id, user_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Address not found")

    deleted = repo_delete_address(db, address_id, user_id)
    db.commit()

    if not deleted:
        raise HTTPException(status_code=404, detail="Address not found")

    return {"message": "Address deleted successfully"}