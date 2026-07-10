from pathlib import Path
from datetime import datetime
from app.sandbox.workspace_mgr import WorkspaceManager


class ExecutionContext:
    def __init__(
        self,
        workspace: WorkspaceManager,
        workspace_path: Path,
    ):
        self.workspace = workspace
        self.workspace_path = workspace_path

        # 🔥 Execution metadata
        self.execution_id: str | None = None
        self.version: int = 1
        self.iteration: int = 0

        self.created_at: datetime = datetime.utcnow()
        self.started_at: datetime | None = None
        self.finished_at: datetime | None = None

        self.status: str = "created"  # created | running | success | failed