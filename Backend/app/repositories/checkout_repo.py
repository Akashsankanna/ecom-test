from typing import Optional, Dict, Any, List
from sqlalchemy import text
from sqlalchemy.orm import Session


def get_cart_id_by_user_id(db: Session, user_id: int) -> Optional[int]:
    query = text("""
        SELECT id
        FROM cart
        WHERE user_id = :user_id
        ORDER BY id DESC
        LIMIT 1
    """)
    return db.execute(query, {"user_id": user_id}).scalar()


def is_valid_user_address(db: Session, user_id: int, address_id: int) -> bool:
    query = text("""
        SELECT 1
        FROM address
        WHERE id = :address_id
          AND user_id = :user_id
        LIMIT 1
    """)
    result = db.execute(query, {"address_id": address_id, "user_id": user_id}).scalar()
    return result is not None


def get_order_ids_by_user(db: Session, user_id: int) -> List[int]:
    query = text("""
        SELECT id
        FROM orders
        WHERE user_id = :user_id
        ORDER BY id
    """)
    rows = db.execute(query, {"user_id": user_id}).fetchall()
    return [row[0] for row in rows]


def call_sp_checkout(db: Session, cart_id: int, address_id: int) -> None:
    db.execute(
        text("CALL sp_checkout(:cart_id, :address_id)"),
        {"cart_id": cart_id, "address_id": address_id}
    )


def get_newly_created_order_id(before_ids: List[int], after_ids: List[int]) -> Optional[int]:
    before_set = set(before_ids)
    for order_id in after_ids:
        if order_id not in before_set:
            return order_id
    return None


def get_order_by_id(db: Session, order_id: int) -> Optional[Dict[str, Any]]:
    query = text("""
        SELECT
            id,
            user_id,
            address_id,
            total_amount,
            status,
            payment_status,
            created_at
        FROM orders
        WHERE id = :order_id
    """)
    row = db.execute(query, {"order_id": order_id}).mappings().first()
    return dict(row) if row else None


def get_order_items_by_order_id(db: Session, order_id: int) -> List[Dict[str, Any]]:
    query = text("""
        SELECT
            oi.id,
            oi.order_id,
            oi.variant_id,
            oi.quantity,
            oi.price,
            oi.created_at
        FROM order_items oi
        WHERE oi.order_id = :order_id
        ORDER BY oi.id
    """)
    rows = db.execute(query, {"order_id": order_id}).mappings().all()
    return [dict(row) for row in rows]

def update_order_total_amount(db: Session, order_id: int, total_amount: float) -> None:
    query = text("""
        UPDATE orders
        SET total_amount = :total_amount
        WHERE id = :order_id
    """)
    db.execute(query, {"order_id": order_id, "total_amount": total_amount})


def apply_coupon_to_order(
    db: Session,
    coupon_code: str,
    user_id: int,
    order_id: int,
    order_amount: float
) -> None:
    db.execute(
        text("""
            CALL sp_apply_coupon(
                :coupon_code,
                :user_id,
                :order_id,
                :order_amount
            )
        """),
        {
            "coupon_code": coupon_code,
            "user_id": user_id,
            "order_id": order_id,
            "order_amount": order_amount
        }
    )


def transaction_ref_exists(db: Session, transaction_ref: str) -> bool:
    query = text("""
        SELECT 1
        FROM transactions
        WHERE transaction_ref = :transaction_ref
        LIMIT 1
    """)
    result = db.execute(query, {"transaction_ref": transaction_ref}).scalar()
    return result is not None


def call_sp_process_payment(
    db: Session,
    order_id: int,
    payment_method: str,
    payment_status: str,
    transaction_ref: str
) -> None:
    db.execute(
        text("""
            CALL sp_process_payment(
                :order_id,
                :payment_method,
                :payment_status,
                :transaction_ref
            )
        """),
        {
            "order_id": order_id,
            "payment_method": payment_method,
            "payment_status": payment_status,
            "transaction_ref": transaction_ref
        }
    )


def get_address_by_id(db: Session, address_id: int, user_id: int) -> Optional[Dict[str, Any]]:
    query = text("""
        SELECT
            id,
            user_id,
            full_name,
            phone,
            email,
            address_line1,
            address_line2,
            landmark,
            city,
            state,
            country,
            postal_code,
            address_type,
            is_default
        FROM address
        WHERE id = :address_id
          AND user_id = :user_id
        LIMIT 1
    """)
    row = db.execute(
        query,
        {"address_id": address_id, "user_id": user_id}
    ).mappings().first()
    return dict(row) if row else None