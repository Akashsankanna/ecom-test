from sqlalchemy import Column, Integer, Text, Date, String, ForeignKey
from sqlalchemy.dialects.postgresql import TIMESTAMP, JSONB
from sqlalchemy.sql import func
from app.db.base import Base


class Shipment(Base):
    __tablename__ = "shipment"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    courier_name = Column(Text, nullable=False)
    tracking_number = Column(Text, nullable=False, unique=True)
    shipment_status = Column(Text, nullable=False, default="PENDING")
    shipped_at = Column(TIMESTAMP, nullable=True)
    estimated_delivery = Column(Date, nullable=True)
    delivered_at = Column(TIMESTAMP, nullable=True)
    tracking_url = Column(Text, nullable=True)
    estimated_delivery_date = Column(Date, nullable=True)
    shipping_label_url = Column(Text, nullable=True)
    shipment_response = Column(JSONB, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, nullable=True)