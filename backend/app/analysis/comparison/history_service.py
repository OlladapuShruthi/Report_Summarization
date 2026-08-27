from typing import Any, Dict, List


class HistoryService:
    """Retrieves only completed parsed reports belonging to one patient."""

    async def get_previous_parsed_reports(self, patient_id: str, current_analysis_id: str) -> List[Dict[str, Any]]:
        # Imported lazily to avoid a service import cycle during application startup.
        from app.services.analysis_service import AnalysisService

        sessions = await AnalysisService.list_sessions(patient_id=patient_id)
        previous_reports = [
            session
            for session in sessions
            if session.get("analysis_id") != current_analysis_id and session.get("parsed_json")
        ]
        return sorted(previous_reports, key=self._report_date)

    @staticmethod
    def _report_date(session: Dict[str, Any]) -> str:
        metadata = (session.get("parsed_json") or {}).get("patient_metadata") or {}
        return str(metadata.get("report_date") or session.get("created_at") or "")
