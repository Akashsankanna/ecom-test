from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.dependencies import require_admin
from app.schemas.order import ShipmentStatusUpdate
from app.services.order_service import OrderService

router = APIRouter(prefix="/admin/shipments", tags=["Admin - Shipments"])


@router.put(
    "/{tracking_number}",
    summary="Update shipment status → uses sp_update_shipment_status",
)
def update_shipment_status(
    tracking_number: str,
    data: ShipmentStatusUpdate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    """
    Allowed statuses: SHIPPED | OUT_FOR_DELIVERY | DELIVERED

    When status = DELIVERED:
    - delivered_at is set automatically by the SP
    - The linked order.status is also updated to DELIVERED
    """
    shipment = OrderService.update_shipment_status(db, tracking_number, data)
    return {
        "message": f"Shipment {tracking_number} updated to {shipment.shipment_status}",
        "shipment_id": shipment.id,
        "order_id": shipment.order_id,
        "tracking_number": shipment.tracking_number,
        "shipment_status": shipment.shipment_status,
        "shipped_at": shipment.shipped_at,
        "delivered_at": shipment.delivered_at,
    }