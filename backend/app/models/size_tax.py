from sqlalchemy import Column, Integer, String, Numeric, Boolean
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.sql import func
from app.db.base import Base


class TaxRate(Base):
    __tablename__ = "tax_rate"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=True)
    rate = Column(Numeric(5, 2), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())


class SizeMaster(Base):
    __tablename__ = "size_master"

    id = Column(Integer, primary_key=True, index=True)
    size_code = Column(String(10), nullable=False, unique=True)
    sort_order = Column(Integer, nullable=True)