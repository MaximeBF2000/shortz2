"""A long-form video the user wants to turn into shorts."""

from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models._base import IdMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.clip import Clip


class ProjectStatus:
    QUEUED = "queued"
    DOWNLOADING = "downloading"
    TRANSCRIBING = "transcribing"
    FINDING_CLIPS = "finding_clips"
    FRAMING = "framing"
    READY = "ready"
    FAILED = "failed"


class Project(IdMixin, TimestampMixin, Base):
    __tablename__ = "projects"

    title: Mapped[str] = mapped_column(String(300), default="Untitled video")
    source_type: Mapped[str] = mapped_column(String(20))  # "youtube" | "upload"
    source_url: Mapped[str | None] = mapped_column(Text)

    status: Mapped[str] = mapped_column(String(30), default=ProjectStatus.QUEUED)
    progress: Mapped[float] = mapped_column(Float, default=0.0)  # 0..1 within the current status
    error: Mapped[str | None] = mapped_column(Text)

    # Filled in once the video is ingested.
    duration: Mapped[float | None] = mapped_column(Float)
    width: Mapped[int | None]
    height: Mapped[int | None]
    fps: Mapped[float | None] = mapped_column(Float)
    language: Mapped[str | None] = mapped_column(String(10))

    # What the user asked for: clip length, number of clips, focus prompt, brand kit...
    settings: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    # {"language": "en", "words": [{"text", "start", "end"}], "segments": [{"start", "end", "text"}]}
    transcript: Mapped[dict[str, Any] | None] = mapped_column(JSON, deferred=True)

    clips: Mapped[list["Clip"]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
        order_by="Clip.rank",
    )
