from typing import Any, Dict, List

from app.analysis.agents.base_agent import BaseAgent
from app.core.logger import logger
from app.graph.routing import log_node_execution

class SummaryAgent(BaseAgent):
    def __init__(self):
        super().__init__("SummaryAgent")

    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        updated_state = log_node_execution(state, self.agent_name)
        parsed_json = updated_state.get("parsed_json") or {}
        abnormal_findings = updated_state.get("abnormal_findings") or []
        risk_assessment = updated_state.get("risk_assessment") or {}
        consultation = updated_state.get("consultation") or {}

        summary_text = self._build_summary(parsed_json, abnormal_findings, risk_assessment, consultation)
        updated_state["summary"] = {
            "text": summary_text,
            "sections": summary_text.split("\n\n"),
        }
        updated_state["status"] = "summary_generated"

        logger.info("[%s] generated summary with %d section(s).", self.agent_name, len(updated_state["summary"]["sections"]))
        return updated_state

    def _build_summary(
        self,
        parsed_json: Dict[str, Any],
        abnormal_findings: List[Dict[str, Any]],
        risk_assessment: Dict[str, Any],
        consultation: Dict[str, Any],
    ) -> str:
        patient_metadata = parsed_json.get("patient_metadata") or {}
        patient_name = patient_metadata.get("name")
        risk_level = (risk_assessment.get("risk_level") or "LOW").lower()
        consultation_required = bool(consultation.get("consultation_required"))
        specialist = consultation.get("recommended_specialist")

        lines: List[str] = []
        if patient_name:
            lines.append(f"Report summary for {patient_name}:")
        else:
            lines.append("Report summary:")

        if abnormal_findings:
            for finding in abnormal_findings:
                test_name = finding.get("test_name", "A test")
                status = finding.get("status", "abnormal").lower()
                severity = finding.get("severity", "mild").lower()
                lines.append(f"- {test_name} is {status} compared with the reference range ({severity} deviation).")
        else:
            lines.append("- No abnormal values were detected in the report.")

        lines.append(f"Overall risk appears {risk_level}.")
        if consultation_required and specialist and specialist != "None":
            lines.append(f"A consultation with a {specialist.lower()} is recommended.")
        elif consultation_required:
            lines.append("A medical consultation is recommended.")
        else:
            lines.append("No urgent consultation is indicated based on the current findings.")

        return "\n".join(lines)
