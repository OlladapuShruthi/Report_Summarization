from collections import Counter
from typing import Any, Dict, List

from app.analysis.agents.base_agent import BaseAgent
from app.core.logger import logger
from app.graph.routing import log_node_execution

class ConsultAgent(BaseAgent):
    SPECIALIST_BY_CATEGORY = {
        "Hematology": "Physician",
        "Endocrinology": "Endocrinologist",
        "Liver Function": "Hepatologist",
        "Kidney Function": "Nephrologist",
        "Lipid Profile": "Physician",
        "Uncategorized": "Physician",
    }
    URGENCY_BY_RISK = {
        "LOW": "Routine",
        "MODERATE": "Routine",
        "HIGH": "Urgent",
        "CRITICAL": "Immediate",
    }

    def __init__(self):
        super().__init__("ConsultAgent")

    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        updated_state = log_node_execution(state, self.agent_name)
        abnormal_findings = updated_state.get("abnormal_findings") or []
        risk_assessment = updated_state.get("risk_assessment") or {}

        consultation = self._build_consultation(abnormal_findings, risk_assessment)
        updated_state["consultation"] = consultation
        updated_state["status"] = "consultation_assessed"

        logger.info(
            "[%s] produced consultation requirement=%s, specialist=%s.",
            self.agent_name,
            consultation["consultation_required"],
            consultation["recommended_specialist"],
        )
        return updated_state

    def _build_consultation(
        self,
        abnormal_findings: List[Dict[str, Any]],
        risk_assessment: Dict[str, Any],
    ) -> Dict[str, Any]:
        risk_level = (risk_assessment.get("risk_level") or "LOW").upper()
        urgency = self.URGENCY_BY_RISK.get(risk_level, "Routine")
        consultation_required = risk_level in {"MODERATE", "HIGH", "CRITICAL"}

        specialist = self._select_specialist(abnormal_findings)
        reasoning = [f"Risk level is {risk_level.lower()}."]
        if abnormal_findings:
            categories = Counter(finding.get("category") or "Uncategorized" for finding in abnormal_findings)
            dominant_category = categories.most_common(1)[0][0]
            if dominant_category in self.SPECIALIST_BY_CATEGORY:
                reasoning.append(f"Dominant abnormality category: {dominant_category}.")

        return {
            "consultation_required": consultation_required,
            "recommended_specialist": specialist if consultation_required else "None",
            "urgency": urgency,
            "reasoning": reasoning,
        }

    def _select_specialist(self, abnormal_findings: List[Dict[str, Any]]) -> str:
        if not abnormal_findings:
            return "None"

        categories = Counter(finding.get("category") or "Uncategorized" for finding in abnormal_findings)
        dominant_category = categories.most_common(1)[0][0]
        return self.SPECIALIST_BY_CATEGORY.get(dominant_category, "Physician")
