from pathlib import Path
import subprocess
import sys



class Runner:
    def run(self, workspace_path: Path) -> dict:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "-v"],
            cwd=workspace_path,
            capture_output=True,
            text=True,
        )

        return {
            "passed": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.returncode,
        }