from sqlalchemy import Column, Integer, String, Numeric, Boolean, DateTime
from app.db.base_class import Base

class TaxRate(Base):
    __tablename__ = "tax_rate"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50))
    rate = Column(Numeric(5, 2))
    is_active = Column(Boolean)
    created_at = Column(DateTime)