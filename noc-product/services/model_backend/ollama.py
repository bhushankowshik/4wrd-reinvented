"""Ollama backend for Mac-host development.

Host Ollama is reachable from containers via
host.docker.internal:11434 — configured in Compose via
`extra_hosts: host-gateway`.
"""
from __future__ import annotations

from typing import Any

import httpx

from services.common.settings import get_settings
from services.common.telemetry import MODEL_CALLS, log
from services.model_backend.base import ChatMessage, ChatResponse, ModelBackend


class OllamaBackend(ModelBackend):
    name = "ollama"

    def __init__(self) -> None:
        s = get_settings()
        self._base = s.ollama_base_url.rstrip("/")
        self._reasoning = s.ollama_reasoning_model
        self._embedding = s.ollama_embedding_model
        self._default_timeout = float(s.ollama_timeout_sec)

    def reasoning_model(self) -> str:
        return self._reasoning

    def embedding_model(self) -> str:
        return self._embedding

    def health(self) -> dict[str, Any]:
        try:
            r = httpx.get(f"{self._base}/api/tags", timeout=5)
            r.raise_for_status()
            tags = [m["name"] for m in r.json().get("models", [])]
            return {
                "ok": True,
                "base_url": self._base,
                "reasoning_model": self._reasoning,
                "embedding_model": self._embedding,
                "reasoning_available": self._reasoning in tags,
                "embedding_available": self._embedding in tags,
                "tags": tags,
            }
        except Exception as exc:  # noqa: BLE001
            return {
                "ok": False,
                "base_url": self._base,
                "reasoning_model": self._reasoning,
                "embedding_model": self._embedding,
                "error": str(exc),
            }

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
        use_model = model or self._reasoning
        options: dict[str, Any] = {"temperature": temperature}
        if max_tokens is not None:
            options["num_predict"] = max_tokens
        if stop:
            options["stop"] = stop

        try:
            r = httpx.post(
                f"{self._base}/api/chat",
                json={
                    "model": use_model,
                    "messages": [
                        {"role": m.role, "content": m.content} for m in messages
                    ],
                    "stream": False,
                    "options": options,
                },
                timeout=timeout_sec or self._default_timeout,
            )
            r.raise_for_status()
            data = r.json()
        except httpx.HTTPError as exc:
            MODEL_CALLS.labels(kind="chat", model=use_model, outcome="error").inc()
            log.error("model_backend.chat_failed", model=use_model, error=str(exc))
            raise

        MODEL_CALLS.labels(kind="chat", model=use_model, outcome="ok").inc()
        content = data.get("message", {}).get("content", "")
        return ChatResponse(
            content=content,
            model=use_model,
            prompt_tokens=data.get("prompt_eval_count"),
            completion_tokens=data.get("eval_count"),
            raw=data,
        )

    def embed(
        self,
        texts: list[str],
        *,
        model: str | None = None,
        timeout_sec: float | None = None,
    ) -> list[list[float]]:
        use_model = model or self._embedding
        vectors: list[list[float]] = []
        for text in texts:
            try:
                r = httpx.post(
                    f"{self._base}/api/embeddings",
                    json={"model": use_model, "prompt": text},
                    timeout=timeout_sec or self._default_timeout,
                )
                r.raise_for_status()
                vec = r.json().get("embedding") or []
            except httpx.HTTPError as exc:
                MODEL_CALLS.labels(kind="embed", model=use_model, outcome="error").inc()
                log.error("model_backend.embed_failed", model=use_model, error=str(exc))
                raise
            MODEL_CALLS.labels(kind="embed", model=use_model, outcome="ok").inc()
            vectors.append(list(vec))
        return vectors
