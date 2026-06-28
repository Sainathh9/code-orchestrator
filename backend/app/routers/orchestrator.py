from fastapi import APIRouter, Body
from pydantic import BaseModel
from app.sandbox.workspace_mgr import WorkspaceManager

from app.agents.coder import CodeAgent
from app.agents.tester import TestAgent

router = APIRouter()

code_agent = CodeAgent()
test_agent = TestAgent()


class GenerateRequest(BaseModel):
    requirement: str


@router.post("/generate")
def generate(request: GenerateRequest):
     workspace = WorkspaceManager()
     workspace_path = workspace.create_workspace()
     code_agent.run(request.requirement, workspace, workspace_path)
     test_agent.run(workspace_path, workspace)

     return {
        "workspace" : workspace_path,
        "status" : "success"
    }