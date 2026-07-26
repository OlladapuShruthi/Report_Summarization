import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class LabResult:
    test_name: str
    value: float
    unit: Optional[str] = None
    reference_range: Optional[Dict[str, Any]] = None
    category: Optional[str] = None
    is_outside_reference: Optional[bool] = None
    raw_line: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "test_name": self.test_name,
            "value": self.value,
            "unit": self.unit,
            "reference_range": self.reference_range,
            "category": self.category,
            "is_outside_reference": self.is_outside_reference,
            "raw_line": self.raw_line,
        }


class DeterministicParser:
    KNOWN_TESTS = [
        "Hemoglobin",
        "WBC",
        "RBC",
        "Platelets",
        "Platelet Count",
        "Hematocrit",
        "MCV",
        "MCH",
        "MCHC",
        "TSH",
        "T3",
        "T4",
        "Total Cholesterol",
        "Cholesterol",
        "Triglycerides",
        "HDL",
        "LDL",
        "VLDL",
        "Bilirubin",
        "SGOT",
        "SGPT",
        "ALT",
        "AST",
        "Creatinine",
        "Urea",
    ]
    TEST_CATEGORIES = {
        "Hemoglobin": "Hematology",
        "WBC": "Hematology",
        "RBC": "Hematology",
        "Platelets": "Hematology",
        "Platelet Count": "Hematology",
        "Hematocrit": "Hematology",
        "MCV": "Hematology",
        "MCH": "Hematology",
        "MCHC": "Hematology",
        "TSH": "Endocrinology",
        "T3": "Endocrinology",
        "T4": "Endocrinology",
        "Total Cholesterol": "Lipid Profile",
        "Cholesterol": "Lipid Profile",
        "Triglycerides": "Lipid Profile",
        "HDL": "Lipid Profile",
        "LDL": "Lipid Profile",
        "VLDL": "Lipid Profile",
        "Bilirubin": "Liver Function",
        "SGOT": "Liver Function",
        "SGPT": "Liver Function",
        "ALT": "Liver Function",
        "AST": "Liver Function",
        "Creatinine": "Kidney Function",
        "Urea": "Kidney Function",
    }

    VALUE_PATTERN = re.compile(
        r"(?P<name>[A-Za-z][A-Za-z0-9 /().%-]{1,45}?)\s*[:\-]?\s*"
        r"(?P<value>-?\d+(?:\.\d+)?)\s*"
        r"(?P<unit>[A-Za-z%/^0-9.]+)?\s*"
        r"(?:(?:ref(?:erence)?(?: range)?|normal)?\s*[:\-]?\s*"
        r"(?P<low>-?\d+(?:\.\d+)?)\s*(?:-|to)\s*(?P<high>-?\d+(?:\.\d+)?))?",
        re.IGNORECASE,
    )

    def parse(self, text: str) -> List[Dict[str, Any]]:
        results: List[LabResult] = []
        seen = set()

        for line in (text or "").splitlines():
            parsed = self._parse_line(line.strip())
            if not parsed:
                continue

            key = (parsed.test_name.lower(), parsed.value, parsed.unit)
            if key in seen:
                continue
            seen.add(key)
            results.append(parsed)

        return [result.to_dict() for result in results]

    def _parse_line(self, line: str) -> Optional[LabResult]:
        if not line or not any(test.lower() in line.lower() for test in self.KNOWN_TESTS):
            return None

        match = self.VALUE_PATTERN.search(line)
        if not match:
            return None

        name = self._normalize_test_name(match.group("name"))
        if not any(test.lower() in name.lower() or name.lower() in test.lower() for test in self.KNOWN_TESTS):
            return None

        reference_range = None
        is_outside_reference = None
        if match.group("low") and match.group("high"):
            low = float(match.group("low"))
            high = float(match.group("high"))
            value = float(match.group("value"))
            reference_range = {
                "low": low,
                "high": high,
                "text": f"{match.group('low')} - {match.group('high')}",
            }
            is_outside_reference = value < low or value > high

        return LabResult(
            test_name=name,
            value=float(match.group("value")),
            unit=match.group("unit"),
            reference_range=reference_range,
            category=self.TEST_CATEGORIES.get(name),
            is_outside_reference=is_outside_reference,
            raw_line=line,
        )

    def _normalize_test_name(self, raw_name: str) -> str:
        name = re.sub(r"\s+", " ", raw_name).strip(" :-")
        for known in self.KNOWN_TESTS:
            if known.lower() in name.lower():
                return known
        return name.title()
