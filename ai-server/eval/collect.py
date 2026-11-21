"""Cut 2-second samples out of a video for the panel-detection test set.

    uv run python eval/collect.py video.mp4 myvideo 95 845 1370

writes eval/samples/myvideo_95.mp4 ... (640 px wide, like the real analysis).
Then add each sample's expected panel to eval/labels.json.
"""

import subprocess
import sys
from pathlib import Path

SAMPLES = Path(__file__).parent / "samples"


def main() -> None:
    video, prefix, times = sys.argv[1], sys.argv[2], sys.argv[3:]
    SAMPLES.mkdir(exist_ok=True)
    for t in times:
        target = SAMPLES / f"{prefix}_{t}.mp4"
        subprocess.run(
            ["ffmpeg", "-v", "error", "-y", "-ss", t, "-t", "2", "-i", video,
             "-vf", "scale=640:-2", "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", str(target)],
            check=True,
        )
        print(target.name)


if __name__ == "__main__":
    main()
