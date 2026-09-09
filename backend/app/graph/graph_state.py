from typing import Any, Dict, List, TypedDict


class GraphState(TypedDict, total=False):
    analysis_id: str
    patient_id: str
    parsed_json: Dict[str, Any]
    comparison_context: Dict[str, Any]
    human_confirmations: List[Dict[str, Any]]
    abnormal_findings: List[Dict[str, Any]]
    risk_assessment: Dict[str, Any]
    consultation: Dict[str, Any]
    summary: Dict[str, Any]
    validation: Dict[str, Any]
    retry_count: int
    execution_log: List[Dict[str, Any]]

    status: str
