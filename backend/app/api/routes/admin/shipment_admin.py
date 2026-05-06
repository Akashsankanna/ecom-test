"""
app/routers/shipment_router.py

FIXED:
- update_shipment_status now returns { shipment, order: { id, status } }
- All endpoints return fresh DB data
"""

from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencies import require_admin
from app.db.session import get_db
from app.schemas.shipment import (
    ShipmentCreate,
    ShipmentDetail,
    ShipmentListItem,
    ShipmentRead,
    ShipmentStats,
    ShipmentStatus,
    ShipmentStatusUpdate,
)
from app.services.shipment_service import ShipmentService

# ── Routers ────────────────────────────────────────────────────────────────────
shipments_router = APIRouter(
    prefix="/admin/shipments",
    tags=["Admin - Shipments"],
)

orders_shipment_router = APIRouter(
    prefix="/admin/orders",
    tags=["Admin - Shipments"],
)


# ══════════════════════════════════════════════════════════════════════════════
# /admin/shipments/*
# ══════════════════════════════════════════════════════════════════════════════

@shipments_router.get(
    "/",
    response_model=List[ShipmentListItem],
    summary="List all shipments with optional filters",
)
def list_shipments(
    status: Optional[ShipmentStatus] = Query(None),
    order_id: Optional[int]          = Query(None),
    courier_name: Optional[str]      = Query(None),
    skip: int  = Query(0,   ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    _admin=Depends(require_admin),
):
    return ShipmentService.list_shipments(db, status, order_id, courier_name, skip, limit)


@shipments_router.get(
    "/stats",
    response_model=ShipmentStats,
    summary="Shipment counts grouped by status",
)
def get_shipment_stats(
    db: Session = Depends(get_db),
    _admin=Depends(require_admin),
):
    return ShipmentService.get_stats(db)


@shipments_router.get(
    "/{shipment_id}",
    response_model=ShipmentRead,
    summary="Get shipment by ID",
)
def get_shipment_by_id(
    shipment_id: int,
    db: Session = Depends(get_db),
    _admin=Depends(require_admin),
):
    return ShipmentService.get_shipment_by_id(db, shipment_id)


@shipments_router.put(
    "/{tracking_number}",
    summary="Update shipment status — also syncs order.status",
)
def update_shipment_status(
    tracking_number: str,
    data: ShipmentStatusUpdate,
    db: Session = Depends(get_db),
    _admin=Depends(require_admin),
):
    """
    Updates shipment status and immediately syncs order.status.

    Mapping:
      PENDING          → order: CONFIRMED
      SHIPPED          → order: SHIPPED
      OUT_FOR_DELIVERY → order: SHIPPED
      DELIVERED        → order: DELIVERED
      FAILED           → order: CONFIRMED
      RETURNED         → order: RETURNED

    Response shape:
    {
      "id": ...,
      "shipment_status": "DELIVERED",
      ...shipment fields...,
      "synced_order_status": "DELIVERED",
      "order": { "id": 42, "status": "DELIVERED" }
    }

    Frontend uses `synced_order_status` / `order.status` to update
    the order panel without an extra API call.
    """
    # ShipmentService.update_shipment_status now returns the full dict
    return ShipmentService.update_shipment_status(db, tracking_number, data)


# ══════════════════════════════════════════════════════════════════════════════
# /admin/orders/{order_id}/shipment
# ══════════════════════════════════════════════════════════════════════════════

@orders_shipment_router.post(
    "/{order_id}/shipment",
    response_model=ShipmentRead,
    status_code=201,
    summary="Create shipment for an order",
)
def create_shipment(
    order_id: int,
    data: ShipmentCreate,
    db: Session = Depends(get_db),
    _admin=Depends(require_admin),
):
    return ShipmentService.create_shipment(db, order_id, data)


@orders_shipment_router.get(
    "/{order_id}/shipment",
    response_model=ShipmentDetail,
    summary="Get shipment for an order",
)
def get_shipment_by_order(
    order_id: int,
    db: Session = Depends(get_db),
    _admin=Depends(require_admin),
):
    return ShipmentService.get_shipment_by_order(db, order_id)