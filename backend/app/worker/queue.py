"""A minimal job queue stored in Postgres.

Workers claim jobs with SELECT ... FOR UPDATE SKIP LOCKED, so several worker
threads or containers can run safely side by side. No Redis needed.
"""

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.db import session_scope
from app.models import Job
from app.models._base import utcnow
from app.models.job import JobStatus


def enqueue(db: Session, kind: str, **payload: str) -> Job:
    job = Job(kind=kind, payload=payload)
    db.add(job)
    return job


def claim_next() -> Job | None:
    with session_scope() as db:
        job = db.execute(
            select(Job)
            .where(Job.status == JobStatus.QUEUED)
            .order_by(Job.created_at)
            .limit(1)
            .with_for_update(skip_locked=True)
        ).scalar_one_or_none()
        if job is not None:
            job.status = JobStatus.RUNNING
            job.started_at = utcnow()
        return job


def finish(job_id: str, error: str | None = None) -> None:
    with session_scope() as db:
        db.execute(
            update(Job)
            .where(Job.id == job_id)
            .values(
                status=JobStatus.FAILED if error else JobStatus.DONE,
                error=error,
                finished_at=utcnow(),
            )
        )


def requeue_interrupted() -> int:
    """Jobs left 'running' by a crashed worker go back in the queue."""
    with session_scope() as db:
        result = db.execute(
            update(Job).where(Job.status == JobStatus.RUNNING).values(status=JobStatus.QUEUED)
        )
        return result.rowcount
