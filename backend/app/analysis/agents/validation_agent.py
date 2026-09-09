from typing import Any, Dict, List
import re

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
        parsed_json = state.get("parsed_json") or {}
        expected_source_facts = self._source_facts(parsed_json)
        actual_source_facts = summary.get("source_facts") or []

        if expected_source_facts and actual_source_facts != expected_source_facts:
            issues.append("summary source facts do not match parsed medical facts")

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

        for finding in abnormal_findings:
            test_name = (finding.get("test_name") or "").lower()
            if not test_name:
                continue
            if finding.get("status") == "LOW" and re.search(rf"{re.escape(test_name)}\s+is\s+normal", summary_text):
                issues.append(f"summary contradicts abnormal status for {finding.get('test_name')}")
            if finding.get("status") == "HIGH" and re.search(rf"{re.escape(test_name)}\s+is\s+within\s+the\s+reference", summary_text):
                issues.append(f"summary contradicts abnormal status for {finding.get('test_name')}")

        for comparison in (state.get("comparison_context") or {}).get("comparisons", []):
            if comparison.get("finding_status") != "UNKNOWN":
                continue
            test_name = (comparison.get("test_name") or "").lower()
            if re.search(rf"{re.escape(test_name)}\s+(?:is|was)\s+(?:normal|resolved)", summary_text):
                issues.append(f"summary invents resolution for missing measurement: {comparison.get('test_name')}")

        passed = len(issues) == 0
        return {
            "is_valid": passed,
            "passed": passed,
            "issues": issues,
            "checked_sections": ["abnormal_findings", "risk_assessment", "consultation", "summary"],
        }

    @staticmethod
    def _source_facts(parsed_json: Dict[str, Any]) -> List[Dict[str, Any]]:
        return [
            {
                "test_name": lab.get("test_name"),
                "value": lab.get("value"),
                "unit": lab.get("unit"),
                "reference_range": lab.get("reference_range"),
            }
            for lab in (parsed_json.get("lab_results") or parsed_json.get("lab_facts") or [])
        ]
