import json
from types import SimpleNamespace

from app.pipeline.highlights import claude
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
    return Request(segments=[], words=words, duration=300, **kwargs)


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


def test_whisper_fragments_are_merged():
    words = [{"text": t, "start": 0, "end": 1} for t in ["decision", "-makers", "self", "-starter,", "it", "'s", "50", "%"]]
    assert [w["text"] for w in merge_fragments(words)] == ["decision-makers", "self-starter,", "it's", "50%"]


def test_claude_response_is_parsed(monkeypatch):
    answer = {
        "clips": [
            {"start": 12.0, "end": 41.5, "title": "Why", "hook": "Watch", "score": 140, "reason": "r", "keywords": [" w3 "]}
        ]
    }
    captured = {}

    class FakeStream:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def get_final_message(self):
            return SimpleNamespace(stop_reason="end_turn", content=[SimpleNamespace(type="text", text=json.dumps(answer))])

    class FakeClient:
        def __init__(self, **_):
            self.beta = SimpleNamespace(messages=SimpleNamespace(stream=self.stream))

        def stream(self, **params):
            captured.update(params)
            return FakeStream()

    monkeypatch.setattr(claude.anthropic, "Anthropic", FakeClient)
    [candidate] = claude.find_with_claude(request(focus="sleep"))

    assert candidate.score == 100  # clamped
    assert candidate.keywords == ["w3"]
    assert captured["output_config"]["format"]["type"] == "json_schema"
    assert "sleep" in captured["messages"][0]["content"]
