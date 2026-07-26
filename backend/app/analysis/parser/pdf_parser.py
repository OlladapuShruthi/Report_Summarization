import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List


@dataclass
class PDFExtractionResult:
    success: bool
    extracted_text: str
    extracted_tables: List[List[List[str]]] = field(default_factory=list)
    page_count: int = 0
    text_density: float = 0.0
    is_digital_pdf: bool = False
    extraction_method: str = "pdf"
    warnings: List[str] = field(default_factory=list)
    processing_time_ms: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


class PDFParser:
    def __init__(self, digital_density_threshold: float = 50.0):
        self.digital_density_threshold = digital_density_threshold

    def parse(self, file_path: str) -> PDFExtractionResult:
        start_time = time.perf_counter()
        path = Path(file_path)
        warnings: List[str] = []

        if not path.exists():
            raise FileNotFoundError(f"PDF file not found: {file_path}")

        if path.suffix.lower() != ".pdf":
            raise ValueError(f"Expected a PDF file, received: {path.suffix or 'unknown'}")

        try:
            text, page_count, tables = self._extract_with_pdfplumber(path)
        except ImportError:
            warnings.append("pdfplumber is not installed; used plain-text fallback.")
            text = self._plain_text_fallback(path)
            page_count = 1 if text else 0
            tables = []
        except Exception as exc:
            warnings.append(f"pdfplumber extraction failed: {exc}")
            text = self._plain_text_fallback(path)
            page_count = 1 if text else 0
            tables = []

        text_density = self.calculate_text_density(text, page_count)

        return PDFExtractionResult(
            success=True,
            extracted_text=text,
            extracted_tables=tables,
            page_count=page_count,
            text_density=text_density,
            is_digital_pdf=self.is_digital_pdf(text_density),
            warnings=warnings,
            processing_time_ms=int((time.perf_counter() - start_time) * 1000),
            metadata={"source_file": str(path), "file_size": path.stat().st_size},
        )

    def extract_text(self, file_path: str) -> str:
        return self.parse(file_path).extracted_text

    def extract_tables(self, file_path: str) -> List[List[List[str]]]:
        return self.parse(file_path).extracted_tables

    def calculate_text_density(self, text: str, page_count: int) -> float:
        if page_count <= 0:
            return 0.0
        return len((text or "").strip()) / page_count

    def is_digital_pdf(self, text_density: float) -> bool:
        return text_density >= self.digital_density_threshold

    def _extract_with_pdfplumber(self, path: Path) -> tuple[str, int, List[List[List[str]]]]:
        import pdfplumber

        page_texts: List[str] = []
        all_tables: List[List[List[str]]] = []

        with pdfplumber.open(str(path)) as pdf:
            for page in pdf.pages:
                page_texts.append(page.extract_text() or "")
                for table in page.extract_tables() or []:
                    normalized_table = [
                        [cell or "" for cell in row]
                        for row in table
                        if row
                    ]
                    if normalized_table:
                        all_tables.append(normalized_table)

            return "\n".join(page_texts).strip(), len(pdf.pages), all_tables

    def _plain_text_fallback(self, path: Path) -> str:
        return path.read_bytes().decode("utf-8", errors="ignore").strip()
