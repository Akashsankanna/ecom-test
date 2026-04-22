from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi import HTTPException
from app.schemas.bulk_order import BulkOrderRequestCreate
from datetime import datetime


def generate_request_number() -> str:
    return f"REQ-{datetime.now().strftime('%Y%m%d%H%M%S')}"


def build_notes(payload: BulkOrderRequestCreate) -> str:
    notes_parts = []

    if payload.fabric_preference:
        notes_parts.append(f"Fabric Preference: {payload.fabric_preference}")

    if payload.additional_requirements:
        notes_parts.append(f"Additional Requirements: {payload.additional_requirements}")

    notes_parts.append(f"Branding Required: {'Yes' if payload.branding_required else 'No'}")

    return " | ".join(notes_parts)


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


def resolve_variant_id(
    db: Session,
    product_category_id: int,
    size: str,
    color: str | None = None,
) -> int:
    query = """
        SELECT pv.id
        FROM product_variant pv
        JOIN product p ON p.id = pv.product_id
        WHERE p.category_id = :category_id
          AND COALESCE(LOWER(pv.size), '') = COALESCE(LOWER(:size), '')
    """
    params = {
        "category_id": product_category_id,
        "size": size,
    }

    if color:
        query += " AND COALESCE(LOWER(pv.color), '') = COALESCE(LOWER(:color), '')"
        params["color"] = color

    query += """
        AND COALESCE(p.is_deleted, FALSE) = FALSE
        AND COALESCE(p.is_active, TRUE) = TRUE
        AND COALESCE(pv.is_deleted, FALSE) = FALSE
        ORDER BY pv.id
        LIMIT 1
    """

    row = db.execute(text(query), params).fetchone()

    if not row:
        raise HTTPException(
            status_code=400,
            detail=f"Variant not found for category_id={product_category_id}, size={size}, color={color}"
        )

    return row.id


def get_variant_price(db: Session, variant_id: int):
    row = db.execute(
        text("""
            SELECT price
            FROM product_variant
            WHERE id = :variant_id
            LIMIT 1
        """),
        {"variant_id": variant_id}
    ).fetchone()

    if not row:
        raise HTTPException(status_code=400, detail=f"Variant {variant_id} not found")

    return row.price


def create_bulk_order_request(db: Session, payload: BulkOrderRequestCreate):
    if not payload.items:
        raise HTTPException(status_code=400, detail="At least one order item is required")

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
            color=item.color
        )

        requested_price = get_variant_price(db, variant_id)

        item_notes_parts = []
        if item.gender:
            item_notes_parts.append(f"Gender: {item.gender}")
        if item.color:
            item_notes_parts.append(f"Color: {item.color}")

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


def get_bulk_form_options(db: Session):
    categories = db.execute(
        text("""
            SELECT id, name
            FROM category
            WHERE COALESCE(is_deleted, FALSE) = FALSE
              AND COALESCE(is_active, TRUE) = TRUE
            ORDER BY name
        """)
    ).mappings().all()

    sizes = db.execute(
        text("""
            SELECT DISTINCT size
            FROM product_variant
            WHERE size IS NOT NULL
              AND TRIM(size) <> ''
              AND COALESCE(is_deleted, FALSE) = FALSE
            ORDER BY size
        """)
    ).fetchall()

    colors = db.execute(
        text("""
            SELECT DISTINCT color
            FROM product_variant
            WHERE color IS NOT NULL
              AND TRIM(color) <> ''
              AND COALESCE(is_deleted, FALSE) = FALSE
            ORDER BY color
        """)
    ).fetchall()

    return {
        "categories": [dict(row) for row in categories],
        "sizes": [row[0] for row in sizes],
        "colors": [row[0] for row in colors],
        "genders": ["Men", "Women", "Unisex"],
        "fabrics": ["Cotton", "Polycotton", "Polyester", "Blend", "Other"]
    }