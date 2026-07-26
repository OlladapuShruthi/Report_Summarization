import os
import sys

backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.graph.graph_builder import GraphBuilder
from app.graph.routing import route_after_anomaly, route_after_risk, route_after_validation


def test_graph_builder_initializes_expected_state():
    builder = GraphBuilder()
    state = builder.initialize_state("analysis-1", {"lab_results": []})

    assert state["analysis_id"] == "analysis-1"
    assert state["retry_count"] == 0
    assert state["status"] == "initialized"
    assert "next_node" not in state


def test_graph_routes_resolve_based_on_state():
    assert route_after_anomaly({"abnormal_findings": []}) == "summary_agent"
    assert route_after_anomaly({"abnormal_findings": [{"test_name": "Hemoglobin"}]}) == "risk_agent"
    assert route_after_risk({"risk_assessment": {"risk_level": "LOW"}}) == "summary_agent"
    assert route_after_risk({"risk_assessment": {"risk_level": "HIGH"}}) == "consult_agent"
    assert route_after_validation({"validation": {"passed": True}, "retry_count": 0}) == "end"
    assert route_after_validation({"validation": {"passed": False}, "retry_count": 0}) == "summary_agent"