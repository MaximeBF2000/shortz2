from datetime import datetime

from pydantic import BaseModel, Field

from app.captions.style import ClipStyle


class BrandKitIn(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    style: ClipStyle = ClipStyle()
    is_default: bool = False


class BrandKitUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=120)
    style: ClipStyle | None = None
    is_default: bool | None = None


class BrandKitOut(BaseModel):
    id: str
    name: str
    is_default: bool
    style: ClipStyle
    logo_url: str | None
    created_at: datetime
