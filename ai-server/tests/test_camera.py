from shortz_ai.framing.camera import Sample, Window, camera_path
from shortz_ai.framing.vision import Face

FULL = Window(width=0.3)


def face(x: float, size: float = 0.1) -> Face:
    return Face(x=x, y=0.4, size=size, score=0.9, height=0.15)


def test_camera_ignores_small_moves_and_cuts_on_new_shots():
    samples = [Sample(t / 5, [face(0.5 + (0.005 if t % 2 else 0))]) for t in range(10)]
    samples.append(Sample(2.0, [face(0.8)], cut=True))
    path = camera_path(samples, [FULL, FULL])
    assert all(abs(k.x - 0.5) < 0.01 for k in path if k.t < 2)
    assert path[-1].cut and abs(path[-1].x - 0.8) < 0.01


def test_tiny_background_faces_are_ignored():
    samples = [Sample(0, [face(0.9, size=0.01), face(0.3, size=0.1)])]
    assert abs(camera_path(samples, [FULL])[0].x - 0.3) < 0.01


def test_camera_stays_inside_the_panel_window():
    panel = Window(width=0.2, left=0.75, right=0.99, top=0.13, bottom=0.87)
    samples = [Sample(0, [face(0.95), face(0.3, size=0.2)])]  # a bigger face outside the panel
    keyframe = camera_path(samples, [panel])[0]
    assert abs(keyframe.x - 0.89) < 1e-6  # follows the face inside, clamped to the panel's edge
    assert keyframe.as_dict(with_box=True)["h"] == 0.74
