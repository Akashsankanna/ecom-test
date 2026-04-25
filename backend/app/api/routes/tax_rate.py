from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from sqlalchemy import text

router = APIRouter(prefix="/admin/tax-rates", tags=["Tax Rates"])

@router.get("/")
def get_tax_rates(db: Session = Depends(get_db)):
    rows = db.execute(text("""
        SELECT id,name,rate,is_active
        FROM tax_rate
        WHERE is_active = true
        ORDER BY id
    """)).mappings().all()

    return list(rows)