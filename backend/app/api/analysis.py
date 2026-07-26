from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.services.analysis_service import AnalysisService
from app.core.response import success_response, error_response
from app.core.logger import logger

router = APIRouter()

@router.post("/create")
async def create_analysis_workspace(patient_id: Optional[str] = Form(None), title: Optional[str] = Form(None)):
    try:
        session = await AnalysisService.create_session(patient_id=patient_id, title=title)
        return success_response(
            data=session,
            message="Analysis workspace initialized successfully."
        )
    except Exception as e:
        logger.error(f"Error creating analysis workspace: {e}", exc_info=True)
        return error_response(
            message="Failed to initialize analysis workspace.",
            code="WORKSPACE_CREATION_FAILED",
            details=str(e)
        )

@router.post("/{analysis_id}/upload")
async def upload_report_to_workspace(analysis_id: str, file: UploadFile = File(...)):
    try:
        updated_session = await AnalysisService.upload_document_to_session(analysis_id, file)
        return success_response(
            data=updated_session,
            message=f"Medical report uploaded successfully to workspace '{analysis_id}'."
        )
    except HTTPException as he:
        return error_response(
            message=he.detail,
            code="UPLOAD_HTTP_ERROR"
        )
    except Exception as e:
        logger.error(f"Error uploading report to workspace {analysis_id}: {e}", exc_info=True)
        return error_response(
            message="Document upload failed.",
            code="DOCUMENT_UPLOAD_FAILED",
            details=str(e)
        )

@router.post("/quick-start")
async def quick_start_analysis(
    file: UploadFile = File(...),
    patient_id: Optional[str] = Form(None),
    title: Optional[str] = Form(None)
):
    try:
        session = await AnalysisService.quick_start_session(file, patient_id=patient_id, title=title)
        return success_response(
            data=session,
            message="Analysis workspace initialized and document uploaded successfully."
        )
    except HTTPException as he:
        return error_response(
            message=he.detail,
            code="QUICK_START_HTTP_ERROR"
        )
    except Exception as e:
        logger.error(f"Error in quick start analysis: {e}", exc_info=True)
        return error_response(
            message="Quick start analysis failed.",
            code="QUICK_START_FAILED",
            details=str(e)
        )

@router.get("/sessions")
async def list_analysis_sessions():
    try:
        sessions = await AnalysisService.list_sessions()
        return success_response(
            data=sessions,
            message=f"Retrieved {len(sessions)} analysis workspaces."
        )
    except Exception as e:
        logger.error(f"Error listing analysis sessions: {e}", exc_info=True)
        return error_response(
            message="Failed to retrieve analysis workspaces.",
            code="FETCH_SESSIONS_FAILED",
            details=str(e)
        )

@router.get("/{analysis_id}")
async def get_analysis_workspace(analysis_id: str):
    try:
        session = await AnalysisService.get_session_by_id(analysis_id)
        if not session:
            return error_response(
                message=f"Analysis workspace '{analysis_id}' not found.",
                code="WORKSPACE_NOT_FOUND"
            )
        return success_response(
            data=session,
            message="Workspace retrieved successfully."
        )
    except Exception as e:
        logger.error(f"Error retrieving workspace {analysis_id}: {e}", exc_info=True)
        return error_response(
            message="Failed to retrieve analysis workspace.",
            code="FETCH_WORKSPACE_FAILED",
            details=str(e)
        )
