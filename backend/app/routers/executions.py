from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from rq.job import Job, NoSuchJobError

from app.db.session import get_db
from app.queue.connection import redis_conn
from app.repositories.execution_read_repository import ExecutionReadRepository
from app.auth.dependencies import get_current_user
from app.db.models.user import User

router = APIRouter(prefix="/executions", tags=["executions"])


# --------------------------
# LIST ALL EXECUTIONS
# --------------------------
@router.get("/")
def list_executions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List all executions belonging to the authenticated user.
    """
    repo = ExecutionReadRepository(db)
    executions = repo.get_all_executions_for_user(current_user.id)

    return [
        {
            "execution_id": str(e.id),
            "requirement": e.requirement,
            "status": e.status,
            "tries_used": e.tries_used,
            "created_at": e.created_at,
        }
        for e in executions
    ]


# --------------------------
# SINGLE EXECUTION + REPLAY
# --------------------------
@router.get("/{execution_id}")
def get_execution(
    execution_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get the details and iteration history of a single execution,
    provided it belongs to the authenticated user.
    """
    repo = ExecutionReadRepository(db)

    # Fetch execution matching both execution_id and current user's ID
    execution = repo.get_execution_for_user(execution_id, current_user.id)
    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Execution not found.",
        )

    iterations = repo.get_iterations(execution_id)

    return {
        "execution_id": str(execution.id),
        "requirement": execution.requirement,
        "status": execution.status,
        "tries_used": execution.tries_used,
        "created_at": execution.created_at,
        "iterations": [
            {
                "iteration": i.iteration_number,
                "code": i.generated_code,
                "test_output": i.test_output,
                "passed": i.passed,
            }
            for i in iterations
        ],
    }


# --------------------------
# JOB STATUS (RQ)
# --------------------------
@router.get("/jobs/{job_id}")
def get_job_status(
    job_id: str,
    current_user: User = Depends(get_current_user),
):
    """
    Poll the status of an enqueued code-generation job.
    Only accessible by the user who initiated the job.
    """
    try:
        job = Job.fetch(job_id, connection=redis_conn)
    except NoSuchJobError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job '{job_id}' not found. It may have expired or never existed.",
        )

    # Security check: verify authenticated user matches job initiator
    if str(job.meta.get("user_id")) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this job resource.",
        )

    status_name = job.get_status()
    status_str = status_name.value if hasattr(status_name, "value") else str(status_name)

    response: dict = {
        "job_id": job_id,
        "status": status_str,
        "stepText": job.meta.get("stepText"),
        "enqueued_at": job.enqueued_at.isoformat() if job.enqueued_at else None,
        "started_at": job.started_at.isoformat() if job.started_at else None,
        "ended_at": job.ended_at.isoformat() if job.ended_at else None,
    }

    if status_name == "finished":
        response["result"] = job.result   # dict from ExecutionResult.model_dump()

    if status_name == "failed":
        response["error"] = job.latest_result().exc_string if job.latest_result() else None

    return response