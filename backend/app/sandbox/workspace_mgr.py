import uuid
from pathlib import Path


class WorkspaceManager:
    def __init__(self):
        self.base_dir = Path.cwd() / "workspace"
        self.base_dir.mkdir(exist_ok=True)

    def create_workspace(self) -> Path:
        workspace_id = str(uuid.uuid4())

        workspace_path = self.base_dir / workspace_id
        workspace_path.mkdir(parents=True, exist_ok=True)

        return workspace_path

    def write_file(self, workspace_path: Path, filename: str,content : str) -> Path :
          file_path = workspace_path/filename 
          
          file_path.write_text(
            content,
            encoding = "utf-8"
            )
          
    def read_file(self,workspace_path: Path, filename: str) -> str:
          file_path = workspace_path/filename
          generated_content = file_path.read_text()
          return generated_content
          

        