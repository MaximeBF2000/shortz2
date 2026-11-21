from shortz_ai.transcription.parakeet import sentences


def word(text: str, start: float) -> dict:
    return {"text": text, "start": start, "end": start + 0.3}


def test_words_are_grouped_into_sentences():
    words = [word("Bonjour", 0), word("à", 0.3), word("tous.", 0.6), word("Ça", 1.0), word("va", 1.3), word("bien", 3.0)]
    assert [s["text"] for s in sentences(words)] == ["Bonjour à tous.", "Ça va", "bien"]  # long pause before "bien"
