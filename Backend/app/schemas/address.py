from typing import Optional, Literal
from pydantic import BaseModel, Field


AddressType = Literal["HOME", "WORK", "OTHER"]


class AddressCreate(BaseModel):
    user_id: int
    full_name: str = Field(..., max_length=150)
    phone: str = Field(..., max_length=15)
    address_line1: str
    address_line2: Optional[str] = None
    landmark: Optional[str] = None
    city: str = Field(..., max_length=100)
    state: str = Field(..., max_length=100)
    country: str = Field(default="India", max_length=100)
    postal_code: str = Field(..., max_length=10)
    address_type: Optional[AddressType] = None
    is_default: bool = False


class AddressUpdate(BaseModel):
    user_id: int
    full_name: Optional[str] = Field(None, max_length=150)
    phone: Optional[str] = Field(None, max_length=15)
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    landmark: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=10)
    address_type: Optional[AddressType] = None
    is_default: Optional[bool] = None


class AddressResponse(BaseModel):
    id: int
    user_id: int
    full_name: str
    phone: str
    address_line1: str
    address_line2: Optional[str] = None
    landmark: Optional[str] = None
    city: str
    state: str
    country: str
    postal_code: str
    address_type: Optional[str] = None
    is_default: bool
    created_at: Optional[str] = None
    updated_at: Optional[str] = None