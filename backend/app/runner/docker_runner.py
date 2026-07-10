"""
DockerRunner — executes pytest inside a disposable Docker container.

Contract (identical to the old subprocess-based Runner):
  runner.run(workspace_path) -> RunnerResult
  RunnerResult has: .passed, .stdout, .stderr, .exit_code

Design:
  - The sandbox image is built once at module import time (if not already
    present). Every subsequent call reuses the same image tag, so there is
    zero rebuild cost per execution.
  - The workspace directory is bind-mounted read-write into the container
    at /sandbox/workspace. No file copying — fast and avoids disk churn.
  - Network is disabled (network_mode="none") so generated code cannot
    make outbound requests.
  - CPU and memory are capped to prevent runaway resource usage.
  - The container is always removed after execution (auto_remove=True)
    even if it times out or crashes.
  - Timeouts are enforced at two levels:
      1. docker SDK container.wait(timeout=) — waits for natural exit.
      2. Explicit container.stop() + container.remove() on TimeoutError.
"""

from __future__ import annotations

import logging
from pathlib import Path

import docker
import docker.errors

logger = logging.getLogger(__name__)

# ── Constants ─────────────────────────────────────────────────────────────────

# Tag used for the sandbox image. Built once, reused forever.
_SANDBOX_IMAGE_TAG = "code-orchestrator-sandbox:latest"

# Path to the Dockerfile that builds the sandbox image.
# backend/app/runner/docker_runner.py
#   [0] = backend/app/runner/
#   [1] = backend/app/
#   [2] = backend/
#   [3] = <project-root>/          ← code-orchestrator/
#   sandbox/ lives at project-root/sandbox/
_SANDBOX_DOCKERFILE_DIR = (
    Path(__file__).resolve().parents[3] / "sandbox"
)

# Path inside the container where the workspace is mounted.
_CONTAINER_WORKSPACE = "/sandbox/workspace"

# pytest command run inside the container.
_PYTEST_CMD = ["pytest", "test_solution.py", "-v", "--tb=short", "--no-header"]

# Resource limits applied to every container.
_MEM_LIMIT = "256m"       # hard memory ceiling
_CPU_QUOTA = 50_000       # 50 000 µs out of 100 000 → 50% of one CPU core
_CPU_PERIOD = 100_000

# Seconds to wait for the container to exit naturally before killing it.
_TIMEOUT_SECONDS = 30


# ── Singleton Docker client ───────────────────────────────────────────────────

def _get_client() -> docker.DockerClient:
    """Return a Docker client, raising a clear error if the daemon is down."""
    try:
        client = docker.from_env()
        client.ping()
        return client
    except Exception as exc:
        raise RuntimeError(
            "Docker daemon is not reachable. "
            "Make sure Docker Desktop (or dockerd) is running."
        ) from exc


def _ensure_sandbox_image(client: docker.DockerClient) -> None:
    """
    Build the sandbox image if it does not already exist locally.

    This runs at most once per process lifetime because the image tag
    persists in the local Docker image store between calls.
    """
    try:
        client.images.get(_SANDBOX_IMAGE_TAG)
        logger.debug("Sandbox image '%s' already exists — skipping build.", _SANDBOX_IMAGE_TAG)
    except docker.errors.ImageNotFound:
        logger.info(
            "Sandbox image '%s' not found — building from %s …",
            _SANDBOX_IMAGE_TAG,
            _SANDBOX_DOCKERFILE_DIR,
        )
        client.images.build(
            path=str(_SANDBOX_DOCKERFILE_DIR),
            tag=_SANDBOX_IMAGE_TAG,
            rm=True,          # remove intermediate layers
            forcerm=True,     # always remove even on failure
        )
        logger.info("Sandbox image built successfully.")


# ── RunnerResult ──────────────────────────────────────────────────────────────

class RunnerResult:
    """Structured result returned by DockerRunner.run()."""

    __slots__ = ("passed", "stdout", "stderr", "exit_code")

    def __init__(self, *, passed: bool, stdout: str, stderr: str, exit_code: int):
        self.passed = passed
        self.stdout = stdout
        self.stderr = stderr
        self.exit_code = exit_code

    def __repr__(self) -> str:
        return (
            f"RunnerResult(passed={self.passed}, exit_code={self.exit_code})"
        )


# ── DockerRunner ──────────────────────────────────────────────────────────────

class DockerRunner:
    """
    Runs pytest inside a disposable Docker container.

    Usage:
        runner = DockerRunner()
        result = runner.run(workspace_path)   # identical call-site to old Runner
    """

    def __init__(self):
        self._client = _get_client()
        _ensure_sandbox_image(self._client)

    def run(self, workspace_path: Path) -> RunnerResult:
        """
        Execute pytest against the files in *workspace_path* inside Docker.

        Args:
            workspace_path: Absolute path to the workspace directory on the host.
                            Must contain solution.py and test_solution.py.

        Returns:
            RunnerResult with .passed, .stdout, .stderr, .exit_code
        """
        workspace_path = Path(workspace_path).resolve()
        container = None

        # Auto-detect if we are running inside a container and what volume/bind mount is used for /app/workspace.
        # This resolves the Docker-in-Docker named volume mount issue on platforms like macOS/Docker Desktop.
        volume_source = None
        volume_mode = "bind"
        
        try:
            import socket
            me = self._client.containers.get(socket.gethostname())
            for mount in me.attrs.get('Mounts', []):
                if mount.get('Destination') == '/app/workspace':
                    if mount.get('Type') == 'volume':
                        volume_source = mount.get('Name')
                        volume_mode = "volume"
                    elif mount.get('Type') == 'bind':
                        volume_source = mount.get('Source')
                        volume_mode = "bind"
                    break
        except Exception as exc:
            logger.warning("Could not auto-detect worker mounts: %s", exc)

        # Fallback to local bind mount if detection failed
        if not volume_source:
            volume_source = str(workspace_path)
            volume_mode = "bind"

        # Construct the volume configuration and working directory
        if volume_mode == "volume":
            # Mount the entire named volume to /app/workspace and run in the subdirectory
            volumes_config = {
                volume_source: {
                    "bind": "/app/workspace",
                    "mode": "ro",
                }
            }
            working_dir = str(workspace_path)
        else:
            # Bind mount: calculate the host path of the specific workspace subdirectory
            try:
                rel_path = workspace_path.relative_to('/app/workspace')
                host_path = Path(volume_source) / rel_path
            except ValueError:
                host_path = Path(volume_source)

            volumes_config = {
                str(host_path): {
                    "bind": _CONTAINER_WORKSPACE,
                    "mode": "ro",
                }
            }
            working_dir = _CONTAINER_WORKSPACE

        try:
            container = self._client.containers.run(
                image=_SANDBOX_IMAGE_TAG,
                command=_PYTEST_CMD,
                # ── Mount ────────────────────────────────────────────────────
                volumes=volumes_config,
                working_dir=working_dir,
                # ── Isolation ────────────────────────────────────────────────
                network_mode="none",    # no outbound network access
                # ── Resource limits ──────────────────────────────────────────
                mem_limit=_MEM_LIMIT,
                cpu_quota=_CPU_QUOTA,
                cpu_period=_CPU_PERIOD,
                # ── Lifecycle ────────────────────────────────────────────────
                detach=True,            # run in background so we can enforce timeout
                auto_remove=False,      # we remove manually after reading logs
            )

            # Wait for the container to finish, with a hard timeout.
            try:
                exit_info = container.wait(timeout=_TIMEOUT_SECONDS)
                exit_code: int = exit_info.get("StatusCode", -1)
            except Exception:
                # TimeoutError or ConnectionError — kill and report timeout.
                logger.warning(
                    "Container timed out after %ds — stopping forcefully.",
                    _TIMEOUT_SECONDS,
                )
                try:
                    container.stop(timeout=2)
                except Exception:
                    pass
                return RunnerResult(
                    passed=False,
                    stdout="",
                    stderr=f"TEST RUN TIMEOUT after {_TIMEOUT_SECONDS}s",
                    exit_code=-1,
                )

            # Retrieve captured output.
            raw_logs = container.logs(stdout=True, stderr=True)
            logs_text = raw_logs.decode("utf-8", errors="replace") if raw_logs else ""

            # pytest writes everything to stdout; stderr carries Docker/system msgs.
            stdout_logs = container.logs(stdout=True, stderr=False)
            stderr_logs = container.logs(stdout=False, stderr=True)
            stdout = stdout_logs.decode("utf-8", errors="replace") if stdout_logs else ""
            stderr = stderr_logs.decode("utf-8", errors="replace") if stderr_logs else ""

            logger.info(
                "Container exited with code %d — passed=%s",
                exit_code,
                exit_code == 0,
            )

            return RunnerResult(
                passed=exit_code == 0,
                stdout=stdout or logs_text,
                stderr=stderr,
                exit_code=exit_code,
            )

        except docker.errors.ImageNotFound:
            logger.error("Sandbox image '%s' not found.", _SANDBOX_IMAGE_TAG)
            return RunnerResult(
                passed=False,
                stdout="",
                stderr=f"Sandbox image '{_SANDBOX_IMAGE_TAG}' not found. Run: docker build sandbox/",
                exit_code=-1,
            )

        except docker.errors.DockerException as exc:
            logger.exception("Docker error during container run.")
            return RunnerResult(
                passed=False,
                stdout="",
                stderr=f"Docker error: {exc}",
                exit_code=-1,
            )

        except Exception as exc:
            logger.exception("Unexpected error in DockerRunner.")
            return RunnerResult(
                passed=False,
                stdout="",
                stderr=str(exc),
                exit_code=-1,
            )

        finally:
            # Always try to remove the container, even on error or timeout.
            if container is not None:
                try:
                    container.remove(force=True)
                except Exception:
                    pass
