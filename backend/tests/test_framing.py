from app.captions.style import FillStyle
from app.render.framing import Rect, crop_size, frame_filter, rect_at, x_at

SMART = [
    {"t": 0, "x": 0.87, "cut": False, "w": 0.2, "top": 0.135, "h": 0.73},
    {"t": 5, "x": 0.5, "cut": True, "w": 0.3164, "top": 0.0, "h": 1.0},
]


def test_crop_size_is_9_16():
    assert crop_size(1920, 1080) == (606, 1076)


def test_x_at_interpolates_and_holds_until_cuts():
    track = [{"t": 0, "x": 0.2, "cut": False}, {"t": 2, "x": 0.4, "cut": False}, {"t": 3, "x": 0.8, "cut": True}]
    assert abs(x_at(track, 1) - 0.3) < 1e-9
    assert x_at(track, 2.9) == 0.4  # held until the cut
    assert x_at(track, 3.5) == 0.8


def test_smart_crop_uses_the_panel_and_can_be_turned_off():
    framing = {"mode": "auto", "smart_crop": True, "track": [{"t": 0, "x": 0.5, "cut": False}], "smart_track": SMART}
    panel = rect_at(framing, 1, 1920, 1080)
    assert (panel.w, panel.h, panel.y) == (384, 788, 146)
    assert rect_at(framing, 6, 1920, 1080).h == 1080  # after the cut: a full-frame shot
    assert rect_at({**framing, "smart_crop": False}, 1, 1920, 1080).h == 1076


def test_fill_only_when_the_crop_is_not_9_16():
    assert "pad=" not in frame_filter(Rect(0, 0, 606, 1076), FillStyle())
    assert "pad=1080:1920" in frame_filter(Rect(0, 0, 384, 788), FillStyle(mode="color", color="#112233"))
    assert "color=0x112233" in frame_filter(Rect(0, 0, 384, 788), FillStyle(mode="color", color="#112233"))
    assert "boxblur" in frame_filter(Rect(0, 0, 384, 788), FillStyle(mode="blur"))
