"""Research Agent — Claude Haiku 4.5.

Per the task knowledge contribution, the Research Agent is a Haiku-tier
fact-gathering pass invoked at Moment 2 BEFORE the Producing Agent
when:

  convergence_state == 'Explorative'
  AND the primary derivation intent names one or more external refs.

Its output is not the skill output. It feeds the Producing Agent's
Layer 3 context package with structured findings + sources. This
separation (INPUT-001 §7 Principle 2) keeps the Sonnet 4.6 Producing
Agent focused on production while using Haiku's cheap fact-gathering
for the inputs.

Chain entry type: `research` (actor_id=producing_agent by default —
the research write is under the producing family; override via
ActorConfig.research_agent if needed).
"""
from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path

import anthropic


RESEARCH_MODEL = "claude-haiku-4-5-20251001"
RESEARCH_MAX_TOKENS = 2048


RESEARCH_SYSTEM_PROMPT = """\
You are the Research Agent in a 4WRD governed delivery cycle. You are
a Haiku-tier fact-gathering pass, NOT a producing agent. You do not
produce the skill output.

Given a direction, a list of primary derivation intent references
(file paths or URLs), and any knowledge contribution text, you emit a
short structured list of findings + sources that the Producing Agent
will consume as part of its context package.

Rules:
- You do not invent. If a referenced file was not provided inline,
  say so in findings. Do not hallucinate its contents.
- Findings are short — one clause each, load-bearing facts only.
- Sources are verbatim references (file paths or URLs) as given.
- Do NOT propose a problem statement, architecture, or decision.
  That is the Producing Agent's job.
- If there are no external references, return an empty findings list
  rather than making things up.

Output format (strict):

<RESEARCH>
{
  "findings": ["..."],
  "sources": ["..."]
}
</RESEARCH>
"""


_RESEARCH_RE = re.compile(r"<RESEARCH>\s*(.*?)\s*</RESEARCH>", re.DOTALL)


@dataclass(frozen=True)
class ResearchOutput:
    findings: list[str]
    sources: list[str]
    raw: str
    model: str = RESEARCH_MODEL
    invoked: bool = True

    def render_for_producing(self) -> str:
        """Compact text block to splice into the Producing context package."""
        if not self.invoked or (not self.findings and not self.sources):
            return ""
        lines: list[str] = ["## Research Agent findings"]
        for f in self.findings:
            lines.append(f"- {f}")
        if self.sources:
            lines.append("")
            lines.append("Sources:")
            for s in self.sources:
                lines.append(f"- {s}")
        return "\n".join(lines)


EMPTY_RESEARCH = ResearchOutput(
    findings=[], sources=[], raw="", invoked=False,
)


def should_invoke(
    *, convergence_state: str, primary_derivation_intent: list[str],
) -> bool:
    """Invoke only when Explorative AND at least one external ref declared."""
    return (
        convergence_state == "Explorative"
        and any(p.strip() for p in primary_derivation_intent)
    )


def _read_ref_contents(ref: str, *, max_chars: int = 4000) -> str | None:
    """Best-effort inline read for local file refs. Returns None on miss."""
    try:
        p = Path(ref)
        if p.is_file():
            return p.read_text(encoding="utf-8", errors="replace")[:max_chars]
    except OSError:
        pass
    return None


class ResearchAgent:
    """Haiku-tier research pass."""

    def __init__(
        self,
        *,
        system_prompt: str = RESEARCH_SYSTEM_PROMPT,
        model: str = RESEARCH_MODEL,
        max_tokens: int = RESEARCH_MAX_TOKENS,
        stream_to: object | None = None,
    ) -> None:
        self._system_prompt = system_prompt
        self._model = model
        self._max_tokens = max_tokens
        self._stream_to = stream_to
        self._client = anthropic.Anthropic(
            api_key=os.environ.get("ANTHROPIC_API_KEY"),
        )

    def gather(
        self,
        *,
        direction: str,
        primary_derivation_intent: list[str],
        knowledge_contribution: str | None,
    ) -> ResearchOutput:
        """Run one research pass. Blocks until streaming finishes."""
        # Build the user prompt with inlined local-file snippets when
        # available so Haiku can cite verbatim rather than hallucinate.
        ref_blobs: list[str] = []
        for ref in primary_derivation_intent:
            snippet = _read_ref_contents(ref)
            if snippet is not None:
                ref_blobs.append(
                    f"### Ref: {ref}\n```\n{snippet}\n```"
                )
            else:
                ref_blobs.append(f"### Ref: {ref}  (not read inline)")

        user_text = (
            f"## Direction\n{direction.strip()}\n\n"
            f"## Knowledge contribution\n"
            f"{(knowledge_contribution or '(none)').strip()}\n\n"
            f"## Primary derivation intent references\n"
            + ("\n\n".join(ref_blobs) if ref_blobs else "(none)")
            + "\n\nEmit the research findings now."
        )

        raw_chunks: list[str] = []
        with self._client.messages.stream(
            model=self._model,
            max_tokens=self._max_tokens,
            system=self._system_prompt,
            messages=[{"role": "user", "content": user_text}],
        ) as stream:
            for delta in stream.text_stream:
                raw_chunks.append(delta)
                if self._stream_to is not None:
                    try:
                        self._stream_to.write(delta)
                        self._stream_to.flush()
                    except Exception:
                        pass

        raw = "".join(raw_chunks)
        findings, sources = self._parse(raw)
        return ResearchOutput(
            findings=findings, sources=sources, raw=raw, model=self._model,
            invoked=True,
        )

    @staticmethod
    def _parse(raw: str) -> tuple[list[str], list[str]]:
        m = _RESEARCH_RE.search(raw)
        if m is None:
            raise ValueError(
                "Research Agent output did not contain the required "
                "<RESEARCH>...</RESEARCH> block."
            )
        try:
            data = json.loads(m.group(1).strip())
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"Research Agent RESEARCH block was not valid JSON: {exc}"
            )
        findings = [str(x) for x in data.get("findings", [])]
        sources = [str(x) for x in data.get("sources", [])]
        return findings, sources
