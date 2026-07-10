from app.db.base import Base
from app.db.session import engine

from app.db.models.execution import Execution
from app.db.models.execution_iteration import ExecutionIteration
from app.db.models.execution_log import ExecutionLog
from app.db.models.job import Job
from app.db.models.user import User


def init_db():
    Base.metadata.create_all(bind=engine)