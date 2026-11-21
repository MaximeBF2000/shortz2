"""Full pipeline for a new video: download -> transcribe -> find clips -> frame them.

Steps that already completed (e.g. before a crash or a retry) are skipped.
"""

import logging

from sqlalchemy import delete

from app import storage
from app.db import session_scope
from app.models import Clip, Project
from app.models.project import ProjectStatus
from app.pipeline import ingest, youtube
from app.pipeline.highlights import Request, clip_words, find_clips
from app.pipeline.transcribe import transcribe as speech_to_text
from app.reframe.analyze import analyze_clip
from app.services.styles import default_style_for
from app.worker.progress import project_progress, set_project_status

log = logging.getLogger(__name__)


def process_project(project_id: str) -> None:
    try:
        download_and_normalize(project_id)
        transcribe(project_id)
        create_clips(project_id)
        frame_clips(project_id)
        set_project_status(project_id, ProjectStatus.READY, 1.0, error=None)
    except Exception as error:
        log.exception("Processing failed for project %s", project_id)
        set_project_status(project_id, ProjectStatus.FAILED, 0.0, error=str(error) or type(error).__name__)
        raise


def download_and_normalize(project_id: str) -> None:
    source = storage.source_video(project_id)
    with session_scope() as db:
        project = db.get(Project, project_id)
        if source.exists() and project.duration:
            return
        source_type, source_url, upload = project.source_type, project.source_url, project.settings.get("upload_file")

    folder = storage.project_dir(project_id)
    set_project_status(project_id, ProjectStatus.DOWNLOADING)
    report = project_progress(project_id)

    if source_type == "youtube":
        raw, title = youtube.download(source_url, folder, lambda p: report(p * 0.8))
        with session_scope() as db:
            db.get(Project, project_id).title = title[:300]
    else:
        raw = folder / upload

    info = ingest.normalize_video(raw, source, lambda p: report(0.8 + p * 0.2))
    ingest.extract_poster(source, folder / "poster.jpg", at=min(5.0, info.duration / 4))
    with session_scope() as db:
        project = db.get(Project, project_id)
        project.duration, project.width, project.height, project.fps = (
            info.duration, info.width, info.height, info.fps,
        )


def transcribe(project_id: str) -> None:
    with session_scope() as db:
        project = db.get(Project, project_id)
        if project.transcript:
            return
        language = project.settings.get("language")

    set_project_status(project_id, ProjectStatus.TRANSCRIBING)
    folder = storage.project_dir(project_id)
    audio = folder / "audio.wav"
    ingest.extract_audio(storage.source_video(project_id), audio)
    transcript = speech_to_text(audio, language, project_progress(project_id))
    audio.unlink(missing_ok=True)
    if not transcript["words"]:
        raise RuntimeError("No speech was found in this video, so there is nothing to caption.")

    with session_scope() as db:
        project = db.get(Project, project_id)
        project.transcript = transcript
        project.language = transcript["language"] or language


def create_clips(project_id: str) -> None:
    set_project_status(project_id, ProjectStatus.FINDING_CLIPS)
    with session_scope() as db:
        project = db.get(Project, project_id)
        settings, transcript = project.settings, project.transcript
        request = Request(
            segments=transcript["segments"],
            words=transcript["words"],
            duration=project.duration,
            length=settings.get("clip_length", "auto"),
            max_clips=int(settings.get("max_clips", 8)),
            focus=settings.get("focus", ""),
            title=project.title,
        )

    candidates = find_clips(request)
    if not candidates:
        raise RuntimeError("No clip-worthy moments were found. Try a different clip length.")

    with session_scope() as db:
        db.execute(delete(Clip).where(Clip.project_id == project_id))
        style = default_style_for(db, settings.get("brand_kit_id"))
        for rank, candidate in enumerate(candidates):
            db.add(
                Clip(
                    project_id=project_id,
                    rank=rank,
                    title=candidate.title[:300],
                    hook=candidate.hook[:300],
                    reason=candidate.reason,
                    score=candidate.score,
                    start=candidate.start,
                    end=candidate.end,
                    words=clip_words(request.words, candidate.start, candidate.end, candidate.keywords),
                    framing={"mode": "auto", "manual_x": 0.5, "track": []},
                    style=style,
                )
            )


def frame_clips(project_id: str) -> None:
    set_project_status(project_id, ProjectStatus.FRAMING)
    report = project_progress(project_id)
    source = storage.source_video(project_id)
    with session_scope() as db:
        clips = [(c.id, c.start, c.end) for c in db.get(Project, project_id).clips]

    for index, (clip_id, start, end) in enumerate(clips):
        thumbnail = storage.clip_dir(project_id, clip_id) / "thumb.jpg"
        track = analyze_clip(source, start, end, thumbnail)
        with session_scope() as db:
            clip = db.get(Clip, clip_id)
            clip.framing = {**clip.framing, "track": track}
            clip.thumbnail = storage.relative(thumbnail) if thumbnail.exists() else None
        report((index + 1) / len(clips))
