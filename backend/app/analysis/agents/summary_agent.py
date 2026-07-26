from typing import Any, Dict, List

from app.analysis.agents.base_agent import BaseAgent
from app.analysis.llm.groq_client import GroqClient
from app.core.config import settings
from app.core.logger import logger
from app.graph.routing import log_node_execution


class SummaryAgent(BaseAgent):
    def __init__(self):
        super().__init__("SummaryAgent")
        self._groq_client = GroqClient()

    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        updated_state = log_node_execution(state, self.agent_name)
        parsed_json = updated_state.get("parsed_json") or {}
        abnormal_findings = updated_state.get("abnormal_findings") or []
        risk_assessment = updated_state.get("risk_assessment") or {}
        consultation = updated_state.get("consultation") or {}
        retry_count = int(updated_state.get("retry_count", 0))

        summary_text = await self._build_summary(parsed_json, abnormal_findings, risk_assessment, consultation, retry_count)
        updated_state["summary"] = {
            "text": summary_text,
            "sections": summary_text.split("\n\n"),
            "source": "deterministic" if retry_count > 0 else ("groq" if self._groq_client.enabled and settings.LLM_PROVIDER.lower() == "groq" else "deterministic"),
        }
        updated_state["status"] = "summary_generated"

        logger.info(
            "[%s] generated summary with %d section(s).",
            self.agent_name,
            len(updated_state["summary"]["sections"]),
        )
        return updated_state

    async def _build_summary(
        self,
        parsed_json: Dict[str, Any],
        abnormal_findings: List[Dict[str, Any]],
        risk_assessment: Dict[str, Any],
        consultation: Dict[str, Any],
        retry_count: int,
    ) -> str:
        if retry_count > 0:
            return self._build_deterministic_summary(parsed_json, abnormal_findings, risk_assessment, consultation)

        llm_summary = await self._build_llm_summary(parsed_json, abnormal_findings, risk_assessment, consultation)
        if llm_summary:
            return llm_summary

        return self._build_deterministic_summary(parsed_json, abnormal_findings, risk_assessment, consultation)

    async def _build_llm_summary(
        self,
        parsed_json: Dict[str, Any],
        abnormal_findings: List[Dict[str, Any]],
        risk_assessment: Dict[str, Any],
        consultation: Dict[str, Any],
    ) -> str:
        if settings.LLM_PROVIDER.lower() != "groq" or not self._groq_client.enabled:
            return ""

        prompt = self._build_prompt(parsed_json, abnormal_findings, risk_assessment, consultation)
        try:
            return await self._groq_client.chat_completion(prompt)
        except Exception as exc:
            logger.warning(
                "[%s] Groq summary generation failed, falling back to deterministic summary: %s",
                self.agent_name,
                exc,
            )
            return ""

    def _build_prompt(
        self,
        parsed_json: Dict[str, Any],
        abnormal_findings: List[Dict[str, Any]],
        risk_assessment: Dict[str, Any],
        consultation: Dict[str, Any],
    ) -> List[Dict[str, str]]:
        patient_metadata = parsed_json.get("patient_metadata") or {}
        patient_name = patient_metadata.get("name") or "the patient"
        system_message = (
            "You are a medical report summarizer. Use only the provided structured facts. "
            "Do not diagnose, do not invent values, and keep the response concise, patient-friendly, and factual."
        )
        user_message = (
            f"Patient: {patient_name}\n"
            f"Abnormal findings: {abnormal_findings}\n"
            f"Risk assessment: {risk_assessment}\n"
            f"Consultation advice: {consultation}\n"
            "Write a short summary with 3-5 short paragraphs or bullet-like sentences."
        )
        return [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message},
        ]

    def _build_deterministic_summary(
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
                lines.append(
                    f"- {test_name} is {status} compared with the reference range ({severity} deviation)."
                )
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
