from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, require_admin
from app.services.admin_service import AdminService

router = APIRouter(prefix="/admin", tags=["Admin - Dashboard"])

service = AdminService()


@router.get("/dashboard", summary="Admin dashboard metrics")
def dashboard(
    db: Session = Depends(get_db),
    admin = Depends(require_admin)
):
    return service.get_dashboard_data(db)