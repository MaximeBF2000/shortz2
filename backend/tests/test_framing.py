from app.reframe.camera import Sample, camera_path
from app.reframe.faces import Face
from app.render.framing import crop_size, x_at


def face(x: float, size: float = 0.1) -> Face:
    return Face(x=x, y=0.4, size=size, score=0.9)


def test_crop_size_is_9_16():
    assert crop_size(1920, 1080) == (606, 1076)


def test_x_at_interpolates_and_holds_until_cuts():
    track = [{"t": 0, "x": 0.2, "cut": False}, {"t": 2, "x": 0.4, "cut": False}, {"t": 3, "x": 0.8, "cut": True}]
    assert abs(x_at(track, 1) - 0.3) < 1e-9
    assert x_at(track, 2.9) == 0.4  # held until the cut
    assert x_at(track, 3.5) == 0.8


def test_camera_ignores_small_moves_and_cuts_on_new_shots():
    samples = [Sample(t / 5, [face(0.5 + (0.005 if t % 2 else 0))]) for t in range(10)]
    samples.append(Sample(2.0, [face(0.8)], cut=True))
    path = camera_path(samples, crop_width=0.3)
    assert all(abs(k.x - 0.5) < 0.01 for k in path if k.t < 2)
    assert path[-1].cut and abs(path[-1].x - 0.8) < 0.01


def test_tiny_background_faces_are_ignored():
    samples = [Sample(0, [face(0.9, size=0.01), face(0.3, size=0.1)])]
    assert abs(camera_path(samples, crop_width=0.3)[0].x - 0.3) < 0.01
