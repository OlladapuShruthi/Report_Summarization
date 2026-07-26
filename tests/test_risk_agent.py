import asyncio
import os
import sys

backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.analysis.agents.risk_agent import RiskAgent


def test_risk_agent_returns_low_for_single_mild_abnormality():
    state = {
        "analysis_id": "analysis-1",
        "abnormal_findings": [
            {"test_name": "Hemoglobin", "status": "LOW", "severity": "Mild", "category": "Hematology"}
        ],
        "execution_log": [],
        "retry_count": 0,
    }

    updated_state = asyncio.run(RiskAgent().process(state))

    assert updated_state["risk_assessment"]["risk_level"] == "LOW"
    assert updated_state["risk_assessment"]["abnormal_count"] == 1
    assert updated_state["status"] == "risk_assessed"


def test_risk_agent_escalates_multiple_abnormalities():
    state = {
        "analysis_id": "analysis-2",
        "abnormal_findings": [
            {"test_name": "Hemoglobin", "status": "LOW", "severity": "Mild", "category": "Hematology"},
            {"test_name": "RBC", "status": "LOW", "severity": "Moderate", "category": "Hematology"},
        ],
        "execution_log": [],
        "retry_count": 0,
    }

    updated_state = asyncio.run(RiskAgent().process(state))

    assert updated_state["risk_assessment"]["risk_level"] == "MODERATE"
    assert "Hematology" in " ".join(updated_state["risk_assessment"]["reasoning"])