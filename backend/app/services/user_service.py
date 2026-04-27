# from sqlalchemy import text
# from sqlalchemy.orm import Session
# from fastapi import HTTPException
# from typing import Optional

# from app.repositories.user_repo import UserRepository

# # supports both locations
# try:
#     from app.schemas.user import UserUpdate, AssignRoleRequest
# except:
#     from app.schemas.user import UserUpdate, AssignRoleRequest


# # ════════════════════════════════════════════════════════════
# # 🔐 AUTH FUNCTIONS (LOGIN SAFE)
# # ════════════════════════════════════════════════════════════

# def create_user_in_db(
#     db,
#     name,
#     email,
#     phone,
#     keycloak_id,
#     is_email_verified=False
# ):
#     try:
#         print(
#             f"\n📝 create_user_in_db: "
#             f"email={email}, phone={phone}, keycloak_id={keycloak_id}"
#         )

#         db.execute(
#             text("""
#                 INSERT INTO public.users (
#                     name,
#                     email,
#                     phone,
#                     user_type,
#                     keycloak_id,
#                     is_email_verified,
#                     is_deleted
#                 )
#                 VALUES (
#                     :name,
#                     :email,
#                     :phone,
#                     :user_type,
#                     :keycloak_id,
#                     :is_email_verified,
#                     :is_deleted
#                 )
#             """),
#             {
#                 "name": name,
#                 "email": email,
#                 "phone": phone,
#                 "user_type": "customer",
#                 "keycloak_id": keycloak_id,
#                 "is_email_verified": is_email_verified,
#                 "is_deleted": False,
#             }
#         )

#         db.commit()

#         result = db.execute(
#             text("""
#                 SELECT
#                     id,
#                     name,
#                     email,
#                     phone,
#                     keycloak_id,
#                     user_type,
#                     is_email_verified,
#                     created_at
#                 FROM public.users
#                 WHERE keycloak_id = :kid
#                 LIMIT 1
#             """),
#             {"kid": keycloak_id}
#         ).fetchone()

#         if not result:
#             raise HTTPException(
#                 status_code=500,
#                 detail="User inserted but not retrievable"
#             )

#         return _row_to_user(result)

#     except HTTPException:
#         raise

#     except Exception as e:
#         import traceback
#         traceback.print_exc()
#         db.rollback()

#         raise HTTPException(
#             status_code=500,
#             detail=f"DB insert error: {str(e)}"
#         )


# def get_user_by_keycloak_id(db, keycloak_id: str):
#     try:
#         result = db.execute(
#             text("""
#                 SELECT
#                     id,
#                     name,
#                     email,
#                     phone,
#                     keycloak_id,
#                     user_type,
#                     is_email_verified,
#                     created_at
#                 FROM public.users
#                 WHERE keycloak_id = :kid
#                 LIMIT 1
#             """),
#             {"kid": keycloak_id}
#         ).fetchone()

#         return _row_to_user(result) if result else None

#     except Exception as e:
#         print(f"⚠️ get_user_by_keycloak_id error: {e}")
#         return None


# def get_user_by_phone(db, phone: str):
#     try:
#         result = db.execute(
#             text("""
#                 SELECT
#                     id,
#                     name,
#                     email,
#                     phone,
#                     keycloak_id,
#                     user_type,
#                     is_email_verified,
#                     created_at
#                 FROM public.users
#                 WHERE phone = :phone
#                 AND is_deleted = FALSE
#                 LIMIT 1
#             """),
#             {"phone": phone}
#         ).fetchone()

#         return _row_to_user(result) if result else None

#     except Exception as e:
#         print(f"⚠️ get_user_by_phone error: {e}")
#         return None


# def get_user_by_email(db, email: str):
#     try:
#         result = db.execute(
#             text("""
#                 SELECT
#                     id,
#                     name,
#                     email,
#                     phone,
#                     keycloak_id,
#                     user_type,
#                     is_email_verified,
#                     created_at
#                 FROM public.users
#                 WHERE email = :email
#                 AND is_deleted = FALSE
#                 LIMIT 1
#             """),
#             {"email": email}
#         ).fetchone()

#         return _row_to_user(result) if result else None

#     except Exception as e:
#         print(f"⚠️ get_user_by_email error: {e}")
#         return None


# def _row_to_user(row):
#     if not row:
#         return None

#     return User(
#         id=row[0],
#         name=row[1],
#         email=row[2],
#         phone=row[3],
#         keycloak_id=row[4],
#         user_type=row[5],
#         is_email_verified=row[6],
#         created_at=row[7],
#     )


# class User:
#     def __init__(
#         self,
#         id,
#         name,
#         email,
#         phone,
#         keycloak_id,
#         user_type,
#         is_email_verified,
#         created_at
#     ):
#         self.id = id
#         self.name = name
#         self.email = email
#         self.phone = phone
#         self.keycloak_id = keycloak_id
#         self.user_type = user_type
#         self.is_email_verified = is_email_verified
#         self.created_at = created_at

#     def __repr__(self):
#         return f"<User id={self.id} email={self.email}>"


# # ════════════════════════════════════════════════════════════
# # 🛠 ADMIN USER SERVICE
# # ════════════════════════════════════════════════════════════

# class UserService:

#     @staticmethod
#     def get_all_users(
#         db: Session,
#         user_type: Optional[str] = None
#     ):
#         return UserRepository.get_all_users(
#             db,
#             user_type
#         )

#     @staticmethod
#     def get_user(
#         db: Session,
#         user_id: int
#     ):
#         user = UserRepository.get_user_by_id(
#             db,
#             user_id
#         )

#         if not user:
#             raise HTTPException(
#                 status_code=404,
#                 detail="User not found"
#             )

#         roles = UserRepository.get_user_roles(
#             db,
#             user_id
#         )

#         return user, roles

#     @staticmethod
#     def update_user(
#         db: Session,
#         user_id: int,
#         data: UserUpdate
#     ):
#         user = UserRepository.get_user_by_id(
#             db,
#             user_id
#         )

#         if not user:
#             raise HTTPException(
#                 status_code=404,
#                 detail="User not found"
#             )

#         update_data = UserUpdate(
#             name=data.name if data.name is not None else user.name,
#             phone=data.phone if data.phone is not None else user.phone,
#         )

#         try:
#             return UserRepository.update_user(
#                 db,
#                 user_id,
#                 update_data
#             )

#         except Exception as e:
#             raise HTTPException(
#                 status_code=400,
#                 detail=str(e)
#             )

#     @staticmethod
#     def delete_user(
#         db: Session,
#         admin_user_id: int,
#         target_user_id: int
#     ):
#         if admin_user_id == target_user_id:
#             raise HTTPException(
#                 status_code=400,
#                 detail="Admin cannot delete own account"
#             )

#         user = UserRepository.get_user_by_id(
#             db,
#             target_user_id
#         )

#         if not user:
#             raise HTTPException(
#                 status_code=404,
#                 detail="User not found"
#             )

#         try:
#             UserRepository.soft_delete_user(
#                 db,
#                 admin_user_id,
#                 target_user_id
#             )

#             return {
#                 "message":
#                 f"User {target_user_id} deleted successfully"
#             }

#         except Exception as e:
#             raise HTTPException(
#                 status_code=400,
#                 detail=str(e)
#             )

#     @staticmethod
#     def assign_role(
#         db: Session,
#         admin_user_id: int,
#         data: AssignRoleRequest
#     ):
#         user = UserRepository.get_user_by_id(
#             db,
#             data.target_user_id
#         )

#         if not user:
#             raise HTTPException(
#                 status_code=404,
#                 detail="Target user not found"
#             )

#         all_roles = UserRepository.get_all_roles(db)
#         valid_role_names = [r.role_name for r in all_roles]

#         if data.role_name not in valid_role_names:
#             raise HTTPException(
#                 status_code=400,
#                 detail=f"Invalid role '{data.role_name}'. Valid roles: {valid_role_names}"
#             )

#         try:
#             UserRepository.assign_role(
#                 db,
#                 admin_user_id,
#                 data.target_user_id,
#                 data.role_name
#             )

#             return {
#                 "message":
#                 f"Role '{data.role_name}' assigned to user {data.target_user_id}",
#                 "user_id": data.target_user_id,
#                 "role": data.role_name,
#             }

#         except Exception as e:
#             raise HTTPException(
#                 status_code=400,
#                 detail=str(e)
#             )

#     @staticmethod
#     def remove_role(
#         db: Session,
#         user_id: int,
#         role_name: str
#     ):
#         user = UserRepository.get_user_by_id(
#             db,
#             user_id
#         )

#         if not user:
#             raise HTTPException(
#                 status_code=404,
#                 detail="User not found"
#             )

#         try:
#             UserRepository.remove_role(
#                 db,
#                 user_id,
#                 role_name
#             )

#             return {
#                 "message":
#                 f"Role '{role_name}' removed from user {user_id}"
#             }

#         except Exception as e:
#             raise HTTPException(
#                 status_code=400,
#                 detail=str(e)
#             )

#     @staticmethod
#     def get_all_roles(db: Session):
#         return UserRepository.get_all_roles(db)

#     @staticmethod
#     def get_user_access_view(db: Session):
#         return UserRepository.get_user_access_view(db)

#     @staticmethod
#     def get_user_full_access(db: Session):
#         return UserRepository.get_user_full_access(db)

#     @staticmethod
#     def get_user_profile(
#         db: Session,
#         user_id: int
#     ):
#         user = UserRepository.get_user_by_id(
#             db,
#             user_id
#         )

#         if not user:
#             raise HTTPException(
#                 status_code=404,
#                 detail="User not found"
#             )

#         return UserRepository.get_user_profile(
#             db,
#             user_id
#         )

#     @staticmethod
#     def upsert_user_profile(
#         db: Session,
#         user_id: int,
#         data
#     ):
#         user = UserRepository.get_user_by_id(
#             db,
#             user_id
#         )

#         if not user:
#             raise HTTPException(
#                 status_code=404,
#                 detail="User not found"
#             )

#         try:
#             return UserRepository.upsert_user_profile(
#                 db,
#                 user_id,
#                 data
#             )

#         except Exception as e:
#             raise HTTPException(
#                 status_code=400,
#                 detail=str(e)
#             )

#     @staticmethod
#     def get_audit_logs(
#         db: Session,
#         entity_type: Optional[str] = None,
#         user_id: Optional[int] = None,
#         limit: int = 100
#     ):
#         return UserRepository.get_audit_logs(
#             db,
#             entity_type,
#             user_id,
#             limit
#         )

from sqlalchemy import text
from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import Optional

from app.repositories.user_repo import UserRepository

try:
    from app.schemas.user import UserUpdate, AssignRoleRequest
except Exception:
    from app.schemas.user import UserUpdate, AssignRoleRequest


# ════════════════════════════════════════════════════════════
# AUTH / LOGIN HELPERS
# ════════════════════════════════════════════════════════════

def create_user_in_db(
    db,
    name,
    email,
    phone,
    keycloak_id,
    is_email_verified=False
):
    try:
        db.execute(
            text(
                """
                INSERT INTO public.users (
                    name,
                    email,
                    phone,
                    user_type,
                    keycloak_id,
                    is_email_verified,
                    is_deleted
                )
                VALUES (
                    :name,
                    :email,
                    :phone,
                    :user_type,
                    :keycloak_id,
                    :is_email_verified,
                    :is_deleted
                )
                """
            ),
            {
                "name": name,
                "email": email,
                "phone": phone,
                "user_type": "customer",
                "keycloak_id": keycloak_id,
                "is_email_verified": is_email_verified,
                "is_deleted": False,
            }
        )

        db.commit()

        result = db.execute(
            text(
                """
                SELECT
                    id,
                    name,
                    email,
                    phone,
                    keycloak_id,
                    user_type,
                    is_email_verified,
                    created_at
                FROM public.users
                WHERE keycloak_id = :kid
                LIMIT 1
                """
            ),
            {"kid": keycloak_id}
        ).fetchone()

        if not result:
            raise HTTPException(
                status_code=500,
                detail="User inserted but not retrievable"
            )

        return _row_to_user(result)

    except HTTPException:
        raise

    except Exception as e:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"DB insert error: {str(e)}"
        )


def get_user_by_keycloak_id(
    db,
    keycloak_id: str
):
    try:
        result = db.execute(
            text(
                """
                SELECT
                    id,
                    name,
                    email,
                    phone,
                    keycloak_id,
                    user_type,
                    is_email_verified,
                    created_at
                FROM public.users
                WHERE keycloak_id = :kid
                LIMIT 1
                """
            ),
            {"kid": keycloak_id}
        ).fetchone()

        return _row_to_user(result) if result else None

    except Exception:
        return None


def get_user_by_phone(
    db,
    phone: str
):
    try:
        result = db.execute(
            text(
                """
                SELECT
                    id,
                    name,
                    email,
                    phone,
                    keycloak_id,
                    user_type,
                    is_email_verified,
                    created_at
                FROM public.users
                WHERE phone = :phone
                AND is_deleted = FALSE
                LIMIT 1
                """
            ),
            {"phone": phone}
        ).fetchone()

        return _row_to_user(result) if result else None

    except Exception:
        return None


def get_user_by_email(
    db,
    email: str
):
    try:
        result = db.execute(
            text(
                """
                SELECT
                    id,
                    name,
                    email,
                    phone,
                    keycloak_id,
                    user_type,
                    is_email_verified,
                    created_at
                FROM public.users
                WHERE email = :email
                AND is_deleted = FALSE
                LIMIT 1
                """
            ),
            {"email": email}
        ).fetchone()

        return _row_to_user(result) if result else None

    except Exception:
        return None


def _row_to_user(row):
    if not row:
        return None

    return User(
        id=row[0],
        name=row[1],
        email=row[2],
        phone=row[3],
        keycloak_id=row[4],
        user_type=row[5],
        is_email_verified=row[6],
        created_at=row[7],
    )


class User:
    def __init__(
        self,
        id,
        name,
        email,
        phone,
        keycloak_id,
        user_type,
        is_email_verified,
        created_at
    ):
        self.id = id
        self.name = name
        self.email = email
        self.phone = phone
        self.keycloak_id = keycloak_id
        self.user_type = user_type
        self.is_email_verified = is_email_verified
        self.created_at = created_at

    def __repr__(self):
        return f"<User id={self.id} email={self.email}>"


# ════════════════════════════════════════════════════════════
# USER SERVICE
# ════════════════════════════════════════════════════════════

class UserService:

    @staticmethod
    def get_all_users(
        db: Session,
        user_type: Optional[str] = None
    ):
        return UserRepository.get_all_users(
            db,
            user_type
        )

    @staticmethod
    def get_user(
        db: Session,
        user_id: int
    ):
        user = UserRepository.get_user_by_id(
            db,
            user_id
        )

        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        roles = UserRepository.get_user_roles(
            db,
            user_id
        )

        return user, roles

    @staticmethod
    def get_user_detail(
        db: Session,
        user_id: int
    ):
        user = UserRepository.get_user_by_id(
            db,
            user_id
        )

        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        result = dict(user)
        result["roles"] = UserRepository.get_user_roles(
            db,
            user_id
        )

        return result

    @staticmethod
    def update_user(
        db: Session,
        user_id: int,
        data: UserUpdate
    ):
        user = UserRepository.get_user_by_id(
            db,
            user_id
        )

        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        update_data = UserUpdate(
            name=data.name if data.name is not None else user["name"],
            phone=data.phone if data.phone is not None else user["phone"],
        )

        try:
            return UserRepository.update_user(
                db,
                user_id,
                update_data
            )

        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=str(e)
            )

    @staticmethod
    def delete_user(
        db: Session,
        admin_user_id: int,
        target_user_id: int
    ):
        if admin_user_id == target_user_id:
            raise HTTPException(
                status_code=400,
                detail="Cannot delete your own account"
            )

        user = UserRepository.get_user_by_id(
            db,
            target_user_id
        )

        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        try:
            UserRepository.soft_delete_user(
                db,
                target_user_id
            )

            return {
                "message": "User soft-deleted",
                "user_id": target_user_id
            }

        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=str(e)
            )

    @staticmethod
    def get_profile(
        db: Session,
        user_id: int
    ):
        profile = UserRepository.get_user_profile(
            db,
            user_id
        )

        if not profile:
            raise HTTPException(
                status_code=404,
                detail="Profile not found"
            )

        return profile

    @staticmethod
    def get_user_profile(
        db: Session,
        user_id: int
    ):
        return UserService.get_profile(
            db,
            user_id
        )

    @staticmethod
    def upsert_profile(
        db: Session,
        user_id: int,
        data
    ):
        try:
            return UserRepository.upsert_user_profile(
                db,
                user_id,
                data
            )

        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=str(e)
            )

    @staticmethod
    def upsert_user_profile(
        db: Session,
        user_id: int,
        data
    ):
        return UserService.upsert_profile(
            db,
            user_id,
            data
        )

    @staticmethod
    def get_all_roles(
        db: Session
    ):
        return UserRepository.get_all_roles(db)

    @staticmethod
    def get_access_view(
        db: Session
    ):
        return UserRepository.get_user_access_view(db)

    @staticmethod
    def get_user_access_view(
        db: Session
    ):
        return UserRepository.get_user_access_view(db)

    @staticmethod
    def get_full_access(
        db: Session
    ):
        return UserRepository.get_user_full_access(db)

    @staticmethod
    def get_user_full_access(
        db: Session
    ):
        return UserRepository.get_user_full_access(db)

    @staticmethod
    def assign_role(
        db: Session,
        user_id: int,
        role_name: str
    ):
        try:
            UserRepository.assign_role(
                db,
                user_id,
                role_name
            )

            return {
                "message": f"Role '{role_name}' assigned to user {user_id}"
            }

        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=str(e)
            )

    @staticmethod
    def assign_role_request(
        db: Session,
        data: AssignRoleRequest
    ):
        return UserService.assign_role(
            db,
            data.target_user_id,
            data.role_name
        )

    @staticmethod
    def remove_role(
        db: Session,
        user_id: int,
        role_name: str
    ):
        try:
            UserRepository.remove_role(
                db,
                user_id,
                role_name
            )

            return {
                "message": f"Role '{role_name}' removed from user {user_id}"
            }

        except ValueError as e:
            status = (
                404
                if "does not have" in str(e)
                or "does not exist" in str(e)
                else 400
            )

            raise HTTPException(
                status_code=status,
                detail=str(e)
            )

        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=str(e)
            )

    @staticmethod
    def get_audit_logs(
        db: Session,
        entity_type: Optional[str] = None,
        user_id: Optional[int] = None,
        limit: int = 500
    ):
        return UserRepository.get_audit_logs(
            db,
            entity_type,
            user_id,
            limit
        )