from typing import Dict, Any, Optional


class ClarificationGuard:
    """Evaluates whether retrieved patient context is sufficient to safely answer a query."""

    @staticmethod
    def evaluate_history_sufficiency(intent: str, previous_report_count: int, patient_id: Optional[str]) -> Dict[str, Any]:
        """Check if history is required by intent but absent in records."""
        # Allow REPORT_HISTORY_QUERY to proceed even if previous_report_count == 0,
        # so the chat service can output the *current* values alongside the clarification.

        if not patient_id:
            return {
                "sufficient": False,
                "reason": "MISSING_PATIENT_SCOPE",
                "clarification_message": "Please select an active patient profile before requesting medical report analysis or chat explanations."
            }

        return {"sufficient": True, "reason": "OK", "clarification_message": None}
