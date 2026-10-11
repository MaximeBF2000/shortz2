"""Ready-made caption looks, shown as one-click options in the editor."""

from app.captions.style import CaptionStyle

PRESETS: dict[str, CaptionStyle] = {
    "Spotlight": CaptionStyle(),
    "Karaoke": CaptionStyle(
        font="Poppins", font_size=72, animation="karaoke", highlight_color="#7DD3FC", max_words=4
    ),
    "Headline": CaptionStyle(
        font="Anton", font_size=96, animation="highlight", highlight_color="#FF4D8D", max_words=2
    ),
    "One word": CaptionStyle(
        font="Bebas Neue", font_size=150, animation="single", stroke_width=9, position=0.62
    ),
    "Comic": CaptionStyle(
        font="Bangers", font_size=96, animation="pop", highlight_color="#FF8A00", stroke_width=9
    ),
    "Quiet": CaptionStyle(
        font="Inter",
        font_size=58,
        uppercase=False,
        animation="none",
        stroke_width=0,
        shadow=True,
        max_words=6,
        position=0.78,
    ),
    "Marker": CaptionStyle(
        font="Permanent Marker", font_size=76, uppercase=False, animation="highlight",
        highlight_color="#FFE14D", max_words=4,
    ),
    "Editorial": CaptionStyle(
        font="DM Serif Display", font_size=80, uppercase=False, animation="karaoke",
        highlight_color="#FFFFFF", text_color="#B8B2C4", stroke_width=0, max_words=4,
    ),
}
