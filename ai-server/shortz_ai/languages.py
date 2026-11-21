"""Which engine transcribes which language."""

# Languages Parakeet TDT 0.6B v3 understands. Everything else goes to Whisper.
PARAKEET_LANGUAGES = {
    "bg", "hr", "cs", "da", "nl", "en", "et", "fi", "fr", "de", "el", "hu", "it",
    "lv", "lt", "mt", "pl", "pt", "ro", "sk", "sl", "es", "sv", "ru", "uk",
}  # fmt: skip


def pick_engine(language: str | None) -> str:
    """Parakeet is much faster; Whisper covers ~100 languages.

    With no language given we use Parakeet, which detects among its 25 languages.
    """
    if language and language not in PARAKEET_LANGUAGES:
        return "whisper"
    return "parakeet"
