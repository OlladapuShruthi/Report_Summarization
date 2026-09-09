from langgraph.graph import END, START, StateGraph

from app.analysis.agents.anomaly_agent import AnomalyAgent
from app.analysis.agents.consult_agent import ConsultAgent
from app.analysis.agents.risk_agent import RiskAgent
from app.analysis.agents.summary_agent import SummaryAgent
from app.analysis.agents.validation_agent import ValidationAgent
from app.graph.graph_state import GraphState
from app.graph.routing import route_after_anomaly, route_after_risk, route_after_validation
from app.graph.supervisor import Supervisor


class GraphBuilder:
    def __init__(self):
        self.supervisor = Supervisor()
        self.anomaly_agent = AnomalyAgent()
        self.risk_agent = RiskAgent()
        self.consult_agent = ConsultAgent()
        self.summary_agent = SummaryAgent()
        self.validation_agent = ValidationAgent()

    def build(self):
        """Compile the official LangGraph workflow for a single report analysis."""
        workflow = StateGraph(GraphState)
        workflow.add_node("supervisor", self.supervisor.decide)
        workflow.add_node("anomaly_agent", self.anomaly_agent.process)
        workflow.add_node("risk_agent", self.risk_agent.process)
        workflow.add_node("consult_agent", self.consult_agent.process)
        workflow.add_node("summary_agent", self.summary_agent.process)
        workflow.add_node("validation_agent", self.validation_agent.process)

        workflow.add_edge(START, "supervisor")
        workflow.add_edge("supervisor", "anomaly_agent")
        workflow.add_conditional_edges(
            "anomaly_agent",
            route_after_anomaly,
            {"risk_agent": "risk_agent", "summary_agent": "summary_agent"},
        )
        workflow.add_conditional_edges(
            "risk_agent",
            route_after_risk,
            {"consult_agent": "consult_agent", "summary_agent": "summary_agent"},
        )
        workflow.add_edge("consult_agent", "summary_agent")
        workflow.add_edge("summary_agent", "validation_agent")
        workflow.add_conditional_edges(
            "validation_agent",
            route_after_validation,
            {"summary_agent": "summary_agent", "end": END},
        )
        return workflow.compile()

    def initialize_state(self, analysis_id: str, parsed_json: dict, patient_id: str = "") -> GraphState:
        return {
            "analysis_id": analysis_id,
            "patient_id": patient_id,
            "parsed_json": parsed_json,
            "comparison_context": {},
            "human_confirmations": [],
            "abnormal_findings": [],
            "risk_assessment": {},
            "consultation": {},
            "summary": {},
            "validation": {},
            "retry_count": 0,
            "execution_log": [],
            "status": "initialized",
        }
