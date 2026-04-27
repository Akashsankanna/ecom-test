from sqlalchemy import (
    Column,
    Integer,
    Text,
    Boolean,
)
from sqlalchemy.dialects.postgresql import TIMESTAMP, UUID
from sqlalchemy.sql import func

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    # =====================================================
    # PRIMARY KEY
    # =====================================================
    id = Column(Integer, primary_key=True, index=True)

    # =====================================================
    # USER DETAILS
    # =====================================================
    name = Column(
        Text,
        nullable=False
    )

    email = Column(
        Text,
        unique=True,
        nullable=True
    )

    phone = Column(
        Text,
        nullable=True
    )

    # customer | admin
    user_type = Column(
        Text,
        nullable=True
    )

    # guest checkout / temporary visitor id
    guest_id = Column(
        UUID(as_uuid=True),
        nullable=True
    )

    keycloak_id = Column(
        Text,
        unique=True,
        nullable=True
    )

    # =====================================================
    # STATUS FLAGS
    # =====================================================
    is_deleted = Column(
        Boolean,
        default=False
    )

    is_email_verified = Column(
        Boolean,
        default=False
    )

    # =====================================================
    # TIMESTAMPS
    # =====================================================
    created_at = Column(
        TIMESTAMP,
        server_default=func.now()
    )

    updated_at = Column(
        TIMESTAMP,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=True
    )