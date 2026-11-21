"""Which engine transcribes which language.

Parakeet is the fastest and most accurate for English, but its automatic language
detection is unreliable (a French video can come out translated to English) and
it can't be told which language to use. So Whisper decides the language, and
handles everything that isn't English.
"""


def pick_engine(language: str) -> str:
    return "parakeet" if language == "en" else "whisper"
