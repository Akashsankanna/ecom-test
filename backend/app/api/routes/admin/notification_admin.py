from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from app.db.session import get_db
from app.core.dependencies import require_admin
from app.schemas.notification import NotificationCreate
from app.repositories.notification_repo import NotificationRepository

router = APIRouter(
    prefix="/admin/notifications",
    tags=["Admin - Notifications"]
)

# ════════════════════════════════════════════════════════════
# LIST ALL
# ════════════════════════════════════════════════════════════

@router.get(
    "/",
    summary="List all notifications"
)
def get_all_notifications(
    user_id: Optional[int] = Query(
        None,
        description="Filter by user ID"
    ),
    status: Optional[str] = Query(
        None,
        description="PENDING | SENT | FAILED"
    ),
    channel: Optional[str] = Query(
        None,
        description="EMAIL | SMS | PUSH | IN_APP"
    ),
    limit: int = Query(
        100,
        ge=1,
        le=500
    ),
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    notifs = NotificationRepository.get_all_notifications(
        db,
        user_id,
        status,
        channel,
        limit
    )

    return [
        {
            "id": n.id,
            "user_id": n.user_id,
            "notification_type": n.notification_type,
            "channel": n.channel,
            "title": n.title,
            "message": n.message,
            "reference_id": n.reference_id,
            "reference_type": n.reference_type,
            "status": n.status,
            "is_read": n.is_read,
            "sent_at": n.sent_at,
            "created_at": n.created_at,
        }
        for n in notifs
    ]


# ════════════════════════════════════════════════════════════
# STATIC ROUTES FIRST
# IMPORTANT:
# must stay ABOVE /{notification_id}
# ════════════════════════════════════════════════════════════

@router.get(
    "/pending",
    summary="Get pending notifications"
)
def get_pending(
    limit: int = Query(
        50,
        ge=1,
        le=200
    ),
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    notifs = NotificationRepository.get_pending_notifications(
        db,
        limit
    )

    return [
        {
            "id": n.id,
            "user_id": n.user_id,
            "notification_type": n.notification_type,
            "channel": n.channel,
            "title": n.title,
            "message": n.message,
            "created_at": n.created_at,
        }
        for n in notifs
    ]


@router.post(
    "/send",
    summary="Create notification using sp_create_notification"
)
def send_notification(
    data: NotificationCreate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    """
    Uses stored procedure:
    sp_create_notification()

    Creates row with status=PENDING
    """

    n = NotificationRepository.create_notification(
        db,
        data
    )

    return {
        "message": "Notification created with PENDING status",
        "notification_id": n.id,
        "user_id": n.user_id,
        "channel": n.channel,
        "notification_type": n.notification_type,
        "title": n.title,
        "status": n.status,
    }


# ════════════════════════════════════════════════════════════
# DYNAMIC ROUTES LAST
# IMPORTANT:
# keep after /pending
# ════════════════════════════════════════════════════════════

@router.get(
    "/{notification_id}",
    summary="Get notification by ID"
)
def get_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    n = NotificationRepository.get_notification_by_id(
        db,
        notification_id
    )

    if not n:
        raise HTTPException(
            status_code=404,
            detail="Notification not found"
        )

    return {
        "id": n.id,
        "user_id": n.user_id,
        "notification_type": n.notification_type,
        "channel": n.channel,
        "title": n.title,
        "message": n.message,
        "reference_id": n.reference_id,
        "reference_type": n.reference_type,
        "status": n.status,
        "is_read": n.is_read,
        "sent_at": n.sent_at,
        "created_at": n.created_at,
    }


@router.patch(
    "/{notification_id}/mark-sent",
    summary="Mark notification as SENT"
)
def mark_sent(
    notification_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    n = NotificationRepository.mark_as_sent(
        db,
        notification_id
    )

    if not n:
        raise HTTPException(
            status_code=404,
            detail="Notification not found"
        )

    return {
        "message": "Notification marked as SENT",
        "notification_id": n.id,
        "status": n.status,
        "sent_at": n.sent_at,
    }


@router.patch(
    "/{notification_id}/mark-failed",
    summary="Mark notification as FAILED"
)
def mark_failed(
    notification_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    n = NotificationRepository.mark_as_failed(
        db,
        notification_id
    )

    if not n:
        raise HTTPException(
            status_code=404,
            detail="Notification not found"
        )

    return {
        "message": "Notification marked as FAILED",
        "notification_id": n.id,
        "status": n.status,
    }