"""Static options the editor needs: caption fonts and presets."""

from fastapi import APIRouter
from pydantic import BaseModel

from app.captions.fonts import CAPTION_FONTS
from app.captions.metrics import line_ratio
from app.captions.presets import PRESETS
from app.captions.style import CaptionStyle
from app.config import get_settings

router = APIRouter(prefix="/api", tags=["catalog"])


class FontOut(BaseModel):
    family: str
    weight: int
    url: str
    line_ratio: float


class PresetOut(BaseModel):
    name: str
    captions: CaptionStyle


@router.get("/fonts", response_model=list[FontOut])
def list_fonts():
    base = get_settings().public_api_url
    return [
        FontOut(family=f.family, weight=f.weight, url=f"{base}/fonts/{f.file_name}", line_ratio=line_ratio(f.family))
        for f in CAPTION_FONTS
    ]


@router.get("/presets", response_model=list[PresetOut])
def list_presets():
    return [PresetOut(name=name, captions=style) for name, style in PRESETS.items()]


@router.get("/health")
def health():
    return {"ok": True, "ai_clip_finder": bool(get_settings().anthropic_api_key)}
