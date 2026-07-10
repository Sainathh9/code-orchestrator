from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.queue.connection import task_queue
from app.queue.tasks import run_orchestration
from app.auth.dependencies import get_current_user
from app.db.models.user import User

router = APIRouter()


class GenerateRequest(BaseModel):
    requirement: str


@router.post("/generate", status_code=202)
def generate(
    request: GenerateRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Enqueue a code-generation job and return immediately.

    The heavy work (code generation, test execution, debug loop) runs inside
    an RQ worker process. Poll ``GET /executions/jobs/{job_id}`` for status and
    results, or ``GET /executions/{execution_id}`` for the full iteration
    history once the job completes.

    Returns:
        202 Accepted with ``job_id`` and initial ``status``.
    """
    # Enqueue with user_id so it gets passed to the worker and GraphState
    job = task_queue.enqueue(
        run_orchestration,
        request.requirement,
        str(current_user.id),
        job_timeout=600,          # 10-minute ceiling per job
        result_ttl=86_400,        # keep result in Redis for 24 h
        failure_ttl=86_400,       # keep failure info for 24 h
    )

    # Persist the ownership to the job metadata in Redis for fast verification
    job.meta["user_id"] = str(current_user.id)
    job.save_meta()

    return {
        "job_id": job.id,
        "status": "queued",
        "queue": task_queue.name,
    }