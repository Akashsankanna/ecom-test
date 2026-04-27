# from typing import Optional, List
# from sqlalchemy.orm import Session
# from sqlalchemy import text

# from app.models.user import User
# from app.models.role import Role, UserRole
# from app.models.user_profile import UserProfile
# from app.models.audit_log import AuditLog


# class UserRepository:

#     # ════════════════════════════════════════════════════════════
#     # USERS
#     # ════════════════════════════════════════════════════════════

#     @staticmethod
#     def get_all_users(db: Session, user_type: Optional[str] = None) -> List[User]:
#         query = db.query(User).filter(User.is_deleted == False)
#         if user_type:
#             query = query.filter(User.user_type == user_type)
#         return query.order_by(User.created_at.desc()).all()

#     @staticmethod
#     def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
#         return db.query(User).filter(
#             User.id == user_id, User.is_deleted == False
#         ).first()

#     @staticmethod
#     def get_user_by_email(db: Session, email: str) -> Optional[User]:
#         return db.query(User).filter(User.email == email).first()

#     @staticmethod
#     def update_user(db: Session, user_id: int, data) -> Optional[User]:
#         """Uses sp_update_user(p_user_id, p_name, p_phone)."""
#         db.execute(
#             text("CALL sp_update_user(:uid, :name, :phone)"),
#             {"uid": user_id, "name": data.name, "phone": data.phone},
#         )
#         db.commit()
#         db.expire_all()
#         return db.query(User).filter(User.id == user_id).first()

#     @staticmethod
#     def soft_delete_user(db: Session, target_user_id: int) -> Optional[User]:
#         """Uses sp_delete_user(p_target_user_id) — 1 param in ecomdb21.
#         SP raises exception if user not found."""
#         db.execute(
#             text("CALL sp_delete_user(:uid)"),
#             {"uid": target_user_id},
#         )
#         db.commit()
#         db.expire_all()
#         return db.query(User).filter(User.id == target_user_id).first()

#     @staticmethod
#     def assign_role(db: Session, target_user_id: int, role_name: str):
#         """
#         Uses NEW sp_assign_role(p_target_user_id, p_role_name) — 2 params only.
#         New DB removed admin permission check from SP.
#         """
#         db.execute(
#             text("CALL sp_assign_role(:target_id, :role)"),
#             {"target_id": target_user_id, "role": role_name},
#         )
#         db.commit()

#     @staticmethod
#     def get_user_roles(db: Session, user_id: int) -> List[str]:
#         result = db.execute(
#             text(
#                 "SELECT r.role_name FROM roles r "
#                 "JOIN user_roles ur ON r.id = ur.role_id "
#                 "WHERE ur.user_id = :uid"
#             ),
#             {"uid": user_id},
#         )
#         return [row[0] for row in result.fetchall()]

#     @staticmethod
#     def remove_role(db: Session, user_id: int, role_name: str):
#         """Remove a role from a user."""
#         db.execute(
#             text(
#                 "DELETE FROM user_roles ur "
#                 "USING roles r "
#                 "WHERE ur.role_id = r.id "
#                 "AND ur.user_id = :uid AND r.role_name = :role"
#             ),
#             {"uid": user_id, "role": role_name},
#         )
#         db.commit()

#     @staticmethod
#     def get_all_roles(db: Session) -> List[Role]:
#         return db.query(Role).order_by(Role.id).all()

#     @staticmethod
#     def get_all_permissions(db: Session):
#         result = db.execute(text("SELECT * FROM permissions ORDER BY id"))
#         return [dict(row) for row in result.mappings()]

#     @staticmethod
#     def get_user_access_view(db: Session):
#         """Uses user_access_view DB view."""
#         result = db.execute(text("SELECT * FROM user_access_view ORDER BY user_id"))
#         return [dict(row) for row in result.mappings()]

#     @staticmethod
#     def get_user_full_access(db: Session):
#         """Uses user_full_access DB view — excludes deleted users."""
#         result = db.execute(text("SELECT * FROM user_full_access ORDER BY id"))
#         return [dict(row) for row in result.mappings()]

#     @staticmethod
#     def get_active_users_count(db: Session) -> int:
#         result = db.execute(text("SELECT COUNT(*) FROM active_users"))
#         return result.scalar()

#     # ════════════════════════════════════════════════════════════
#     # USER PROFILE
#     # ════════════════════════════════════════════════════════════

#     @staticmethod
#     def get_user_profile(db: Session, user_id: int) -> Optional[UserProfile]:
#         return db.query(UserProfile).filter(UserProfile.user_id == user_id).first()

#     @staticmethod
#     def upsert_user_profile(db: Session, user_id: int, data) -> Optional[UserProfile]:
#         """Uses sp_upsert_user_profile — INSERT ON CONFLICT UPDATE."""
#         db.execute(
#             text("CALL sp_upsert_user_profile(:uid, :img, :gender, :dob)"),
#             {
#                 "uid": user_id,
#                 "img": data.profile_image,
#                 "gender": data.gender,
#                 "dob": data.date_of_birth,
#             },
#         )
#         db.commit()
#         db.expire_all()
#         return db.query(UserProfile).filter(UserProfile.user_id == user_id).first()

#     @staticmethod
#     def get_user_profile_view(db: Session):
#         """Uses user_profile_view DB view."""
#         result = db.execute(text("SELECT * FROM user_profile_view"))
#         return [dict(row) for row in result.mappings()]

#     # ════════════════════════════════════════════════════════════
#     # AUDIT LOGS
#     # ════════════════════════════════════════════════════════════

#     @staticmethod
#     def get_audit_logs(
#         db: Session,
#         entity_type: Optional[str] = None,
#         user_id: Optional[int] = None,
#         limit: int = 100,
#     ) -> List[AuditLog]:
#         query = db.query(AuditLog)
#         if entity_type:
#             query = query.filter(AuditLog.entity_type == entity_type)
#         if user_id:
#             query = query.filter(AuditLog.user_id == user_id)
#         return query.order_by(AuditLog.created_at.desc()).limit(limit).all()

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.models.user import User
from app.models.role import Role
from app.models.user_profile import UserProfile
from app.models.audit_log import AuditLog


class UserRepository:

    # ════════════════════════════════════════════════════════════
    # USERS
    # ════════════════════════════════════════════════════════════

    @staticmethod
    def get_all_users(
        db: Session,
        user_type: Optional[str] = None
    ):
        where = "WHERE u.is_deleted = FALSE"
        params = {}

        if user_type:
            where += " AND u.user_type = :utype"
            params["utype"] = user_type.lower()

        result = db.execute(
            text(
                f"""
                SELECT
                    u.id,
                    u.name,
                    u.email,
                    u.phone,
                    u.user_type,
                    u.is_email_verified,
                    u.is_deleted,
                    u.created_at,
                    ARRAY_AGG(DISTINCT r.role_name)
                    FILTER (
                        WHERE r.role_name IS NOT NULL
                    ) AS roles
                FROM users u
                LEFT JOIN user_roles ur
                    ON u.id = ur.user_id
                LEFT JOIN roles r
                    ON ur.role_id = r.id
                {where}
                GROUP BY u.id
                ORDER BY u.created_at DESC
                """
            ),
            params
        )

        return [
            dict(row)
            for row in result.mappings()
        ]

    @staticmethod
    def get_user_by_id(
        db: Session,
        user_id: int
    ):
        user = db.execute(
            text(
                """
                SELECT
                    u.id,
                    u.name,
                    u.email,
                    u.phone,
                    u.user_type,
                    u.is_email_verified,
                    u.is_deleted,
                    u.created_at,
                    u.updated_at
                FROM users u
                WHERE u.id = :id
                """
            ),
            {"id": user_id}
        ).mappings().first()

        if not user:
            return None

        return user

    @staticmethod
    def get_user_by_email(
        db: Session,
        email: str
    ) -> Optional[User]:

        return (
            db.query(User)
            .filter(User.email == email)
            .first()
        )

    @staticmethod
    def update_user(
        db: Session,
        user_id: int,
        data
    ):
        db.execute(
            text(
                "CALL sp_update_user("
                ":uid, :name, :phone)"
            ),
            {
                "uid": user_id,
                "name": data.name,
                "phone": data.phone,
            },
        )

        db.commit()

        return db.execute(
            text(
                """
                SELECT
                    id,
                    name,
                    email,
                    phone
                FROM users
                WHERE id = :id
                """
            ),
            {"id": user_id},
        ).mappings().first()

    @staticmethod
    def soft_delete_user(
        db: Session,
        target_user_id: int
    ):
        db.execute(
            text(
                "CALL sp_delete_user(:uid)"
            ),
            {"uid": target_user_id},
        )

        db.commit()

        return db.query(User).filter(
            User.id == target_user_id
        ).first()

    @staticmethod
    def assign_role(
        db: Session,
        target_user_id: int,
        role_name: str
    ):
        db.execute(
            text(
                "CALL sp_assign_role("
                ":target_id, :role)"
            ),
            {
                "target_id": target_user_id,
                "role": role_name,
            },
        )

        db.commit()

    @staticmethod
    def remove_role(
        db: Session,
        user_id: int,
        role_name: str
    ):
        role_row = db.execute(
            text(
                """
                SELECT id
                FROM roles
                WHERE role_name =
                UPPER(TRIM(:rname))
                """
            ),
            {"rname": role_name},
        ).mappings().first()

        if not role_row:
            raise ValueError(
                f"Role '{role_name}' does not exist"
            )

        result = db.execute(
            text(
                """
                DELETE FROM user_roles
                WHERE user_id = :uid
                AND role_id = :rid
                RETURNING user_id
                """
            ),
            {
                "uid": user_id,
                "rid": role_row["id"],
            },
        )

        db.commit()

        deleted = result.mappings().first()

        if not deleted:
            raise ValueError(
                f"User {user_id} does not have "
                f"role '{role_name}'"
            )

    @staticmethod
    def get_user_roles(
        db: Session,
        user_id: int
    ) -> List[str]:

        result = db.execute(
            text(
                """
                SELECT r.role_name
                FROM roles r
                JOIN user_roles ur
                    ON r.id = ur.role_id
                WHERE ur.user_id = :uid
                """
            ),
            {"uid": user_id},
        )

        return [
            row[0]
            for row in result.fetchall()
        ]

    @staticmethod
    def get_all_roles(
        db: Session
    ) -> List[Role]:

        return (
            db.query(Role)
            .order_by(Role.id)
            .all()
        )

    @staticmethod
    def get_all_permissions(
        db: Session
    ):
        result = db.execute(
            text(
                "SELECT * "
                "FROM permissions "
                "ORDER BY id"
            )
        )

        return [
            dict(row)
            for row in result.mappings()
        ]

    @staticmethod
    def get_user_access_view(
        db: Session
    ):
        result = db.execute(
            text(
                "SELECT * "
                "FROM user_access_view "
                "ORDER BY user_id"
            )
        )

        return [
            dict(row)
            for row in result.mappings()
        ]

    @staticmethod
    def get_user_full_access(
        db: Session
    ):
        result = db.execute(
            text(
                "SELECT * "
                "FROM user_full_access "
                "ORDER BY id"
            )
        )

        return [
            dict(row)
            for row in result.mappings()
        ]

    @staticmethod
    def get_active_users_count(
        db: Session
    ) -> int:

        result = db.execute(
            text(
                "SELECT COUNT(*) "
                "FROM active_users"
            )
        )

        return result.scalar()

    # ════════════════════════════════════════════════════════════
    # USER PROFILE
    # ════════════════════════════════════════════════════════════

    @staticmethod
    def get_user_profile(
        db: Session,
        user_id: int
    ):

        return (
            db.query(UserProfile)
            .filter(
                UserProfile.user_id == user_id
            )
            .first()
        )

    @staticmethod
    def upsert_user_profile(
        db: Session,
        user_id: int,
        data
    ):
        db.execute(
            text(
                """
                CALL sp_upsert_user_profile(
                    :uid,
                    :img,
                    :gender,
                    :dob
                )
                """
            ),
            {
                "uid": user_id,
                "img": data.profile_image,
                "gender": data.gender,
                "dob": data.date_of_birth,
            },
        )

        db.commit()

        return db.query(UserProfile).filter(
            UserProfile.user_id == user_id
        ).first()

    @staticmethod
    def get_user_profile_view(
        db: Session
    ):
        result = db.execute(
            text(
                "SELECT * "
                "FROM user_profile_view"
            )
        )

        return [
            dict(row)
            for row in result.mappings()
        ]

    # ════════════════════════════════════════════════════════════
    # AUDIT LOGS
    # ════════════════════════════════════════════════════════════

    @staticmethod
    def get_audit_logs(
        db: Session,
        entity_type: Optional[str] = None,
        user_id: Optional[int] = None,
        limit: int = 500,
    ):
        where = "WHERE 1=1"
        params = {"limit": limit}

        if entity_type:
            where += " AND a.entity_type = :etype"
            params["etype"] = entity_type

        if user_id:
            where += " AND a.user_id = :uid"
            params["uid"] = user_id

        result = db.execute(
            text(
                f"""
                SELECT
                    a.id,
                    a.user_id,
                    u.name AS user_name,
                    a.action,
                    a.entity_type,
                    a.entity_id,
                    a.old_data,
                    a.new_data,
                    a.created_at
                FROM audit_log a
                LEFT JOIN users u
                    ON a.user_id = u.id
                {where}
                ORDER BY a.created_at DESC
                LIMIT :limit
                """
            ),
            params
        )

        return [
            dict(row)
            for row in result.mappings()
        ]