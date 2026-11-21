"""Re-run framing analysis after a clip was trimmed."""

from app import storage
from app.db import session_scope
from app.models import Clip
from app.pipeline.reframe import analyze_clip, write_thumbnail


def reframe_clip(clip_id: str) -> None:
    with session_scope() as db:
        clip = db.get(Clip, clip_id)
        if clip is None:
            return
        project_id, start, end = clip.project_id, clip.start, clip.end
        width, height = clip.project.width, clip.project.height

    source = storage.source_video(project_id)
    folder = storage.clip_dir(project_id, clip_id)
    thumbnail = folder / "thumb.jpg"
    track = analyze_clip(source, start, end, width, height, folder)
    write_thumbnail(source, track, start + min(1.0, (end - start) / 3), width, height, thumbnail)

    with session_scope() as db:
        clip = db.get(Clip, clip_id)
        # Skip if the clip was trimmed again meanwhile: a newer job will handle it.
        if clip is not None and (clip.start, clip.end) == (start, end):
            clip.framing = {**clip.framing, "track": track}
            clip.thumbnail = storage.relative(thumbnail)
