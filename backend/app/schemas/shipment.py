"""
app/schemas/shipment.py
Pydantic v2 schemas aligned exactly with the DB `shipment` table.

Field mapping (schema  →  DB column):
  courier_name       → courier_name
  tracking_number    → tracking_number
  shipment_status    → shipment_status
  shipped_at         → shipped_at
  estimated_delivery → estimated_delivery   ← CORRECT column name (Date)
  delivered_at       → delivered_at
  tracking_url       → tracking_url
  shipping_label_url → shipping_label_url
  shipment_response  → shipment_response
"""

from __future__ import annotations

import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


# ── Enum: exactly matches DB check constraint ──────────────────────────────
class ShipmentStatus(str, Enum):
    PENDING          = "PENDING"
    SHIPPED          = "SHIPPED"
    OUT_FOR_DELIVERY = "OUT_FOR_DELIVERY"
    DELIVERED        = "DELIVERED"
    FAILED           = "FAILED"
    RETURNED         = "RETURNED"


# ── Create ─────────────────────────────────────────────────────────────────
class ShipmentCreate(BaseModel):
    """
    Payload for POST /admin/orders/{order_id}/shipment
    Calls sp_create_shipment(order_id, courier_name, tracking_number, estimated_delivery)
    """
    courier_name:       str            = Field(..., min_length=1, description="Courier / logistics company name")
    tracking_number:    str            = Field(..., min_length=1, description="Unique tracking number")
    estimated_delivery: Optional[datetime.date] = Field(None,  description="Expected delivery date (YYYY-MM-DD)")
    tracking_url:       Optional[str]  = Field(None, description="Courier tracking page URL")


# ── Status update ──────────────────────────────────────────────────────────
class ShipmentStatusUpdate(BaseModel):
    """
    Payload for PUT /admin/shipments/{tracking_number}
    Calls sp_update_shipment_status(tracking_number, status)
    Allowed: SHIPPED | OUT_FOR_DELIVERY | DELIVERED
    """
    status: ShipmentStatus = Field(
        ...,
        description="New shipment status. DELIVERED auto-sets delivered_at and updates order status.",
    )


# ── Response (read) ────────────────────────────────────────────────────────
class ShipmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id:                 int
    order_id:           int
    courier_name:       str
    tracking_number:    str
    shipment_status:    ShipmentStatus
    shipped_at:         Optional[datetime.datetime] = None
    estimated_delivery: Optional[datetime.date]     = None   # matches DB column
    delivered_at:       Optional[datetime.datetime] = None
    created_at:         Optional[datetime.datetime] = None
    updated_at:         Optional[datetime.datetime] = None
    tracking_url:       Optional[str]               = None
    shipping_label_url: Optional[str]               = None
    shipment_response:  Optional[Any]               = None


# ── Response enriched with order context ──────────────────────────────────
class ShipmentDetail(ShipmentRead):
    """Returned from GET /admin/orders/{order_id}/shipment"""
    order_status:   Optional[str] = None
    user_id:        Optional[int] = None


# ── List item (lightweight, used in admin table) ───────────────────────────
class ShipmentListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id:                 int
    order_id:           int
    courier_name:       str
    tracking_number:    str
    shipment_status:    ShipmentStatus
    estimated_delivery: Optional[datetime.date]     = None
    shipped_at:         Optional[datetime.datetime] = None
    delivered_at:       Optional[datetime.datetime] = None
    created_at:         Optional[datetime.datetime] = None


# ── Stats (computed by service layer) ─────────────────────────────────────
class ShipmentStats(BaseModel):
    total:           int = 0
    pending:         int = 0
    shipped:         int = 0
    out_for_delivery:int = 0
    delivered:       int = 0
    failed:          int = 0
    returned:        int = 0