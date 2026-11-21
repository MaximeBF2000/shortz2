from typing import Literal

from pydantic import BaseModel, Field

from app.captions.style import ClipStyle


class CaptionWord(BaseModel):
    text: str
    start: float
    end: float
    emphasis: bool = False
    hidden: bool = False  # left out of the captions (e.g. "um")


class TrackPoint(BaseModel):
    t: float
    x: float
    cut: bool = False


class Framing(BaseModel):
    mode: Literal["auto", "fit", "manual"] = "auto"
    manual_x: float = Field(0.5, ge=0, le=1)
    track: list[TrackPoint] = []


class ClipOut(BaseModel):
    id: str
    project_id: str
    rank: int
    title: str
    reason: str
    score: int
    start: float
    end: float
    words: list[CaptionWord]
    framing: Framing
    style: ClipStyle
    thumbnail_url: str | None
    render_status: str
    render_progress: float
    render_error: str | None
    output_url: str | None


class ClipUpdate(BaseModel):
    """Every field is optional: send only what changed."""

    title: str | None = Field(None, max_length=300)
    start: float | None = None
    end: float | None = None
    words: list[CaptionWord] | None = None
    framing_mode: Literal["auto", "fit", "manual"] | None = None
    manual_x: float | None = Field(None, ge=0, le=1)
    style: ClipStyle | None = None
