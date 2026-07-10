import uuid
from sqlalchemy import Column, String, Text, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.db.base import Base
from app.db.models.execution import Execution


class ExecutionIteration(Base):
    __tablename__ = "execution_iterations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    execution_id = Column(
        UUID(as_uuid=True),
        ForeignKey("executions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    iteration_number = Column(Integer, nullable=False)

    generated_code = Column(Text, nullable=True)
    generated_tests = Column(Text, nullable=True)
    test_output = Column(Text, nullable=True)
    debugger_output = Column(Text, nullable=True)
    error_type = Column(String(100), nullable=True)

    passed = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())