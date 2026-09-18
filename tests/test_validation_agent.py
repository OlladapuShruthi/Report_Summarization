import asyncio
import os
import sys

backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.analysis.agents.validation_agent import ValidationAgent


def test_validation_agent_passes_consistent_summary():
    state = {
        "analysis_id": "analysis-1",
        "abnormal_findings": [
            {"test_name": "Hemoglobin", "status": "LOW", "severity": "Mild", "category": "Hematology"}
        ],
        "risk_assessment": {"risk_level": "MODERATE"},
        "consultation": {"consultation_required": True, "recommended_specialist": "Physician"},
        "summary": {"text": "Hemoglobin is low. Overall risk appears moderate. A consultation with a physician is recommended."},
        "execution_log": [],
        "retry_count": 0,
    }

    updated_state = asyncio.run(ValidationAgent().process(state))

    assert updated_state["validation"]["passed"] is True
    assert updated_state["status"] == "validated"


def test_validation_agent_flags_missing_facts():
    state = {
        "analysis_id": "analysis-2",
        "abnormal_findings": [
            {"test_name": "Hemoglobin", "status": "LOW", "severity": "Mild", "category": "Hematology"}
        ],
        "risk_assessment": {"risk_level": "MODERATE"},
        "consultation": {"consultation_required": True, "recommended_specialist": "Physician"},
        "summary": {"text": "Overall risk appears high."},
        "execution_log": [],
        "retry_count": 0,
    }

    updated_state = asyncio.run(ValidationAgent().process(state))

    assert updated_state["validation"]["passed"] is False
    assert updated_state["retry_count"] == 1


def test_validation_agent_requires_source_fact_traceability():
    state = {
        "analysis_id": "analysis-3",
        "parsed_json": {
            "lab_results": [
                {
                    "test_name": "Hemoglobin",
                    "value": 10.2,
                    "unit": "g/dL",
                    "reference_range": {"low": 13.5, "high": 17.5},
                }
            ]
        },
        "abnormal_findings": [{"test_name": "Hemoglobin", "status": "LOW"}],
        "risk_assessment": {"risk_level": "MODERATE"},
        "consultation": {},
        "summary": {"text": "Hemoglobin is low. Overall risk appears moderate."},
        "execution_log": [],
        "retry_count": 0,
    }

    updated_state = asyncio.run(ValidationAgent().process(state))

    assert updated_state["validation"]["passed"] is False
    assert "source facts" in " ".join(updated_state["validation"]["issues"])


def test_validation_agent_rejects_unknown_finding_claimed_as_normal():
    state = {
        "analysis_id": "analysis-4",
        "parsed_json": {},
        "abnormal_findings": [],
        "risk_assessment": {},
        "consultation": {},
        "comparison_context": {
            "comparisons": [{"test_name": "Hemoglobin", "finding_status": "UNKNOWN"}]
        },
        "summary": {
            "text": "Hemoglobin is normal.",
            "source_facts": [],
        },
        "execution_log": [],
        "retry_count": 0,
    }

    updated_state = asyncio.run(ValidationAgent().process(state))

    assert updated_state["validation"]["passed"] is False
    assert "invents resolution" in " ".join(updated_state["validation"]["issues"])