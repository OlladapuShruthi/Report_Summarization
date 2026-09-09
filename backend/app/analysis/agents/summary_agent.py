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
        comparison_context = updated_state.get("comparison_context") or {}
        human_confirmations = updated_state.get("human_confirmations") or []
        retry_count = int(updated_state.get("retry_count", 0))

        summary_text = await self._build_summary(
            parsed_json,
            abnormal_findings,
            risk_assessment,
            consultation,
            retry_count,
            comparison_context,
            human_confirmations,
        )
        updated_state["summary"] = {
            "text": summary_text,
            "sections": summary_text.split("\n\n"),
            "source": "deterministic" if retry_count > 0 else ("groq" if self._groq_client.enabled and settings.LLM_PROVIDER.lower() == "groq" else "deterministic"),
            "source_facts": self._source_facts(parsed_json),
        }
        updated_state["status"] = "summary_generated"

        logger.info(
            "[%s] generated summary with %d section(s).",
            self.agent_name,
            len(updated_state["summary"]["sections"]),
        )
        return updated_state

    @staticmethod
    def _source_facts(parsed_json: Dict[str, Any]) -> List[Dict[str, Any]]:
        facts = []
        for lab in parsed_json.get("lab_results") or parsed_json.get("lab_facts") or []:
            facts.append(
                {
                    "test_name": lab.get("test_name"),
                    "value": lab.get("value"),
                    "unit": lab.get("unit"),
                    "reference_range": lab.get("reference_range"),
                }
            )
        return facts

    async def _build_summary(
        self,
        parsed_json: Dict[str, Any],
        abnormal_findings: List[Dict[str, Any]],
        risk_assessment: Dict[str, Any],
        consultation: Dict[str, Any],
        retry_count: int,
        comparison_context: Dict[str, Any],
        human_confirmations: List[Dict[str, Any]],
    ) -> str:
        if retry_count > 0:
            return self._build_deterministic_summary(parsed_json, abnormal_findings, risk_assessment, consultation, comparison_context, human_confirmations)

        llm_summary = await self._build_llm_summary(parsed_json, abnormal_findings, risk_assessment, consultation, comparison_context, human_confirmations)
        if llm_summary:
            return llm_summary

        return self._build_deterministic_summary(parsed_json, abnormal_findings, risk_assessment, consultation, comparison_context, human_confirmations)

    async def _build_llm_summary(
        self,
        parsed_json: Dict[str, Any],
        abnormal_findings: List[Dict[str, Any]],
        risk_assessment: Dict[str, Any],
        consultation: Dict[str, Any],
        comparison_context: Dict[str, Any],
        human_confirmations: List[Dict[str, Any]],
    ) -> str:
        if settings.LLM_PROVIDER.lower() != "groq" or not self._groq_client.enabled:
            return ""

        prompt = self._build_prompt(parsed_json, abnormal_findings, risk_assessment, consultation, comparison_context, human_confirmations)
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
        comparison_context: Dict[str, Any],
        human_confirmations: List[Dict[str, Any]],
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
            f"Historical comparison: {comparison_context}\n"
            f"Patient-reported context (not objective evidence): {human_confirmations}\n"
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
        comparison_context: Dict[str, Any],
        human_confirmations: List[Dict[str, Any]],
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

        for comparison in comparison_context.get("comparisons") or []:
            finding_status = comparison.get("finding_status")
            previous_value = comparison.get("previous_value")
            if previous_value is not None and finding_status in {"PERSISTENT_IMPROVING", "PERSISTENT_WORSENING", "RESOLVED", "NEW_ABNORMAL"}:
                lines.append(
                    f"- {comparison.get('test_name')} changed from {previous_value:g} to {comparison.get('current_value'):g} ({finding_status.lower().replace('_', ' ')})."
                )
            elif finding_status == "CURRENTLY_NORMAL" and previous_value is not None:
                lines.append(
                    f"- {comparison.get('test_name')} is currently within the provided reference range after a previous recorded abnormal result; clinical resolution is not confirmed by this report alone."
                )
            elif finding_status == "UNKNOWN" and previous_value is not None:
                lines.append(
                    f"- The current report does not include {comparison.get('test_name')}; its current status is unknown and cannot be called normal or resolved."
                )

        if human_confirmations:
            lines.append(
                "- Patient-reported context is recorded separately and does not replace objective report measurements."
            )

        return "\n".join(lines)
