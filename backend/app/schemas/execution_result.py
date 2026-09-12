from pydantic import BaseModel


class ExecutionResult(BaseModel):
    workspace: str
    passed: bool
    tries_used: int
    stdout: str
    stderr: str
    exit_code: int
    execution_id: str | None = None