from app.agents.base import BaseAgent
from app.services.llm.factory import LLMFactory
from app.services.llm.prompts import DEBUGGER_PROMPT
from app.sandbox.workspace_mgr import WorkspaceManager
from pathlib import Path

class DebuggerAgent(BaseAgent):
     def __init__(self):
           self.llm = LLMFactory.create()

     def run(self,workspace : WorkspaceManager, workspace_path: Path, test_output: str) -> None :
         generated_code = workspace.read_file(workspace_path, "solution.py")
         prompt = DEBUGGER_PROMPT.format(
              code = generated_code,
              test_output = test_output
          )
         new_code = self.llm.generate(prompt)
         workspace.write_file(workspace_path, "solution.py", new_code)
         
          