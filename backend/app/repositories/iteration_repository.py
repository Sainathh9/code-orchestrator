from app.db.models.execution_iteration import ExecutionIteration


class ExecutionIterationRepository:

    def __init__(self, db):
        self.db = db

    def create(self, execution_id, iteration_number, generated_code,
               test_output, passed, generated_tests=None,
               debugger_output=None, error_type=None):
        row = ExecutionIteration(
            execution_id=execution_id,
            iteration_number=iteration_number,
            generated_code=generated_code,
            test_output=test_output,
            passed=passed,
            generated_tests=generated_tests,
            debugger_output=debugger_output,
            error_type=error_type,
        )

        self.db.add(row)
        self.db.commit()
        return row