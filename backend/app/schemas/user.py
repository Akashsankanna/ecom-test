# app/schemas/user.py

from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import date, datetime
from enum import Enum


# ════════════════════════════════════════════════════════════
# ENUMS
# ════════════════════════════════════════════════════════════

class UserType(str, Enum):
    CUSTOMER = "customer"
    ADMIN    = "admin"


class GenderType(str, Enum):
    MALE   = "male"
    FEMALE = "female"
    OTHER  = "other"


# ════════════════════════════════════════════════════════════
# USER SCHEMAS
# ════════════════════════════════════════════════════════════

class UserCreate(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    keycloak_id: Optional[str] = None
    user_type: UserType = UserType.CUSTOMER


class UserUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None


class UserOut(BaseModel):
    id: int
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    user_type: Optional[str] = None
    is_deleted: bool
    is_email_verified: bool
    keycloak_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserDetailOut(UserOut):
    roles: List[str] = []


class AssignRoleRequest(BaseModel):
    target_user_id: int
    role_name: str


class RemoveRoleRequest(BaseModel):
    role_name: str


class RoleOut(BaseModel):
    id: int
    role_name: str

    class Config:
        from_attributes = True


class PermissionOut(BaseModel):
    id: int
    permission_name: str

    class Config:
        from_attributes = True


# ════════════════════════════════════════════════════════════
# USER PROFILE SCHEMAS
# ════════════════════════════════════════════════════════════

class UserProfileUpsert(BaseModel):
    """Input for sp_upsert_user_profile(user_id, profile_image, gender, date_of_birth)"""
    profile_image: Optional[str] = None
    gender: Optional[GenderType] = None
    date_of_birth: Optional[date] = None


class UserProfileOut(BaseModel):
    user_id: int
    profile_image: Optional[str] = None
    gender: Optional[str] = None
    date_of_birth: Optional[date] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ════════════════════════════════════════════════════════════
# AUDIT LOG SCHEMA
# ════════════════════════════════════════════════════════════

class AuditLogOut(BaseModel):
    id: int
    user_id: Optional[int] = None
    action: Optional[str] = None
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None
    old_data: Optional[dict] = None
    new_data: Optional[dict] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True