from collections import Counter
from typing import Any, Dict, List

from app.analysis.agents.base_agent import BaseAgent
from app.core.logger import logger
from app.graph.routing import log_node_execution

class RiskAgent(BaseAgent):
    SEVERITY_WEIGHTS = {
        "Mild": 1,
        "Moderate": 2,
        "Marked": 3,
        "Critical": 4,
    }
    DEFAULT_RISK_LEVELS = ["LOW", "MODERATE", "HIGH", "CRITICAL"]

    def __init__(self):
        super().__init__("RiskAgent")

    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        updated_state = log_node_execution(state, self.agent_name)
        abnormal_findings = updated_state.get("abnormal_findings") or []

        risk_assessment = self._assess_risk(abnormal_findings)
        updated_state["risk_assessment"] = risk_assessment
        updated_state["status"] = "risk_assessed"

        logger.info(
            "[%s] assessed %d abnormal findings as %s.",
            self.agent_name,
            len(abnormal_findings),
            risk_assessment["risk_level"],
        )
        return updated_state

    def _assess_risk(self, abnormal_findings: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not abnormal_findings:
            return {
                "risk_level": "LOW",
                "reasoning": ["No abnormal findings detected."],
                "score": 0,
                "abnormal_count": 0,
            }

        severity_counts = Counter(
            finding.get("severity", "Mild") for finding in abnormal_findings
        )
        score = sum(self.SEVERITY_WEIGHTS.get(severity, 1) for severity in severity_counts.elements())
        critical_count = severity_counts.get("Critical", 0)

        if critical_count >= 2:
            risk_level = "CRITICAL"
        elif critical_count == 1:
            risk_level = "HIGH"
        elif score <= 1:
            risk_level = "LOW"
        elif score <= 3:
            risk_level = "MODERATE"
        elif score <= 5:
            risk_level = "HIGH"
        else:
            risk_level = "CRITICAL"

        reasoning = self._build_reasoning(abnormal_findings, risk_level)
        return {
            "risk_level": risk_level,
            "reasoning": reasoning,
            "score": score,
            "abnormal_count": len(abnormal_findings),
            "severity_breakdown": dict(severity_counts),
        }

    def _build_reasoning(self, abnormal_findings: List[Dict[str, Any]], risk_level: str) -> List[str]:
        if not abnormal_findings:
            return ["No abnormal findings detected."]

        category_counts = Counter(
            finding.get("category") or "Uncategorized" for finding in abnormal_findings
        )
        top_category, top_count = category_counts.most_common(1)[0]

        reasoning = [f"{len(abnormal_findings)} abnormal finding(s) detected."]
        if top_category != "Uncategorized":
            if top_count == 1:
                reasoning.append(f"One {top_category} parameter is outside range.")
            else:
                reasoning.append(f"{top_count} {top_category} parameters are below range.")
        reasoning.append(f"Overall report risk is {risk_level}.")
        return reasoning
