"""Which design a new clip starts with."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.captions.style import ClipStyle, parse_style
from app.models import BrandKit


def default_style_for(db: Session, brand_kit_id: str | None) -> dict:
    """The chosen brand kit, else the default brand kit, else the built-in style."""
    kit = db.get(BrandKit, brand_kit_id) if brand_kit_id else None
    if kit is None:
        kit = db.execute(select(BrandKit).where(BrandKit.is_default)).scalars().first()
    if kit is None:
        return ClipStyle().model_dump()
    style = parse_style(kit.style)
    style.brand_kit_id = kit.id
    return style.model_dump()
