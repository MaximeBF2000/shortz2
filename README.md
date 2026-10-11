# Shortz

Turn long videos into captioned vertical shorts. Paste a YouTube link or upload a file:
Shortz transcribes it, finds the moments worth posting, keeps the speaker in frame
and burns in animated captions in your brand's style.

- **Best clip detection**: Claude reads the timestamped transcript and picks
  self-contained moments with a hook and a payoff, scores them, writes a title and an
  on-screen hook, and flags keywords for emphasis.
- **Speaker framing for 9:16**: faces are tracked shot by shot. The virtual camera stays
  calm (dead zone, easing) and cuts when the video cuts. You can also fix the position
  by hand or show the whole frame over a blurred background.
- **Animated captions**: word-level timing from faster-whisper. 8 presets (pop,
  karaoke, one word…), 12 fonts, colors, outline, size and position.
- **Brand kits**: save caption + hook + logo designs, set a default for new clips.
- **Live editor**: what you see is what you export. The preview uses the same fonts,
  sizes and crop math as the renderer. Trim with word-snapping handles, fix words, mark
  keywords, hide filler words.

## Quick start (Docker)

```bash
cp .env.example .env        # optional: add your ANTHROPIC_API_KEY
docker compose up --build
```

Open http://localhost:3000. The first video takes longer because the Whisper model is
downloaded (it is then cached in a volume).

Without `ANTHROPIC_API_KEY`, a simple heuristic picks clips so the app still works,
but Claude's picks, titles and hooks are much better.

## Configuration

All settings are environment variables (see `.env.example`):

| Variable | Default | What it does |
| --- | --- | --- |
| `ANTHROPIC_API_KEY` | – | Enables AI clip detection |
| `ANTHROPIC_MODEL` | `claude-opus-5-5` | Model used to pick clips |
| `WHISPER_MODEL` | `small` | `tiny` → `large-v3` / `turbo`. Bigger is better and slower |
| `WHISPER_DEVICE` | `auto` | `cpu`, `cuda` or `auto` |
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
 │ 2. transcribe  faster-whisper, word timestamps                      │
 │ 3. highlights  Claude (or heuristic) → clips snapped to words       │
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
      transcribe.py      faster-whisper
      highlights/        clip detection: prompt, Claude call, heuristic, snapping
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

Requirements: Python 3.12, Node 22+, ffmpeg, Postgres, and [Deno](https://deno.com) for
YouTube downloads.

```bash
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
- For GPU transcription, run the backend on an image with CUDA + cuDNN and set
  `WHISPER_DEVICE=cuda`, `WHISPER_COMPUTE_TYPE=float16`, `WHISPER_MODEL=turbo`.
