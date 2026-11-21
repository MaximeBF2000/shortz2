import shutil

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app import storage
from app.api.deps import get_or_404
from app.api.serializers import clip_out
from app.db import get_db
from app.models import Clip
from app.models.clip import RenderStatus
from app.schemas.clip import ClipOut, ClipUpdate
from app.services.clip_edits import retime_words
from app.worker.queue import enqueue

router = APIRouter(prefix="/api/clips", tags=["clips"])

MIN_DURATION, MAX_DURATION = 3.0, 180.0


@router.get("/{clip_id}", response_model=ClipOut)
def get_clip(clip_id: str, db: Session = Depends(get_db)):
    return clip_out(get_or_404(db, Clip, clip_id))


@router.patch("/{clip_id}", response_model=ClipOut)
def update_clip(clip_id: str, body: ClipUpdate, db: Session = Depends(get_db)):
    clip = get_or_404(db, Clip, clip_id)
    changes = body.model_dump(exclude_unset=True)

    if "title" in changes:
        clip.title = body.title or "Untitled clip"
    if body.words is not None:
        clip.words = [w.model_dump() for w in body.words]
    if body.style is not None:
        clip.style = body.style.model_dump()
    if body.framing_mode is not None or body.manual_x is not None:
        framing = dict(clip.framing)
        if body.framing_mode is not None:
            framing["mode"] = body.framing_mode
        if body.manual_x is not None:
            framing["manual_x"] = body.manual_x
        clip.framing = framing

    start = body.start if body.start is not None else clip.start
    end = body.end if body.end is not None else clip.end
    if (start, end) != (clip.start, clip.end):
        trim(clip, start, end, db)

    if changes and clip.render_status == RenderStatus.DONE:
        clip.render_status = RenderStatus.IDLE  # the export is now out of date
    db.commit()
    return clip_out(clip)


def trim(clip: Clip, start: float, end: float, db: Session) -> None:
    duration = clip.project.duration or end
    start, end = max(0.0, start), min(duration, end)
    if not MIN_DURATION <= end - start <= MAX_DURATION:
        raise HTTPException(422, f"Clips must be between {MIN_DURATION:.0f} and {MAX_DURATION:.0f} seconds long.")
    transcript_words = (clip.project.transcript or {}).get("words", [])
    clip.words = retime_words(transcript_words, clip.words, start, end)
    clip.start, clip.end = start, end
    enqueue(db, "reframe_clip", clip_id=clip.id)


@router.post("/{clip_id}/render", response_model=ClipOut)
def render_clip(clip_id: str, db: Session = Depends(get_db)):
    clip = get_or_404(db, Clip, clip_id)
    if clip.render_status in (RenderStatus.QUEUED, RenderStatus.RENDERING):
        return clip_out(clip)
    clip.render_status, clip.render_progress, clip.render_error = RenderStatus.QUEUED, 0.0, None
    enqueue(db, "render_clip", clip_id=clip.id)
    db.commit()
    return clip_out(clip)


@router.get("/{clip_id}/download")
def download_clip(clip_id: str, db: Session = Depends(get_db)):
    clip = get_or_404(db, Clip, clip_id)
    if not clip.output or not storage.absolute(clip.output).exists():
        raise HTTPException(404, "This clip hasn't been exported yet.")
    path = storage.absolute(clip.output)
    return FileResponse(path, media_type="video/mp4", filename=path.name)


@router.delete("/{clip_id}", status_code=204)
def delete_clip(clip_id: str, db: Session = Depends(get_db)):
    clip = get_or_404(db, Clip, clip_id)
    folder = storage.clip_dir(clip.project_id, clip.id)
    db.delete(clip)
    db.commit()
    shutil.rmtree(folder, ignore_errors=True)
