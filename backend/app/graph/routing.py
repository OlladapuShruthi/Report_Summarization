from typing import Literal

from app.graph.graph_state import GraphState

RouteName = Literal[
    "supervisor",
    "anomaly_agent",
    "risk_agent",
    "consult_agent",
    "summary_agent",
    "validation_agent",
    "end",
]


def log_node_execution(state: GraphState, node_name: str, status: str = "executed") -> GraphState:
    execution_log = list(state.get("execution_log", []))
    execution_log.append({"node": node_name, "status": status})
    updated_state = dict(state)
    updated_state["execution_log"] = execution_log
    return updated_state


def route_after_anomaly(state: GraphState) -> RouteName:
    findings = state.get("abnormal_findings") or []
    return "risk_agent" if findings else "summary_agent"


def route_after_risk(state: GraphState) -> RouteName:
    risk = str((state.get("risk_assessment") or {}).get("risk_level") or "").upper()
    if risk in {"MODERATE", "HIGH", "CRITICAL"}:
        return "consult_agent"
    return "summary_agent"


def route_after_validation(state: GraphState) -> RouteName:
    validation = state.get("validation") or {}
    if validation.get("passed"):
        return "end"
    if state.get("retry_count", 0) >= 2:
        return "end"
    return "summary_agent"
