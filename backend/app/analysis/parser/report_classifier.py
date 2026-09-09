from dataclasses import dataclass, field
import re
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
    STRUCTURED_LAB_LABELS = (
        "hemoglobin", "wbc", "rbc", "platelets", "platelet count", "hematocrit",
        "mcv", "mch", "mchc", "tsh", "t3", "t4", "cholesterol", "triglycerides",
        "hdl", "ldl", "vldl", "bilirubin", "sgot", "sgpt", "alt", "ast", "creatinine",
        "urea",
    )
    NARRATIVE_MARKERS = (
        "chronological analysis", "medical board", "the patient was", "in conclusion",
        "case review", "consultation was obtained", "retrospective review",
    )
    NARRATIVE_TERMS = (
        "patient", "physician", "consultant", "diagnosis", "hospital", "history",
        "case", "conclusion", "aneurysm", "syncope",
    )

    def classify(self, text: str) -> ClassificationResult:
        normalized = re.sub(r"\(cid:\d+\)", " ", (text or "").lower())
        scores: Dict[str, int] = {}
        matches: Dict[str, List[str]] = {}

        for report_type, keywords in self.REPORT_KEYWORDS.items():
            matched = [keyword for keyword in keywords if keyword in normalized]
            scores[report_type] = len(matched)
            matches[report_type] = matched

        structured_lab_lines = self._count_structured_lab_lines(text)
        narrative_marker_count = sum(marker in normalized for marker in self.NARRATIVE_MARKERS)
        narrative_term_count = sum(term in normalized for term in self.NARRATIVE_TERMS)

        if structured_lab_lines == 0 and (
            narrative_marker_count >= 2
            or (len(normalized) >= 500 and narrative_term_count >= 4)
        ):
            return ClassificationResult(
                report_type="UNKNOWN",
                confidence=0.75,
                matched_keywords=[],
                scores=scores,
            )

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

    def _count_structured_lab_lines(self, text: str) -> int:
        count = 0
        for line in (text or "").splitlines():
            normalized_line = line.strip().lower()
            if not normalized_line or len(normalized_line) > 180:
                continue
            has_known_label = any(
                re.match(rf"^{re.escape(label)}(?:\\s|:|$)", normalized_line)
                for label in self.STRUCTURED_LAB_LABELS
            )
            has_numeric_value = bool(re.search(r"\\b\\d+(?:\\.\\d+)?\\b", normalized_line))
            if has_known_label and has_numeric_value:
                count += 1
        return count
