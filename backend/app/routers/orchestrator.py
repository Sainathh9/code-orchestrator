from fastapi import APIRouter, Body
from pydantic import BaseModel
from app.sandbox.workspace_mgr import WorkspaceManager

from app.agents.coder import CodeAgent
from app.agents.tester import TestAgent
from app.runner.runner import Runner
from app.agents.debugger import DebuggerAgent

router = APIRouter()

code_agent = CodeAgent()
test_agent = TestAgent()
runner = Runner()
debugger = DebuggerAgent()



MAX_TRIES = 3


class GenerateRequest(BaseModel):
    requirement: str


@router.post("/generate")
def generate(request: GenerateRequest):
    workspace = WorkspaceManager()
    workspace_path = workspace.create_workspace()

    code_agent.run(request.requirement, workspace, workspace_path)
    test_agent.run(workspace_path, workspace)

    result = None

    for attempt in range(MAX_TRIES):
        print(f"Attempt {attempt + 1}/{MAX_TRIES}")

        result = runner.run(workspace_path)

        if result["passed"]:
            print("✅ Tests passed!")
            break

        print("❌ Tests failed. Debugging...")
        debugger.run(
            workspace,
            workspace_path,
            result["stdout"],
        )

    return {
        "workspace": str(workspace_path),
        "passed": result["passed"],
        "tries_used": attempt + 1,
        "stdout": result["stdout"],
        "stderr": result["stderr"],
    }