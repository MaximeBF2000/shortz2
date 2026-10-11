import json
import shutil
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app import storage
from app.api.deps import get_or_404
from app.api.serializers import project_detail, project_summary
from app.db import get_db
from app.models import Project
from app.models.clip import RenderStatus
from app.models.project import ProjectStatus
from app.pipeline.youtube import is_youtube_url
from app.schemas.project import ProjectCreate, ProjectDetail, ProjectSettings, ProjectSummary, TranscriptOut
from app.worker.queue import enqueue

router = APIRouter(prefix="/api/projects", tags=["projects"])

VIDEO_EXTENSIONS = {".mp4", ".mov", ".m4v", ".mkv", ".webm", ".avi"}


@router.get("", response_model=list[ProjectSummary])
def list_projects(db: Session = Depends(get_db)):
    projects = db.execute(
        select(Project).options(selectinload(Project.clips)).order_by(Project.created_at.desc())
    ).scalars()
    return [project_summary(p) for p in projects]


@router.post("", response_model=ProjectDetail, status_code=201)
def create_from_url(body: ProjectCreate, db: Session = Depends(get_db)):
    url = body.url.strip()
    if not is_youtube_url(url):
        raise HTTPException(422, "Paste a YouTube link, like https://youtube.com/watch?v=...")
    project = Project(source_type="youtube", source_url=url, title="YouTube video", settings=body.settings.model_dump())
    db.add(project)
    db.flush()
    enqueue(db, "process_project", project_id=project.id)
    db.commit()
    return project_detail(project)


@router.post("/upload", response_model=ProjectDetail, status_code=201)
def create_from_upload(
    file: UploadFile = File(...),
    settings: str = Form("{}"),
    db: Session = Depends(get_db),
):
    extension = Path(file.filename or "").suffix.lower()
    if extension not in VIDEO_EXTENSIONS:
        raise HTTPException(422, "Upload a video file (mp4, mov, mkv, webm, m4v or avi).")
    try:
        parsed = ProjectSettings.model_validate(json.loads(settings))
    except (ValueError, ValidationError) as error:
        raise HTTPException(422, "Invalid project settings.") from error

    upload_name = f"upload{extension}"
    project = Project(
        source_type="upload",
        title=Path(file.filename or "Video").stem[:300],
        settings={**parsed.model_dump(), "upload_file": upload_name},
    )
    db.add(project)
    db.flush()
    with open(storage.project_dir(project.id) / upload_name, "wb") as target:
        shutil.copyfileobj(file.file, target, length=4 * 1024 * 1024)
    enqueue(db, "process_project", project_id=project.id)
    db.commit()
    return project_detail(project)


@router.get("/{project_id}", response_model=ProjectDetail)
def get_project(project_id: str, db: Session = Depends(get_db)):
    return project_detail(get_or_404(db, Project, project_id))


@router.get("/{project_id}/transcript", response_model=TranscriptOut)
def get_transcript(project_id: str, db: Session = Depends(get_db)):
    project = get_or_404(db, Project, project_id)
    transcript = project.transcript or {}
    return TranscriptOut(language=transcript.get("language"), words=transcript.get("words", []))


@router.post("/{project_id}/retry", response_model=ProjectDetail)
def retry_project(project_id: str, db: Session = Depends(get_db)):
    project = get_or_404(db, Project, project_id)
    if project.status != ProjectStatus.FAILED:
        raise HTTPException(409, "Only failed projects can be retried.")
    project.status, project.progress, project.error = ProjectStatus.QUEUED, 0.0, None
    enqueue(db, "process_project", project_id=project.id)
    db.commit()
    return project_detail(project)


@router.post("/{project_id}/render-all", response_model=ProjectDetail)
def render_all(project_id: str, db: Session = Depends(get_db)):
    project = get_or_404(db, Project, project_id)
    for clip in project.clips:
        if clip.render_status not in (RenderStatus.QUEUED, RenderStatus.RENDERING, RenderStatus.DONE):
            clip.render_status, clip.render_progress = RenderStatus.QUEUED, 0.0
            enqueue(db, "render_clip", clip_id=clip.id)
    db.commit()
    return project_detail(project)


@router.delete("/{project_id}", status_code=204)
def delete_project(project_id: str, db: Session = Depends(get_db)):
    project = get_or_404(db, Project, project_id)
    db.delete(project)
    db.commit()
    storage.delete_project_files(project_id)
