from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app import storage
from app.api.deps import get_or_404
from app.api.serializers import brand_kit_out
from app.db import get_db
from app.models import BrandKit
from app.schemas.brand_kit import BrandKitIn, BrandKitOut, BrandKitUpdate

router = APIRouter(prefix="/api/brand-kits", tags=["brand kits"])

LOGO_TYPES = {"image/png": ".png", "image/jpeg": ".jpg", "image/webp": ".webp"}
MAX_LOGO_BYTES = 5 * 1024 * 1024


@router.get("", response_model=list[BrandKitOut])
def list_brand_kits(db: Session = Depends(get_db)):
    kits = db.execute(select(BrandKit).order_by(BrandKit.created_at)).scalars()
    return [brand_kit_out(k) for k in kits]


@router.post("", response_model=BrandKitOut, status_code=201)
def create_brand_kit(body: BrandKitIn, db: Session = Depends(get_db)):
    kit = BrandKit(name=body.name, style=body.style.model_dump())
    db.add(kit)
    db.flush()
    if body.is_default or db.query(BrandKit).count() == 1:
        make_default(db, kit)
    db.commit()
    return brand_kit_out(kit)


@router.patch("/{kit_id}", response_model=BrandKitOut)
def update_brand_kit(kit_id: str, body: BrandKitUpdate, db: Session = Depends(get_db)):
    kit = get_or_404(db, BrandKit, kit_id)
    if body.name is not None:
        kit.name = body.name
    if body.style is not None:
        kit.style = body.style.model_dump()
    if body.is_default:
        make_default(db, kit)
    db.commit()
    return brand_kit_out(kit)


@router.delete("/{kit_id}", status_code=204)
def delete_brand_kit(kit_id: str, db: Session = Depends(get_db)):
    kit = get_or_404(db, BrandKit, kit_id)
    if kit.logo:
        storage.absolute(kit.logo).unlink(missing_ok=True)
    db.delete(kit)
    db.commit()


@router.post("/{kit_id}/logo", response_model=BrandKitOut)
def upload_logo(kit_id: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    kit = get_or_404(db, BrandKit, kit_id)
    extension = LOGO_TYPES.get(file.content_type or "")
    if extension is None:
        raise HTTPException(422, "Upload a PNG, JPG or WebP image.")
    data = file.file.read(MAX_LOGO_BYTES + 1)
    if len(data) > MAX_LOGO_BYTES:
        raise HTTPException(422, "Logos must be 5 MB or smaller.")
    if kit.logo:
        storage.absolute(kit.logo).unlink(missing_ok=True)
    path = storage.brand_kit_dir(kit.id) / f"logo-{storage.new_suffix()}{extension}"
    path.write_bytes(data)
    kit.logo = storage.relative(path)
    db.commit()
    return brand_kit_out(kit)


@router.delete("/{kit_id}/logo", response_model=BrandKitOut)
def delete_logo(kit_id: str, db: Session = Depends(get_db)):
    kit = get_or_404(db, BrandKit, kit_id)
    if kit.logo:
        storage.absolute(kit.logo).unlink(missing_ok=True)
        kit.logo = None
        db.commit()
    return brand_kit_out(kit)


def make_default(db: Session, kit: BrandKit) -> None:
    db.execute(update(BrandKit).where(BrandKit.id != kit.id).values(is_default=False))
    kit.is_default = True
