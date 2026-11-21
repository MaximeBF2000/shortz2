"""Re-run framing analysis after a clip was trimmed."""

from app.db import session_scope
from app.models import Clip
from app.services.framing import update_framing


def reframe_clip(clip_id: str) -> None:
    with session_scope() as db:
        clip = db.get(Clip, clip_id)
        if clip is None:
            return
        args = (clip.id, clip.project_id, clip.start, clip.end, clip.project.width, clip.project.height)
    update_framing(*args)
