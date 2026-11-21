# Shortz

Turn long videos into captioned vertical shorts. Paste a YouTube link or upload a file:
Shortz transcribes it, finds the moments worth posting, keeps the speaker in frame
and burns in animated captions in your brand's style.

- **Best clip detection**: a local LLM (Ollama, `qwen3.6:35b-mlx` by default) reads the
  timestamped transcript and picks self-contained moments with a hook and a payoff, scores
  them, writes a title and an on-screen hook, and flags keywords for emphasis. Nothing
  leaves your machine and there's no API key.
- **Speaker framing for 9:16**: faces are tracked shot by shot. The virtual camera stays
  calm (dead zone, easing) and cuts when the video cuts. You can also fix the position
  by hand or show the whole frame over a blurred background.
- **Animated captions**: word-level timing from Parakeet (Whisper for other languages),
  transcribed on your Mac's GPU. 8 presets (pop,
  karaoke, one word…), 12 fonts, colors, outline, size and position.
- **Brand kits**: save caption + hook + logo designs, set a default for new clips.
- **Live editor**: what you see is what you export. The preview uses the same fonts,
  sizes and crop math as the renderer. Trim with word-snapping handles, fix words, mark
  keywords, hide filler words.

## Where things run

All AI runs natively on your Mac so it can use the Apple Silicon GPU. Docker only runs
the app itself.

| Runs on your Mac | Runs in Docker |
| --- | --- |
| **Ollama**: picks the clips (`qwen3.6:35b-mlx`) | **web**: the Next.js site (port 3000) |
| **Shortz AI** (`ai-server/`): speech-to-text with Parakeet, or Whisper for languages Parakeet doesn't cover, both on MLX (port 8765) | **api**: FastAPI (port 8000) |
| | **worker**: downloads, video processing, face tracking, rendering |
| | **db**: Postgres |

The containers reach your Mac at `host.docker.internal`.

## Quick start

You need [Docker Desktop](https://www.docker.com/products/docker-desktop/),
[Ollama](https://ollama.com), [uv](https://docs.astral.sh/uv/) and ffmpeg
(`brew install ffmpeg`).

1. Start the Ollama app. If you don't have the model yet: `ollama pull qwen3.6:35b-mlx`.
2. Start the Shortz AI service in its own terminal (leave it running):
   ```bash
   cd ai-server
   uv run shortz-ai
   ```
   The first start downloads Parakeet (about 1.2 GB). The Whisper model is only
   downloaded the first time you pick a language Parakeet doesn't support.
3. Start the app:
   ```bash
   cp .env.example .env
   docker compose up -d --build
   ```
4. Open http://localhost:3000. If Ollama or the AI service isn't reachable, the home page
   says so.

To stop: `docker compose down`, then Ctrl+C in the AI service terminal.

Any Ollama model that supports structured outputs works: set `OLLAMA_MODEL` in `.env`.
The default is the MLX build of Qwen3.6 35B-A3B, made for Apple Silicon; on other
machines use `qwen3.6:35b-a3b`.

### Languages

Parakeet (fast, the default) covers 25 European languages, English and French included,
and detects which one is spoken. If you pick another language when creating a project
(Japanese, Chinese, Korean, Hindi, Arabic…), Shortz uses Whisper large-v3-turbo instead.

## Configuration

All settings are environment variables (see `.env.example`):

| Variable | Default | What it does |
| --- | --- | --- |
| `CLIP_FINDER` | `ollama` | `ollama`, or `heuristic` to pick clips by speaking pace without AI |
| `OLLAMA_MODEL` | `qwen3.6:35b-mlx` | Ollama model used to pick clips |
| `OLLAMA_CONTEXT` | `32768` | Context window (tokens). Longer transcripts are split into parts |
| `OLLAMA_THINK` | `true` | Let the model reason before answering (slower, better picks) |
| `OLLAMA_URL` | `http://localhost:11434` | Where Ollama listens (Docker uses `host.docker.internal`) |
| `TRANSCRIBER_URL` | `http://localhost:8765` | Where the Shortz AI service listens (Docker uses `host.docker.internal`) |
| `WORKER_CONCURRENCY` | `2` | Jobs processed in parallel |
| `MAX_VIDEO_HEIGHT` | `1080` | Highest resolution downloaded from YouTube |
| `YTDLP_COOKIES_FILE` | – | Cookies file, if YouTube asks to confirm you're not a bot |
| `PUBLIC_API_URL` / `PUBLIC_WEB_URL` | `localhost` | Where the browser reaches the app when deployed |

## How it works

```
 YouTube link / upload
        │
        ▼
 ┌─ worker: process_project ──────────────────────────────────────────┐
 │ 1. ingest      yt-dlp download → H.264 mp4 → 16 kHz audio           │
 │ 2. transcribe  Shortz AI on the Mac: Parakeet/Whisper, word timing  │
 │ 3. highlights  Ollama LLM (or heuristic) → clips snapped to words   │
 │ 4. reframe     shot cuts + face tracking → crop track per clip      │
 └─────────────────────────────────────────────────────────────────────┘
        │
        ▼
 Editor (Next.js) ── live preview: canvas crop + HTML captions
        │ export
        ▼
 worker: render_clip  ffmpeg: crop (sendcmd) → 1080×1920 → .ass captions → logo
```

Jobs are stored in Postgres and claimed with `SELECT … FOR UPDATE SKIP LOCKED`, so no
Redis or Celery is needed. Run more `worker` containers to process more videos at once.

## Project layout

```
ai-server/               runs natively on the Mac (MLX), not in Docker
  shortz_ai/
    server.py            HTTP API: POST /transcribe streams progress, then the transcript
    parakeet_engine.py   Parakeet TDT 0.6B v3
    whisper_engine.py    Whisper large-v3-turbo, for other languages
    languages.py         which engine handles which language
backend/
  app/
    main.py              FastAPI app
    config.py            settings from env vars
    db.py, storage.py    database session, file locations
    models/              Project, Clip, BrandKit, Job
    schemas/             API request/response shapes
    api/                 routes: projects, clips, brand kits, fonts/presets
    services/            small domain helpers (default style, retiming words)
    pipeline/
      youtube.py         download with yt-dlp
      ingest.py          normalize video, extract audio/poster
      transcribe.py      client for the Shortz AI service
      highlights/        clip detection: prompt, Ollama call, heuristic, snapping
    reframe/             faces (YuNet), shot cuts, virtual camera, per-clip analysis
    captions/            caption style, presets, fonts, pagination of words
    render/              .ass subtitles, crop/fit filters, final ffmpeg render
    worker/              job queue, progress reporting, tasks
  scripts/download_assets.py   caption fonts + face model
  tests/
frontend/
  app/                   pages: home, project, clip editor, brand kits
  components/
    home/                new project form, project list
    project/             processing steps, clip grid
    editor/              editor shell, preview (stage, video, caption layers), inspector panels
    style/               caption/hook/logo style editors, font + preset pickers
    brand/               brand kit page parts
    ui/                  buttons, sliders, toggles…
  lib/                   API client, types, caption pagination + crop math (mirrors the backend)
```

## Local development (without Docker)

Requirements: Python 3.12, Node 22+, ffmpeg, Postgres, Ollama, uv, and
[Deno](https://deno.com) for YouTube downloads.

```bash
# AI service (same as with Docker)
cd ai-server && uv run shortz-ai

# backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
python -m scripts.download_assets
echo "DATABASE_URL=postgresql+psycopg://user:pass@localhost:5432/shortz" > .env
uvicorn app.main:app --reload          # API on :8000
python -m app.worker                   # in another terminal
pytest                                 # tests

# frontend
cd frontend
npm install
npm run dev                            # http://localhost:3000
```

## Notes

- Shortz is single-user: there are no accounts. Put it behind your own auth before
  exposing it on the internet.
- Tables are created on startup (no migrations yet).
- Caption pagination (`captions/pages.py` ↔ `lib/captions/pages.ts`) and crop math
  (`render/framing.py` ↔ `lib/framing.ts`) exist in both languages so the preview matches
  the export. Change them together.
- Face tracking (OpenCV's YuNet, a 300 KB model) stays in the Docker worker: it runs on
  the CPU and is fast enough there.
