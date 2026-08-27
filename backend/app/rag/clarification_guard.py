from typing import Dict, Any, Optional


class ClarificationGuard:
    """Evaluates whether retrieved patient context is sufficient to safely answer a query."""

    @staticmethod
    def evaluate_history_sufficiency(intent: str, previous_report_count: int, patient_id: Optional[str]) -> Dict[str, Any]:
        """Check if history is required by intent but absent in records."""
        if intent == "REPORT_HISTORY_QUERY" and previous_report_count == 0:
            return {
                "sufficient": False,
                "reason": "MISSING_HISTORICAL_REPORTS",
                "clarification_message": (
                    "I only have your current medical report available and do not have any previous reports stored for your patient profile. "
                    "Please upload an earlier medical report if you would like me to analyze historical trends or compare changes over time."
                )
            }

        if not patient_id:
            return {
                "sufficient": False,
                "reason": "MISSING_PATIENT_SCOPE",
                "clarification_message": "Please select an active patient profile before requesting medical report analysis or chat explanations."
            }

        return {"sufficient": True, "reason": "OK", "clarification_message": None}
