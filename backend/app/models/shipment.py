"""
app/models/shipment.py
SQLAlchemy model aligned exactly with the `shipment` table in PostgreSQL.

DB columns (from pg_dump):
  id, order_id, courier_name, tracking_number, shipment_status,
  shipped_at, estimated_delivery, delivered_at, created_at, updated_at,
  tracking_url, shipping_label_url, shipment_response

Constraint:
  chk_shipment_status: PENDING | SHIPPED | OUT_FOR_DELIVERY |
                        DELIVERED | FAILED | RETURNED
"""

from sqlalchemy import (
    Column, Integer, Text, Date, ForeignKey, CheckConstraint
)
from sqlalchemy.dialects.postgresql import TIMESTAMP, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.base import Base


class Shipment(Base):
    __tablename__ = "shipment"

    # ── Primary key ────────────────────────────────────────────────
    id = Column(Integer, primary_key=True, index=True)

    # ── Foreign key ────────────────────────────────────────────────
    order_id = Column(
        Integer,
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # ── Core shipment fields ────────────────────────────────────────
    courier_name    = Column(Text, nullable=False)
    tracking_number = Column(Text, nullable=False, unique=True)

    # Allowed values enforced by DB check constraint
    shipment_status = Column(
        Text,
        nullable=False,
        default="PENDING",
    )

    # ── Timestamps ─────────────────────────────────────────────────
    shipped_at          = Column(TIMESTAMP, nullable=True)
    estimated_delivery  = Column(Date,      nullable=True)   # DB column name
    delivered_at        = Column(TIMESTAMP, nullable=True)
    created_at          = Column(TIMESTAMP, server_default=func.now())
    updated_at          = Column(TIMESTAMP, nullable=True)

    # ── Optional logistics fields ───────────────────────────────────
    tracking_url        = Column(Text,  nullable=True)
    shipping_label_url  = Column(Text,  nullable=True)
    shipment_response   = Column(JSONB, nullable=True)

    # ── Relationships ───────────────────────────────────────────────
    order = relationship("Order", back_populates="shipment")

    __table_args__ = (
        CheckConstraint(
            "shipment_status IN "
            "('PENDING','SHIPPED','OUT_FOR_DELIVERY','DELIVERED','FAILED','RETURNED')",
            name="chk_shipment_status",
        ),
    )