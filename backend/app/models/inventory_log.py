# app/models/inventory_log.py
# UPDATED MODEL FOR NEW DB

from sqlalchemy import Column, Integer, Text, String, ForeignKey
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.sql import func

from app.db.base import Base


class InventoryLog(Base):
    __tablename__ = "inventory_log"

    id = Column(Integer, primary_key=True, index=True)

    # relations
    variant_id = Column(
        Integer,
        ForeignKey("product_variant.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    created_by = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )

    updated_by = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )

    # stock movement type
    # ORDER_PLACED
    # ORDER_CANCELLED
    # EXCHANGE
    # RESTOCK
    # ADJUSTMENT
    # RETURN
    # DAMAGED
    change_type = Column(
        String(40),
        nullable=False,
        index=True
    )

    quantity = Column(
        Integer,
        nullable=False
    )

    reference_id = Column(
        Integer,
        nullable=True,
        index=True
    )

    notes = Column(
        Text,
        nullable=True
    )

    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now()
    )
    reference_type = Column(String(50), nullable=True)