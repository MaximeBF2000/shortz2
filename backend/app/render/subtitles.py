"""Build an .ass subtitle file (captions + hook) for a clip.

The video is rendered at 1080x1920 and the .ass file uses the same coordinates,
so every size in ClipStyle maps 1:1 to output pixels.
"""

from app.captions.fonts import get_font
from app.captions.metrics import line_ratio
from app.captions.pages import Page, Word, build_pages
from app.captions.style import CaptionStyle, ClipStyle, HookStyle

WIDTH, HEIGHT = 1080, 1920
HOOK_TEXT_WIDTH = 860


def ass_color(hex_color: str, alpha: int = 0) -> str:
    """'#RRGGBB' -> '&HAABBGGRR' (ASS colors are BGR, alpha 0 = opaque)."""
    value = hex_color.lstrip("#")
    r, g, b = value[0:2], value[2:4], value[4:6]
    return f"&H{alpha:02X}{b}{g}{r}".upper()


def ass_time(seconds: float) -> str:
    seconds = max(0.0, seconds)
    cs = round(seconds * 100)
    h, cs = divmod(cs, 360000)
    m, cs = divmod(cs, 6000)
    s, cs = divmod(cs, 100)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace("{", "(").replace("}", ")")


def build_ass(words: list[Word], hook: str, style: ClipStyle, duration: float) -> str:
    captions, hook_style = style.captions, style.hook
    lines = [header(captions, hook_style)]
    if hook_style.enabled and hook.strip():
        lines.append(hook_event(hook, hook_style, min(hook_style.duration, duration)))
    if captions.enabled:
        lines.extend(caption_events(words, captions))
    return "\n".join(lines) + "\n"


def header(captions: CaptionStyle, hook: HookStyle) -> str:
    caption_font = get_font(captions.font)
    hook_font = get_font(hook.font)
    caption_size = round(captions.font_size * line_ratio(caption_font.family))
    hook_size = round(hook.font_size * line_ratio(hook_font.family))
    shadow = 5 if captions.shadow else 0
    box = ass_color(hook.background_color)
    return "\n".join(
        [
            "[Script Info]",
            "ScriptType: v4.00+",
            f"PlayResX: {WIDTH}",
            f"PlayResY: {HEIGHT}",
            "WrapStyle: 2",
            "ScaledBorderAndShadow: yes",
            "",
            "[V4+ Styles]",
            "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, "
            "BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, "
            "BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
            f"Style: Caption,{caption_font.family},{caption_size},{ass_color(captions.text_color)},"
            f"{ass_color(captions.text_color)},{ass_color(captions.stroke_color)},&H80000000,"
            f"0,0,0,0,100,100,0,0,1,{captions.stroke_width},{shadow},5,40,40,0,1",
            f"Style: Hook,{hook_font.family},{hook_size},{ass_color(hook.text_color)},"
            f"{ass_color(hook.text_color)},{box},{box},0,0,0,0,100,100,0,0,3,18,0,5,40,40,0,1",
            "",
            "[Events]",
            "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
        ]
    )


def hook_event(hook: str, style: HookStyle, duration: float) -> str:
    max_chars = max(8, int(HOOK_TEXT_WIDTH / (0.55 * style.font_size)))
    text = r"\N".join(wrap(escape(hook.strip()), max_chars))
    y = round(style.position * HEIGHT)
    return (
        f"Dialogue: 1,{ass_time(0)},{ass_time(duration)},Hook,,0,0,0,,"
        f"{{\\an5\\pos({WIDTH // 2},{y})\\fad(150,200)}}{text}"
    )


def wrap(text: str, max_chars: int) -> list[str]:
    lines: list[str] = []
    for word in text.split():
        if lines and len(lines[-1]) + 1 + len(word) <= max_chars:
            lines[-1] += " " + word
        else:
            lines.append(word)
    return lines


def caption_events(words: list[Word], style: CaptionStyle) -> list[str]:
    max_words = 1 if style.animation == "single" else style.max_words
    pages = build_pages(words, max_words, style.font_size)
    y = round(style.position * HEIGHT)
    events = []
    for page in pages:
        if style.animation in ("none", "single"):
            # One static event per page.
            events.append(dialogue(page.start, page.end, page_text(page, style, None), y, pop=True))
            continue
        for index, word in enumerate(page.words):
            start = page.start if index == 0 else word.start
            end = page.active_until(index)
            if end - start < 0.01:
                continue
            events.append(dialogue(start, end, page_text(page, style, index), y, pop=index == 0 and style.animation == "pop"))
    return events


def dialogue(start: float, end: float, text: str, y: int, pop: bool) -> str:
    tags = f"\\an5\\pos({WIDTH // 2},{y})"
    if pop:
        tags += r"\fscx82\fscy82\t(0,110,\fscx100\fscy100)"
    return f"Dialogue: 0,{ass_time(start)},{ass_time(end)},Caption,,0,0,0,,{{{tags}}}{text}"


def word_color(page: Page, index: int, active: int | None, style: CaptionStyle) -> str:
    word = page.words[index]
    if active is not None:
        if style.animation == "karaoke" and index <= active:
            return style.highlight_color
        if style.animation in ("highlight", "pop") and index == active:
            return style.highlight_color
    if word.emphasis:
        return style.emphasis_color
    return style.text_color


def page_text(page: Page, style: CaptionStyle, active: int | None) -> str:
    rendered_lines = []
    for line in page.lines:
        parts = []
        for index in line:
            text = escape(page.words[index].text.strip())
            if style.uppercase:
                text = text.upper()
            color = ass_color(word_color(page, index, active, style))
            parts.append(f"{{\\1c{color}}}{text}")
        rendered_lines.append(" ".join(parts))
    return r"\N".join(rendered_lines)
