"""Turn per-frame face detections into a smooth virtual camera path.

Behaves like a calm camera operator: it locks on one subject per shot, ignores
small movements (dead zone), eases toward the subject when it moves, and
jumps instantly on hard cuts.
"""

from dataclasses import dataclass, field

from shortz_ai.framing.vision import Face

DEAD_ZONE = 0.18  # fraction of the crop width the subject can drift before we move
EASE = 0.3  # how much of the remaining distance we cover per sample
STICKINESS = 2.5  # how strongly we prefer the subject we were already following
MIN_FACE_SIZE = 0.035  # smaller faces (crowds, background) are ignored
JUMP = 0.5  # if the subject is this far away (in crop widths), cut instead of panning


@dataclass
class Sample:
    t: float
    faces: list[Face]
    cut: bool = False  # first sample of a new shot


@dataclass
class Keyframe:
    t: float
    x: float  # crop center, normalized 0..1 of source width
    cut: bool = False

    def as_dict(self) -> dict:
        return {"t": round(self.t, 3), "x": round(self.x, 4), "cut": self.cut}


@dataclass
class Shot:
    samples: list[Sample] = field(default_factory=list)


def pick_subject(faces: list[Face], following: float | None) -> Face | None:
    faces = [f for f in faces if f.size >= MIN_FACE_SIZE]
    if not faces:
        return None
    if following is None:
        return max(faces, key=lambda f: f.weight)
    return max(faces, key=lambda f: f.weight / (1 + STICKINESS * abs(f.x - following)))


def split_shots(samples: list[Sample]) -> list[Shot]:
    shots: list[Shot] = []
    for sample in samples:
        if sample.cut or not shots:
            shots.append(Shot())
        shots[-1].samples.append(sample)
    return shots


def subject_positions(shot: Shot) -> list[float | None]:
    positions: list[float | None] = []
    following: float | None = None
    for sample in shot.samples:
        face = pick_subject(sample.faces, following)
        if face is not None:
            following = face.x
        positions.append(following)
    # Fill the start of the shot (before the first face) with the first known position.
    first_known = next((p for p in positions if p is not None), None)
    return [p if p is not None else first_known for p in positions]


def camera_path(samples: list[Sample], crop_width: float) -> list[Keyframe]:
    """crop_width is the crop window width as a fraction of the source width."""
    half = crop_width / 2
    keyframes: list[Keyframe] = []

    for shot_index, shot in enumerate(split_shots(samples)):
        positions = subject_positions(shot)
        camera = positions[0] if positions[0] is not None else 0.5
        for sample, target in zip(shot.samples, positions, strict=True):
            cut = shot_index > 0 and sample is shot.samples[0]
            if target is not None:
                distance = target - camera
                if abs(distance) > JUMP * crop_width:
                    camera, cut = target, True  # new subject: cut to it
                elif abs(distance) > DEAD_ZONE * crop_width:
                    camera += distance * EASE
            camera = min(max(camera, half), 1 - half)
            keyframes.append(Keyframe(sample.t, camera, cut=cut))

    return simplify(keyframes)


def simplify(keyframes: list[Keyframe], tolerance: float = 0.002) -> list[Keyframe]:
    """Drop keyframes that don't change the position, keeping cuts and moves."""
    if len(keyframes) <= 2:
        return keyframes
    kept = [keyframes[0]]
    for previous, current, following in zip(keyframes, keyframes[1:], keyframes[2:]):
        still = abs(current.x - previous.x) < tolerance and abs(following.x - current.x) < tolerance
        if current.cut or following.cut or not still:
            kept.append(current)
    kept.append(keyframes[-1])
    return kept
