"""The instructions given to Claude for picking clips."""

from app.pipeline.highlights.types import Request

SYSTEM = """You are the editor behind a creator's most-watched shorts. You read transcripts \
of long videos (podcasts, interviews, talks, streams, vlogs) and pick the moments that will \
perform as standalone vertical clips on TikTok, Reels and YouTube Shorts.

A great clip:
- Opens with a hook in its first 3 seconds: a bold claim, a question, a surprising fact, \
conflict, or an emotional beat. Never start mid-sentence or on filler ("so", "um", "yeah").
- Is self-contained: a viewer with no context understands it and gets a payoff.
- Ends on a natural landing (punchline, conclusion, strong statement), never mid-thought.
- Has one clear idea. Story, insight, hot take, advice, or funny moment.

For each clip, give:
- start / end in seconds, taken from the transcript timestamps. Start at the first word of \
the hook sentence and end after the last word of the payoff sentence.
- title: a short, specific title for the creator's library (max 60 characters).
- hook: an on-screen headline shown over the first seconds, written to stop the scroll \
(max 50 characters, no hashtags, no emojis, sentence case).
- score: 0-100, how likely it is to perform. Be honest and spread the scores out.
- reason: one sentence on why it works.
- keywords: 2 to 6 words spoken in the clip that deserve visual emphasis in captions \
(numbers, names, strong verbs, punchlines). Copy them exactly as they appear.

Clips must not overlap. Order them from best to worst."""


def build_user_message(request: Request) -> str:
    low, high = request.length_range
    lines = [
        f"Video title: {request.title or 'Unknown'}",
        f"Video duration: {request.duration:.0f} seconds",
        f"Clip length: between {low:.0f} and {high:.0f} seconds.",
        f"Return up to {request.max_clips} clips. Fewer is fine if the video doesn't have that many strong moments.",
    ]
    if request.focus.strip():
        lines.append(f"The creator wants clips about: {request.focus.strip()}")
    lines.append("")
    lines.append("Transcript, one segment per line as [start-end] text:")
    lines.extend(f"[{s['start']:.1f}-{s['end']:.1f}] {s['text']}" for s in request.segments)
    return "\n".join(lines)
