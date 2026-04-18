"""Deterministic mock backend for unit tests."""
from __future__ import annotations

import hashlib
from typing import Any

from services.model_backend.base import ChatMessage, ChatResponse, ModelBackend


def _seeded_vector(text: str, dim: int = 768) -> list[float]:
    # Deterministic pseudo-embedding. Normalised to unit length.
    h = hashlib.sha512(text.encode("utf-8")).digest()
    vec: list[float] = []
    while len(vec) < dim:
        for i in range(0, len(h), 2):
            if len(vec) >= dim:
                break
            raw = int.from_bytes(h[i:i + 2], "big") / 65535.0 - 0.5
            vec.append(raw)
        h = hashlib.sha512(h).digest()
    # Normalise.
    norm = sum(v * v for v in vec) ** 0.5 or 1.0
    return [v / norm for v in vec]


class MockBackend(ModelBackend):
    name = "mock"

    def reasoning_model(self) -> str:
        return "mock-reasoning"

    def embedding_model(self) -> str:
        return "mock-embedding"

    def health(self) -> dict[str, Any]:
        return {"ok": True, "backend": "mock"}

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
        # Echo-style deterministic response — useful for unit tests.
        last_user = next((m for m in reversed(messages) if m.role == "user"), None)
        body = f"MOCK_RESPONSE::{last_user.content if last_user else ''}"
        return ChatResponse(
            content=body,
            model=model or self.reasoning_model(),
            prompt_tokens=sum(len(m.content) for m in messages),
            completion_tokens=len(body),
        )

    def embed(
        self,
        texts: list[str],
        *,
        model: str | None = None,
        timeout_sec: float | None = None,
    ) -> list[list[float]]:
        return [_seeded_vector(t) for t in texts]
