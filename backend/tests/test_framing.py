from app.render.framing import crop_size, x_at


def test_crop_size_is_9_16():
    assert crop_size(1920, 1080) == (606, 1076)


def test_x_at_interpolates_and_holds_until_cuts():
    track = [{"t": 0, "x": 0.2, "cut": False}, {"t": 2, "x": 0.4, "cut": False}, {"t": 3, "x": 0.8, "cut": True}]
    assert abs(x_at(track, 1) - 0.3) < 1e-9
    assert x_at(track, 2.9) == 0.4  # held until the cut
    assert x_at(track, 3.5) == 0.8
