"""HTTP API the Shortz worker (in Docker) calls to transcribe audio on this Mac.

    uv run shortz-ai            # listens on http://0.0.0.0:8765

POST /transcribe streams newline-delimited JSON: {"progress": 0.4} lines while
working, then {"result": {...}} or {"error": "..."} at the end.
"""

import json
import os
import queue
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import uvicorn
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import StreamingResponse

from shortz_ai import parakeet_engine, whisper_engine
from shortz_ai.languages import pick_engine

app = FastAPI(title="Shortz AI")
# MLX ties GPU work to the thread that started it, so every model call runs on
# this one thread. That also means one transcription at a time.
gpu = ThreadPoolExecutor(max_workers=1, thread_name_prefix="gpu")


@app.get("/health")
def health():
    return {"ok": True, "engines": ["parakeet", "whisper"]}


@app.post("/transcribe")
def transcribe(audio: UploadFile = File(...), language: str = Form("")):
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        while chunk := audio.file.read(4 * 1024 * 1024):
            tmp.write(chunk)
    path = Path(tmp.name)
    events: queue.Queue[dict | None] = queue.Queue()

    def work() -> None:
        try:
            progress = lambda value: events.put({"progress": round(min(1.0, value), 3)})  # noqa: E731
            if pick_engine(language or None) == "whisper":
                result = whisper_engine.transcribe(path, language, progress)
            else:
                result = parakeet_engine.transcribe(path, progress)
            events.put({"result": result})
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


def main() -> None:
    # Load Parakeet up front so the first video doesn't wait for it.
    gpu.submit(parakeet_engine.load_model).result()
    uvicorn.run(app, host=os.environ.get("HOST", "0.0.0.0"), port=int(os.environ.get("PORT", "8765")))
