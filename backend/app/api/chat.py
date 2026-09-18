from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.core.response import success_response, error_response
from app.services.chat_service import ChatService
from app.services.patient_service import PatientService
from app.core.security import get_current_user_id as get_optional_user_id

router = APIRouter()
chat_service = ChatService()


class ChatMessageRequest(BaseModel):
    patient_id: str
    message: str
    analysis_id: Optional[str] = None


@router.get("/status")
async def chat_status():
    return success_response(
        data={"module": "chat", "status": "active", "rag_enabled": True},
        message="Chat & RAG subsystem is active."
    )


@router.post("/message")
async def send_chat_message(request: ChatMessageRequest, authenticated_user_id: Optional[str] = Depends(get_optional_user_id)):
    try:
        if not request.patient_id:
            return error_response(message="patient_id is required", code="PATIENT_ID_REQUIRED")
        if not request.message or not request.message.strip():
            return error_response(message="message cannot be empty", code="MESSAGE_EMPTY")
        await PatientService.require_patient_access(request.patient_id, authenticated_user_id)

        result = await chat_service.process_chat_message(
            patient_id=request.patient_id,
            message=request.message,
            analysis_id=request.analysis_id
        )

        return success_response(
            data=result,
            message="Chat message processed successfully."
        )
    except HTTPException as exc:
        return error_response(message=exc.detail, code="ACCESS_DENIED" if exc.status_code == 403 else "CHAT_ACCESS_ERROR", status_code=exc.status_code)
    except Exception as exc:
        return error_response(
            message="Failed to process chat message.",
            code="CHAT_PROCESSING_FAILED",
            details=str(exc)
        )


@router.get("/history/{patient_id}")
async def get_chat_history(patient_id: str, authenticated_user_id: Optional[str] = Depends(get_optional_user_id)):
    try:
        await PatientService.require_patient_access(patient_id, authenticated_user_id)
        history = await chat_service.get_chat_history(patient_id)
        return success_response(
            data=history,
            message=f"Retrieved {len(history)} chat message(s) for patient."
        )
    except HTTPException as exc:
        return error_response(message=exc.detail, code="ACCESS_DENIED" if exc.status_code == 403 else "CHAT_ACCESS_ERROR", status_code=exc.status_code)
    except Exception as exc:
        return error_response(
            message="Failed to retrieve chat history.",
            code="CHAT_HISTORY_FAILED",
            details=str(exc)
        )


@router.delete("/history/{patient_id}")
async def clear_chat_history(patient_id: str, authenticated_user_id: Optional[str] = Depends(get_optional_user_id)):
    try:
        await PatientService.require_patient_access(patient_id, authenticated_user_id)
        await chat_service.clear_chat_history(patient_id)
        return success_response(
            data={"cleared": True},
            message="Chat history cleared successfully."
        )
    except HTTPException as exc:
        return error_response(message=exc.detail, code="ACCESS_DENIED" if exc.status_code == 403 else "CHAT_ACCESS_ERROR", status_code=exc.status_code)
    except Exception as exc:
        return error_response(
            message="Failed to clear chat history.",
            code="CHAT_CLEAR_FAILED",
            details=str(exc)
        )
