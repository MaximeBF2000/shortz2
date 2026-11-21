"""Keep a clip's framing (camera paths + thumbnail) up to date."""

from app import storage
from app.captions.style import parse_style
from app.db import session_scope
from app.models import Clip
from app.pipeline.reframe import analyze_clip, write_thumbnail


def update_framing(clip_id: str, project_id: str, start: float, end: float, width: int, height: int) -> None:
    """Analyze where the crop goes, store both camera paths and refresh the thumbnail."""
    source = storage.source_video(project_id)
    folder = storage.clip_dir(project_id, clip_id)
    thumbnail = folder / "thumb.jpg"
    tracks = analyze_clip(source, start, end, width, height, folder)
    with session_scope() as db:
        clip = db.get(Clip, clip_id)
        if clip is None or (clip.start, clip.end) != (start, end):
            return  # deleted, or trimmed again meanwhile: a newer job will handle it
        framing = {**clip.framing, **tracks}
        fill = parse_style(clip.style).fill
    write_thumbnail(source, framing, start + min(1.0, (end - start) / 3), width, height, fill, thumbnail)
    with session_scope() as db:
        clip = db.get(Clip, clip_id)
        if clip is not None and (clip.start, clip.end) == (start, end):
            clip.framing = framing
            clip.thumbnail = storage.relative(thumbnail) if thumbnail.exists() else None
