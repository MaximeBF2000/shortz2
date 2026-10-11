"""Download caption fonts and the face detection model.

Run once (the Docker image does it at build time):
    python -m scripts.download_assets
"""

import urllib.request
from pathlib import Path

from fontTools.ttLib import TTFont

from app.captions.fonts import CAPTION_FONTS, CaptionFont
from app.config import get_settings
from app.reframe.faces import MODEL_FILE, MODEL_URL

FONT_URL = "https://cdn.jsdelivr.net/fontsource/fonts/{id}@latest/latin-{weight}-normal.ttf"


def download(url: str, target: Path) -> None:
    if target.exists():
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    print(f"Downloading {target.name}")
    request = urllib.request.Request(url, headers={"User-Agent": "shortz"})
    with urllib.request.urlopen(request) as response:
        target.write_bytes(response.read())


def rename_font(path: Path, font: CaptionFont) -> None:
    """Give the file a plain family name ("Montserrat", not "Montserrat Thin Black")
    so libass finds it by the name we write in the subtitle file."""
    ttf = TTFont(path)
    names = ttf["name"]
    names.removeNames(nameID=16)
    names.removeNames(nameID=17)
    for name_id, value in [
        (1, font.family),
        (2, "Regular"),
        (4, font.family),
        (6, font.family.replace(" ", "")),
    ]:
        names.setName(value, name_id, 3, 1, 0x409)
        names.setName(value, name_id, 1, 0, 0)
    ttf.save(path)


def main() -> None:
    settings = get_settings()
    for font in CAPTION_FONTS:
        url = FONT_URL.format(id=font.fontsource_id, weight=font.weight)
        path = settings.fonts_dir / font.file_name
        if not path.exists():
            download(url, path)
            rename_font(path, font)
    download(MODEL_URL, settings.models_dir / MODEL_FILE)


if __name__ == "__main__":
    main()
