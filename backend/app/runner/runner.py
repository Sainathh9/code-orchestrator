"""
Runner — thin façade that selects the execution backend.

The public interface is unchanged:
    runner = Runner()
    result = runner.run(workspace_path)
    # result.passed, result.stdout, result.stderr, result.exit_code

Internally this now delegates to DockerRunner, which runs pytest inside a
disposable Docker container with network disabled and resource limits applied.

If the Docker daemon is unavailable (e.g. local dev without Docker Desktop),
the error is caught and returned as a failed RunnerResult so the rest of the
orchestration pipeline continues gracefully.
"""

from __future__ import annotations

import logging
from pathlib import Path

from app.runner.docker_runner import DockerRunner, RunnerResult

logger = logging.getLogger(__name__)

# Module-level singleton — the DockerRunner builds/validates the sandbox image
# once when it is first instantiated, then reuses it for every run() call.
_docker_runner: DockerRunner | None = None


def _get_docker_runner() -> DockerRunner:
    global _docker_runner
    if _docker_runner is None:
        _docker_runner = DockerRunner()
    return _docker_runner


class Runner:
    """
    Public runner interface used by LangGraph nodes.

    Call signature is identical to the previous subprocess-based version:
        runner = Runner()
        result = runner.run(workspace_path)
    """

    def run(self, workspace_path: Path) -> RunnerResult:
        try:
            docker_runner = _get_docker_runner()
            return docker_runner.run(workspace_path)
        except RuntimeError as exc:
            # DockerRunner raises RuntimeError when the daemon is unreachable.
            logger.error("DockerRunner unavailable: %s", exc)
            return RunnerResult(
                passed=False,
                stdout="",
                stderr=str(exc),
                exit_code=-1,
            )
        except Exception as exc:
            logger.exception("Unexpected error in Runner.run()")
            return RunnerResult(
                passed=False,
                stdout="",
                stderr=str(exc),
                exit_code=-1,
            )