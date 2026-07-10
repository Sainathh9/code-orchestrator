"""
User database model.

Stores users who have authenticated via Google OAuth. The ``google_id``
column holds Google's stable ``sub`` claim — this is the immutable identity
key across logins. Emails can change (e.g. workspace domain migration),
so we never use email as the primary match key.
"""

import uuid
from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    google_id = Column(String(255), unique=True, index=True, nullable=True)

    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=True)
    profile_picture = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
