from datetime import datetime
from typing import Any, Dict, List, Optional

from app.database.mongodb import get_database


in_memory_findings: Dict[str, Dict[str, Any]] = {}


class FindingService:
    @staticmethod
    async def upsert_from_events(patient_id: str, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        grouped: Dict[str, List[Dict[str, Any]]] = {}
        for event in events:
            finding_id = event.get("finding_id")
            if finding_id:
                grouped.setdefault(finding_id, []).append(event)

        findings = []
        for finding_id, finding_events in grouped.items():
            ordered = sorted(finding_events, key=lambda event: event.get("date") or "")
            latest = ordered[-1]
            finding = {
                "finding_id": finding_id,
                "patient_id": patient_id,
                "test_name": latest.get("test_name"),
                "canonical_test_name": latest.get("canonical_test_name"),
                "unit": latest.get("unit"),
                "first_observed": ordered[0].get("date"),
                "last_observed": latest.get("date"),
                "latest_objective_status": latest.get("status"),
                "lifecycle_state": latest.get("lifecycle_state", "UNKNOWN"),
                "evidence_history": ordered,
                "updated_at": datetime.utcnow().isoformat(),
            }
            db = get_database()
            if db is not None:
                try:
                    await db.findings.update_one(
                        {"patient_id": patient_id, "finding_id": finding_id},
                        {"$set": finding},
                        upsert=True,
                    )
                except Exception:
                    pass
            in_memory_findings[f"{patient_id}:{finding_id}"] = finding
            findings.append(finding)
        return findings

    @staticmethod
    async def list_for_patient(patient_id: str) -> List[Dict[str, Any]]:
        db = get_database()
        if db is not None:
            try:
                cursor = db.findings.find({"patient_id": patient_id}).sort("first_observed", 1)
                findings = []
                async for finding in cursor:
                    finding["_id"] = str(finding["_id"])
                    findings.append(finding)
                return findings
            except Exception:
                pass
        return sorted(
            [finding for finding in in_memory_findings.values() if finding.get("patient_id") == patient_id],
            key=lambda finding: finding.get("first_observed") or "",
        )

    @staticmethod
    async def get_for_patient(patient_id: str, finding_id: str) -> Optional[Dict[str, Any]]:
        db = get_database()
        if db is not None:
            try:
                finding = await db.findings.find_one({"patient_id": patient_id, "finding_id": finding_id})
                if finding:
                    finding["_id"] = str(finding["_id"])
                    return finding
            except Exception:
                pass
        return in_memory_findings.get(f"{patient_id}:{finding_id}")
