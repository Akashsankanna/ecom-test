from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi import HTTPException
from app.schemas.bulk_order import BulkOrderRequestCreate
from datetime import datetime


# =====================================================
# HELPERS
# =====================================================

def generate_request_number() -> str:
    return f"REQ-{datetime.now().strftime('%Y%m%d%H%M%S')}"


def generate_bulk_order_number() -> str:
    return f"BULK-{datetime.now().strftime('%Y%m%d%H%M%S')}"


def build_notes(payload: BulkOrderRequestCreate) -> str:
    notes_parts = []

    if payload.fabric_preference:
        notes_parts.append(f"Fabric Preference: {payload.fabric_preference}")

    if payload.additional_requirements:
        notes_parts.append(f"Additional Requirements: {payload.additional_requirements}")

    notes_parts.append(f"Branding Required: {'Yes' if payload.branding_required else 'No'}")

    return " | ".join(notes_parts)


# =====================================================
# ORGANIZATION
# =====================================================

def get_or_create_organization(db: Session, payload: BulkOrderRequestCreate) -> int:
    existing_org = db.execute(
        text("""
            SELECT id
            FROM organization
            WHERE
                (gst_number = :gst_number AND :gst_number IS NOT NULL)
                OR (
                    LOWER(name) = LOWER(:name)
                    AND phone = :phone
                )
            LIMIT 1
        """),
        {
            "gst_number": payload.gst_number,
            "name": payload.organization_name,
            "phone": payload.phone,
        }
    ).fetchone()

    if existing_org:
        db.execute(
            text("""
                UPDATE organization
                SET
                    contact_person = :contact_person,
                    email = :email,
                    phone = :phone,
                    gst_number = :gst_number,
                    address = :address,
                    city = :city,
                    state = :state,
                    postal_code = :postal_code,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = :org_id
            """),
            {
                "org_id": existing_org.id,
                "contact_person": payload.contact_person,
                "email": payload.email,
                "phone": payload.phone,
                "gst_number": payload.gst_number,
                "address": payload.address,
                "city": payload.city,
                "state": payload.state,
                "postal_code": payload.postal_code,
            }
        )

        return existing_org.id

    new_org = db.execute(
        text("""
            INSERT INTO organization (
                name,
                contact_person,
                email,
                phone,
                gst_number,
                address,
                city,
                state,
                country,
                postal_code,
                is_active,
                created_at,
                updated_at
            )
            VALUES (
                :name,
                :contact_person,
                :email,
                :phone,
                :gst_number,
                :address,
                :city,
                :state,
                'India',
                :postal_code,
                TRUE,
                CURRENT_TIMESTAMP,
                CURRENT_TIMESTAMP
            )
            RETURNING id
        """),
        {
            "name": payload.organization_name,
            "contact_person": payload.contact_person,
            "email": payload.email,
            "phone": payload.phone,
            "gst_number": payload.gst_number,
            "address": payload.address,
            "city": payload.city,
            "state": payload.state,
            "postal_code": payload.postal_code,
        }
    ).fetchone()

    return new_org.id


# =====================================================
# DYNAMIC VARIANT RESOLUTION
# =====================================================

def resolve_variant_id(
    db: Session,
    product_category_id: int,
    size: str,
    color: str | None = None,
) -> int:
    base_query = """
        SELECT
            pv.id,
            c.name AS color_name
        FROM product_variant pv
        JOIN product p ON p.id = pv.product_id
        LEFT JOIN color c ON c.id = pv.color_id
        WHERE p.category_id = :category_id
          AND LOWER(TRIM(pv.size)) = LOWER(TRIM(:size))
          AND COALESCE(p.is_deleted, FALSE) = FALSE
          AND COALESCE(p.is_active, TRUE) = TRUE
          AND COALESCE(pv.is_deleted, FALSE) = FALSE
    """

    params = {
        "category_id": product_category_id,
        "size": size,
    }

    if color:
        exact_query = base_query + """
          AND (
                LOWER(TRIM(c.name)) = LOWER(TRIM(:color))
                OR CAST(c.id AS TEXT) = CAST(:color AS TEXT)
          )
          ORDER BY pv.id
          LIMIT 1
        """

        row = db.execute(
            text(exact_query),
            {
                **params,
                "color": color,
            }
        ).fetchone()

        if row:
            return row.id

    fallback_query = base_query + """
        ORDER BY pv.id
        LIMIT 1
    """

    row = db.execute(text(fallback_query), params).fetchone()

    if row:
        return row.id

    available_rows = db.execute(
        text("""
            SELECT
                pv.size,
                c.name AS color_name
            FROM product_variant pv
            JOIN product p ON p.id = pv.product_id
            LEFT JOIN color c ON c.id = pv.color_id
            WHERE p.category_id = :category_id
              AND COALESCE(p.is_deleted, FALSE) = FALSE
              AND COALESCE(p.is_active, TRUE) = TRUE
              AND COALESCE(pv.is_deleted, FALSE) = FALSE
            ORDER BY pv.size, c.name
        """),
        {
            "category_id": product_category_id,
        }
    ).fetchall()

    available = [
        f"size={row.size}, color={row.color_name}"
        for row in available_rows
    ]

    raise HTTPException(
        status_code=400,
        detail={
            "message": f"Variant not found for category_id={product_category_id}, size={size}, color={color}",
            "available_variants": available,
        }
    )


def get_variant_price(db: Session, variant_id: int):
    row = db.execute(
        text("""
            SELECT price
            FROM product_variant
            WHERE id = :variant_id
            LIMIT 1
        """),
        {
            "variant_id": variant_id,
        }
    ).fetchone()

    if not row:
        raise HTTPException(
            status_code=400,
            detail=f"Variant {variant_id} not found"
        )

    return row.price


# =====================================================
# PUBLIC BULK ORDER REQUEST
# =====================================================

def create_bulk_order_request(db: Session, payload: BulkOrderRequestCreate):
    try:
        if not payload.items:
            raise HTTPException(
                status_code=400,
                detail="At least one order item is required"
            )

        org_id = get_or_create_organization(db, payload)
        request_number = generate_request_number()
        notes = build_notes(payload)

        request_row = db.execute(
            text("""
                INSERT INTO bulk_order_request (
                    organization_id,
                    user_id,
                    request_number,
                    status,
                    notes,
                    expected_delivery_date,
                    created_at,
                    updated_at
                )
                VALUES (
                    :organization_id,
                    :user_id,
                    :request_number,
                    'PENDING',
                    :notes,
                    :expected_delivery_date,
                    CURRENT_TIMESTAMP,
                    CURRENT_TIMESTAMP
                )
                RETURNING id
            """),
            {
                "organization_id": org_id,
                "user_id": payload.user_id,
                "request_number": request_number,
                "notes": notes,
                "expected_delivery_date": payload.expected_delivery_date,
            }
        ).fetchone()

        bulk_request_id = request_row.id

        for item in payload.items:
            variant_id = resolve_variant_id(
                db=db,
                product_category_id=item.product_category_id,
                size=item.size,
                color=item.color,
            )

            requested_price = get_variant_price(db, variant_id)

            item_notes_parts = []

            if item.gender:
                item_notes_parts.append(f"Gender: {item.gender}")

            if item.color:
                item_notes_parts.append(f"Requested Color: {item.color}")

            item_notes = " | ".join(item_notes_parts) if item_notes_parts else None

            db.execute(
                text("""
                    INSERT INTO bulk_order_request_item (
                        bulk_request_id,
                        variant_id,
                        quantity,
                        requested_price,
                        quoted_price,
                        notes
                    )
                    VALUES (
                        :bulk_request_id,
                        :variant_id,
                        :quantity,
                        :requested_price,
                        NULL,
                        :notes
                    )
                """),
                {
                    "bulk_request_id": bulk_request_id,
                    "variant_id": variant_id,
                    "quantity": item.quantity,
                    "requested_price": requested_price,
                    "notes": item_notes,
                }
            )

        db.commit()

        return {
            "success": True,
            "message": "Bulk order request submitted successfully",
            "bulk_request_id": bulk_request_id,
            "request_number": request_number,
            "organization_id": org_id,
        }

    except HTTPException:
        db.rollback()
        raise

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Bulk order request failed: {str(e)}"
        )


# =====================================================
# DYNAMIC FORM OPTIONS
# =====================================================

def get_bulk_form_options(db: Session):
    categories = db.execute(
        text("""
            SELECT DISTINCT
                c.id,
                c.name
            FROM category c
            JOIN product p ON p.category_id = c.id
            JOIN product_variant pv ON pv.product_id = p.id
            WHERE COALESCE(c.is_deleted, FALSE) = FALSE
              AND COALESCE(c.is_active, TRUE) = TRUE
              AND COALESCE(p.is_deleted, FALSE) = FALSE
              AND COALESCE(p.is_active, TRUE) = TRUE
              AND COALESCE(pv.is_deleted, FALSE) = FALSE
            ORDER BY c.name
        """)
    ).mappings().all()

    sizes = db.execute(
        text("""
            SELECT DISTINCT TRIM(pv.size) AS size
            FROM product_variant pv
            JOIN product p ON p.id = pv.product_id
            WHERE pv.size IS NOT NULL
              AND TRIM(pv.size) <> ''
              AND COALESCE(pv.is_deleted, FALSE) = FALSE
              AND COALESCE(p.is_deleted, FALSE) = FALSE
              AND COALESCE(p.is_active, TRUE) = TRUE
            ORDER BY TRIM(pv.size)
        """)
    ).fetchall()

    colors = db.execute(
        text("""
            SELECT DISTINCT
                c.id,
                c.name,
                c.hex_code
            FROM product_variant pv
            JOIN color c ON c.id = pv.color_id
            JOIN product p ON p.id = pv.product_id
            WHERE pv.color_id IS NOT NULL
              AND COALESCE(pv.is_deleted, FALSE) = FALSE
              AND COALESCE(p.is_deleted, FALSE) = FALSE
              AND COALESCE(p.is_active, TRUE) = TRUE
              AND COALESCE(c.is_active, TRUE) = TRUE
            ORDER BY c.name
        """)
    ).mappings().all()

    return {
        "categories": [dict(row) for row in categories],
        "sizes": [row[0] for row in sizes],
        "colors": [
            {
                "id": row["id"],
                "name": row["name"],
                "hex_code": row["hex_code"],
            }
            for row in colors
        ],
        "genders": ["Men", "Women", "Unisex"],
        "fabrics": ["Cotton", "Polycotton", "Polyester", "Blend", "Other"],
    }


# =====================================================
# ADMIN SERVICE CLASS
# Required by: app/api/routes/admin/bulk_admin.py
# =====================================================

class BulkOrderService:

    @staticmethod
    def get_all_organizations(db: Session):
        return db.execute(
            text("""
                SELECT *
                FROM organization
                WHERE COALESCE(is_active, TRUE) = TRUE
                ORDER BY created_at DESC
            """)
        ).fetchall()

    @staticmethod
    def create_organization(db: Session, data):
        row = db.execute(
            text("""
                INSERT INTO organization (
                    name,
                    contact_person,
                    email,
                    phone,
                    gst_number,
                    address,
                    city,
                    state,
                    country,
                    postal_code,
                    is_active,
                    created_at,
                    updated_at
                )
                VALUES (
                    :name,
                    :contact_person,
                    :email,
                    :phone,
                    :gst_number,
                    :address,
                    :city,
                    :state,
                    'India',
                    :postal_code,
                    TRUE,
                    CURRENT_TIMESTAMP,
                    CURRENT_TIMESTAMP
                )
                RETURNING *
            """),
            data.model_dump()
        ).fetchone()

        db.commit()
        return row

    @staticmethod
    def get_all_bulk_requests(db: Session, status: str | None = None):
        query = """
            SELECT *
            FROM bulk_order_request
            WHERE 1 = 1
        """

        params = {}

        if status:
            query += " AND LOWER(status) = LOWER(:status)"
            params["status"] = status

        query += " ORDER BY created_at DESC"

        return db.execute(text(query), params).fetchall()

    @staticmethod
    def get_bulk_request(db: Session, request_id: int):
        req = db.execute(
            text("""
                SELECT *
                FROM bulk_order_request
                WHERE id = :request_id
            """),
            {
                "request_id": request_id
            }
        ).fetchone()

        if not req:
            raise HTTPException(status_code=404, detail="Bulk request not found")

        items = db.execute(
            text("""
                SELECT *
                FROM bulk_order_request_item
                WHERE bulk_request_id = :request_id
                ORDER BY id
            """),
            {
                "request_id": request_id
            }
        ).fetchall()

        return req, items

    @staticmethod
    def approve_bulk_request(db: Session, request_id: int):
        row = db.execute(
            text("""
                UPDATE bulk_order_request
                SET status = 'APPROVED',
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = :request_id
                RETURNING *
            """),
            {
                "request_id": request_id
            }
        ).fetchone()

        if not row:
            db.rollback()
            raise HTTPException(status_code=404, detail="Bulk request not found")

        db.commit()
        return row

    @staticmethod
    def reject_bulk_request(db: Session, request_id: int):
        row = db.execute(
            text("""
                UPDATE bulk_order_request
                SET status = 'REJECTED',
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = :request_id
                RETURNING *
            """),
            {
                "request_id": request_id
            }
        ).fetchone()

        if not row:
            db.rollback()
            raise HTTPException(status_code=404, detail="Bulk request not found")

        db.commit()
        return row

    @staticmethod
    def convert_to_order(db: Session, request_id: int, data, admin_id: int):
        req = db.execute(
            text("""
                SELECT *
                FROM bulk_order_request
                WHERE id = :request_id
            """),
            {
                "request_id": request_id
            }
        ).fetchone()

        if not req:
            raise HTTPException(status_code=404, detail="Bulk request not found")

        if str(req.status).upper() not in ["APPROVED", "PENDING"]:
            raise HTTPException(
                status_code=400,
                detail=f"Only approved requests can be converted. Current status: {req.status}"
            )

        items = db.execute(
            text("""
                SELECT *
                FROM bulk_order_request_item
                WHERE bulk_request_id = :request_id
            """),
            {
                "request_id": request_id
            }
        ).fetchall()

        if not items:
            raise HTTPException(status_code=400, detail="No items found in bulk request")

        total_amount = 0

        for item in items:
            price = item.quoted_price if item.quoted_price else item.requested_price
            total_amount += float(price or 0) * int(item.quantity or 0)

        order_number = generate_bulk_order_number()

        order_row = db.execute(
            text("""
                INSERT INTO bulk_order (
                    organization_id,
                    order_number,
                    total_amount,
                    status,
                    payment_status,
                    is_urgent,
                    expected_delivery_date,
                    created_by,
                    created_at,
                    updated_at
                )
                VALUES (
                    :organization_id,
                    :order_number,
                    :total_amount,
                    'CONFIRMED',
                    :payment_status,
                    :is_urgent,
                    :expected_delivery_date,
                    :created_by,
                    CURRENT_TIMESTAMP,
                    CURRENT_TIMESTAMP
                )
                RETURNING *
            """),
            {
                "organization_id": req.organization_id,
                "order_number": order_number,
                "total_amount": total_amount,
                "payment_status": data.payment_status or "pending",
                "is_urgent": data.is_urgent or False,
                "expected_delivery_date": data.expected_delivery_date or req.expected_delivery_date,
                "created_by": admin_id,
            }
        ).fetchone()

        for item in items:
            price = item.quoted_price if item.quoted_price else item.requested_price

            db.execute(
                text("""
                    INSERT INTO bulk_order_item (
                        bulk_order_id,
                        variant_id,
                        quantity,
                        price
                    )
                    VALUES (
                        :bulk_order_id,
                        :variant_id,
                        :quantity,
                        :price
                    )
                """),
                {
                    "bulk_order_id": order_row.id,
                    "variant_id": item.variant_id,
                    "quantity": item.quantity,
                    "price": price,
                }
            )

        db.execute(
            text("""
                UPDATE bulk_order_request
                SET status = 'CONVERTED',
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = :request_id
            """),
            {
                "request_id": request_id
            }
        )

        db.commit()
        return order_row

    @staticmethod
    def get_all_bulk_orders(db: Session, status: str | None = None):
        query = """
            SELECT *
            FROM bulk_order
            WHERE 1 = 1
        """

        params = {}

        if status:
            query += " AND LOWER(status) = LOWER(:status)"
            params["status"] = status

        query += " ORDER BY created_at DESC"

        return db.execute(text(query), params).fetchall()

    @staticmethod
    def get_bulk_order_view(db: Session):
        return db.execute(
            text("""
                SELECT
                    bo.id,
                    bo.order_number,
                    bo.organization_id,
                    o.name AS organization_name,
                    o.contact_person,
                    o.phone,
                    o.city,
                    o.state,
                    bo.total_amount,
                    bo.status,
                    bo.payment_status,
                    bo.is_urgent,
                    bo.expected_delivery_date,
                    bo.created_at
                FROM bulk_order bo
                JOIN organization o ON o.id = bo.organization_id
                ORDER BY bo.created_at DESC
            """)
        ).mappings().all()

    @staticmethod
    def get_bulk_order(db: Session, bulk_order_id: int):
        order = db.execute(
            text("""
                SELECT *
                FROM bulk_order
                WHERE id = :bulk_order_id
            """),
            {
                "bulk_order_id": bulk_order_id
            }
        ).fetchone()

        if not order:
            raise HTTPException(status_code=404, detail="Bulk order not found")

        items = db.execute(
            text("""
                SELECT *
                FROM bulk_order_item
                WHERE bulk_order_id = :bulk_order_id
                ORDER BY id
            """),
            {
                "bulk_order_id": bulk_order_id
            }
        ).fetchall()

        return order, items

    @staticmethod
    def update_bulk_order_status(db: Session, bulk_order_id: int, status: str, admin_id: int):
        order = db.execute(
            text("""
                UPDATE bulk_order
                SET status = :status,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = :bulk_order_id
                RETURNING *
            """),
            {
                "bulk_order_id": bulk_order_id,
                "status": status.upper(),
            }
        ).fetchone()

        if not order:
            db.rollback()
            raise HTTPException(status_code=404, detail="Bulk order not found")

        db.execute(
            text("""
                INSERT INTO bulk_order_status_history (
                    bulk_order_id,
                    status,
                    changed_by,
                    notes,
                    changed_at
                )
                VALUES (
                    :bulk_order_id,
                    :status,
                    :changed_by,
                    NULL,
                    CURRENT_TIMESTAMP
                )
            """),
            {
                "bulk_order_id": bulk_order_id,
                "status": status.upper(),
                "changed_by": admin_id,
            }
        )

        db.commit()
        return order

    @staticmethod
    def get_bulk_order_status_history(db: Session, bulk_order_id: int):
        return db.execute(
            text("""
                SELECT *
                FROM bulk_order_status_history
                WHERE bulk_order_id = :bulk_order_id
                ORDER BY changed_at DESC
            """),
            {
                "bulk_order_id": bulk_order_id
            }
        ).fetchall()