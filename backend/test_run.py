from fastapi import APIRouter, Body
from pydantic import BaseModel
from app.sandbox.workspace_mgr import WorkspaceManager

from app.agents.coder import CodeAgent
from app.agents.tester import TestAgent
from app.runner.runner import Runner
from pathlib import Path

runner = Runner()

print(runner.run(Path("/Users/sainath/Documents/code-orchestrator/backend/workspace/84d1fce9-6db3-4e9c-91cc-f97a7f976b71")))