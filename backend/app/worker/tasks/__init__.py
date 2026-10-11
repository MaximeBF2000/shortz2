"""Background tasks, keyed by Job.kind."""

from collections.abc import Callable

from app.worker.tasks.process_project import process_project
from app.worker.tasks.reframe_clip import reframe_clip
from app.worker.tasks.render_clip import render_clip

TASKS: dict[str, Callable[..., None]] = {
    "process_project": process_project,
    "render_clip": render_clip,
    "reframe_clip": reframe_clip,
}
