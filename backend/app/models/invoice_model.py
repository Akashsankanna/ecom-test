from sqlalchemy import (
    Column,
    Integer,
    String,
    Numeric,
    DateTime,
    ForeignKey,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.base import Base


class Invoice(Base):
    __tablename__ = "invoice"

    id = Column(Integer, primary_key=True, index=True)

    order_id = Column(
        Integer,
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    invoice_number = Column(String(50), nullable=False, unique=True, index=True)

    invoice_date = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    billing_address = Column(JSONB, nullable=True)
    gst_number = Column(String(20), nullable=True)

    total_tax = Column(Numeric(10, 2), nullable=True)
    total_amount = Column(Numeric(12, 2), nullable=True)
    tax_amount = Column(Numeric(12, 2), nullable=True)
    final_amount = Column(Numeric(12, 2), nullable=True)

    reference_type = Column(String(20), nullable=True)
    reference_id = Column(Integer, nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Optional but useful
    order = relationship("Order")

    items = relationship(
        "InvoiceItem",
        back_populates="invoice",
        cascade="all, delete-orphan",
    )


class InvoiceItem(Base):
    __tablename__ = "invoice_item"

    id = Column(Integer, primary_key=True, index=True)

    invoice_id = Column(
        Integer,
        ForeignKey("invoice.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    product_id = Column(Integer, nullable=True)
    product_name = Column(Text, nullable=True)
    description = Column(Text, nullable=True)

    variant_id = Column(Integer, nullable=True)
    hsn_code = Column(String(50), nullable=True)

    quantity = Column(Integer, nullable=False, default=1)
    price = Column(Numeric(12, 2), nullable=True)

    taxable_value = Column(Numeric(12, 2), nullable=True)
    gst_rate = Column(Numeric(5, 2), nullable=True)
    gst_amount = Column(Numeric(12, 2), nullable=True)

    total_amount = Column(Numeric(12, 2), nullable=True)
    total_price = Column(Numeric(12, 2), nullable=True)

    invoice = relationship(
        "Invoice",
        back_populates="items",
    )