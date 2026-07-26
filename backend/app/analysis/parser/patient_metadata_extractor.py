import re
from typing import Any, Dict, Optional


class PatientMetadataExtractor:
    GENDER_VALUES = {
        "m": "Male",
        "male": "Male",
        "f": "Female",
        "female": "Female",
        "other": "Other",
    }

    def extract(self, text: str) -> Dict[str, Any]:
        return {
            "name": self._extract_name(text),
            "age": self._extract_age(text),
            "gender": self._extract_gender(text),
        }

    def _extract_name(self, text: str) -> Optional[str]:
        patterns = [
            r"(?:patient\s*name|name)\s*[:\-]\s*(?P<value>[A-Za-z][A-Za-z .]{1,80}?)(?=\s+(?:age|gender|sex|date)\b|\n|$)",
            r"(?:patient)\s*[:\-]\s*(?P<value>[A-Za-z][A-Za-z .]{1,80}?)(?=\s+(?:age|gender|sex|date)\b|\n|$)",
        ]
        return self._extract_text_value(text, patterns)

    def _extract_age(self, text: str) -> Optional[int]:
        match = re.search(r"\bage\s*[:\-]?\s*(?P<value>\d{1,3})\b", text or "", re.IGNORECASE)
        if not match:
            return None

        age = int(match.group("value"))
        if 0 <= age <= 120:
            return age
        return None

    def _extract_gender(self, text: str) -> Optional[str]:
        match = re.search(r"\b(?:gender|sex)\s*[:\-]?\s*(?P<value>male|female|other|m|f)\b", text or "", re.IGNORECASE)
        if not match:
            return None
        return self.GENDER_VALUES.get(match.group("value").lower())

    def _extract_text_value(self, text: str, patterns: list[str]) -> Optional[str]:
        for pattern in patterns:
            match = re.search(pattern, text or "", re.IGNORECASE)
            if match:
                value = re.split(r"\s{2,}|\n", match.group("value").strip())[0].strip(" .:-")
                return value.title() if value else None
        return None
