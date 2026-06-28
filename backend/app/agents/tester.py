from pathlib import Path
from app.services.llm.factory import LLMFactory
from app.agents.base import BaseAgent
from app.services.llm.prompts import TEST_GENERATION_PROMPT
from app.sandbox.workspace_mgr import WorkspaceManager


class TestAgent(BaseAgent):
     def __init__(self):
           self.llm = LLMFactory.create()
    
     def run(self, workspace_path: Path, workspace: WorkspaceManager) -> None:
           generated_code = workspace.read_file(workspace_path, "solution.py")
           prompt = TEST_GENERATION_PROMPT.format(code=generated_code)
           test_cases = self.llm.generate(prompt)
           workspace.write_file(workspace_path, "test_solution.py", test_cases)
