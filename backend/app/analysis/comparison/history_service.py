from typing import Any, Dict, List


class HistoryService:
    """Retrieves only completed parsed reports belonging to one patient."""

    async def get_previous_parsed_reports(self, patient_id: str, current_analysis_id: str) -> List[Dict[str, Any]]:
        # Imported lazily to avoid a service import cycle during application startup.
        from app.services.analysis_service import AnalysisService

        sessions = await AnalysisService.list_sessions(patient_id=patient_id)
        current_session = next((s for s in sessions if s.get("analysis_id") == current_analysis_id), None)
        current_created_at = current_session.get("created_at") if current_session else None

        previous_reports = []
        for session in sessions:
            if session.get("analysis_id") == current_analysis_id:
                continue
            if not session.get("parsed_json"):
                continue
            if current_created_at and session.get("created_at") and session.get("created_at") >= current_created_at:
                continue
            previous_reports.append(session)

        return sorted(previous_reports, key=self._report_date)

    @staticmethod
    def _report_date(session: Dict[str, Any]) -> str:
        metadata = (session.get("parsed_json") or {}).get("patient_metadata") or {}
        return str(metadata.get("report_date") or session.get("created_at") or "")
