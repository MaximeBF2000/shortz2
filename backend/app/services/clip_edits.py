"""Keep caption words consistent when a clip is trimmed."""

from app.pipeline.highlights.snap import clip_words


def retime_words(transcript_words: list[dict], old_words: list[dict], start: float, end: float) -> list[dict]:
    """Words for the new [start, end] range, keeping the user's edits (text, keyword, hidden).

    Edits are matched by the word's start time, which never changes.
    """
    edits = {round(w["start"], 3): w for w in old_words}
    words = clip_words(transcript_words, start, end, keywords=[])
    for word in words:
        edited = edits.get(round(word["start"], 3))
        if edited is not None:
            word["text"] = edited["text"]
            word["emphasis"] = edited.get("emphasis", False)
            word["hidden"] = edited.get("hidden", False)
    return words
