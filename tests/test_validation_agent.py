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