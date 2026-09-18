from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Query
from app.services.analysis_service import AnalysisService
from app.services.patient_service import PatientService
from app.models.analysis_session import ReviewAnswerRequest
from app.core.security import get_current_user_id as get_optional_user_id
from app.core.response import success_response, error_response
from app.core.logger import logger

router = APIRouter()

@router.post("/create")
async def create_analysis_workspace(
    patient_id: Optional[str] = Form(None),
    title: Optional[str] = Form(None),
    authenticated_user_id: Optional[str] = Depends(get_optional_user_id),
):
    if not patient_id or not patient_id.strip():
        return error_response(message="patient_id is required to create an analysis workspace.", code="PATIENT_ID_REQUIRED", status_code=400)
    try:
        session = await AnalysisService.create_session(patient_id=patient_id.strip(), title=title, user_id=authenticated_user_id)
        return success_response(
            data=session,
            message="Analysis workspace initialized successfully."
        )
    except HTTPException as he:
        return error_response(
            message=he.detail,
            code="ACCESS_DENIED" if he.status_code == 403 else "WORKSPACE_CREATION_FAILED",
            status_code=he.status_code
        )
    except Exception as e:
        logger.error(f"Error creating analysis workspace: {e}", exc_info=True)
        return error_response(
            message="Failed to initialize analysis workspace.",
            code="WORKSPACE_CREATION_FAILED",
            details=str(e)
        )

@router.post("/{analysis_id}/upload")
async def upload_report_to_workspace(analysis_id: str, file: UploadFile = File(...), authenticated_user_id: Optional[str] = Depends(get_optional_user_id)):
    try:
        await AnalysisService.require_session_access(analysis_id, authenticated_user_id)
        updated_session = await AnalysisService.upload_document_to_session(analysis_id, file)
        return success_response(
            data=updated_session,
            message=f"Medical report uploaded successfully to workspace '{analysis_id}'."
        )
    except HTTPException as he:
        return error_response(
            message=he.detail,
            code="ACCESS_DENIED" if he.status_code == 403 else "UPLOAD_HTTP_ERROR",
            status_code=he.status_code
        )
    except Exception as e:
        logger.error(f"Error uploading report to workspace {analysis_id}: {e}", exc_info=True)
        return error_response(
            message="Document upload failed.",
            code="DOCUMENT_UPLOAD_FAILED",
            details=str(e)
        )

@router.post("/{analysis_id}/parse")
async def parse_report_in_workspace(analysis_id: str, authenticated_user_id: Optional[str] = Depends(get_optional_user_id)):
    try:
        await AnalysisService.require_session_access(analysis_id, authenticated_user_id)
        updated_session = await AnalysisService.parse_session_document(analysis_id)
        return success_response(
            data=updated_session,
            message=f"Medical report parsed successfully for workspace '{analysis_id}'."
        )
    except HTTPException as he:
        return error_response(
            message=he.detail,
            code="ACCESS_DENIED" if he.status_code == 403 else "PARSE_HTTP_ERROR",
            status_code=he.status_code
        )
    except Exception as e:
        logger.error(f"Error parsing report in workspace {analysis_id}: {e}", exc_info=True)
        return error_response(
            message="Document parsing failed.",
            code="DOCUMENT_PARSE_FAILED",
            details=str(e)
        )

@router.post("/{analysis_id}/analyze")
async def analyze_report_in_workspace(analysis_id: str, authenticated_user_id: Optional[str] = Depends(get_optional_user_id)):
    try:
        await AnalysisService.require_session_access(analysis_id, authenticated_user_id)
        updated_session = await AnalysisService.analyze_session_document(analysis_id)
        return success_response(
            data=updated_session,
            message=f"Medical report analyzed successfully for workspace '{analysis_id}'."
        )
    except HTTPException as he:
        detail = he.detail if isinstance(he.detail, dict) else None
        return error_response(
            message=detail.get("message") if detail else str(he.detail),
            code=detail.get("code", "ANALYZE_HTTP_ERROR") if detail else ("ACCESS_DENIED" if he.status_code == 403 else "ANALYZE_HTTP_ERROR"),
            details=detail or None,
            status_code=he.status_code,
        )
    except Exception as e:
        logger.error(f"Error analyzing report in workspace {analysis_id}: {e}", exc_info=True)
        return error_response(
            message="Document analysis failed.",
            code="DOCUMENT_ANALYZE_FAILED",
            details=str(e)
        )

@router.post("/{analysis_id}/follow-up")
async def upload_follow_up_report(analysis_id: str, file: UploadFile = File(...), authenticated_user_id: Optional[str] = Depends(get_optional_user_id)):
    try:
        await AnalysisService.require_session_access(analysis_id, authenticated_user_id)
        updated_session = await AnalysisService.create_follow_up_session(analysis_id, file)
        return success_response(
            data=updated_session,
            message=f"Follow-up report uploaded to workspace '{updated_session['analysis_id']}'.",
        )
    except HTTPException as he:
        return error_response(
            message=he.detail,
            code="ACCESS_DENIED" if he.status_code == 403 else "FOLLOW_UP_UPLOAD_ERROR",
            status_code=he.status_code
        )
    except Exception as e:
        logger.error(f"Error uploading follow-up report for {analysis_id}: {e}", exc_info=True)
        return error_response(
            message="Follow-up document upload failed.",
            code="FOLLOW_UP_UPLOAD_FAILED",
            details=str(e),
        )

@router.get("/{analysis_id}/progress")
async def get_analysis_progress(analysis_id: str, authenticated_user_id: Optional[str] = Depends(get_optional_user_id)):
    try:
        session = await AnalysisService.require_session_access(analysis_id, authenticated_user_id)
        if not session:
            return error_response(
                message=f"Analysis workspace '{analysis_id}' not found.",
                code="WORKSPACE_NOT_FOUND",
                status_code=404
            )

        execution_log = session.get("execution_log") or []
        current_stage = execution_log[-1]["stage"] if execution_log else session.get("status", "created")
        return success_response(
            data={
                "analysis_id": analysis_id,
                "status": session.get("status"),
                "current_stage": current_stage,
                "execution_log": execution_log,
                "risk_assessment": session.get("risk_assessment"),
                "consultation_advice": session.get("consultation_advice"),
                "validation_status": session.get("validation_status"),
                "summary_report": session.get("summary_report"),
                "review_required": session.get("review_required", False),
                "review_reasons": session.get("review_reasons") or [],
                "review_questions": session.get("review_questions") or [],
                "review_policy": AnalysisService.review_policy(session),
            },
            message="Analysis progress retrieved successfully."
        )
    except HTTPException as he:
        return error_response(
            message=he.detail,
            code="ACCESS_DENIED" if he.status_code == 403 else "WORKSPACE_ACCESS_ERROR",
            status_code=he.status_code
        )
    except Exception as e:
        logger.error(f"Error retrieving analysis progress for {analysis_id}: {e}", exc_info=True)
        return error_response(
            message="Failed to retrieve analysis progress.",
            code="PROGRESS_LOOKUP_FAILED",
            details=str(e)
        )

@router.get("/{analysis_id}/review-questions")
async def get_review_questions(analysis_id: str, authenticated_user_id: Optional[str] = Depends(get_optional_user_id)):
    try:
        session = await AnalysisService.require_session_access(analysis_id, authenticated_user_id)
    except HTTPException as he:
        return error_response(
            message=he.detail,
            code="ACCESS_DENIED" if he.status_code == 403 else "WORKSPACE_ACCESS_ERROR",
            status_code=he.status_code
        )
    return success_response(
        data={
            "analysis_id": analysis_id,
            "questions": session.get("review_questions") or [],
            "review_policy": AnalysisService.review_policy(session),
        },
        message="Review questions retrieved successfully.",
    )

@router.post("/{analysis_id}/review-questions/{question_id}/answer")
async def answer_review_question(analysis_id: str, question_id: str, request: ReviewAnswerRequest, authenticated_user_id: Optional[str] = Depends(get_optional_user_id)):
    try:
        await AnalysisService.require_session_access(analysis_id, authenticated_user_id)
        answer = await AnalysisService.answer_review_question(
            analysis_id,
            question_id,
            request.action,
            request.response,
            request.finding_id,
        )
        return success_response(data=answer, message="Review response recorded successfully.")
    except HTTPException as he:
        return error_response(
            message=he.detail,
            code="ACCESS_DENIED" if he.status_code == 403 else "REVIEW_RESPONSE_ERROR",
            status_code=he.status_code
        )

@router.get("/{analysis_id}/result")
async def get_analysis_result(analysis_id: str, authenticated_user_id: Optional[str] = Depends(get_optional_user_id)):
    try:
        session = await AnalysisService.require_session_access(analysis_id, authenticated_user_id)
        if not session.get("parsed_json"):
            return error_response(message="Parse the document before requesting a result.", code="RESULT_NOT_READY", status_code=400)

        return success_response(
            data={
                "analysis_id": analysis_id,
                "patient_id": session.get("patient_id"),
                "status": session.get("status"),
                "report_type": (session.get("parsed_json") or {}).get("report_type"),
                "patient_metadata": (session.get("parsed_json") or {}).get("patient_metadata"),
                "abnormal_findings": session.get("abnormal_findings") or [],
                "comparison_context": session.get("comparison_context") or {},
                "risk_assessment": session.get("risk_assessment") or {},
                "consultation_advice": session.get("consultation_advice") or {},
                "summary_report": session.get("summary_report"),
                "validation_status": session.get("validation_status") or {},
                "review_required": session.get("review_required", False),
                "review_reasons": session.get("review_reasons") or [],
                "review_questions": session.get("review_questions") or [],
                "review_policy": AnalysisService.review_policy(session),
            },
            message="Analysis result retrieved successfully.",
        )
    except HTTPException as he:
        return error_response(
            message=he.detail,
            code="ACCESS_DENIED" if he.status_code == 403 else "WORKSPACE_ACCESS_ERROR",
            status_code=he.status_code
        )
    except Exception as e:
        logger.error(f"Error retrieving analysis result for {analysis_id}: {e}", exc_info=True)
        return error_response(message="Failed to retrieve analysis result.", code="RESULT_LOOKUP_FAILED", details=str(e))

@router.post("/quick-start")
async def quick_start_analysis(
    file: UploadFile = File(...),
    patient_id: Optional[str] = Form(None),
    title: Optional[str] = Form(None),
    authenticated_user_id: Optional[str] = Depends(get_optional_user_id),
):
    if not patient_id or not patient_id.strip():
        return error_response(message="patient_id is required for quick start analysis.", code="PATIENT_ID_REQUIRED", status_code=400)
    try:
        session = await AnalysisService.create_session(patient_id=patient_id.strip(), title=title, user_id=authenticated_user_id)
        session = await AnalysisService.upload_document_to_session(session["analysis_id"], file)
        return success_response(
            data=session,
            message="Analysis workspace initialized and document uploaded successfully."
        )
    except HTTPException as he:
        return error_response(
            message=he.detail,
            code="ACCESS_DENIED" if he.status_code == 403 else "QUICK_START_HTTP_ERROR",
            status_code=he.status_code
        )
    except Exception as e:
        logger.error(f"Error in quick start analysis: {e}", exc_info=True)
        return error_response(
            message="Quick start analysis failed.",
            code="QUICK_START_FAILED",
            details=str(e)
        )

@router.get("/sessions")
async def list_analysis_sessions(patient_id: Optional[str] = Query(None), authenticated_user_id: Optional[str] = Depends(get_optional_user_id)):
    try:
        if patient_id:
            await PatientService.require_patient_access(patient_id, authenticated_user_id)
        sessions = await AnalysisService.list_sessions(patient_id=patient_id, user_id=authenticated_user_id)
        return success_response(
            data=sessions,
            message=f"Retrieved {len(sessions)} analysis workspaces."
        )
    except HTTPException as he:
        return error_response(
            message=he.detail,
            code="ACCESS_DENIED" if he.status_code == 403 else "FETCH_SESSIONS_FAILED",
            status_code=he.status_code
        )
    except Exception as e:
        logger.error(f"Error listing analysis sessions: {e}", exc_info=True)
        return error_response(
            message="Failed to retrieve analysis workspaces.",
            code="FETCH_SESSIONS_FAILED",
            details=str(e)
        )

@router.get("/{analysis_id}")
async def get_analysis_workspace(analysis_id: str, authenticated_user_id: Optional[str] = Depends(get_optional_user_id)):
    try:
        session = await AnalysisService.require_session_access(analysis_id, authenticated_user_id)
        return success_response(
            data=session,
            message="Workspace retrieved successfully."
        )
    except HTTPException as he:
        return error_response(
            message=he.detail,
            code="ACCESS_DENIED" if he.status_code == 403 else "WORKSPACE_ACCESS_ERROR",
            status_code=he.status_code
        )
    except Exception as e:
        logger.error(f"Error retrieving workspace {analysis_id}: {e}", exc_info=True)
        return error_response(
            message="Failed to retrieve analysis workspace.",
            code="FETCH_WORKSPACE_FAILED",
            details=str(e)
        )
