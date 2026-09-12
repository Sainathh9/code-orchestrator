"""
RQ task functions executed by the background worker.

Rules:
- Every function here must be importable by the worker process.
- Heavy objects (Orchestrator, DB sessions) are instantiated *inside* the
  function — never at module level — so each job gets an isolated context.
- Return values are serialised to Redis by RQ (must be JSON-serialisable).
"""

import logging

from app.orchestrator.orchestrator import Orchestrator

logger = logging.getLogger(__name__)


def run_orchestration(requirement: str, user_id: str = None, model: str = None) -> dict:
    """
    Entry point called by the RQ worker for every code-generation job.

    Instantiates a fresh Orchestrator (and therefore fresh agents, DB session,
    workspace, and logger) so jobs are fully isolated from one another.

    Args:
        requirement: Natural-language description of the code to generate.
        user_id: The ID of the authenticated user who requested this execution.
        model: Optional LLM model name selected by the user.

    Returns:
        A dict representation of ExecutionResult, stored by RQ in Redis so
        callers can retrieve it via ``Job.result``.

    Raises:
        Any exception raised by Orchestrator.run() propagates to RQ, which
        marks the job as ``failed`` and stores the traceback.
    """
    logger.info(f"[worker] Starting orchestration — requirement: {requirement!r}, user_id: {user_id}, model: {model}")

    orchestrator = Orchestrator()
    result = orchestrator.run(requirement, user_id, model=model)

    logger.info(
        f"[worker] Finished — passed={result.passed}, tries={result.tries_used}"
    )

    # ExecutionResult is a Pydantic model; .model_dump() gives a plain dict
    # that RQ can serialise to Redis without issues.
    return result.model_dump()
