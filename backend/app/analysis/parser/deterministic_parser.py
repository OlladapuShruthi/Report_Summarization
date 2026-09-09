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

    def parse_tables(self, tables: List[List[List[str]]]) -> List[Dict[str, Any]]:
        results: List[LabResult] = []
        seen = set()
        for table in tables or []:
            if not table:
                continue
            headers = [self._normalize_header(cell) for cell in table[0]]
            test_index = self._find_column(headers, {"test", "test name", "analyte", "parameter"})
            value_index = self._find_column(headers, {"result", "value", "reading", "observed value"})
            unit_index = self._find_column(headers, {"unit", "units"})
            reference_index = self._find_column(headers, {"reference range", "reference", "normal range", "range"})
            if test_index is None or value_index is None:
                continue

            for row in table[1:]:
                if not row or max(test_index, value_index) >= len(row):
                    continue
                test_name = str(row[test_index] or "").strip()
                value = self._numeric(row[value_index])
                if not test_name or value is None:
                    continue
                normalized_name = self._normalize_test_name(test_name)
                if not any(test.lower() == normalized_name.lower() for test in self.KNOWN_TESTS):
                    continue
                unit = str(row[unit_index]).strip() if unit_index is not None and unit_index < len(row) else None
                reference_text = str(row[reference_index]).strip() if reference_index is not None and reference_index < len(row) else ""
                reference_range = self._parse_reference_range(reference_text)
                is_outside_reference = None
                if reference_range:
                    is_outside_reference = value < reference_range["low"] or value > reference_range["high"]
                result = LabResult(
                    test_name=normalized_name,
                    value=value,
                    unit=unit,
                    reference_range=reference_range,
                    category=self.TEST_CATEGORIES.get(normalized_name),
                    is_outside_reference=is_outside_reference,
                    raw_line=" | ".join(str(cell or "").strip() for cell in row),
                )
                key = (result.test_name.casefold(), result.value, result.unit)
                if key not in seen:
                    seen.add(key)
                    results.append(result)
        return [result.to_dict() for result in results]

    @staticmethod
    def _normalize_header(value: Any) -> str:
        return re.sub(r"\s+", " ", str(value or "").strip().casefold())

    @staticmethod
    def _find_column(headers: List[str], names: set[str]) -> Optional[int]:
        for index, header in enumerate(headers):
            if header in names:
                return index
        return None

    @staticmethod
    def _numeric(value: Any) -> Optional[float]:
        try:
            return float(str(value).replace(",", "").strip())
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _parse_reference_range(value: str) -> Optional[Dict[str, Any]]:
        match = re.search(r"(-?\d+(?:\.\d+)?)\s*(?:-|to)\s*(-?\d+(?:\.\d+)?)", value or "", re.IGNORECASE)
        if not match:
            return None
        low = float(match.group(1))
        high = float(match.group(2))
        if low > high:
            return None
        return {"low": low, "high": high, "text": f"{match.group(1)} - {match.group(2)}"}

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
