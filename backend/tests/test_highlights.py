from json import dumps

import httpx
import pytest

from app.pipeline.highlights import ollama
from app.pipeline.highlights.snap import clip_words, snap_candidates
from app.pipeline.highlights.types import Candidate, Request
from app.pipeline.transcribe import merge_fragments


def transcript(seconds: int) -> list[dict]:
    """One word per second; every 5th word ends a sentence."""
    return [
        {"text": f"w{i}" + ("." if i % 5 == 4 else ""), "start": float(i), "end": i + 0.8}
        for i in range(seconds)
    ]


def request(**kwargs) -> Request:
    words = transcript(300)
    segments = [{"start": w["start"], "end": w["end"], "text": w["text"]} for w in words]
    return Request(segments=segments, words=words, duration=300, **kwargs)


def test_snap_to_word_boundaries():
    [clip] = snap_candidates([Candidate(start=10.3, end=40.6, title="x")], request())
    assert (clip.start, clip.end) == (10.0, 40.8)


def test_too_long_clips_are_cut_at_a_sentence_end():
    [clip] = snap_candidates([Candidate(start=0, end=200, title="x")], request(length="short"))
    assert clip.end - clip.start <= 32
    assert clip.end == 29.8  # "w29." ends a sentence


def test_overlapping_clips_keep_the_best():
    clips = snap_candidates(
        [Candidate(start=10, end=40, title="a", score=60), Candidate(start=12, end=42, title="b", score=90)],
        request(),
    )
    assert [c.title for c in clips] == ["b"]


def test_keywords_are_flagged_for_emphasis():
    words = clip_words(transcript(10), 0, 10, keywords=["W3"])
    assert [w["text"] for w in words if w["emphasis"]] == ["w3"]


def test_keyword_phrases_only_match_as_a_whole():
    words = [{"text": t, "start": i, "end": i + 0.5} for i, t in enumerate("easy and fun and more".split())]
    flagged = [w["text"] for w in clip_words(words, 0, 10, keywords=["easy and fun"]) if w["emphasis"]]
    assert flagged == ["easy", "and", "fun"]


def test_whisper_fragments_are_merged():
    words = [{"text": t, "start": 0, "end": 1} for t in ["decision", "-makers", "self", "-starter,", "it", "'s", "50", "%"]]
    assert [w["text"] for w in merge_fragments(words)] == ["decision-makers", "self-starter,", "it's", "50%"]


def test_ollama_response_is_parsed(monkeypatch):
    answer = {
        "clips": [
            {"start": 12.0, "end": 41.5, "title": "Why", "hook": "Watch", "score": 140, "reason": "r", "keywords": [" w3 "]},
            {"start": 50, "end": 40, "title": "backwards", "hook": "", "score": 50, "reason": "", "keywords": []},
        ]
    }
    sent = {}

    def fake_post(url, json, timeout):
        sent.update(json)
        return httpx.Response(200, json={"done_reason": "stop", "message": {"content": dumps(answer)}})

    monkeypatch.setattr(ollama.httpx, "post", fake_post)
    [candidate] = ollama.find_with_ollama(request(focus="sleep"))  # the backwards clip is dropped

    assert candidate.score == 100  # clamped
    assert candidate.keywords == ["w3"]
    assert sent["format"]["type"] == "object"
    assert "sleep" in sent["messages"][1]["content"]


def test_missing_model_gives_a_helpful_error(monkeypatch):
    monkeypatch.setattr(ollama.httpx, "post", lambda *a, **k: httpx.Response(404, json={"error": "not found"}))
    with pytest.raises(ollama.ClipFinderError, match="ollama pull"):
        ollama.find_with_ollama(request())


def test_long_transcripts_are_split_to_fit_the_context():
    segments = [{"start": i, "end": i + 1, "text": "x" * 1000} for i in range(100)]
    chunks = ollama.split_into_chunks(segments, context_tokens=20_000)
    assert len(chunks) > 1
    assert sum(len(c) for c in chunks) == 100
