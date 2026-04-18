"""ModelBackend abstraction per E6a §3.6.

Swapping Ollama (dev) for Granite/vLLM (E8) is a config
change, not a code change. Any backend implementation
lives in a sibling module and is registered in factory.py.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Literal


@dataclass
class ChatMessage:
    role: Literal["system", "user", "assistant"]
    content: str


@dataclass
class ChatResponse:
    content: str
    model: str
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    raw: dict[str, Any] = field(default_factory=dict)


class ModelBackend(ABC):
    """Contract shared by every model backend (Ollama dev,
    Granite/vLLM E8, mocks)."""

    name: str = "abstract"

    @abstractmethod
    def health(self) -> dict[str, Any]:
        """Return backend-dependent health info. Must not raise;
        failures should appear in the dict."""

    @abstractmethod
    def chat(
        self,
        messages: list[ChatMessage],
        *,
        model: str | None = None,
        temperature: float = 0.1,
        max_tokens: int | None = None,
        stop: list[str] | None = None,
        timeout_sec: float | None = None,
    ) -> ChatResponse:
        """Run an instruct/chat call. Returns a ChatResponse."""

    @abstractmethod
    def embed(
        self,
        texts: list[str],
        *,
        model: str | None = None,
        timeout_sec: float | None = None,
    ) -> list[list[float]]:
        """Return one embedding vector per input text."""

    def reasoning_model(self) -> str:
        """The configured default reasoning model for this backend."""
        return ""

    def embedding_model(self) -> str:
        """The configured default embedding model."""
        return ""
