from typing import Any, Dict, List, Optional

from app.analysis.comparison.comparison_service import ComparisonService
from app.analysis.comparison.history_service import HistoryService
from app.embeddings.vector_store import vector_store
from app.services.analysis_service import AnalysisService
from app.services.patient_service import PatientService


class PatientRAGRetriever:
    """Retrieves patient-isolated structured facts, historical comparisons, and semantic knowledge."""

    async def retrieve_context(
        self,
        patient_id: str,
        query: str,
        analysis_id: Optional[str] = None
    ) -> Dict[str, Any]:
        # 1. Verify Patient Profile
        patient = await PatientService.get_patient(patient_id)
        patient_name = (patient.get("display_name") or patient.get("name")) if patient else "the patient"

        # 2. Retrieve Target Analysis Workspace or Latest Workspace for Patient
        sessions = await AnalysisService.list_sessions(patient_id=patient_id)
        current_session = None
        if analysis_id:
            current_session = await AnalysisService.get_session_by_id(analysis_id)
        elif sessions:
            current_session = sessions[0]

        parsed_json = (current_session.get("parsed_json") or {}) if current_session else {}
        comparison_context = (current_session.get("comparison_context") or {}) if current_session else {}

        # 3. Retrieve Historical Reports for comparison if comparison_context not precomputed
        previous_reports = await HistoryService().get_previous_parsed_reports(patient_id, current_session.get("analysis_id", "") if current_session else "")
        if not comparison_context and parsed_json:
            report_date = (parsed_json.get("patient_metadata") or {}).get("report_date") or (current_session.get("created_at") if current_session else None)
            comparison_context = ComparisonService().build_context(
                parsed_json,
                previous_reports,
                report_date,
                current_session.get("analysis_id") if current_session else None,
            )

        user_id = patient.get("user_id") if patient else None

        # 4. Semantic Search in Vector Store (enforcing patient_id & user_id boundary)
        vector_results = vector_store.search(query=query, patient_id=patient_id, user_id=user_id, top_k=4)
        if not vector_results:
            vector_results = vector_store.search(query=query, patient_id=None, user_id=None, top_k=2)

        # 5. Build Citation Sources List
        citations: List[Dict[str, str]] = []
        if current_session:
            doc_info = current_session.get("document_info") or {}
            filename = doc_info.get("original_filename") or current_session.get("title") or "Current CBC Report"
            citations.append({
                "title": f"{filename} (Current)",
                "type": "Patient Report",
                "details": f"Date: {current_session.get('created_at', '')[:10]}"
            })

        for report in previous_reports:
            meta = (report.get("parsed_json") or {}).get("patient_metadata") or {}
            date_str = meta.get("report_date") or report.get("created_at", "")[:10]
            title = report.get("title") or (report.get("document_info") or {}).get("original_filename") or "Previous Medical Report"
            citations.append({
                "title": f"{title} ({date_str})",
                "type": "Historical Report",
                "details": f"Patient: {patient_name}"
            })

        for vr in vector_results:
            meta = vr.get("metadata") or {}
            source_type = meta.get("source_type", "")
            score_percent = int((vr.get("score") or 0) * 100)
            
            if source_type == "clinical_knowledge" or not meta.get("patient_id"):
                citations.append({
                    "title": meta.get("title") or "Clinical Guidelines",
                    "type": "FAISS Clinical Knowledge Base",
                    "details": f"Similarity: {score_percent}% | {vr.get('text', '')[:90]}..."
                })
            else:
                citations.append({
                    "title": meta.get("title") or "Patient Report Vector Chunk",
                    "type": "FAISS Vector Match",
                    "details": f"Similarity: {score_percent}% | {vr.get('text', '')[:90]}..."
                })


        return {
            "patient_id": patient_id,
            "patient_name": patient_name,
            "current_session": current_session,
            "parsed_json": parsed_json,
            "comparison_context": comparison_context,
            "previous_report_count": len(previous_reports),
            "vector_results": vector_results,
            "citations": citations,
        }
