from app.db.models.execution import Execution
from app.db.models.execution_iteration import ExecutionIteration


class ExecutionReadRepository:

    def __init__(self, db):
        self.db = db

    def get_all_executions(self):
        return self.db.query(Execution).all()

    def get_all_executions_for_user(self, user_id):
        return self.db.query(Execution).filter(
            Execution.user_id == user_id
        ).order_by(Execution.created_at.desc()).all()

    def get_execution(self, execution_id):
        return self.db.query(Execution).filter(
            Execution.id == execution_id
        ).first()

    def get_execution_for_user(self, execution_id, user_id):
        return self.db.query(Execution).filter(
            Execution.id == execution_id,
            Execution.user_id == user_id
        ).first()

    def get_iterations(self, execution_id):
        return self.db.query(ExecutionIteration).filter(
            ExecutionIteration.execution_id == execution_id
        ).order_by(ExecutionIteration.iteration_number.asc()).all()