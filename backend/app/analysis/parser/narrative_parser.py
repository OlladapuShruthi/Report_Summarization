import re
from typing import Dict, List


class NarrativeParser:
    def parse(self, text: str) -> List[Dict[str, str]]:
        if not text:
            return []

        sections = []
        current_section = "narrative"
        current_lines: List[str] = []

        for line in text.splitlines():
            stripped = line.strip()
            if not stripped:
                continue

            section_match = re.match(
                r"^(findings|impression|conclusion|diagnosis)\s*:?\s*(.*)$",
                stripped,
                re.IGNORECASE,
            )
            if section_match:
                self._append_section(sections, current_section, current_lines)
                current_section = section_match.group(1).lower()
                current_lines = [section_match.group(2).strip()] if section_match.group(2).strip() else []
            else:
                current_lines.append(stripped)

        self._append_section(sections, current_section, current_lines)
        return sections

    def _append_section(self, sections: List[Dict[str, str]], section: str, lines: List[str]) -> None:
        text = " ".join(line for line in lines if line).strip()
        if text:
            sections.append({"section": section, "text": text})
