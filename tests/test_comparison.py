import os
import sys

backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.analysis.comparison.comparison_service import ComparisonService


def lab(value, low=13.5, high=17.5):
    return {"test_name": "Hemoglobin", "value": value, "unit": "g/dL", "reference_range": {"low": low, "high": high}}


def report(value, date):
    return {"created_at": date, "parsed_json": {"lab_results": [lab(value)]}}


def test_comparison_identifies_persistent_improvement():
    context = ComparisonService().build_context({"lab_results": [lab(12.4)]}, [report(10.2, "2026-01-10")])
    comparison = context["comparisons"][0]

    assert comparison["previous_status"] == "LOW"
    assert comparison["current_status"] == "LOW"
    assert comparison["trend"] == "INCREASING"
    assert comparison["finding_status"] == "PERSISTENT_IMPROVING"
    assert comparison["history"][-1]["date"] == "current"


def test_comparison_identifies_resolved_and_new_findings():
    resolved = ComparisonService().build_context({"lab_results": [lab(14.0)]}, [report(10.2, "2026-01-10")])["comparisons"][0]
    new = ComparisonService().build_context({"lab_results": [lab(10.2)]}, [report(14.0, "2026-01-10")])["comparisons"][0]

    assert resolved["finding_status"] == "RESOLVED"
    assert new["finding_status"] == "NEW_ABNORMAL"


def test_comparison_matches_catalog_aliases_but_never_converts_units():
    current = {"test_name": "HGB", "value": 12.4, "unit": "g/dL", "reference_range": {"low": 13.5, "high": 17.5}}
    historic = {"created_at": "2026-01-10", "parsed_json": {"lab_results": [{"test_name": "Hemoglobin", "value": 10.2, "unit": "g/dL", "reference_range": {"low": 13.5, "high": 17.5}}]}}
    comparison = ComparisonService().build_context({"lab_results": [current]}, [historic])["comparisons"][0]

    assert comparison["canonical_test_name"] == "hemoglobin"
    assert comparison["comparison_method"] == "catalog_alias_and_unit"
    assert comparison["previous_value"] == 10.2


def test_comparison_identifies_persistent_worsening_multi_report_trend():
    prior_reports = [
        report(11.2, "2026-01-15"),
        report(10.8, "2026-04-15"),
    ]
    context = ComparisonService().build_context({"lab_results": [lab(10.2)]}, prior_reports, current_report_date="2026-07-15")
    comparison = context["comparisons"][0]

    assert comparison["previous_value"] == 10.8
    assert comparison["current_value"] == 10.2
    assert comparison["previous_status"] == "LOW"
    assert comparison["current_status"] == "LOW"
    assert comparison["trend"] == "DECREASING"
    assert comparison["finding_status"] == "PERSISTENT_WORSENING"
    assert len(comparison["history"]) == 3
    assert comparison["history"][0]["value"] == 11.2
    assert comparison["history"][1]["value"] == 10.8
    assert comparison["history"][2]["value"] == 10.2

