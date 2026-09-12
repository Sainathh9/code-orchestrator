from app.services.llm.factory import LLMFactory
from app.services.llm.prompts import DEBUGGER_PROMPT


class DebuggerAgent:

    def __init__(self, model: str | None = None):
        self.llm = LLMFactory.create(model=model)

    def run(self, context, test_output: str) -> None:

        # 1. Read current code
        old_code = context.workspace.read_file(
            context.workspace_path,
            "solution.py"
        )

        # 2. Generate fix
        prompt = DEBUGGER_PROMPT.format(
            code=old_code,
            test_output=test_output
        )

        new_code = self.llm.generate(prompt)

        # 3. SAFETY CHECKS (BEFORE ANY WRITE)
        if not new_code:
            return

        new_code = new_code.strip()
        old_code = old_code.strip()

        if len(new_code) < 10:
            return

        # 4. If no improvement → skip
        if new_code == old_code:
            return

        # 5. Update version ONLY when valid change exists
        context.version += 1

        # 6. Write updated solution
        context.workspace.write_file(
            context.workspace_path,
            "solution.py",
            new_code
        )

        # 7. Save version snapshot
        context.workspace.save_version(
            context.workspace_path,
            context.version,
            new_code
        )

       