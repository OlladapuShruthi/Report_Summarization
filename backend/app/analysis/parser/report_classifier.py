from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class ClassificationResult:
    report_type: str
    confidence: float
    matched_keywords: List[str] = field(default_factory=list)
    scores: Dict[str, int] = field(default_factory=dict)


class ReportClassifier:
    REPORT_KEYWORDS = {
        "LAB_REPORT_CBC": ["hemoglobin", "wbc", "rbc", "platelet", "mcv", "mch", "hematocrit"],
        "LAB_REPORT_THYROID": ["tsh", "t3", "t4", "thyroid"],
        "LAB_REPORT_LIPID": ["cholesterol", "triglycerides", "hdl", "ldl", "vldl"],
        "LAB_REPORT_LFT": ["bilirubin", "sgot", "sgpt", "alt", "ast", "alkaline phosphatase"],
        "LAB_REPORT_KFT": ["creatinine", "urea", "uric acid", "egfr", "kidney"],
        "RADIOLOGY_REPORT": ["impression", "findings", "mri", "ct scan", "x-ray", "ultrasound"],
        "DISCHARGE_SUMMARY": ["discharge", "diagnosis", "hospital course", "medications", "follow up"],
    }

    def classify(self, text: str) -> ClassificationResult:
        normalized = (text or "").lower()
        scores: Dict[str, int] = {}
        matches: Dict[str, List[str]] = {}

        for report_type, keywords in self.REPORT_KEYWORDS.items():
            matched = [keyword for keyword in keywords if keyword in normalized]
            scores[report_type] = len(matched)
            matches[report_type] = matched

        best_type = max(scores, key=scores.get)
        best_score = scores[best_type]

        if best_score == 0:
            return ClassificationResult("UNKNOWN", 0.2, [], scores)

        confidence = min(0.95, 0.45 + (best_score * 0.12))
        return ClassificationResult(
            report_type=best_type,
            confidence=round(confidence, 2),
            matched_keywords=matches[best_type],
            scores=scores,
        )
