from app.graph.graph_state import GraphState
from app.graph.routing import route_after_anomaly, route_after_risk, route_after_validation
from app.graph.supervisor import Supervisor


class GraphBuilder:
    def __init__(self):
        self.supervisor = Supervisor()

    def build(self) -> dict:
        return {
            "nodes": [
                "supervisor",
                "anomaly_agent",
                "risk_agent",
                "consult_agent",
                "summary_agent",
                "validation_agent",
            ],
            "routes": {
                "after_anomaly": route_after_anomaly.__name__,
                "after_risk": route_after_risk.__name__,
                "after_validation": route_after_validation.__name__,
            },
            "retry_limit": 2,
        }

    def initialize_state(self, analysis_id: str, parsed_json: dict) -> GraphState:
        return {
            "analysis_id": analysis_id,
            "parsed_json": parsed_json,
            "abnormal_findings": [],
            "risk_assessment": {},
            "consultation": {},
            "summary": {},
            "validation": {},
            "retry_count": 0,
            "execution_log": [],
            "status": "initialized",
        }
