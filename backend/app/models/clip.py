"""A short vertical clip cut out of a project."""

from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models._base import IdMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.project import Project


class RenderStatus:
    IDLE = "idle"
    QUEUED = "queued"
    RENDERING = "rendering"
    DONE = "done"
    FAILED = "failed"


class Clip(IdMixin, TimestampMixin, Base):
    __tablename__ = "clips"

    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    rank: Mapped[int] = mapped_column(Integer, default=0)

    title: Mapped[str] = mapped_column(String(300))
    reason: Mapped[str] = mapped_column(Text, default="")  # why this moment works
    score: Mapped[int] = mapped_column(Integer, default=50)  # 0-100 virality estimate

    # Absolute times in the source video, in seconds.
    start: Mapped[float] = mapped_column(Float)
    end: Mapped[float] = mapped_column(Float)

    # Caption words: [{"text", "start", "end", "emphasis"}], absolute times.
    words: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list)
    # Framing: {"mode": "auto" | "fit" | "manual", "manual_x": 0.5, "track": [{"t", "x", "cut"}]}
    framing: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    # Caption + overlay design, see app/captions/style.py
    style: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)

    thumbnail: Mapped[str | None] = mapped_column(String(300))  # path relative to data dir

    render_status: Mapped[str] = mapped_column(String(20), default=RenderStatus.IDLE)
    render_progress: Mapped[float] = mapped_column(Float, default=0.0)
    render_error: Mapped[str | None] = mapped_column(Text)
    output: Mapped[str | None] = mapped_column(String(300))  # path relative to data dir

    project: Mapped["Project"] = relationship(back_populates="clips")

    @property
    def duration(self) -> float:
        return self.end - self.start
