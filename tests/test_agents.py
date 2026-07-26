import asyncio
import os
import sys

# Add backend directory to sys.path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.analysis.agents.anomaly_agent import AnomalyAgent
from app.graph.routing import route_after_anomaly


def test_anomaly_agent_flags_out_of_range_lab_results():
    state = {
        "analysis_id": "analysis-1",
        "parsed_json": {
            "lab_results": [
                {
                    "test_name": "Hemoglobin",
                    "value": 10.2,
                    "unit": "g/dL",
                    "reference_range": {"low": 13.5, "high": 17.5, "text": "13.5 - 17.5"},
                    "category": "Hematology",
                    "raw_line": "Hemoglobin 10.2 g/dL 13.5 - 17.5",
                },
                {
                    "test_name": "WBC",
                    "value": 6200,
                    "unit": "cells/uL",
                    "reference_range": {"low": 4000, "high": 11000, "text": "4000 - 11000"},
                    "category": "Hematology",
                    "raw_line": "WBC 6200 cells/uL 4000 - 11000",
                },
            ]
        },
        "abnormal_findings": [],
        "execution_log": [],
        "retry_count": 0,
    }

    updated_state = asyncio.run(AnomalyAgent().process(state))

    assert updated_state["status"] == "anomaly_evaluated"
    assert len(updated_state["abnormal_findings"]) == 1
    finding = updated_state["abnormal_findings"][0]
    assert finding["test_name"] == "Hemoglobin"
    assert finding["status"] == "LOW"
    assert finding["severity"] == "Marked"
    assert updated_state["execution_log"][-1]["node"] == "AnomalyAgent"
    assert route_after_anomaly(updated_state) == "risk_agent"


def test_anomaly_agent_skips_normal_reports():
    state = {
        "analysis_id": "analysis-2",
        "parsed_json": {
            "lab_results": [
                {
                    "test_name": "Hemoglobin",
                    "value": 14.2,
                    "unit": "g/dL",
                    "reference_range": {"low": 13.5, "high": 17.5, "text": "13.5 - 17.5"},
                    "category": "Hematology",
                    "raw_line": "Hemoglobin 14.2 g/dL 13.5 - 17.5",
                }
            ]
        },
        "abnormal_findings": [],
        "execution_log": [],
        "retry_count": 0,
    }

    updated_state = asyncio.run(AnomalyAgent().process(state))

    assert updated_state["abnormal_findings"] == []
    assert updated_state["execution_log"][-1]["node"] == "AnomalyAgent"
    assert route_after_anomaly(updated_state) == "summary_agent"