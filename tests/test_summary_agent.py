import asyncio
import os
import sys

backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.analysis.agents.summary_agent import SummaryAgent


def test_summary_agent_mentions_facts_and_advice():
    state = {
        "analysis_id": "analysis-1",
        "parsed_json": {"patient_metadata": {"name": "Rahul Sharma"}},
        "abnormal_findings": [
            {"test_name": "Hemoglobin", "status": "LOW", "severity": "Mild", "category": "Hematology"}
        ],
        "risk_assessment": {"risk_level": "MODERATE"},
        "consultation": {"consultation_required": True, "recommended_specialist": "Physician", "urgency": "Routine"},
        "execution_log": [],
        "retry_count": 0,
    }

    updated_state = asyncio.run(SummaryAgent().process(state))

    summary_text = updated_state["summary"]["text"]
    assert "Rahul Sharma" in summary_text
    assert "Hemoglobin" in summary_text
    assert "moderate" in summary_text.lower()
    assert "physician" in summary_text.lower()
