"""Export a clip to a finished mp4."""

import logging
import re
import shutil

from app import storage
from app.captions.pages import Word
from app.captions.style import parse_style
from app.db import session_scope
from app.models import BrandKit, Clip
from app.models.clip import RenderStatus
from app.render.video import RenderJob, render_clip as run_render
from app.worker.progress import clip_render_progress

log = logging.getLogger(__name__)


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:60] or "clip"


def render_clip(clip_id: str) -> None:
    with session_scope() as db:
        clip = db.get(Clip, clip_id)
        if clip is None:
            return
        project = clip.project
        style = parse_style(clip.style)
        kit = db.get(BrandKit, style.brand_kit_id) if style.brand_kit_id else None
        folder = storage.clip_dir(project.id, clip.id)
        job = RenderJob(
            source=storage.source_video(project.id),
            src_width=project.width,
            src_height=project.height,
            fps=project.fps or 30,
            start=clip.start,
            end=clip.end,
            framing=clip.framing,
            style=style,
            words=[
                Word(w["text"], w["start"] - clip.start, w["end"] - clip.start, w.get("emphasis", False))
                for w in clip.words
                if not w.get("hidden")
            ],
            hook=clip.hook,
            logo=storage.absolute(kit.logo) if kit and kit.logo else None,
            work_dir=folder / "render",
            output=folder / f"{slugify(clip.title)}.mp4",
        )
        previous_output = clip.output
        clip.render_status, clip.render_progress, clip.render_error = RenderStatus.RENDERING, 0.0, None

    try:
        run_render(job, clip_render_progress(clip_id))
    except Exception as error:
        log.exception("Render failed for clip %s", clip_id)
        with session_scope() as db:
            clip = db.get(Clip, clip_id)
            if clip is not None:
                clip.render_status, clip.render_error = RenderStatus.FAILED, str(error)
        raise
    finally:
        shutil.rmtree(job.work_dir, ignore_errors=True)

    with session_scope() as db:
        clip = db.get(Clip, clip_id)
        if clip is not None:
            clip.render_status, clip.render_progress = RenderStatus.DONE, 1.0
            clip.output = storage.relative(job.output)
    if previous_output and storage.absolute(previous_output) != job.output:
        storage.absolute(previous_output).unlink(missing_ok=True)
