from typing import List, Optional
from pydantic import BaseModel, Field
from decimal import Decimal
from typing import Optional

class InvoiceBuyer(BaseModel):
    name: str
    address: str
    gstin: Optional[str] = None
    state: Optional[str] = None
    state_code: Optional[str] = None
    contact: Optional[str] = None
    invoice_no: Optional[str] = None

class InvoiceItem(BaseModel):
    name: str
    description: Optional[str] = None
    hsn: str
    quantity: int = Field(gt=0)
    rate: Decimal = Field(gt=0)
    gst_rate: Decimal = Field(default=5, ge=0)


class InvoiceCreate(BaseModel):
    invoice_no: str
    invoice_date: str
    dispatch_through: Optional[str] = None
    destination: Optional[str] = None
    buyer: InvoiceBuyer
    items: List[InvoiceItem]


class InvoiceResponse(BaseModel):
    message: str
    file_path: str