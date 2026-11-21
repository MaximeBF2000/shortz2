"""HTTP API the Shortz worker (in Docker) calls to run AI on this Mac.

    uv run shortz-ai            # listens on http://0.0.0.0:8765

POST /transcribe  audio (16 kHz mono wav) -> newline-delimited JSON: {"progress": 0.4}
                  lines while working, then {"result": {...}} or {"error": "..."}.
POST /reframe     a small copy of a clip -> {"track": [{t, x, cut}]}
"""

import json
import logging
import os
import queue
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import uvicorn
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
import transcribe_cpp

from shortz_ai import transcription
from shortz_ai.framing.analyze import analyze_clip
from shortz_ai.transcription import language, parakeet

app = FastAPI(title="Shortz AI")
# GPU frameworks (MLX in particular) tie work to the thread that started it, so
# every model call runs on this one thread. That also means one job at a time.
gpu = ThreadPoolExecutor(max_workers=1, thread_name_prefix="gpu")


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/transcribe")
def transcribe(audio: UploadFile = File(...), language: str = Form("")):
    path = save_upload(audio, ".wav")
    events: queue.Queue[dict | None] = queue.Queue()

    def work() -> None:
        try:
            progress = lambda value: events.put({"progress": round(min(1.0, value), 3)})  # noqa: E731
            events.put({"result": transcription.transcribe(path, language or None, progress)})
        except Exception as error:  # report it to the worker instead of dropping the connection
            events.put({"error": f"{type(error).__name__}: {error}"})
        finally:
            path.unlink(missing_ok=True)
            events.put(None)

    gpu.submit(work)

    def stream():
        while (event := events.get()) is not None:
            yield json.dumps(event) + "\n"

    return StreamingResponse(stream(), media_type="application/x-ndjson")


@app.post("/reframe")
def reframe(video: UploadFile = File(...), source_aspect: float = Form(...)):
    path = save_upload(video, ".mp4")
    try:
        return {"track": gpu.submit(analyze_clip, path, source_aspect).result()}
    except Exception as error:
        raise HTTPException(500, f"{type(error).__name__}: {error}") from error
    finally:
        path.unlink(missing_ok=True)


def save_upload(upload: UploadFile, suffix: str) -> Path:
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        while chunk := upload.file.read(4 * 1024 * 1024):
            tmp.write(chunk)
    return Path(tmp.name)


def warm_up() -> None:
    """Load the models up front so the first video doesn't wait for them."""
    parakeet.load_model()
    language.load_model()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    # transcribe.cpp logs every decoding step; keep only its warnings and errors.
    engine_log = logging.getLogger("transcribe.cpp")
    transcribe_cpp.set_log_callback(lambda level, message: level in (2, 3) and engine_log.warning(message.strip()))
    gpu.submit(warm_up).result()
    uvicorn.run(app, host=os.environ.get("HOST", "0.0.0.0"), port=int(os.environ.get("PORT", "8765")))
