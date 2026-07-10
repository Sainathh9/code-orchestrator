from datetime import datetime
from typing import List, Optional


class ExecutionSummary:
    def __init__(
        self,
        execution_id: str,
        requirement: str,
        status: str,
        tries_used: int,
        created_at: datetime,
    ):
        self.execution_id = execution_id
        self.requirement = requirement
        self.status = status
        self.tries_used = tries_used
        self.created_at = created_at


class ExecutionIterationView:
    def __init__(
        self,
        iteration: int,
        code: str,
        test_output: str,
        passed: bool,
    ):
        self.iteration = iteration
        self.code = code
        self.test_output = test_output
        self.passed = passed


class ExecutionDetail:
    def __init__(
        self,
        execution_id: str,
        status: str,
        tries_used: int,
        iterations: List[ExecutionIterationView],
    ):
        self.execution_id = execution_id
        self.status = status
        self.tries_used = tries_used
        self.iterations = iterations