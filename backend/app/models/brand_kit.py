"""A reusable caption + overlay design."""

from typing import Any

from sqlalchemy import JSON, Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models._base import IdMixin, TimestampMixin


class BrandKit(IdMixin, TimestampMixin, Base):
    __tablename__ = "brand_kits"

    name: Mapped[str] = mapped_column(String(120))
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    style: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    logo: Mapped[str | None] = mapped_column(String(300))  # path relative to data dir
