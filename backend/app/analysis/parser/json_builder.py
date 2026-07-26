from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


class MedicalJSONBuilder:
    SCHEMA_VERSION = "1.0"
    DEFAULT_CONFIDENCE = {
        "text_extraction": 0.0,
        "classification": 0.0,
        "entity_extraction": 0.0,
        "overall": 0.5,
    }
    DEFAULT_PARSER_METADATA = {
        "parser_version": "1.0.0",
        "ocr_used": False,
        "llm_used": False,
    }

    def build(
        self,
        report_type: str,
        lab_results: Optional[List[Dict[str, Any]]] = None,
        narrative_impressions: Optional[List[Dict[str, Any]]] = None,
        patient_metadata: Optional[Dict[str, Any]] = None,
        confidence: Optional[Dict[str, float]] = None,
        parser_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        return {
            "schema_version": self.SCHEMA_VERSION,
            "report_type": report_type,
            "patient_metadata": patient_metadata or {},
            "lab_results": lab_results or [],
            "narrative_impressions": narrative_impressions or [],
            "confidence": {
                **self.DEFAULT_CONFIDENCE,
                **(confidence or {}),
            },
            "parser_metadata": {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                **self.DEFAULT_PARSER_METADATA,
                **(parser_metadata or {}),
            },
        }
