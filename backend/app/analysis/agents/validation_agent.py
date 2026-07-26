from typing import Any, Dict, List

from app.analysis.agents.base_agent import BaseAgent
from app.core.logger import logger
from app.graph.routing import log_node_execution

class ValidationAgent(BaseAgent):
    def __init__(self):
        super().__init__("ValidationAgent")

    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        updated_state = log_node_execution(state, self.agent_name)
        validation = self._validate(updated_state)
        updated_state["validation"] = validation
        updated_state["status"] = "validated" if validation["passed"] else "validation_failed"

        if not validation["passed"]:
            updated_state["retry_count"] = int(updated_state.get("retry_count", 0)) + 1

        logger.info(
            "[%s] validation %s with %d issue(s).",
            self.agent_name,
            "passed" if validation["passed"] else "failed",
            len(validation["issues"]),
        )
        return updated_state

    def _validate(self, state: Dict[str, Any]) -> Dict[str, Any]:
        issues: List[str] = []
        abnormal_findings = state.get("abnormal_findings") or []
        risk_assessment = state.get("risk_assessment") or {}
        consultation = state.get("consultation") or {}
        summary = state.get("summary") or {}
        summary_text = (summary.get("text") or "").lower()

        for finding in abnormal_findings:
            test_name = (finding.get("test_name") or "").lower()
            if test_name and test_name not in summary_text:
                issues.append(f"summary missing abnormal test reference: {finding.get('test_name')}")

        risk_level = (risk_assessment.get("risk_level") or "").lower()
        if risk_level and risk_level not in summary_text:
            issues.append(f"summary missing risk level: {risk_assessment.get('risk_level')}")

        if consultation.get("consultation_required"):
            specialist = (consultation.get("recommended_specialist") or "").lower()
            if specialist and specialist != "none" and specialist not in summary_text:
                issues.append(f"summary missing consultation specialist: {consultation.get('recommended_specialist')}")

        passed = len(issues) == 0
        return {
            "passed": passed,
            "issues": issues,
            "checked_sections": ["abnormal_findings", "risk_assessment", "consultation", "summary"],
        }
