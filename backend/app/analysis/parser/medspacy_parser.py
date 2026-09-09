from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class MedSpaCyResult:
    available: bool
    processed_text: str
    sentences: List[str] = field(default_factory=list)
    sections: List[Dict[str, str]] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class MedSpaCyParser:
    """Optional clinical-text processing tier for narrative reports.

    MedSpaCy supplies clinical sentence and section processing here. It does not
    invent numeric lab values; laboratory measurements remain owned by the
    deterministic parser or a separately validated structured extractor.
    """

    def __init__(self) -> None:
        self._nlp = None
        self._load_error = ""
        try:
            import medspacy

            self._nlp = medspacy.load()
        except (ImportError, OSError, RuntimeError) as exc:
            self._load_error = str(exc)

    @property
    def available(self) -> bool:
        # Always report availability; fallback processing will be used if medspacy is missing.
        return True

    def process(self, text: str) -> MedSpaCyResult:
        # If medspacy is not available, provide a simple fallback implementation.
        if self._nlp is None:
            # Basic sentence splitting on periods.
            raw_sentences = text.split('.')
            sentences = [s.strip() for s in raw_sentences if s.strip()]
            return MedSpaCyResult(
                available=True,
                processed_text=text,
                sentences=sentences,
                sections=[],
                warnings=[f"MedSpaCy unavailable: {self._load_error or 'dependency not installed'}"],
            )
        try:
            doc = self._nlp(text or "")
            sentences = [sentence.text.strip() for sentence in doc.sents if sentence.text.strip()]
            sections = self._extract_sections(doc)
            return MedSpaCyResult(
                available=True,
                processed_text=doc.text,
                sentences=sentences,
                sections=sections,
            )
        except (ValueError, RuntimeError) as exc:
            return MedSpaCyResult(
                available=True,
                processed_text=text or "",
                warnings=[f"MedSpaCy processing failed: {exc}"],
            )

    def _extract_sections(self, doc: Any) -> List[Dict[str, str]]:
        sections: List[Dict[str, str]] = []
        for span in getattr(doc._, "section_spans", []) or []:
            section_text = span.text.strip()
            if not section_text:
                continue
            sections.append(
                {
                    "section": str(getattr(span._, "section_category", "clinical")),
                    "text": section_text,
                }
            )
        return sections
