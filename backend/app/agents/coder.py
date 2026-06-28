from app.agents.base import BaseAgent
from app.services.llm.factory import LLMFactory
from app.services.llm.prompts import CODE_GENERATION_PROMPT
from app.sandbox.workspace_mgr import WorkspaceManager
from pathlib import Path


class CodeAgent(BaseAgent):

    def __init__(self):
        self.llm = LLMFactory.create()

    def run(self, 
            requirement: str, 
            workspace: WorkspaceManager,
              workspace_path: Path):

        prompt = CODE_GENERATION_PROMPT.format(
            requirement=requirement
        )

        generated_code = self.llm.generate(prompt)
        workspace.write_file(workspace_path, "solution.py", generated_code)
       