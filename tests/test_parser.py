import os
import sys

backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.analysis.parser.deterministic_parser import DeterministicParser
from app.analysis.parser.json_builder import MedicalJSONBuilder
from app.analysis.parser.patient_metadata_extractor import PatientMetadataExtractor
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
    assert results[0]["reference_range"] == {"low": 13.5, "high": 17.5, "text": "13.5 - 17.5"}
    assert results[0]["category"] == "Hematology"
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


def test_parsing_service_builds_medical_json_from_plain_text_pdf(tmp_path):
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

    result = ParsingService().parse_document(str(report_path))

    assert result.parsed_json["schema_version"] == "1.0"
    assert result.parsed_json["report_type"] == "LAB_REPORT_CBC"
    assert result.parsed_json["patient_metadata"]["name"] == "Rahul Sharma"
    assert result.parsed_json["patient_metadata"]["age"] == 32
    assert result.parsed_json["confidence"]["text_extraction"] > 0
    assert result.parsed_json["confidence"]["entity_extraction"] > 0
    assert result.parsed_json["parser_metadata"]["parser_version"] == "1.0.0"
    assert result.parsed_json["parser_metadata"]["ocr_used"] is False
    assert result.parsed_json["parser_metadata"]["llm_used"] is False
    assert len(result.parsed_json["lab_results"]) >= 3
