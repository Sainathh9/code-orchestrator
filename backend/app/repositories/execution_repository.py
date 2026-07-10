from datetime import datetime

from app.db.models.execution import Execution


class ExecutionRepository:

    def __init__(self, db):
        self.db = db

    def create(self, requirement, workspace_path, started_at, user_id):
        execution = Execution(
            requirement=requirement,
            workspace_path=workspace_path,
            status="running",
            tries_used=0,
            started_at=started_at,
            user_id=user_id,
        )

        self.db.add(execution)
        self.db.commit()
        self.db.refresh(execution)
        return execution

    def update_status(self, execution, status, tries_used, finished_at):
        execution.status = status
        execution.tries_used = tries_used
        execution.finished_at = finished_at

        self.db.commit()