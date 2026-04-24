from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.session import get_db

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.get("/")
def get_orders(user_id: int = Query(...), db: Session = Depends(get_db)):
    orders = db.execute(
        text("""
            SELECT
                o.id,
                o.user_id,
                o.total_amount,
                o.gross_amount,
                o.final_amount,
                o.status,
                o.payment_status,
                o.address_id,
                o.created_at
            FROM orders o
            WHERE o.user_id = :user_id
            ORDER BY o.id DESC
        """),
        {"user_id": user_id}
    ).mappings().all()

    result = []

    for order in orders:
        items = db.execute(
            text("""
                SELECT
                    oi.id,
                    oi.product_id,
                    oi.variant_id,
                    oi.quantity,
                    oi.price,
                    p.name AS product_name,
                    pv.variant_name
                FROM order_items oi
                LEFT JOIN product p ON p.id = oi.product_id
                LEFT JOIN product_variant pv ON pv.id = oi.variant_id
                WHERE oi.order_id = :order_id
            """),
            {"order_id": order["id"]}
        ).mappings().all()

        order_dict = dict(order)
        order_dict["items"] = [dict(item) for item in items]
        result.append(order_dict)

    return {
        "success": True,
        "orders": result
    }