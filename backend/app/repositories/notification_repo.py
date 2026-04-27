from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models.notification import Notification
from typing import Optional, List


class NotificationRepository:

    @staticmethod
    def get_all_notifications(
        db: Session,
        user_id: Optional[int] = None,
        status: Optional[str] = None,
        channel: Optional[str] = None,
        limit: int = 100,
    ) -> List[Notification]:
        query = db.query(Notification)
        if user_id:
            query = query.filter(Notification.user_id == user_id)
        if status:
            query = query.filter(Notification.status == status.upper())
        if channel:
            query = query.filter(Notification.channel == channel.upper())
        return query.order_by(Notification.created_at.desc()).limit(limit).all()

    @staticmethod
    def get_notification_by_id(db: Session, notif_id: int) -> Optional[Notification]:
        return db.query(Notification).filter(Notification.id == notif_id).first()

    @staticmethod
    def create_notification(db: Session, data) -> Notification:
        """Uses sp_create_notification stored procedure."""
        db.execute(
            text(
                "CALL sp_create_notification("
                ":user_id, :ntype, :channel, :title, :message, :ref_id, :ref_type)"
            ),
            {
                "user_id": data.user_id,
                "ntype": data.notification_type.value,
                "channel": data.channel.value,
                "title": data.title,
                "message": data.message,
                "ref_id": data.reference_id,
                "ref_type": data.reference_type,
            },
        )
        db.commit()
        db.expire_all()
        return (
            db.query(Notification)
            .filter(Notification.user_id == data.user_id)
            .order_by(Notification.created_at.desc())
            .first()
        )

    @staticmethod
    def mark_as_sent(db: Session, notif_id: int) -> Optional[Notification]:
        notif = db.query(Notification).filter(Notification.id == notif_id).first()
        if not notif:
            return None
        db.execute(
            text(
                "UPDATE notification SET status='SENT', sent_at=CURRENT_TIMESTAMP, "
                "updated_at=CURRENT_TIMESTAMP WHERE id=:nid"
            ),
            {"nid": notif_id},
        )
        db.commit()
        db.expire_all()
        return db.query(Notification).filter(Notification.id == notif_id).first()

    @staticmethod
    def mark_as_failed(db: Session, notif_id: int) -> Optional[Notification]:
        db.execute(
            text(
                "UPDATE notification SET status='FAILED', updated_at=CURRENT_TIMESTAMP "
                "WHERE id=:nid"
            ),
            {"nid": notif_id},
        )
        db.commit()
        db.expire_all()
        return db.query(Notification).filter(Notification.id == notif_id).first()

    @staticmethod
    def get_pending_notifications(db: Session, limit: int = 50) -> List[Notification]:
        return (
            db.query(Notification)
            .filter(Notification.status == "PENDING")
            .order_by(Notification.created_at.asc())
            .limit(limit)
            .all()
        )