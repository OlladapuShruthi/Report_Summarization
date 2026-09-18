import re
from typing import Dict, Any


class IntentType:
    REPORT_HISTORY_QUERY = "REPORT_HISTORY_QUERY"
    REPORT_FACT_QUERY = "REPORT_FACT_QUERY"
    EXPLANATION_QUERY = "EXPLANATION_QUERY"
    REANALYSIS_REQUEST = "REANALYSIS_REQUEST"
    LIFESTYLE_ADVICE = "LIFESTYLE_ADVICE"
    GENERAL_MEDICAL = "GENERAL_MEDICAL"


class IntentClassifier:
    """Classifies user chat queries into medical RAG intent categories."""

    # These patterns indicate a lifestyle/advice question that should NOT be treated
    # as a history/trend query even if they mention "better" or "improve"
    LIFESTYLE_PATTERNS = [
        r"\b(diet|food|eat|meal|nutrition|tips|suggestion|advice|recommend|lifestyle|exercise|habit|supplement|vitamin)\b",
        r"\b(what should i|how can i|how do i|should i)\b.{0,40}\b(do|eat|take|improve|get better|recover)\b",
        r"\b(get better|feel better|recover|improve my health|what to do now)\b",
    ]

    HISTORY_PATTERNS = [
        r"\b(improved|improving|worse|worsening|progress|trend|changed|compared|previous|prior|over time|history|before|last report|earlier)\b",
        r"\b(has my|is my|did my).*(improved|changed|decreased|increased)\b",
    ]

    FACT_PATTERNS = [
        r"\b(what is|what's|show|check|value|level|current|status of|my)\s+(hemoglobin|hb|rbc|wbc|platelets|mcv|mch|mchc|rdw|tsh|t3|t4|cholesterol|triglycerides|glucose)\b",
        r"\b(what are my|list my|summary of|findings in)\b",
    ]

    EXPLANATION_PATTERNS = [
        r"\b(what does|what is|explain|meaning of|define|means)\s+([a-z0-9\s]+)\b",
        r"\b(why is|reason for|what causes)\b",
    ]

    REANALYSIS_PATTERNS = [
        r"\b(re-analyze|reanalyze|re-run|analyze again|recompare|compare all|run analysis again)\b",
    ]

    def classify(self, query: str) -> Dict[str, Any]:
        text = (query or "").strip().lower()
        if not text:
            return {"intent": IntentType.REPORT_FACT_QUERY, "confidence": 0.5, "matched_pattern": "empty_fallback"}

        # 0. Lifestyle / Advice Intent (check FIRST to prevent false history matches on "better", "improve")
        for pattern in self.LIFESTYLE_PATTERNS:
            if re.search(pattern, text):
                return {"intent": IntentType.LIFESTYLE_ADVICE, "confidence": 0.92, "matched_pattern": pattern}

        # 1. Re-analysis Intent
        for pattern in self.REANALYSIS_PATTERNS:
            if re.search(pattern, text):
                return {"intent": IntentType.REANALYSIS_REQUEST, "confidence": 0.95, "matched_pattern": pattern}

        # 2. Longitudinal History / Trend Intent
        for pattern in self.HISTORY_PATTERNS:
            if re.search(pattern, text):
                return {"intent": IntentType.REPORT_HISTORY_QUERY, "confidence": 0.90, "matched_pattern": pattern}

        # 3. Current Report Fact Query Intent
        for pattern in self.FACT_PATTERNS:
            if re.search(pattern, text):
                return {"intent": IntentType.REPORT_FACT_QUERY, "confidence": 0.88, "matched_pattern": pattern}

        # 4. Explanation Query Intent
        for pattern in self.EXPLANATION_PATTERNS:
            if re.search(pattern, text):
                return {"intent": IntentType.EXPLANATION_QUERY, "confidence": 0.85, "matched_pattern": pattern}

        # Default fallback to General Medical
        return {"intent": IntentType.GENERAL_MEDICAL, "confidence": 0.70, "matched_pattern": "general_fallback"}
