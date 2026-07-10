from app.agents.base import BaseAgent
from app.services.llm.factory import LLMFactory
from app.services.llm.prompts import CODE_GENERATION_PROMPT
from app.schemas.execution_context import ExecutionContext


class CodeAgent(BaseAgent):

    def __init__(self):
        self.llm = LLMFactory.create()

    def run(
        self,
        requirement: str,
        context: ExecutionContext,
    ) -> None:

        prompt = CODE_GENERATION_PROMPT.format(
            requirement=requirement
        )

        generated_code = self.llm.generate(prompt)

        # SAFETY CHECK
        if not generated_code or len(generated_code.strip()) < 10:
            raise ValueError("LLM returned invalid code")

        generated_code = generated_code.strip()

        # write solution
        context.workspace.write_file(
            context.workspace_path,
            "solution.py",
            generated_code
        )

        # save version (IMPORTANT: use current version)
        context.workspace.save_version(
            context.workspace_path,
            context.version,
            generated_code,
        )