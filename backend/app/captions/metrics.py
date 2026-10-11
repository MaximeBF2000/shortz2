"""Font metrics needed to make libass and the browser draw text the same size.

libass sizes text so that (winAscent + winDescent) equals the font size, while
browsers size the em box. `line_ratio` converts between the two:
    ass_font_size = css_font_size * line_ratio
It is also the CSS line-height that matches libass line spacing.
"""

from functools import lru_cache

from fontTools.ttLib import TTFont

from app.captions.fonts import get_font
from app.config import get_settings


@lru_cache
def line_ratio(family: str) -> float:
    path = get_settings().fonts_dir / get_font(family).file_name
    try:
        font = TTFont(path, lazy=True)
        os2 = font["OS/2"]
        return (os2.usWinAscent + os2.usWinDescent) / font["head"].unitsPerEm
    except (OSError, KeyError):
        return 1.2  # sensible fallback if the font file is missing
