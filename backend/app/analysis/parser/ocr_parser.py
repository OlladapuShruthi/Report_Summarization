import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List


@dataclass
class OCRExtractionResult:
    success: bool
    extracted_text: str
    extraction_method: str = "ocr"
    warnings: List[str] = field(default_factory=list)
    processing_time_ms: int = 0
    metadata: Dict[str, str] = field(default_factory=dict)


class OCRParser:
    def extract_text(self, file_path: str) -> OCRExtractionResult:
        start_time = time.perf_counter()
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"OCR source file not found: {file_path}")

        warnings: List[str] = []
        text = ""

        try:
            if path.suffix.lower() == ".pdf":
                text = self._extract_pdf_text(path)
            else:
                text = self._extract_image_text(path)
        except ImportError as exc:
            warnings.append(f"OCR dependency missing: {exc}")
        except Exception as exc:
            warnings.append(f"OCR extraction failed: {exc}")

        return OCRExtractionResult(
            success=bool(text.strip()),
            extracted_text=text.strip(),
            warnings=warnings,
            processing_time_ms=int((time.perf_counter() - start_time) * 1000),
            metadata={"source_file": str(path)},
        )

    def _extract_image_text(self, path: Path) -> str:
        from PIL import Image
        import pytesseract

        with Image.open(path) as image:
            return pytesseract.image_to_string(image)

    def _extract_pdf_text(self, path: Path) -> str:
        from pdf2image import convert_from_path
        import pytesseract

        images = convert_from_path(str(path))
        return "\n".join(pytesseract.image_to_string(image) for image in images)
