import asyncio
import os
import sys

backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.analysis.agents.consult_agent import ConsultAgent


def test_consult_agent_recommends_physician_for_moderate_risk():
    state = {
        "analysis_id": "analysis-1",
        "abnormal_findings": [
            {"test_name": "Hemoglobin", "status": "LOW", "severity": "Mild", "category": "Hematology"},
            {"test_name": "RBC", "status": "LOW", "severity": "Moderate", "category": "Hematology"},
        ],
        "risk_assessment": {"risk_level": "MODERATE"},
        "execution_log": [],
        "retry_count": 0,
    }

    updated_state = asyncio.run(ConsultAgent().process(state))

    assert updated_state["consultation"]["consultation_required"] is True
    assert updated_state["consultation"]["recommended_specialist"] == "Physician"
    assert updated_state["consultation"]["urgency"] == "Routine"


def test_consult_agent_skips_consult_for_low_risk():
    state = {
        "analysis_id": "analysis-2",
        "abnormal_findings": [],
        "risk_assessment": {"risk_level": "LOW"},
        "execution_log": [],
        "retry_count": 0,
    }

    updated_state = asyncio.run(ConsultAgent().process(state))

    assert updated_state["consultation"]["consultation_required"] is False
    assert updated_state["consultation"]["recommended_specialist"] == "None"