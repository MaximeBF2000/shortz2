"""Throttled progress reporting, so long tasks don't hammer the database."""

import time
from collections.abc import Callable

from app.db import session_scope
from app.models import Clip, Project


class Reporter:
    def __init__(self, write: Callable[[float], None], min_interval: float = 1.0) -> None:
        self.write = write
        self.min_interval = min_interval
        self.last_time = 0.0
        self.last_value = -1.0

    def __call__(self, value: float) -> None:
        now = time.monotonic()
        if value >= 1 or (now - self.last_time >= self.min_interval and value - self.last_value >= 0.005):
            self.write(value)
            self.last_time, self.last_value = now, value


def set_project_status(project_id: str, status: str, progress: float = 0.0, **fields) -> None:
    with session_scope() as db:
        project = db.get(Project, project_id)
        if project is not None:
            project.status, project.progress = status, progress
            for key, value in fields.items():
                setattr(project, key, value)


def project_progress(project_id: str) -> Reporter:
    def write(value: float) -> None:
        with session_scope() as db:
            project = db.get(Project, project_id)
            if project is not None:
                project.progress = value

    return Reporter(write)


def clip_render_progress(clip_id: str) -> Reporter:
    def write(value: float) -> None:
        with session_scope() as db:
            clip = db.get(Clip, clip_id)
            if clip is not None:
                clip.render_progress = value

    return Reporter(write)
