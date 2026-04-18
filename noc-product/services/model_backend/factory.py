from functools import lru_cache

from services.common.settings import get_settings
from services.model_backend.base import ModelBackend


@lru_cache(maxsize=1)
def get_model_backend() -> ModelBackend:
    s = get_settings()
    kind = (s.model_backend or "ollama").lower()
    if kind == "ollama":
        from services.model_backend.ollama import OllamaBackend
        return OllamaBackend()
    if kind == "mock":
        from services.model_backend.mock import MockBackend
        return MockBackend()
    # E8 will add: "granite" → GraniteVLLMBackend
    raise ValueError(f"unknown model backend: {kind}")
