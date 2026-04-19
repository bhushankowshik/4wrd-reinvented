"""Adversarial Agent — Claude Opus 4.6.

Per INPUT-001 §4: highest-capability tier, permanent challenger in
every cycle moment. Also the secondary Frame Change Sidecar Detector
(§2.3) — so the challenge output includes a FRAME_CHANGE axis that
the orchestrator reads to decide whether to interrupt the cycle.

Model string per the task knowledge contribution: `claude-opus-4-6`.
"""
from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field

import anthropic

from harness.context_package import ChallengeContextPackage


ADVERSARIAL_MODEL = "claude-opus-4-6"
ADVERSARIAL_MAX_TOKENS = 4096


_CHALLENGES_RE = re.compile(
    r"<CHALLENGES>\s*(.*?)\s*</CHALLENGES>", re.DOTALL,
)


@dataclass(frozen=True)
class Challenge:
    axis: str  # OUTPUT | REASONING | DIRECTION | FRAME_CHANGE
    severity: str  # CRITICAL | MAJOR | MINOR
    challenge: str
    evidence: str


@dataclass(frozen=True)
class AdversarialOutput:
    challenges: list[Challenge]
    frame_change_detected: bool
    raw: str
    model: str = ADVERSARIAL_MODEL

    @property
    def severities(self) -> list[str]:
        return [c.severity for c in self.challenges]

    def render(self) -> str:
        if not self.challenges:
            return "(no challenges)"
        lines: list[str] = []
        for i, c in enumerate(self.challenges, 1):
            lines.append(
                f"{i}. [{c.severity}] ({c.axis}) {c.challenge}\n"
                f"   evidence: {c.evidence}"
            )
        return "\n".join(lines)


class AdversarialAgent:
    """Opus 4.6 subagent that challenges output + reasoning + direction."""

    def __init__(
        self,
        *,
        system_prompt: str,
        model: str = ADVERSARIAL_MODEL,
        max_tokens: int = ADVERSARIAL_MAX_TOKENS,
        stream_to: object | None = None,
    ) -> None:
        self._system_prompt = system_prompt
        self._model = model
        self._max_tokens = max_tokens
        self._stream_to = stream_to
        self._client = anthropic.Anthropic(
            api_key=os.environ.get("ANTHROPIC_API_KEY"),
        )

    def challenge(self, package: ChallengeContextPackage) -> AdversarialOutput:
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
        challenges = self._parse(raw)
        frame_change = any(
            c.axis == "FRAME_CHANGE" and c.severity == "CRITICAL"
            for c in challenges
        )
        return AdversarialOutput(
            challenges=challenges,
            frame_change_detected=frame_change,
            raw=raw,
            model=self._model,
        )

    @staticmethod
    def _parse(raw: str) -> list[Challenge]:
        m = _CHALLENGES_RE.search(raw)
        if m is None:
            raise ValueError(
                "Adversarial Agent output did not contain the required "
                "<CHALLENGES>...</CHALLENGES> JSON block."
            )
        try:
            data = json.loads(m.group(1).strip())
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"Adversarial Agent CHALLENGES block was not valid JSON: {exc}"
            )
        if not isinstance(data, list):
            raise ValueError("CHALLENGES block must be a JSON array.")
        return [
            Challenge(
                axis=str(d.get("axis", "")).upper(),
                severity=str(d.get("severity", "")).upper(),
                challenge=str(d.get("challenge", "")),
                evidence=str(d.get("evidence", "")),
            )
            for d in data
        ]
