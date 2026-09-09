from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

from app.analysis.parser.deterministic_parser import DeterministicParser
from app.analysis.parser.json_builder import MedicalJSONBuilder
from app.analysis.parser.llm_structurer import LLMStructurer
from app.analysis.parser.medspacy_parser import MedSpaCyParser
from app.analysis.parser.narrative_parser import NarrativeParser
from app.analysis.parser.ocr_parser import OCRParser
from app.analysis.parser.patient_metadata_extractor import PatientMetadataExtractor
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
        self.patient_metadata_extractor = PatientMetadataExtractor()
        self.text_cleaner = TextCleaner()
        self.report_classifier = ReportClassifier()
        self.deterministic_parser = DeterministicParser()
        self.narrative_parser = NarrativeParser()
        self.medspacy_parser = MedSpaCyParser()
        self.llm_structurer = LLMStructurer()
        self.json_builder = MedicalJSONBuilder()
        self.validator = MedicalJSONValidator()

    def parse_document(self, file_path: str) -> ParsingResult:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Uploaded file does not exist: {file_path}")

        raw_text, extraction_metadata = self._extract_text(path)
        cleaned_text = self.text_cleaner.clean(raw_text)
        patient_metadata = self.patient_metadata_extractor.extract(cleaned_text)
        classification = self.report_classifier.classify(cleaned_text)

        lab_results = []
        narrative_impressions = []
        medspacy_result = None

        if classification.report_type.startswith("LAB_REPORT"):
            lab_results = self.deterministic_parser.parse_tables(extraction_metadata.get("tables") or [])
            if not lab_results:
                lab_results = self.deterministic_parser.parse(cleaned_text)
        elif classification.report_type in {"RADIOLOGY_REPORT", "DISCHARGE_SUMMARY"}:
            medspacy_result = self.medspacy_parser.process(cleaned_text)
            narrative_impressions = self._build_narrative_impressions(cleaned_text, medspacy_result)
        else:
            medspacy_result = self.medspacy_parser.process(cleaned_text)
            narrative_impressions = self._build_narrative_impressions(cleaned_text, medspacy_result)
            if not narrative_impressions:
                lab_results = self.deterministic_parser.parse(cleaned_text)

        llm_fallback_used = False
        if not lab_results and not narrative_impressions:
            if not self.llm_structurer.enabled:
                raise ValueError("No supported medical measurements or narrative findings were extracted")
            try:
                llm_data = self.llm_structurer.extract(cleaned_text, classification.report_type)
                lab_results = llm_data.get("lab_results") or []
                narrative_impressions = llm_data.get("narrative_impressions") or []
                if not lab_results and not narrative_impressions:
                    raise ValueError("LLM returned no supported medical content")
                llm_fallback_used = True
            except Exception as exc:
                raise ValueError(f"Structured extraction failed: {exc}") from exc

        review_reasons = []
        if extraction_metadata.get("warnings"):
            review_reasons.append("document_extraction_warning")
        if classification.confidence < 0.5:
            review_reasons.append("low_report_classification_confidence")
        if classification.report_type == "UNKNOWN":
            review_reasons.append("unknown_report_type")
        if medspacy_result and not medspacy_result.available:
            review_reasons.append("medspacy_unavailable")
        if medspacy_result and medspacy_result.warnings:
            review_reasons.append("medspacy_processing_warning")
        if llm_fallback_used:
            review_reasons.append("llm_structuring_fallback")

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
            "parser_version": "1.0.0",
            "llm_used": llm_fallback_used,
            "medspacy_used": bool(medspacy_result and medspacy_result.available),
            "medspacy_warnings": medspacy_result.warnings if medspacy_result else [],
            "review_required": bool(review_reasons),
            "review_reasons": review_reasons,
        }

        medical_json = self.json_builder.build(
            report_type=classification.report_type,
            lab_results=lab_results,
            narrative_impressions=narrative_impressions,
            patient_metadata=patient_metadata,
            confidence={
                "text_extraction": self._compute_text_extraction_confidence(extraction_metadata, bool(cleaned_text)),
                "classification": classification.confidence,
                "entity_extraction": self._compute_entity_extraction_confidence(lab_results, narrative_impressions),
                "overall": self._compute_overall_confidence(
                    extraction_metadata,
                    classification.confidence,
                    bool(cleaned_text),
                    bool(lab_results or narrative_impressions),
                ),
            },
            parser_metadata=parser_metadata,
        )

        return ParsingResult(
            raw_text=raw_text,
            cleaned_text=cleaned_text,
            parsed_json=self.validator.validate(medical_json),
            parser_metadata=parser_metadata,
        )

    def _build_narrative_impressions(self, text: str, medspacy_result: Any) -> list[Dict[str, str]]:
        if medspacy_result and medspacy_result.sections:
            return medspacy_result.sections
        return self.narrative_parser.parse(text)

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
                "ocr_used": False,
                "tables": pdf_result.extracted_tables,
            }

            if pdf_result.is_digital_pdf:
                return pdf_result.extracted_text, metadata

            ocr_result = self.ocr_parser.extract_text(str(path))
            metadata["ocr"] = {
                "success": ocr_result.success,
                "warnings": ocr_result.warnings,
                "processing_time_ms": ocr_result.processing_time_ms,
            }
            metadata["ocr_used"] = True
            return ocr_result.extracted_text or pdf_result.extracted_text, metadata

        ocr_result = self.ocr_parser.extract_text(str(path))
        return ocr_result.extracted_text, {
            "extraction_method": "ocr",
            "warnings": ocr_result.warnings,
            "processing_time_ms": ocr_result.processing_time_ms,
            "ocr_used": True,
        }

    def _compute_overall_confidence(
        self,
        extraction_metadata: Dict[str, Any],
        classification_confidence: float,
        has_text: bool,
        has_structured_data: bool,
    ) -> float:
        score = classification_confidence
        if has_text:
            score += 0.15
        if has_structured_data:
            score += 0.2
        if extraction_metadata.get("warnings"):
            score -= 0.1
        return round(min(score, 0.98), 2)

    def _compute_text_extraction_confidence(self, extraction_metadata: Dict[str, Any], has_text: bool) -> float:
        if not has_text:
            return 0.0
        if extraction_metadata.get("ocr_used"):
            return 0.75
        if extraction_metadata.get("warnings"):
            return 0.8
        return 0.99

    def _compute_entity_extraction_confidence(
        self,
        lab_results: list[Dict[str, Any]],
        narrative_impressions: list[Dict[str, Any]],
    ) -> float:
        structured_count = len(lab_results) + len(narrative_impressions)
        if structured_count == 0:
            return 0.0
        return round(min(0.98, 0.7 + structured_count * 0.04), 2)
