"""Producing Agent — Claude Sonnet 4.6.

Per INPUT-001 §4: one persona family, one instance per skill per
domain-specialisation. Produces OUTPUT + REASONING_TRACE as two
separable components in a single streamed response.

We use the anthropic Python SDK's streaming API directly — the 4WRD
harness does not need the tool-use loop that `anthropic.Agent` would
give it, because this subagent produces text, not tool calls.

Model string per the task knowledge contribution: `claude-sonnet-4-6`.
"""
from __future__ import annotations

import os
import re
import sys
from dataclasses import dataclass

import anthropic

from harness.context_package import ProducingContextPackage


PRODUCING_MODEL = "claude-sonnet-4-6"
PRODUCING_MAX_TOKENS = 8192


_OUTPUT_RE = re.compile(r"<OUTPUT>\s*(.*?)\s*</OUTPUT>", re.DOTALL)
_REASONING_RE = re.compile(
    r"<REASONING_TRACE>\s*(.*?)\s*</REASONING_TRACE>", re.DOTALL,
)


@dataclass(frozen=True)
class ProducingOutput:
    output: str
    reasoning_trace: str
    raw: str
    model: str = PRODUCING_MODEL


class ProducingAgent:
    """Sonnet 4.6 subagent that produces the two-component artefact."""

    def __init__(
        self,
        *,
        system_prompt: str,
        model: str = PRODUCING_MODEL,
        max_tokens: int = PRODUCING_MAX_TOKENS,
        stream_to: object | None = None,
    ) -> None:
        self._system_prompt = system_prompt
        self._model = model
        self._max_tokens = max_tokens
        self._stream_to = stream_to  # writable; set to sys.stdout to tee tokens
        self._client = anthropic.Anthropic(
            api_key=os.environ.get("ANTHROPIC_API_KEY"),
        )

    def produce(self, package: ProducingContextPackage) -> ProducingOutput:
        """Run one production turn. Blocks until the stream finishes."""
        user_text = package.render()
        raw_chunks: list[str] = []

        with self._client.messages.stream(
            model=self._model,
            max_tokens=self._max_tokens,
            system=self._system_prompt,
            messages=[{"role": "user", "content": user_text}],
        ) as stream:
            for text_delta in stream.text_stream:
                raw_chunks.append(text_delta)
                if self._stream_to is not None:
                    try:
                        self._stream_to.write(text_delta)
                        self._stream_to.flush()
                    except Exception:
                        pass

        raw = "".join(raw_chunks)
        output, reasoning = self._parse(raw)
        return ProducingOutput(
            output=output, reasoning_trace=reasoning, raw=raw, model=self._model,
        )

    @staticmethod
    def _parse(raw: str) -> tuple[str, str]:
        m_out = _OUTPUT_RE.search(raw)
        m_reason = _REASONING_RE.search(raw)
        if m_out is None or m_reason is None:
            # Fail loudly — LRN-003 (hooks must surface failures explicitly).
            raise ValueError(
                "Producing Agent output did not contain the required "
                "<OUTPUT>...</OUTPUT> and <REASONING_TRACE>...</REASONING_TRACE> "
                f"blocks. Got {len(raw)} chars."
            )
        return m_out.group(1).strip(), m_reason.group(1).strip()
