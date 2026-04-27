from typing import Optional, List, Dict, Any
from sqlalchemy import text
from sqlalchemy.orm import Session


def get_user_by_id(db: Session, user_id: int) -> Optional[int]:
    query = text("""
        SELECT id
        FROM users
        WHERE id = :user_id
          AND COALESCE(is_deleted, FALSE) = FALSE
        LIMIT 1
    """)
    return db.execute(query, {"user_id": user_id}).scalar()


def get_addresses_by_user_id(db: Session, user_id: int) -> List[Dict[str, Any]]:
    query = text("""
        SELECT
            id,
            user_id,
            full_name,
            phone,
            address_line1,
            address_line2,
            landmark,
            city,
            state,
            country,
            postal_code,
            address_type,
            is_default,
            created_at,
            updated_at
        FROM address
        WHERE user_id = :user_id
        ORDER BY is_default DESC, id DESC
    """)
    result = db.execute(query, {"user_id": user_id})
    return [dict(row._mapping) for row in result.fetchall()]


def get_address_by_id_and_user_id(db: Session, address_id: int, user_id: int) -> Optional[Dict[str, Any]]:
    query = text("""
        SELECT
            id,
            user_id,
            full_name,
            phone,
            address_line1,
            address_line2,
            landmark,
            city,
            state,
            country,
            postal_code,
            address_type,
            is_default,
            created_at,
            updated_at
        FROM address
        WHERE id = :address_id
          AND user_id = :user_id
        LIMIT 1
    """)
    result = db.execute(query, {"address_id": address_id, "user_id": user_id}).mappings().first()
    return dict(result) if result else None


def clear_default_addresses(db: Session, user_id: int, exclude_address_id: Optional[int] = None) -> None:
    if exclude_address_id is None:
        query = text("""
            UPDATE address
            SET is_default = FALSE,
                updated_at = CURRENT_TIMESTAMP
            WHERE user_id = :user_id
              AND is_default = TRUE
        """)
        db.execute(query, {"user_id": user_id})
    else:
        query = text("""
            UPDATE address
            SET is_default = FALSE,
                updated_at = CURRENT_TIMESTAMP
            WHERE user_id = :user_id
              AND id <> :exclude_address_id
              AND is_default = TRUE
        """)
        db.execute(query, {
            "user_id": user_id,
            "exclude_address_id": exclude_address_id
        })


def create_address(db: Session, data: Dict[str, Any]) -> Dict[str, Any]:
    query = text("""
        INSERT INTO address (
            user_id,
            full_name,
            phone,
            address_line1,
            address_line2,
            landmark,
            city,
            state,
            country,
            postal_code,
            address_type,
            is_default,
            created_at,
            updated_at
        )
        VALUES (
            :user_id,
            :full_name,
            :phone,
            :address_line1,
            :address_line2,
            :landmark,
            :city,
            :state,
            :country,
            :postal_code,
            :address_type,
            :is_default,
            CURRENT_TIMESTAMP,
            CURRENT_TIMESTAMP
        )
        RETURNING
            id,
            user_id,
            full_name,
            phone,
            address_line1,
            address_line2,
            landmark,
            city,
            state,
            country,
            postal_code,
            address_type,
            is_default,
            created_at,
            updated_at
    """)
    result = db.execute(query, data).mappings().first()
    return dict(result)


def update_address(db: Session, address_id: int, user_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    query = text("""
        UPDATE address
        SET
            full_name = COALESCE(:full_name, full_name),
            phone = COALESCE(:phone, phone),
            address_line1 = COALESCE(:address_line1, address_line1),
            address_line2 = COALESCE(:address_line2, address_line2),
            landmark = COALESCE(:landmark, landmark),
            city = COALESCE(:city, city),
            state = COALESCE(:state, state),
            country = COALESCE(:country, country),
            postal_code = COALESCE(:postal_code, postal_code),
            address_type = COALESCE(:address_type, address_type),
            is_default = COALESCE(:is_default, is_default),
            updated_at = CURRENT_TIMESTAMP
        WHERE id = :address_id
          AND user_id = :user_id
        RETURNING
            id,
            user_id,
            full_name,
            phone,
            address_line1,
            address_line2,
            landmark,
            city,
            state,
            country,
            postal_code,
            address_type,
            is_default,
            created_at,
            updated_at
    """)
    params = {
        "address_id": address_id,
        "user_id": user_id,
        **data
    }
    result = db.execute(query, params).mappings().first()
    return dict(result) if result else None


def delete_address(db: Session, address_id: int, user_id: int) -> bool:
    query = text("""
        DELETE FROM address
        WHERE id = :address_id
          AND user_id = :user_id
    """)
    result = db.execute(query, {"address_id": address_id, "user_id": user_id})
    return result.rowcount > 0