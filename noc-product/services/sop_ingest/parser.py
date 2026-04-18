"""PDF/Word SOP parser — E6a §2.1 / E5 §3.1.

Primary: `unstructured[pdf]` for layout-aware parsing of
typical SOPs. Fallback: `pdfminer.six` when unstructured
returns empty text. Word: `python-docx`. OCR via
`pytesseract` on image-only pages is best-effort.

Returns a list of ParsedSection dicts consumable by the
chunker.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class ParsedSection:
    section_path: str
    section_type: str
    raw_text: str
    source_file: str
    page_range: tuple[int, int] | None = None


def _parse_docx(path: Path) -> list[ParsedSection]:
    try:
        from docx import Document  # lazy import
    except ImportError:
        return []
    doc = Document(str(path))
    sections: list[ParsedSection] = []
    cur_heading = "Untitled"
    buf: list[str] = []
    for p in doc.paragraphs:
        style = (p.style.name or "").lower() if p.style else ""
        if style.startswith("heading"):
            if buf:
                sections.append(
                    ParsedSection(
                        section_path=cur_heading,
                        section_type=_guess_section_type(cur_heading),
                        raw_text="\n".join(buf).strip(),
                        source_file=path.name,
                    )
                )
            cur_heading = p.text.strip() or cur_heading
            buf = []
        elif p.text.strip():
            buf.append(p.text.strip())
    if buf:
        sections.append(
            ParsedSection(
                section_path=cur_heading,
                section_type=_guess_section_type(cur_heading),
                raw_text="\n".join(buf).strip(),
                source_file=path.name,
            )
        )
    return [s for s in sections if s.raw_text]


def _parse_pdf_unstructured(path: Path) -> list[ParsedSection]:
    try:
        from unstructured.partition.pdf import partition_pdf
    except ImportError:
        return []
    try:
        elements = partition_pdf(
            filename=str(path),
            strategy="fast",
            infer_table_structure=False,
        )
    except Exception:  # noqa: BLE001
        return []
    sections: list[ParsedSection] = []
    cur_heading = path.stem
    buf: list[str] = []
    page_start = 1
    cur_page = 1
    for el in elements:
        kind = el.__class__.__name__
        meta = getattr(el, "metadata", None)
        cur_page = getattr(meta, "page_number", cur_page) or cur_page
        if kind in {"Title", "Header"}:
            if buf:
                sections.append(
                    ParsedSection(
                        section_path=cur_heading,
                        section_type=_guess_section_type(cur_heading),
                        raw_text="\n".join(buf).strip(),
                        source_file=path.name,
                        page_range=(page_start, cur_page),
                    )
                )
            cur_heading = (el.text or cur_heading).strip()[:200]
            buf = []
            page_start = cur_page
        else:
            t = (el.text or "").strip()
            if t:
                buf.append(t)
    if buf:
        sections.append(
            ParsedSection(
                section_path=cur_heading,
                section_type=_guess_section_type(cur_heading),
                raw_text="\n".join(buf).strip(),
                source_file=path.name,
                page_range=(page_start, cur_page),
            )
        )
    return [s for s in sections if s.raw_text]


def _parse_pdf_pdfminer(path: Path) -> list[ParsedSection]:
    try:
        from pdfminer.high_level import extract_text
    except ImportError:
        return []
    try:
        txt = extract_text(str(path)) or ""
    except Exception:  # noqa: BLE001
        return []
    if not txt.strip():
        return []
    # Very coarse fallback — whole doc as one section.
    return [
        ParsedSection(
            section_path=path.stem,
            section_type="overview",
            raw_text=txt.strip(),
            source_file=path.name,
        )
    ]


def _guess_section_type(heading: str) -> str:
    h = (heading or "").lower()
    if any(k in h for k in ("remediat", "resolve", "fix", "restore", "action")):
        return "remediation"
    if any(k in h for k in ("pre-condition", "precondition", "prerequisite")):
        return "precondition"
    if any(k in h for k in ("escalat", "handover", "incident severity")):
        return "escalation"
    if any(k in h for k in ("reference", "see also", "glossary")):
        return "reference"
    if any(k in h for k in ("overview", "scope", "purpose", "introduction")):
        return "overview"
    return "other"


def parse_sop(path: Path | str) -> list[ParsedSection]:
    p = Path(path)
    suffix = p.suffix.lower()
    if suffix == ".docx":
        return _parse_docx(p)
    if suffix == ".pdf":
        got = _parse_pdf_unstructured(p)
        if got:
            return got
        return _parse_pdf_pdfminer(p)
    if suffix in (".md", ".txt"):
        txt = p.read_text(encoding="utf-8")
        return [
            ParsedSection(
                section_path=p.stem,
                section_type="overview",
                raw_text=txt,
                source_file=p.name,
            )
        ]
    return []
