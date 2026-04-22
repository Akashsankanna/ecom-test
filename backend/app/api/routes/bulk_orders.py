from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.bulk_order import (
    BulkOrderRequestCreate,
    BulkOrderRequestResponse
)
from app.services.bulk_order_service import (
    create_bulk_order_request,
    get_bulk_form_options
)

router = APIRouter(prefix="/bulk-orders", tags=["Bulk Orders"])


@router.get("/options")
def bulk_order_options(db: Session = Depends(get_db)):
    return get_bulk_form_options(db)


@router.post("/request", response_model=BulkOrderRequestResponse)
def submit_bulk_order_request(
    payload: BulkOrderRequestCreate,
    db: Session = Depends(get_db)
):
    return create_bulk_order_request(db, payload)