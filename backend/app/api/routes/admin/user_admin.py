from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.db.session import get_db
from app.core.dependencies import require_admin
from app.schemas.user import (
    UserUpdate,
    AssignRoleRequest,
    RemoveRoleRequest,
    UserProfileUpsert,
)
from app.services.user_service import UserService

router = APIRouter(
    prefix="/admin/users",
    tags=["Admin - Users"]
)

# ════════════════════════════════════════════════════════════
# LIST / STATIC ROUTES FIRST
# IMPORTANT:
# Keep all fixed paths ABOVE /{user_id}
# ════════════════════════════════════════════════════════════

@router.get(
    "/",
    summary="List all users"
)
def get_all_users(
    user_type: Optional[str] = Query(
        None,
        description="customer | admin"
    ),
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    return UserService.get_all_users(
        db,
        user_type
    )


@router.get(
    "/roles",
    summary="List all available roles"
)
def get_all_roles(
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    return UserService.get_all_roles(db)


@router.get(
    "/access-view",
    summary="User access view"
)
def get_user_access_view(
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    return UserService.get_user_access_view(db)


@router.get(
    "/full-access",
    summary="User full access view"
)
def get_user_full_access(
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    return UserService.get_user_full_access(db)


@router.get(
    "/audit-logs",
    summary="Audit logs"
)
def get_audit_logs(
    entity_type: Optional[str] = Query(None),
    user_id: Optional[int] = Query(None),
    limit: int = Query(
        500,
        ge=1,
        le=500
    ),
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    return UserService.get_audit_logs(
        db,
        entity_type,
        user_id,
        limit
    )


# ════════════════════════════════════════════════════════════
# DYNAMIC USER ROUTES
# Keep after static routes
# ════════════════════════════════════════════════════════════

@router.get(
    "/{user_id}",
    summary="Get user detail with roles"
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    return UserService.get_user_detail(
        db,
        user_id
    )


@router.put(
    "/{user_id}",
    summary="Update user"
)
def update_user(
    user_id: int,
    data: UserUpdate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    return UserService.update_user(
        db,
        user_id,
        data
    )


@router.delete(
    "/{user_id}",
    summary="Soft delete user"
)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    return UserService.delete_user(
        db,
        admin.id,
        user_id
    )


# ════════════════════════════════════════════════════════════
# PROFILE
# ════════════════════════════════════════════════════════════

@router.get(
    "/{user_id}/profile",
    summary="Get user profile"
)
def get_user_profile(
    user_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    return UserService.get_user_profile(
        db,
        user_id
    )


@router.put(
    "/{user_id}/profile",
    summary="Create or update profile"
)
def upsert_user_profile(
    user_id: int,
    data: UserProfileUpsert,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    return UserService.upsert_user_profile(
        db,
        user_id,
        data
    )


# ════════════════════════════════════════════════════════════
# ROLE MANAGEMENT
# GAP FIX:
# sp_assign_role expects UPPER(role_name)
# We force uppercase here safely
# ════════════════════════════════════════════════════════════

@router.post(
    "/{user_id}/assign-role",
    summary="Assign role to user"
)
def assign_role(
    user_id: int,
    data: AssignRoleRequest,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    data.target_user_id = user_id

    # IMPORTANT FIX
    data.role_name = data.role_name.upper()

    return UserService.assign_role_request(
        db,
        data
    )


@router.delete(
    "/{user_id}/remove-role",
    summary="Remove role from user"
)
def remove_role(
    user_id: int,
    data: RemoveRoleRequest,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    return UserService.remove_role(
        db,
        user_id,
        data.role_name
    )