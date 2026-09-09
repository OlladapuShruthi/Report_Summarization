from datetime import datetime
from typing import Any, Dict, List, Optional

from app.database.mongodb import get_database


# Development fallback matching the existing analysis and patient services.
in_memory_finding_events: Dict[str, List[Dict[str, Any]]] = {}


class FindingEventService:
    @staticmethod
    async def replace_for_analysis(
        patient_id: str,
        analysis_id: str,
        events: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        records = [
            {
                **event,
                "patient_id": patient_id,
                "analysis_id": analysis_id,
                "created_at": datetime.utcnow().isoformat(),
            }
            for event in events
        ]
        db = get_database()
        if db is not None:
            try:
                await db.finding_events.delete_many({"analysis_id": analysis_id})
                if records:
                    await db.finding_events.insert_many([dict(record) for record in records])
                return records
            except Exception:
                pass

        in_memory_finding_events[analysis_id] = records
        return records

    @staticmethod
    async def list_for_patient(
        patient_id: str,
        finding_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        db = get_database()
        if db is not None:
            try:
                query: Dict[str, Any] = {"patient_id": patient_id}
                if finding_id:
                    query["finding_id"] = finding_id
                cursor = db.finding_events.find(query).sort("date", 1)
                events = []
                async for event in cursor:
                    event["_id"] = str(event["_id"])
                    events.append(event)
                return events
            except Exception:
                pass

        events = [
            event
            for records in in_memory_finding_events.values()
            for event in records
            if event.get("patient_id") == patient_id
            and (finding_id is None or event.get("finding_id") == finding_id)
        ]
        return sorted(events, key=lambda event: event.get("date") or "")
