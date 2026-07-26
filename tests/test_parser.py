import os
import sys

backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.analysis.parser.deterministic_parser import DeterministicParser
from app.analysis.parser.parsing_service import ParsingService
from app.analysis.parser.report_classifier import ReportClassifier
from app.analysis.parser.text_cleaner import TextCleaner
from app.analysis.parser.validator import MedicalJSONValidator


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
    assert results[0]["reference_range"] == {"low": 13.5, "high": 17.5}


def test_medical_json_validator_accepts_schema_v1():
    data = {
        "schema_version": "1.0",
        "report_type": "LAB_REPORT_CBC",
        "patient_metadata": {},
        "lab_results": [{"test_name": "Hemoglobin", "value": 10.2, "unit": "g/dL"}],
        "narrative_impressions": [],
        "confidence": {"overall": 0.9},
        "parser_metadata": {},
    }

    validated = MedicalJSONValidator().validate(data)

    assert validated["schema_version"] == "1.0"
    assert validated["lab_results"][0]["test_name"] == "Hemoglobin"


def test_parsing_service_builds_medical_json_from_plain_text_pdf(tmp_path):
    report_path = tmp_path / "cbc_report.pdf"
    report_path.write_text(
        "Complete Blood Count Report\n"
        "Hemoglobin 10.2 g/dL 13.5-17.5\n"
        "WBC 6200 cells/uL 4000-11000\n"
        "Platelets 250000 cells/uL 150000-450000\n",
        encoding="utf-8",
    )

    result = ParsingService().parse_document(str(report_path))

    assert result.parsed_json["schema_version"] == "1.0"
    assert result.parsed_json["report_type"] == "LAB_REPORT_CBC"
    assert len(result.parsed_json["lab_results"]) >= 3
