import uuid
from sqlalchemy import Column, String, Text, DateTime, Integer, BigInteger, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.db.base import Base
from app.db.models.user import User


class Execution(Base):
    __tablename__ = "executions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    requirement = Column(Text, nullable=False)

    status = Column(
        String(20),
        nullable=False,
        default="queued",
    )

    current_step = Column(String(100), nullable=True)

    tries_used = Column(Integer, default=0)
    execution_time_ms = Column(BigInteger, nullable=True)

    workspace_path = Column(Text, nullable=True)

    started_at = Column(DateTime(timezone=True), nullable=True)
    finished_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        CheckConstraint(
            "status IN ('queued', 'running', 'success', 'failed', 'cancelled')",
            name="executions_status_check",
        ),
    )