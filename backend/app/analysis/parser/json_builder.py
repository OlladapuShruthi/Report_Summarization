from datetime import datetime
from typing import Any, Dict, List, Optional


class MedicalJSONBuilder:
    SCHEMA_VERSION = "1.0"

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
            "confidence": confidence or {"overall": 0.5},
            "parser_metadata": {
                "generated_at": datetime.utcnow().isoformat(),
                **(parser_metadata or {}),
            },
        }
