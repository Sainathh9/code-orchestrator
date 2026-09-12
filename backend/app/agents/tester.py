from pathlib import Path
from app.services.llm.factory import LLMFactory
from app.agents.base import BaseAgent
from app.services.llm.prompts import TEST_GENERATION_PROMPT
from app.sandbox.workspace_mgr import WorkspaceManager
from app.schemas.execution_context import ExecutionContext


class TestAgent(BaseAgent):
     def __init__(self, model: str | None = None):
           self.llm = LLMFactory.create(model=model)
    
     def run(self,
       context: ExecutionContext) -> None:
           generated_code = context.workspace.read_file(context.workspace_path, "solution.py")
           prompt = TEST_GENERATION_PROMPT.format(code=generated_code)
           test_cases = self.llm.generate(prompt)
           context.workspace.write_file(context.workspace_path, "test_solution.py", test_cases)
