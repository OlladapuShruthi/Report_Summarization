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
    assert comparison["lifecycle_state"] == "IMPROVING"
    assert comparison["history"][-1]["date"] == "current"


def test_comparison_identifies_resolved_and_new_findings():
    resolved = ComparisonService().build_context({"lab_results": [lab(14.0)]}, [report(10.2, "2026-01-10")])["comparisons"][0]
    new = ComparisonService().build_context({"lab_results": [lab(10.2)]}, [report(14.0, "2026-01-10")])["comparisons"][0]

    assert resolved["finding_status"] == "CURRENTLY_NORMAL"
    assert resolved["lifecycle_state"] == "CURRENTLY_NORMAL"
    assert new["finding_status"] == "NEW_ABNORMAL"
    assert new["lifecycle_state"] == "ACTIVE"


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
    assert comparison["lifecycle_state"] == "WORSENED"
    assert len(comparison["history"]) == 3
    assert comparison["history"][0]["value"] == 11.2
    assert comparison["history"][1]["value"] == 10.8
    assert comparison["history"][2]["value"] == 10.2


def test_comparison_preserves_source_report_ids_for_history_evidence():
    prior_reports = [
        {"analysis_id": "jan-cbc", **report(10.2, "2026-01-10")},
        {"report_id": "apr-cbc", **report(11.1, "2026-04-10")},
    ]

    comparison = ComparisonService().build_context(
        {"lab_results": [lab(12.4)]},
        prior_reports,
        current_report_date="2026-07-10",
        current_report_id="jul-cbc",
    )["comparisons"][0]

    assert [entry["report_id"] for entry in comparison["history"]] == ["jan-cbc", "apr-cbc", "jul-cbc"]
    assert all(entry["evidence_type"] == "LAB_REPORT" for entry in comparison["history"])

    events = ComparisonService().build_context(
        {"lab_results": [lab(12.4)]},
        prior_reports,
        current_report_date="2026-07-10",
        current_report_id="jul-cbc",
    )["finding_events"]
    assert [event["report_id"] for event in events] == ["jan-cbc", "apr-cbc", "jul-cbc"]
    assert all(event["finding_id"] == "hemoglobin|g/dl" for event in events)
    assert events[-1]["is_current"] is True


def test_normal_followup_is_currently_normal_not_clinically_resolved():
    current = {
        "lab_results": [lab(13.8, low=13.5, high=17.5)],
        "patient_metadata": {"report_date": "2026-03-10"},
    }
    previous = {
        "analysis_id": "jan-cbc",
        "parsed_json": {
            "patient_metadata": {"report_date": "2026-01-10"},
            "lab_results": [lab(10.2)],
        },
    }

    comparison = ComparisonService().build_context(current, [previous], "2026-03-10")["comparisons"][0]

    assert comparison["current_status"] == "NORMAL"
    assert comparison["finding_status"] == "CURRENTLY_NORMAL"
    assert comparison["evidence_type"] == "LAB_REPORT"
    assert comparison["lifecycle_state"] == "CURRENTLY_NORMAL"


def test_missing_followup_measurement_is_unknown_with_historical_evidence():
    lipid_only_current = {
        "lab_results": [
            {
                "test_name": "Total Cholesterol",
                "value": 180,
                "unit": "mg/dL",
                "reference_range": {"low": 0, "high": 200},
            }
        ],
        "patient_metadata": {"report_date": "2026-03-10"},
    }
    previous = {
        "analysis_id": "jan-cbc",
        "parsed_json": {
            "patient_metadata": {"report_date": "2026-01-10"},
            "lab_results": [lab(10.2)],
        },
    }

    context = ComparisonService().build_context(lipid_only_current, [previous], "2026-03-10")
    hemoglobin = next(item for item in context["comparisons"] if item["test_name"] == "Hemoglobin")

    assert hemoglobin["current_status"] == "UNKNOWN"
    assert hemoglobin["finding_status"] == "UNKNOWN"
    assert hemoglobin["lifecycle_state"] == "UNKNOWN"
    assert hemoglobin["current_value"] is None
    assert hemoglobin["uncertainty_reason"] == "measurement_not_present_in_current_report"
    assert hemoglobin["history"][0]["report_id"] == "jan-cbc"

