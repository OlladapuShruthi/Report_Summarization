from typing import Any, Dict, Optional

from app.analysis.agents.base_agent import BaseAgent
from app.core.logger import logger
from app.graph.routing import log_node_execution


class AnomalyAgent(BaseAgent):
    def __init__(self):
        super().__init__("AnomalyAgent")

    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        updated_state = log_node_execution(state, self.agent_name)
        parsed_json = state.get("parsed_json") or {}
        lab_results = parsed_json.get("lab_results") or parsed_json.get("lab_facts") or []

        abnormal_findings = []
        for lab_result in lab_results:
            finding = self._evaluate_lab_result(lab_result)
            if finding is not None:
                abnormal_findings.append(finding)

        updated_state["abnormal_findings"] = abnormal_findings
        updated_state["status"] = "anomaly_evaluated"

        logger.info(
            "[%s] evaluated %d lab results and found %d abnormalities.",
            self.agent_name,
            len(lab_results),
            len(abnormal_findings),
        )
        return updated_state

    def _evaluate_lab_result(self, lab_result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        reference_range = lab_result.get("reference_range") or {}
        low = reference_range.get("low")
        high = reference_range.get("high")
        value = lab_result.get("value")

        if low is None or high is None or value is None:
            return None

        try:
            numeric_value = float(value)
            numeric_low = float(low)
            numeric_high = float(high)
        except (TypeError, ValueError):
            return None

        if numeric_low > numeric_high:
            return None

        if numeric_value < numeric_low:
            deviation = numeric_low - numeric_value
            span = max(numeric_high - numeric_low, 1.0)
            return self._build_finding(lab_result, "LOW", deviation / span, reference_range)

        if numeric_value > numeric_high:
            deviation = numeric_value - numeric_high
            span = max(numeric_high - numeric_low, 1.0)
            return self._build_finding(lab_result, "HIGH", deviation / span, reference_range)

        return None

    def _build_finding(
        self,
        lab_result: Dict[str, Any],
        status: str,
        deviation_ratio: float,
        reference_range: Dict[str, Any],
    ) -> Dict[str, Any]:
        if deviation_ratio <= 0.1:
            severity = "Mild"
        elif deviation_ratio <= 0.25:
            severity = "Moderate"
        else:
            severity = "Marked"

        return {
            "test_name": lab_result.get("test_name"),
            "status": status,
            "severity": severity,
            "value": lab_result.get("value"),
            "unit": lab_result.get("unit"),
            "reference_range": reference_range,
            "category": lab_result.get("category"),
            "raw_line": lab_result.get("raw_line"),
        }
