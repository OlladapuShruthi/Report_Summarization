from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

from app.analysis.parser.deterministic_parser import DeterministicParser
from app.analysis.parser.json_builder import MedicalJSONBuilder
from app.analysis.parser.narrative_parser import NarrativeParser
from app.analysis.parser.ocr_parser import OCRParser
from app.analysis.parser.pdf_parser import PDFParser
from app.analysis.parser.report_classifier import ReportClassifier
from app.analysis.parser.text_cleaner import TextCleaner
from app.analysis.parser.validator import MedicalJSONValidator


@dataclass
class ParsingResult:
    raw_text: str
    cleaned_text: str
    parsed_json: Dict[str, Any]
    parser_metadata: Dict[str, Any]


class ParsingService:
    def __init__(self):
        self.pdf_parser = PDFParser()
        self.ocr_parser = OCRParser()
        self.text_cleaner = TextCleaner()
        self.report_classifier = ReportClassifier()
        self.deterministic_parser = DeterministicParser()
        self.narrative_parser = NarrativeParser()
        self.json_builder = MedicalJSONBuilder()
        self.validator = MedicalJSONValidator()

    def parse_document(self, file_path: str) -> ParsingResult:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Uploaded file does not exist: {file_path}")

        raw_text, extraction_metadata = self._extract_text(path)
        cleaned_text = self.text_cleaner.clean(raw_text)
        classification = self.report_classifier.classify(cleaned_text)

        lab_results = []
        narrative_impressions = []

        if classification.report_type.startswith("LAB_REPORT"):
            lab_results = self.deterministic_parser.parse(cleaned_text)
        elif classification.report_type in {"RADIOLOGY_REPORT", "DISCHARGE_SUMMARY"}:
            narrative_impressions = self.narrative_parser.parse(cleaned_text)
        else:
            lab_results = self.deterministic_parser.parse(cleaned_text)
            if not lab_results:
                narrative_impressions = self.narrative_parser.parse(cleaned_text)

        parser_metadata = {
            **extraction_metadata,
            "classification": {
                "report_type": classification.report_type,
                "confidence": classification.confidence,
                "matched_keywords": classification.matched_keywords,
                "scores": classification.scores,
            },
            "lab_result_count": len(lab_results),
            "narrative_impression_count": len(narrative_impressions),
        }

        medical_json = self.json_builder.build(
            report_type=classification.report_type,
            lab_results=lab_results,
            narrative_impressions=narrative_impressions,
            confidence={
                "overall": self._compute_confidence(
                    classification.confidence,
                    bool(cleaned_text),
                    bool(lab_results or narrative_impressions),
                ),
                "classification": classification.confidence,
            },
            parser_metadata=parser_metadata,
        )

        return ParsingResult(
            raw_text=raw_text,
            cleaned_text=cleaned_text,
            parsed_json=self.validator.validate(medical_json),
            parser_metadata=parser_metadata,
        )

    def _extract_text(self, path: Path) -> tuple[str, Dict[str, Any]]:
        if path.suffix.lower() == ".pdf":
            pdf_result = self.pdf_parser.parse(str(path))
            metadata = {
                "extraction_method": "pdf",
                "page_count": pdf_result.page_count,
                "text_density": pdf_result.text_density,
                "is_digital_pdf": pdf_result.is_digital_pdf,
                "warnings": pdf_result.warnings,
                "processing_time_ms": pdf_result.processing_time_ms,
            }

            if pdf_result.is_digital_pdf:
                return pdf_result.extracted_text, metadata

            ocr_result = self.ocr_parser.extract_text(str(path))
            metadata["ocr"] = {
                "success": ocr_result.success,
                "warnings": ocr_result.warnings,
                "processing_time_ms": ocr_result.processing_time_ms,
            }
            return ocr_result.extracted_text or pdf_result.extracted_text, metadata

        ocr_result = self.ocr_parser.extract_text(str(path))
        return ocr_result.extracted_text, {
            "extraction_method": "ocr",
            "warnings": ocr_result.warnings,
            "processing_time_ms": ocr_result.processing_time_ms,
        }

    def _compute_confidence(self, classification_confidence: float, has_text: bool, has_structured_data: bool) -> float:
        score = classification_confidence
        if has_text:
            score += 0.15
        if has_structured_data:
            score += 0.2
        return round(min(score, 0.98), 2)
