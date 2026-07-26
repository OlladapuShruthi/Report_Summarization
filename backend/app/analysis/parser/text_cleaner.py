import re


class TextCleaner:
    UNIT_REPLACEMENTS = {
        "g / dL": "g/dL",
        "g/ dL": "g/dL",
        "mg / dL": "mg/dL",
        "uIU / mL": "uIU/mL",
    }

    def clean(self, text: str) -> str:
        if not text:
            return ""

        cleaned = text.replace("\r\n", "\n").replace("\r", "\n")
        cleaned = self._remove_repeated_headers(cleaned)
        cleaned = self._normalize_units(cleaned)
        cleaned = re.sub(r"[ \t]+", " ", cleaned)
        cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
        cleaned = "\n".join(line.strip() for line in cleaned.splitlines() if line.strip())
        return cleaned.strip()

    def _normalize_units(self, text: str) -> str:
        normalized = text
        for source, target in self.UNIT_REPLACEMENTS.items():
            normalized = normalized.replace(source, target)
        return normalized

    def _remove_repeated_headers(self, text: str) -> str:
        lines = text.splitlines()
        filtered = []
        for line in lines:
            stripped = line.strip()
            if re.match(r"^page\s+\d+\s*(of\s+\d+)?$", stripped, re.IGNORECASE):
                continue
            if re.match(r"^-{3,}$", stripped):
                continue
            filtered.append(line)
        return "\n".join(filtered)
