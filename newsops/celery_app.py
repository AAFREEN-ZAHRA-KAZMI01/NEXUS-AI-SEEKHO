import os
from celery import Celery

# ---------------------------------------------------------------------------
# Celery application — NewsOps async pipeline broker
# ---------------------------------------------------------------------------
# REDIS_URL is read from the environment so that the same image works both
# locally (redis://localhost:6379/0) and inside Docker Compose
# (redis://redis:6379/0).
# ---------------------------------------------------------------------------

celery = Celery(
    "newsops",
    broker=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    backend=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    include=["tasks.pipeline_task"],
)

celery.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    result_expires=3600,
)
