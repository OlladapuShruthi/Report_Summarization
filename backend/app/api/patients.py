from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.response import error_response, success_response
from app.models.patient import PatientCreate
from app.services.patient_service import PatientService
from app.services.analysis_service import AnalysisService
from app.services.finding_event_service import FindingEventService
from app.services.human_confirmation_service import HumanConfirmationService
from app.services.finding_service import FindingService
from app.core.security import get_current_user_id as get_optional_user_id

router = APIRouter()


@router.post("")
async def create_patient(patient: PatientCreate, authenticated_user_id: Optional[str] = Depends(get_optional_user_id)):
    try:
        if authenticated_user_id and patient.user_id and patient.user_id != authenticated_user_id:
            return error_response(message="Patient ownership does not match the authenticated account.", code="PATIENT_OWNERSHIP_MISMATCH", status_code=403)
        created = await PatientService.create_patient(
            display_name=patient.display_name,
            date_of_birth=patient.date_of_birth,
            sex=patient.sex,
            user_id=authenticated_user_id or patient.user_id,
        )
        return success_response(data=created, message="Patient profile created successfully.")
    except Exception as exc:
        return error_response(message="Failed to create patient profile.", code="PATIENT_CREATION_FAILED", details=str(exc))


@router.get("")
async def list_patients(user_id: Optional[str] = Query(default=None), authenticated_user_id: Optional[str] = Depends(get_optional_user_id)):
    """List patients. Enforces authenticated account identity."""
    try:
        if authenticated_user_id and user_id and user_id != authenticated_user_id:
            return error_response(message="Requested user_id does not match the authenticated account.", code="FORBIDDEN", status_code=403)
        effective_user_id = authenticated_user_id or user_id
        patients = await PatientService.list_patients(user_id=effective_user_id)
        return success_response(data=patients, message=f"Retrieved {len(patients)} patient profile(s).")
    except Exception as exc:
        return error_response(message="Failed to retrieve patient profiles.", code="PATIENT_LIST_FAILED", details=str(exc))


@router.delete("/{patient_id}")
async def delete_patient(patient_id: str, authenticated_user_id: Optional[str] = Depends(get_optional_user_id)):
    try:
        await PatientService.require_patient_access(patient_id, authenticated_user_id)
        await PatientService.delete_patient(patient_id)
        return success_response(data=None, message="Patient profile deleted successfully.")
    except HTTPException as exc:
        return error_response(message=exc.detail, code="ACCESS_DENIED" if exc.status_code == 403 else "PATIENT_NOT_FOUND", status_code=exc.status_code)
    except Exception as exc:
        return error_response(message="Failed to delete patient profile.", code="PATIENT_DELETE_FAILED", details=str(exc))


@router.get("/{patient_id}/timeline")
async def get_patient_timeline(patient_id: str, authenticated_user_id: Optional[str] = Depends(get_optional_user_id)):
    try:
        patient = await PatientService.require_patient_access(patient_id, authenticated_user_id)
        sessions = await AnalysisService.list_sessions(patient_id=patient_id)
        finding_events = await FindingEventService.list_for_patient(patient_id)
        findings = await FindingService.list_for_patient(patient_id)
        human_confirmations = await HumanConfirmationService.list_for_patient(patient_id)
        timeline = []
        for session in sessions:
            parsed_json = session.get("parsed_json") or {}
            metadata = parsed_json.get("patient_metadata") or {}
            timeline.append(
                {
                    "analysis_id": session.get("analysis_id"),
                    "date": metadata.get("report_date") or session.get("created_at"),
                    "title": session.get("title"),
                    "status": session.get("status"),
                    "report_type": parsed_json.get("report_type"),
                    "comparison_context": session.get("comparison_context") or {},
                }
            )
        return success_response(
            data={
                "patient": patient,
                "reports": timeline,
                "finding_events": finding_events,
                "findings": findings,
                "human_confirmations": human_confirmations,
            },
            message="Patient timeline retrieved successfully.",
        )
    except HTTPException as exc:
        return error_response(message=exc.detail, code="ACCESS_DENIED" if exc.status_code == 403 else "PATIENT_NOT_FOUND", status_code=exc.status_code)
    except Exception as exc:
        return error_response(message="Failed to retrieve patient timeline.", code="TIMELINE_LOOKUP_FAILED", details=str(exc))


@router.get("/{patient_id}")
async def get_patient(patient_id: str, authenticated_user_id: Optional[str] = Depends(get_optional_user_id)):
    try:
        patient = await PatientService.require_patient_access(patient_id, authenticated_user_id)
        return success_response(data=patient, message="Patient profile retrieved successfully.")
    except HTTPException as exc:
        return error_response(message=exc.detail, code="ACCESS_DENIED" if exc.status_code == 403 else "PATIENT_NOT_FOUND", status_code=exc.status_code)
