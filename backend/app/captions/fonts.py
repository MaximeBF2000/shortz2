"""Fonts available for captions.

The same .ttf files are used by libass when rendering and served to the browser
for the live preview, so what you see in the editor is what you export.
Files are downloaded by scripts/download_assets.py.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class CaptionFont:
    family: str
    weight: int

    @property
    def file_name(self) -> str:
        return f"{self.family.replace(' ', '')}-{self.weight}.ttf"

    @property
    def fontsource_id(self) -> str:
        return self.family.lower().replace(" ", "-")


CAPTION_FONTS = [
    CaptionFont("Montserrat", 900),
    CaptionFont("Anton", 400),
    CaptionFont("Bebas Neue", 400),
    CaptionFont("Poppins", 800),
    CaptionFont("Archivo Black", 400),
    CaptionFont("Oswald", 700),
    CaptionFont("Inter", 800),
    CaptionFont("Bangers", 400),
    CaptionFont("Permanent Marker", 400),
    CaptionFont("Lilita One", 400),
    CaptionFont("DM Serif Display", 400),
    CaptionFont("Space Grotesk", 700),
]

FONTS_BY_FAMILY = {font.family: font for font in CAPTION_FONTS}
DEFAULT_FONT = CAPTION_FONTS[0]


def get_font(family: str) -> CaptionFont:
    return FONTS_BY_FAMILY.get(family, DEFAULT_FONT)
