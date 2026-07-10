from pydantic import BaseModel

class RunnerResult(BaseModel):
    passed: bool
    stdout: str
    stderr: str
    exit_code: int