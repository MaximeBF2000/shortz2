"""Model files used by the AI service. Downloaded once into the Hugging Face cache
(the Handy app uses the same cache, so files it already downloaded are reused)."""

from functools import lru_cache
from pathlib import Path

from huggingface_hub import hf_hub_download

# Parakeet Ultra: Moondream's post-trained Parakeet TDT 0.6B v3 (25 European languages).
PARAKEET = ("handy-computer/parakeet-ultra-gguf", "parakeet-ultra-Q8_0.gguf")
# VoxLingua107 language identifier (107 languages, 27 MB).
LANGUAGE_ID = ("handy-computer/lang-id-voxlingua107-ecapa-gguf", "lang-id-voxlingua107-ecapa-Q8_0.gguf")
# Whisper on MLX, for languages Parakeet doesn't know.
WHISPER = "mlx-community/whisper-large-v3-turbo"


@lru_cache
def model_path(repo: str, filename: str) -> Path:
    return Path(hf_hub_download(repo, filename))
