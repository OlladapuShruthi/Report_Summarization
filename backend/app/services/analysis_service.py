import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import UploadFile, HTTPException

from app.database.mongodb import get_database
from app.analysis.parser.parsing_service import ParsingService
from app.models.analysis_session import PipelineStatus
from app.utils.file_handler import save_uploaded_file
from app.core.logger import logger
from app.graph.runtime import GraphRuntime
from app.services.patient_service import PatientService
from app.analysis.comparison.comparison_service import ComparisonService
from app.analysis.comparison.history_service import HistoryService
from app.embeddings.vector_store import vector_store
from app.services.finding_event_service import FindingEventService
from app.services.finding_service import FindingService
from app.services.human_confirmation_service import HumanConfirmationService


# In-memory session store fallback if Mongo Atlas connection is degraded
in_memory_sessions: Dict[str, Dict[str, Any]] = {}

class AnalysisService:

    @staticmethod
    async def create_session(
        patient_id: str,
        title: Optional[str] = "Clinical Analysis Session",
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        if not patient_id or not str(patient_id).strip():
            raise HTTPException(status_code=400, detail="patient_id is required to initialize an analysis workspace.")
        patient = await PatientService.require_patient_access(patient_id, user_id)
        effective_user_id = user_id or patient.get("user_id")
        analysis_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        
        session_data = {
            "analysis_id": analysis_id,
            "patient_id": patient_id,
            "user_id": effective_user_id,
            "title": title or "Clinical Analysis Session",
            "status": PipelineStatus.CREATED.value,
            "document_info": None,
            "raw_text": None,
            "cleaned_text": None,
            "parsed_json": None,
            "parser_metadata": None,
            "review_required": False,
            "review_reasons": [],
            "review_questions": [],
            "follow_up_for_analysis_id": None,
            "comparison_context": None,
            "abnormal_findings": None,
            "risk_assessment": None,
            "consultation_advice": None,
            "summary_report": None,
            "validation_status": None,
            "retry_count": 0,
            "execution_log": [],
            "created_at": now,
            "updated_at": now
        }

        db = get_database()
        if db is not None:
            try:
                await db.analysis_sessions.insert_one(dict(session_data))
                logger.info(f"Created AnalysisSession workspace in MongoDB Atlas: {analysis_id}")
            except Exception as e:
                logger.warning(f"MongoDB write failed for session {analysis_id}, using in-memory store: {e}")
                in_memory_sessions[analysis_id] = session_data
        else:
            in_memory_sessions[analysis_id] = session_data

        return session_data

    @staticmethod
    async def upload_document_to_session(analysis_id: str, file: UploadFile) -> Dict[str, Any]:
        session = await AnalysisService.get_session_by_id(analysis_id)
        if not session:
            raise HTTPException(status_code=404, detail=f"Analysis session '{analysis_id}' not found.")

        # 1. Save File to disk
        saved_file = await save_uploaded_file(file)
        now = datetime.utcnow().isoformat()

        # Duplicate check within same patient scope
        patient_id = session.get("patient_id")
        user_id = session.get("user_id")
        file_hash = saved_file.get("file_hash")
        is_duplicate = False
        original_analysis_id = None

        if patient_id and file_hash:
            existing_sessions = await AnalysisService.list_sessions(patient_id=patient_id)
            for prev_session in existing_sessions:
                if prev_session.get("analysis_id") == analysis_id:
                    continue
                prev_doc = prev_session.get("document_info") or {}
                if prev_doc.get("file_hash") == file_hash:
                    is_duplicate = True
                    original_analysis_id = prev_session.get("analysis_id")
                    logger.info(f"Duplicate document detected for patient {patient_id}. Matches session {original_analysis_id}")
                    break

        doc_record = {
            "analysis_id": analysis_id,
            "file_id": saved_file["file_id"],
            "original_filename": saved_file["original_filename"],
            "stored_filename": saved_file["stored_filename"],
            "file_path": saved_file["file_path"],
            "file_size": saved_file["file_size"],
            "file_hash": file_hash,
            "content_type": saved_file["content_type"],
            "is_duplicate": is_duplicate,
            "original_analysis_id": original_analysis_id,
            "status": "uploaded",
            "created_at": now
        }

        # 2. Update session
        update_fields = {
            "document_info": doc_record,
            "is_duplicate": is_duplicate,
            "original_analysis_id": original_analysis_id,
            "status": PipelineStatus.UPLOADED.value,
            "execution_log": AnalysisService._append_execution_event(
                session,
                "document_uploaded",
                "executed",
                f"{saved_file['original_filename']}{' (DUPLICATE DETECTED)' if is_duplicate else ''}"
            ),
            "updated_at": now
        }

        db = get_database()
        if db is not None:
            try:
                await db.documents.insert_one(dict(doc_record))
                await db.analysis_sessions.update_one(
                    {"analysis_id": analysis_id},
                    {"$set": update_fields}
                )
                logger.info(f"Uploaded file '{saved_file['original_filename']}' to workspace '{analysis_id}' in MongoDB.")
            except Exception as e:
                logger.warning(f"MongoDB update failed for session upload {analysis_id}: {e}")
                if analysis_id in in_memory_sessions:
                    in_memory_sessions[analysis_id].update(update_fields)
        else:
            if analysis_id in in_memory_sessions:
                in_memory_sessions[analysis_id].update(update_fields)

        # Return updated session
        session.update(update_fields)
        return session

    @staticmethod
    async def parse_session_document(analysis_id: str) -> Dict[str, Any]:
        session = await AnalysisService.get_session_by_id(analysis_id)
        if not session:
            raise HTTPException(status_code=404, detail=f"Analysis session '{analysis_id}' not found.")

        document_info = session.get("document_info")
        if not document_info or not document_info.get("file_path"):
            raise HTTPException(status_code=400, detail="No uploaded document found for this analysis session.")

        await AnalysisService._update_session_fields(
            analysis_id,
            {
                "status": PipelineStatus.PARSING.value,
                "execution_log": AnalysisService._append_execution_event(session, "parsing_started", "executed"),
                "updated_at": datetime.utcnow().isoformat(),
            },
        )

        try:
            parsing_result = ParsingService().parse_document(document_info["file_path"])
            
            # Automatically chunk & index parsed report into FAISS vector store
            patient_id = session.get("patient_id")
            if patient_id:
                try:
                    vector_store.index_report(
                        patient_id=patient_id,
                        analysis_id=analysis_id,
                        parsed_json=parsing_result.parsed_json,
                        raw_text=parsing_result.raw_text,
                        user_id=session.get("user_id"),
                    )
                except Exception as index_err:
                    logger.warning(f"Failed to auto-index report in FAISS for session {analysis_id}: {index_err}")

            review_required = bool(parsing_result.parser_metadata.get("review_required"))
            review_reasons = parsing_result.parser_metadata.get("review_reasons") or []
            review_questions = AnalysisService._build_review_questions(analysis_id, review_reasons)
            update_fields = {

                "raw_text": parsing_result.raw_text,
                "cleaned_text": parsing_result.cleaned_text,
                "parsed_json": parsing_result.parsed_json,
                "parser_metadata": parsing_result.parser_metadata,
                "status": PipelineStatus.NEEDS_REVIEW.value if review_required else PipelineStatus.PARSED.value,
                "review_required": review_required,
                "review_reasons": review_reasons,
                "review_questions": review_questions,
                "execution_log": AnalysisService._append_execution_event(
                    session,
                    "needs_review" if review_required else "parsed",
                    "review_required" if review_required else "executed",
                    ", ".join(review_reasons) if review_reasons else None,
                ),
                "updated_at": datetime.utcnow().isoformat(),
            }
            await AnalysisService._update_session_fields(analysis_id, update_fields)
            session.update(update_fields)
            return session
        except Exception as exc:
            failure_fields = {
                "status": PipelineStatus.FAILED.value,
                "parser_metadata": {"error": str(exc)},
                "updated_at": datetime.utcnow().isoformat(),
            }
            await AnalysisService._update_session_fields(analysis_id, failure_fields)
            logger.error(f"Parsing failed for workspace {analysis_id}: {exc}", exc_info=True)
            raise

    @staticmethod
    def _build_review_questions(analysis_id: str, reasons: List[str]) -> List[Dict[str, Any]]:
        question_text = {
            "document_extraction_warning": "The report could not be extracted with complete confidence. Can you provide a clearer or follow-up report?",
            "low_report_classification_confidence": "The report type is uncertain. Can you confirm that this is the intended medical report?",
            "unknown_report_type": "The report type could not be identified. Can you confirm what kind of report this is?",
            "medspacy_unavailable": "Narrative clinical processing was unavailable. Is there a follow-up report or clinician-confirmed status you want to provide?",
            "medspacy_processing_warning": "Narrative processing produced a warning. Is there a follow-up report or clinician-confirmed status you want to provide?",
            "llm_structuring_fallback": "Structured extraction required a fallback method. Can you provide a clearer report or confirm the extracted information?",
        }
        return [
            {
                "question_id": f"{analysis_id}-review-{index}",
                "analysis_id": analysis_id,
                "reason": reason,
                "question": question_text.get(reason, "Additional evidence is required before analysis can continue. What evidence can you provide?"),
                "status": "pending",
                "answer": None,
                "answered_at": None,
                "evidence_type": "UNKNOWN",
            }
            for index, reason in enumerate(reasons, start=1)
        ]

    @staticmethod
    async def answer_review_question(
        analysis_id: str,
        question_id: str,
        action: str,
        response: Optional[str] = None,
        finding_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        session = await AnalysisService.get_session_by_id(analysis_id)
        if not session:
            raise HTTPException(status_code=404, detail=f"Analysis session '{analysis_id}' not found.")

        questions = list(session.get("review_questions") or [])
        question = next((item for item in questions if item.get("question_id") == question_id), None)
        if question is None:
            raise HTTPException(status_code=404, detail=f"Review question '{question_id}' not found.")

        question["status"] = "answered" if action in {"confirm", "no_report"} else action
        question["answer"] = response
        question["answered_at"] = datetime.utcnow().isoformat()
        question["evidence_type"] = "PATIENT_REPORTED" if action == "confirm" else "UNKNOWN"
        question["finding_id"] = finding_id
        await AnalysisService._update_session_fields(
            analysis_id,
            {"review_questions": questions, "updated_at": datetime.utcnow().isoformat()},
        )
        await HumanConfirmationService.record(
            patient_id=session.get("patient_id"),
            analysis_id=analysis_id,
            question_id=question_id,
            action=action,
            response=response,
            finding_id=finding_id,
            evidence_type=question["evidence_type"],
        )
        session["review_questions"] = questions
        return question

    @staticmethod
    def review_policy(session: Dict[str, Any]) -> Dict[str, Any]:
        review_required = bool(session.get("review_required") or (session.get("parser_metadata") or {}).get("review_required"))
        questions = session.get("review_questions") or []
        pending_count = sum(1 for question in questions if question.get("status") == "pending")
        if not review_required:
            return {
                "status": "not_required",
                "analysis_allowed": True,
                "reason": None,
                "pending_questions": 0,
            }
        if pending_count:
            return {
                "status": "pending",
                "analysis_allowed": False,
                "reason": "human_review_questions_pending",
                "pending_questions": pending_count,
            }
        return {
            "status": "acknowledged",
            "analysis_allowed": False,
            "reason": "objective_evidence_review_required",
            "pending_questions": 0,
        }

    @staticmethod
    async def analyze_session_document(analysis_id: str) -> Dict[str, Any]:
        session = await AnalysisService.get_session_by_id(analysis_id)
        if not session:
            raise HTTPException(status_code=404, detail=f"Analysis session '{analysis_id}' not found.")

        parsed_json = session.get("parsed_json")
        if not parsed_json:
            raise HTTPException(status_code=400, detail="Parse the uploaded document before analysis.")
        if session.get("review_required") or (session.get("parser_metadata") or {}).get("review_required"):
            reasons = session.get("review_reasons") or (session.get("parser_metadata") or {}).get("review_reasons") or []
            raise HTTPException(
                status_code=409,
                detail={
                    "code": "ANALYSIS_REVIEW_REQUIRED",
                    "message": "Human review is required before analysis can continue.",
                    "reasons": reasons,
                },
            )

        await AnalysisService._update_session_fields(
            analysis_id,
            {
                "status": PipelineStatus.ANALYZING.value,
                "execution_log": AnalysisService._append_execution_event(session, "analysis_started", "executed"),
                "updated_at": datetime.utcnow().isoformat(),
            },
        )

        comparison_context: Dict[str, Any] = {"history_available": False, "previous_report_count": 0, "comparisons": []}
        patient_id = session.get("patient_id")
        if patient_id:
            previous_reports = await HistoryService().get_previous_parsed_reports(patient_id, analysis_id)
            report_metadata = (parsed_json or {}).get("patient_metadata") or {}
            current_report_date = report_metadata.get("report_date") or session.get("created_at")
            comparison_context = ComparisonService().build_context(
                parsed_json,
                previous_reports,
                current_report_date,
                analysis_id,
            )
            finding_events = await FindingEventService.replace_for_analysis(
                patient_id,
                analysis_id,
                comparison_context.get("finding_events") or [],
            )
            await FindingService.upsert_from_events(patient_id, finding_events)
            human_confirmations = await HumanConfirmationService.list_for_patient(patient_id)
        else:
            human_confirmations = []

        async def persist_graph_state(graph_state: Dict[str, Any]) -> None:
            consultation_block = graph_state.get("consultation") or {}
            summary_block = graph_state.get("summary") or {}
            validation_block = graph_state.get("validation") or {}
            update_fields = {
                "abnormal_findings": graph_state.get("abnormal_findings"),
                "comparison_context": graph_state.get("comparison_context"),
                "risk_assessment": graph_state.get("risk_assessment"),
                "consultation_advice": consultation_block,
                "summary_report": summary_block.get("text"),
                "validation_status": validation_block,
                "retry_count": graph_state.get("retry_count", 0),
                "execution_log": graph_state.get("execution_log", []),
                "updated_at": datetime.utcnow().isoformat(),
            }
            await AnalysisService._update_session_fields(analysis_id, update_fields)

        final_state = await GraphRuntime().execute(
            analysis_id=analysis_id,
            parsed_json=parsed_json,
            state_callback=persist_graph_state,
            patient_metadata=(parsed_json or {}).get("patient_metadata") or {},
            comparison_context=comparison_context,
            patient_id=patient_id,
            human_confirmations=human_confirmations,
        )

        update_fields = {
            "status": final_state.get("status", PipelineStatus.ANALYZING.value),
            "abnormal_findings": final_state.get("abnormal_findings"),
            "comparison_context": final_state.get("comparison_context"),
            "risk_assessment": final_state.get("risk_assessment"),
            "consultation_advice": final_state.get("consultation"),
            "summary_report": (final_state.get("summary") or {}).get("text"),
            "validation_status": final_state.get("validation"),
            "retry_count": final_state.get("retry_count", 0),
            "execution_log": final_state.get("execution_log", []),
            "updated_at": datetime.utcnow().isoformat(),
        }
        await AnalysisService._update_session_fields(analysis_id, update_fields)
        session.update(update_fields)
        return session

    @staticmethod
    async def quick_start_session(file: UploadFile, patient_id: Optional[str] = None, title: Optional[str] = None) -> Dict[str, Any]:
        # Convenience endpoint: create workspace & upload document in one step
        title = title or f"Analysis - {file.filename}"
        new_session = await AnalysisService.create_session(patient_id=patient_id, title=title)
        updated_session = await AnalysisService.upload_document_to_session(new_session["analysis_id"], file)
        return updated_session

    @staticmethod
    async def create_follow_up_session(analysis_id: str, file: UploadFile) -> Dict[str, Any]:
        original = await AnalysisService.get_session_by_id(analysis_id)
        if not original:
            raise HTTPException(status_code=404, detail=f"Analysis session '{analysis_id}' not found.")
        follow_up = await AnalysisService.create_session(
            patient_id=original.get("patient_id"),
            title=f"Follow-up for {original.get('title') or analysis_id}",
            user_id=original.get("user_id"),
        )
        await AnalysisService._update_session_fields(
            follow_up["analysis_id"],
            {"follow_up_for_analysis_id": analysis_id},
        )
        updated_session = await AnalysisService.upload_document_to_session(follow_up["analysis_id"], file)
        updated_session["follow_up_for_analysis_id"] = analysis_id
        return updated_session

    @staticmethod
    async def get_session_by_id(analysis_id: str) -> Optional[Dict[str, Any]]:
        db = get_database()
        if db is not None:
            try:
                session = await db.analysis_sessions.find_one({"analysis_id": analysis_id})
                if session:
                    session["_id"] = str(session["_id"])
                    return session
            except Exception:
                pass
        return in_memory_sessions.get(analysis_id)

    @staticmethod
    async def require_session_access(analysis_id: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        session = await AnalysisService.get_session_by_id(analysis_id)
        if not session:
            raise HTTPException(status_code=404, detail=f"Analysis session '{analysis_id}' not found.")
        owner_id = session.get("user_id")
        if owner_id is not None:
            if not user_id or owner_id != user_id:
                raise HTTPException(status_code=403, detail="You do not have access to this analysis workspace.")
        return session

    @staticmethod
    async def list_sessions(patient_id: Optional[str] = None, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        db = get_database()
        sessions = []
        if db is not None:
            try:
                query: Dict[str, Any] = {}
                if patient_id:
                    query["patient_id"] = patient_id
                if user_id:
                    query["user_id"] = user_id
                cursor = db.analysis_sessions.find(query).sort("created_at", -1)
                async for doc in cursor:
                    doc["_id"] = str(doc["_id"])
                    sessions.append(doc)
                return sessions
            except Exception as e:
                logger.warning(f"MongoDB list sessions failed: {e}")

        # Fallback in-memory sessions
        sessions_list = list(in_memory_sessions.values())
        if patient_id:
            sessions_list = [s for s in sessions_list if s.get("patient_id") == patient_id]
        if user_id:
            sessions_list = [s for s in sessions_list if s.get("user_id") == user_id]
        return sorted(sessions_list, key=lambda x: x["created_at"], reverse=True)

    @staticmethod
    async def _update_session_fields(analysis_id: str, update_fields: Dict[str, Any]) -> None:
        db = get_database()
        if db is not None:
            try:
                await db.analysis_sessions.update_one(
                    {"analysis_id": analysis_id},
                    {"$set": update_fields},
                )
            except Exception as exc:
                logger.warning(f"MongoDB session update failed for {analysis_id}: {exc}")

        if analysis_id in in_memory_sessions:
            in_memory_sessions[analysis_id].update(update_fields)

    @staticmethod
    def _append_execution_event(session: Dict[str, Any], stage: str, status: str, details: Optional[str] = None) -> List[Dict[str, Any]]:
        execution_log = list(session.get("execution_log") or [])
        execution_log.append(
            {
                "stage": stage,
                "status": status,
                "timestamp": datetime.utcnow().isoformat(),
                "details": details,
            }
        )
        return execution_log
