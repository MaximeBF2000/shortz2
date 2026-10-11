"""The caption + overlay design of a clip (also what a brand kit stores).

All sizes are in pixels of the 1080x1920 output frame.
"""

from typing import Literal

from pydantic import BaseModel, Field

Animation = Literal["highlight", "pop", "karaoke", "single", "none"]
LogoCorner = Literal["top-left", "top-right", "bottom-left", "bottom-right"]


class CaptionStyle(BaseModel):
    enabled: bool = True
    font: str = "Montserrat"
    font_size: int = Field(78, ge=30, le=180)
    uppercase: bool = True
    text_color: str = "#FFFFFF"
    highlight_color: str = "#FFD83D"  # the word being spoken
    emphasis_color: str = "#4ADE80"  # keywords picked by the AI
    stroke_color: str = "#000000"
    stroke_width: int = Field(7, ge=0, le=20)
    shadow: bool = True
    position: float = Field(0.7, ge=0.1, le=0.95)  # vertical center, fraction of height
    max_words: int = Field(3, ge=1, le=8)  # words shown at once
    animation: Animation = "pop"


class HookStyle(BaseModel):
    enabled: bool = True
    duration: float = Field(3.0, ge=0.5, le=10)
    font: str = "Montserrat"
    font_size: int = Field(58, ge=30, le=120)
    text_color: str = "#111111"
    background_color: str = "#FFFFFF"
    position: float = Field(0.2, ge=0.05, le=0.9)


class LogoStyle(BaseModel):
    enabled: bool = False
    corner: LogoCorner = "top-right"
    size: int = Field(160, ge=60, le=400)  # width in px
    opacity: float = Field(0.9, ge=0.1, le=1)


class ClipStyle(BaseModel):
    captions: CaptionStyle = CaptionStyle()
    hook: HookStyle = HookStyle()
    logo: LogoStyle = LogoStyle()
    # Brand kit whose logo should be overlaid (the logo file lives on the kit).
    brand_kit_id: str | None = None


def parse_style(raw: dict | None) -> ClipStyle:
    return ClipStyle.model_validate(raw or {})
