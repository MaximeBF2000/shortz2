"""Shared route helpers."""

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.db import Base


def get_or_404[T: Base](db: Session, model: type[T], item_id: str) -> T:
    item = db.get(model, item_id)
    if item is None:
        raise HTTPException(404, f"{model.__name__} not found")
    return item
