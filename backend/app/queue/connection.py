"""
Redis connection and RQ queue singleton.

Both the FastAPI app and the RQ worker import from this module so that
the queue name and connection settings are defined in exactly one place.
"""

import redis
from rq import Queue

from app.core.config import settings

# Shared Redis connection — created once at import time.
# RQ is thread-safe; the same connection object can be reused across requests.
redis_conn = redis.from_url(settings.REDIS_URL, decode_responses=False)

# All code-generation jobs go into this named queue.
# The worker must listen on the same queue name.
task_queue = Queue("code_generation", connection=redis_conn)
