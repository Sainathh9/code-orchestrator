#!/usr/bin/env python
"""
RQ worker process.

Usage (run from the `backend/` directory):

    python worker.py

The worker picks jobs off the "code_generation" queue and calls
app.queue.tasks.run_orchestration() for each one.

Environment:
    REDIS_URL  — defaults to redis://localhost:6379/0 (set in .env or env var)

For production, run multiple workers in parallel:
    python worker.py &
    python worker.py &
    python worker.py &

Or use a process manager (Supervisor, systemd, Docker Compose) to keep them alive.
"""

import sys
import os

# backend/ dir — resolves `app.*` imports (e.g. app.orchestrator.orchestrator)
_backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _backend_dir)


import logging
from rq import Worker
from app.queue.connection import redis_conn, task_queue

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("worker")

if __name__ == "__main__":
    logger.info("Starting RQ worker — listening on queue: %s", task_queue.name)

    worker = Worker(
        queues=[task_queue],
        connection=redis_conn,
    )
    worker.work(with_scheduler=False)
