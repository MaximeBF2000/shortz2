"""Score the panel detector against the labeled test set.

    uv run python eval/run.py            # results table + summary
    uv run python eval/run.py --sheet    # also writes eval/sheet.jpg (red: found, green: expected)

A sample passes when the detector agrees there is no panel, or finds a box
overlapping the expected one by at least MIN_IOU.
"""

import json
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))

from shortz_ai.framing.analyze import analyze_shot, read_samples  # noqa: E402
from shortz_ai.framing.panels import Panel  # noqa: E402

HERE = Path(__file__).parent
MIN_IOU = 0.85


def main() -> None:
    labels = json.loads((HERE / "labels.json").read_text())
    rows, tiles = [], []
    for name, expected_box in labels.items():
        path = HERE / "samples" / f"{name}.mp4"
        if not path.exists():
            print(f"{name}: sample missing (run eval/collect.py)")
            continue
        samples, frames = read_samples(path)
        # Judge the first shot only, like production does shot by shot (a sample
        # can contain a cut; its label describes its first frame).
        first_shot = next((i for i, s in enumerate(samples) if s.cut), len(samples))
        found = analyze_shot(frames[:first_shot], [s.faces for s in samples[:first_shot]]).panel
        expected = Panel(*expected_box) if expected_box else None
        iou = found.iou(expected) if found and expected else None
        passed = (found is None and expected is None) or (iou is not None and iou >= MIN_IOU)
        rows.append((name, passed, describe(expected), describe(found), iou))
        if "--sheet" in sys.argv:
            tiles.append(draw(path, name, found, expected, passed))

    for name, passed, expected, found, iou in rows:
        score = f"IoU {iou:.2f}" if iou is not None else ""
        print(f"{'PASS' if passed else 'FAIL'}  {name:<14} expected {expected:<26} found {found:<26} {score}")
    passes = sum(r[1] for r in rows)
    with_panel = [r for r in rows if r[2] != "none"]
    print(f"\n{passes}/{len(rows)} passed  |  panels found right: {sum(r[1] for r in with_panel)}/{len(with_panel)}"
          f"  |  false panels: {sum(1 for r in rows if r[2] == 'none' and not r[1])}/{len(rows) - len(with_panel)}")
    if tiles:
        write_sheet(tiles, HERE / "sheet.jpg")


def describe(panel: Panel | None) -> str:
    if panel is None:
        return "none"
    return f"[{panel.left:.2f} {panel.top:.2f} {panel.right:.2f} {panel.bottom:.2f}]"


def draw(path: Path, name: str, found: Panel | None, expected: Panel | None, passed: bool) -> np.ndarray:
    capture = cv2.VideoCapture(str(path))
    ok, frame = capture.read()
    height, width = frame.shape[:2]
    for panel, color, thickness in ((expected, (0, 255, 0), 5), (found, (0, 0, 255), 2)):
        if panel:
            cv2.rectangle(frame, (int(panel.left * width), int(panel.top * height)),
                          (int(panel.right * width) - 1, int(panel.bottom * height) - 1), color, thickness)
    cv2.putText(frame, f"{name} {'PASS' if passed else 'FAIL'}", (10, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                (0, 255, 0) if passed else (0, 0, 255), 2)
    return frame


def write_sheet(tiles: list[np.ndarray], target: Path, columns: int = 4) -> None:
    blank = np.zeros_like(tiles[0])
    rows = [np.hstack((tiles[i : i + columns] + [blank] * columns)[:columns]) for i in range(0, len(tiles), columns)]
    cv2.imwrite(str(target), cv2.resize(np.vstack(rows), None, fx=0.5, fy=0.5))
    print(f"Sheet: {target}")


if __name__ == "__main__":
    main()
