from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import date


class BulkOrderItemCreate(BaseModel):
    product_category_id: int
    quantity: int = Field(..., gt=0)
    size: str
    gender: Optional[str] = None
    color: Optional[str] = None


class BulkOrderRequestCreate(BaseModel):
    user_id: Optional[int] = None

    organization_name: str
    contact_person: str
    email: Optional[EmailStr] = None
    phone: str
    gst_number: Optional[str] = None
    state: str
    city: str
    address: str
    postal_code: str

    expected_delivery_date: Optional[date] = None
    fabric_preference: Optional[str] = None
    additional_requirements: Optional[str] = None
    branding_required: bool = False

    items: List[BulkOrderItemCreate]


class BulkOrderRequestResponse(BaseModel):
    success: bool
    message: str
    bulk_request_id: int
    request_number: str
    organization_id: int