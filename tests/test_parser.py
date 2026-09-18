import os
import shutil
import sys
from pathlib import Path

import pytest

backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.analysis.parser.deterministic_parser import DeterministicParser
from app.analysis.parser.json_builder import MedicalJSONBuilder
from app.analysis.parser.medspacy_parser import MedSpaCyParser
from app.analysis.parser.llm_structurer import LLMStructurer
from app.analysis.parser.ocr_parser import OCRParser
from app.analysis.parser.patient_metadata_extractor import PatientMetadataExtractor
from app.analysis.parser.parsing_service import ParsingService
from app.analysis.parser.report_classifier import ReportClassifier
from app.analysis.parser.text_cleaner import TextCleaner
from app.analysis.parser.validator import MedicalJSONValidator


class FakeStructuredClient:
    enabled = True
    model = "fake-medical-model"

    def __init__(self, response):
        self.response = response

    def chat_completion_sync(self, messages, temperature=0.0):
        return self.response


def test_text_cleaner_normalizes_spacing_and_units():
    text = "Hemoglobin   10.2   g / dL\n\n\nPage 1"
    cleaned = TextCleaner().clean(text)

    assert cleaned == "Hemoglobin 10.2 g/dL"


def test_report_classifier_detects_cbc_report():
    result = ReportClassifier().classify("Hemoglobin 10.2 g/dL\nWBC 6200\nPlatelet Count 250000")

    assert result.report_type == "LAB_REPORT_CBC"
    assert result.confidence > 0.5


def test_deterministic_parser_extracts_lab_values():
    results = DeterministicParser().parse("Hemoglobin 10.2 g/dL 13.5-17.5\nWBC 6200 cells/uL 4000-11000")

    assert len(results) == 2
    assert results[0]["test_name"] == "Hemoglobin"
    assert results[0]["value"] == 10.2
    assert results[0]["reference_range"] == {"low": 13.5, "high": 17.5, "text": "13.5 - 17.5"}
    assert results[0]["category"] == "Hematology"
    assert results[0]["is_outside_reference"] is True


def test_deterministic_parser_extracts_explicit_lab_table_rows():
    tables = [[
        ["Test", "Result", "Unit", "Reference Range"],
        ["Hemoglobin", "10.2", "g/dL", "13.5 - 17.5"],
        ["WBC", "8400", "cells/uL", "4000 - 11000"],
    ]]

    results = DeterministicParser().parse_tables(tables)

    assert [result["test_name"] for result in results] == ["Hemoglobin", "WBC"]
    assert results[0]["reference_range"] == {"low": 13.5, "high": 17.5, "text": "13.5 - 17.5"}
    assert results[0]["is_outside_reference"] is True


def test_patient_metadata_extractor_reads_demographics():
    text = "Patient Name: Rahul Sharma\nAge: 32\nGender: Male\nComplete Blood Count"
    metadata = PatientMetadataExtractor().extract(text)

    assert metadata == {"name": "Rahul Sharma", "age": 32, "gender": "Male"}


def test_medical_json_validator_accepts_schema_v1():
    data = {
        "schema_version": "1.0",
        "report_type": "LAB_REPORT_CBC",
        "patient_metadata": {},
        "lab_results": [
            {
                "test_name": "Hemoglobin",
                "value": 10.2,
                "unit": "g/dL",
                "reference_range": {"low": 13.5, "high": 17.5, "text": "13.5 - 17.5"},
                "category": "Hematology",
                "is_outside_reference": True,
            }
        ],
        "narrative_impressions": [],
        "confidence": {
            "text_extraction": 0.99,
            "classification": 0.95,
            "entity_extraction": 0.98,
            "overall": 0.97,
        },
        "parser_metadata": {},
    }

    validated = MedicalJSONValidator().validate(data)

    assert validated["schema_version"] == "1.0"
    assert validated["lab_results"][0]["test_name"] == "Hemoglobin"
    assert validated["confidence"]["text_extraction"] == 0.99
    assert validated["confidence"]["overall"] == 0.97


def test_medical_json_builder_populates_default_structure():
    medical_json = MedicalJSONBuilder().build(report_type="LAB_REPORT_CBC")

    assert medical_json["confidence"] == {
        "text_extraction": 0.0,
        "classification": 0.0,
        "entity_extraction": 0.0,
        "overall": 0.5,
    }
    assert medical_json["parser_metadata"]["parser_version"] == "1.0.0"
    assert medical_json["parser_metadata"]["ocr_used"] is False
    assert medical_json["parser_metadata"]["llm_used"] is False


def test_medical_json_validator_rejects_invalid_lab_value():
    data = {
        "schema_version": "1.0",
        "report_type": "LAB_REPORT_CBC",
        "patient_metadata": {},
        "lab_results": [{"test_name": "Hemoglobin", "value": -10.0, "unit": "g/dL"}],
        "narrative_impressions": [],
        "confidence": {"overall": 0.9},
        "parser_metadata": {},
    }

    try:
        MedicalJSONValidator().validate(data)
    except ValueError as exc:
        assert "value cannot be negative" in str(exc)
    else:
        raise AssertionError("validator accepted a negative lab value")


def test_medical_json_validator_rejects_invalid_unit():
    data = {
        "schema_version": "1.0",
        "report_type": "LAB_REPORT_CBC",
        "patient_metadata": {},
        "lab_results": [
            {
                "test_name": "Hemoglobin",
                "value": 10.2,
                "unit": "g/dL!!",
                "reference_range": {"low": 13.5, "high": 17.5, "text": "13.5 - 17.5"},
            }
        ],
        "narrative_impressions": [],
        "confidence": {"overall": 0.9},
        "parser_metadata": {},
    }

    try:
        MedicalJSONValidator().validate(data)
    except ValueError as exc:
        assert "invalid characters" in str(exc)
    else:
        raise AssertionError("validator accepted an invalid unit")


def test_parsing_service_rejects_plain_text_with_pdf_extension(tmp_path):
    report_path = tmp_path / "cbc_report.pdf"
    report_path.write_text(
        "Patient Name: Rahul Sharma\n"
        "Age: 32\n"
        "Gender: Male\n"
        "Complete Blood Count Report\n"
        "Hemoglobin 10.2 g/dL 13.5-17.5\n"
        "WBC 6200 cells/uL 4000-11000\n"
        "Platelets 250000 cells/uL 150000-450000\n",
        encoding="utf-8",
    )

    try:
        ParsingService().parse_document(str(report_path))
    except ValueError as exc:
        assert "valid PDF" in str(exc)
    else:
        raise AssertionError("parser accepted plain text with a PDF extension")


def test_narrative_cardio_report_does_not_become_a_lab_result():
    report_path = Path(__file__).parent.parent / "documents" / "uploads" / "91f29440-69b5-4991-ab9e-944375e791d7_OMC Report Sample - Cardio.pdf"

    result = ParsingService().parse_document(str(report_path))

    assert result.parsed_json["report_type"] != "LAB_REPORT_CBC"
    assert result.parsed_json["lab_results"] == []
    assert result.parsed_json["narrative_impressions"]


def test_real_sample_review_metadata_distinguishes_clean_and_uncertain_reports():
    parser = ParsingService()
    clean_report = parser.parse_document(
        str(Path(__file__).parent.parent / "documents" / "uploads" / "33b70989-729d-4bb6-a24a-ccbd31183833_Sample_CBC_Lab_Report.pdf")
    )

    assert clean_report.parser_metadata["review_required"] is False
    malformed_report = Path(__file__).parent.parent / "documents" / "uploads" / "0434356a-2806-458d-adf2-6fc2ee045b3e_quick_report.pdf"
    try:
        parser.parse_document(str(malformed_report))
    except ValueError as exc:
        assert "valid PDF" in str(exc)
    else:
        raise AssertionError("parser accepted malformed PDF bytes")


def test_medspacy_capability_is_reported_without_owning_numeric_extraction():
    result = MedSpaCyParser().process("Hemoglobin was low. Follow-up was recommended.")

    assert result.available is True
    assert result.sentences
    assert not result.sections or all("text" in section for section in result.sections)


def test_llm_structurer_validates_fenced_json_before_accepting_it():
    response = """```json
    {
      "schema_version": "1.0",
      "report_type": "LAB_REPORT_CBC",
      "patient_metadata": {},
      "lab_results": [{"test_name": "Hemoglobin", "value": 10.2, "unit": "g/dL", "reference_range": {"low": 13.5, "high": 17.5}}],
      "narrative_impressions": [],
      "confidence": {"overall": 0.6},
      "parser_metadata": {}
    }
    ```"""

    result = LLMStructurer(FakeStructuredClient(response)).extract("Hemoglobin 10.2 g/dL")

    assert result["lab_results"][0]["test_name"] == "Hemoglobin"
    assert result["parser_metadata"]["llm_used"] is True


def test_llm_structurer_rejects_non_json_and_schema_invalid_responses():
    for response in [
        "The hemoglobin is low.",
        '{"schema_version":"1.0","report_type":"LAB_REPORT_CBC","lab_results":[{"test_name":"Hemoglobin","value":-1}],"narrative_impressions":[]}',
    ]:
        with pytest.raises((ValueError, TypeError)):
            LLMStructurer(FakeStructuredClient(response)).extract("untrusted source")


@pytest.mark.skipif(
    not shutil.which("tesseract") or not shutil.which("pdftoppm"),
    reason="native Tesseract and Poppler are required for OCR integration",
)
def test_real_cbc_pdf_ocr_round_trip(tmp_path):
    from pdf2image import convert_from_path

    source = Path(__file__).parent.parent / "documents" / "uploads" / "33b70989-729d-4bb6-a24a-ccbd31183833_Sample_CBC_Lab_Report.pdf"
    image_path = tmp_path / "cbc_page.png"
    image = convert_from_path(str(source), first_page=1, last_page=1)[0]
    image.save(image_path)

    ocr_result = OCRParser().extract_text(str(image_path))

    assert ocr_result.success is True
    assert "Hemoglobin" in ocr_result.extracted_text
    assert "10.2" in ocr_result.extracted_text
