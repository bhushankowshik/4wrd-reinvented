"""Structure-aware chunker — E6a §2.1 / E5 §3.3.

One chunk per ParsedSection when length ≤ max_tokens; else
recursive split at paragraph → sentence preserving
section_path. Target 500-1000 tokens with 100 overlap.

Token count via tiktoken cl100k_base (ubiquitous tokenizer
available without model download).
"""
from __future__ import annotations

import re
from dataclasses import dataclass

import tiktoken

from services.sop_ingest.parser import ParsedSection


@dataclass
class Chunk:
    section_path: str
    section_type: str
    chunk_seq: int
    text: str
    source_file: str


_TARGET_MAX = 1000
_TARGET_MIN = 300
_OVERLAP_TOKENS = 100


def _enc() -> tiktoken.Encoding:
    return tiktoken.get_encoding("cl100k_base")


def _split_paragraphs(text: str) -> list[str]:
    return [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]


def _split_sentences(text: str) -> list[str]:
    # Cheap sentence splitter — sufficient for SOPs.
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z(])", text)
    return [p.strip() for p in parts if p.strip()]


def _split_recursive(text: str, max_tokens: int) -> list[str]:
    enc = _enc()
    if len(enc.encode(text)) <= max_tokens:
        return [text]
    units = _split_paragraphs(text)
    if len(units) == 1:
        units = _split_sentences(text)
    chunks: list[str] = []
    buf: list[str] = []
    buf_tokens = 0
    for u in units:
        toks = len(enc.encode(u))
        if buf_tokens + toks > max_tokens and buf:
            chunks.append(" ".join(buf).strip())
            # Overlap — last N tokens worth of previous text.
            tail_tokens = enc.encode(chunks[-1])[-_OVERLAP_TOKENS:]
            tail = enc.decode(tail_tokens)
            buf = [tail]
            buf_tokens = len(tail_tokens)
        buf.append(u)
        buf_tokens += toks
    if buf:
        chunks.append(" ".join(buf).strip())
    # Merge tiny trailing chunks.
    out: list[str] = []
    for c in chunks:
        if out and len(enc.encode(out[-1])) < _TARGET_MIN:
            out[-1] = (out[-1] + " " + c).strip()
        else:
            out.append(c)
    return out


def chunk_sections(sections: list[ParsedSection]) -> list[Chunk]:
    out: list[Chunk] = []
    seq = 0
    enc = _enc()
    for s in sections:
        pieces = [s.raw_text] if len(enc.encode(s.raw_text)) <= _TARGET_MAX \
            else _split_recursive(s.raw_text, _TARGET_MAX)
        for p in pieces:
            seq += 1
            out.append(
                Chunk(
                    section_path=s.section_path,
                    section_type=s.section_type,
                    chunk_seq=seq,
                    text=p,
                    source_file=s.source_file,
                )
            )
    return out
