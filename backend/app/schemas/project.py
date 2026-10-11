from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.clip import ClipOut

ClipLength = Literal["auto", "short", "medium", "long"]


class ProjectSettings(BaseModel):
    clip_length: ClipLength = "auto"
    max_clips: int = Field(8, ge=1, le=20)
    language: str | None = None  # None = detect automatically
    focus: str = Field("", max_length=500)
    brand_kit_id: str | None = None


class ProjectCreate(BaseModel):
    url: str
    settings: ProjectSettings = ProjectSettings()


class ProjectSummary(BaseModel):
    id: str
    title: str
    source_type: str
    source_url: str | None
    status: str
    progress: float
    error: str | None
    duration: float | None
    poster_url: str | None
    clip_count: int
    created_at: datetime


class ProjectDetail(ProjectSummary):
    width: int | None
    height: int | None
    fps: float | None
    language: str | None
    settings: dict
    video_url: str | None
    clips: list[ClipOut]


class TranscriptOut(BaseModel):
    language: str | None
    words: list[dict]
