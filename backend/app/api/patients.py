from typing import Optional
from fastapi import APIRouter, HTTPException, Query

from app.core.response import error_response, success_response
from app.models.patient import PatientCreate
from app.services.patient_service import PatientService
from app.services.analysis_service import AnalysisService

router = APIRouter()


@router.post("")
async def create_patient(patient: PatientCreate):
    try:
        created = await PatientService.create_patient(
            display_name=patient.display_name,
            date_of_birth=patient.date_of_birth,
            sex=patient.sex,
            user_id=patient.user_id,
        )
        return success_response(data=created, message="Patient profile created successfully.")
    except Exception as exc:
        return error_response(message="Failed to create patient profile.", code="PATIENT_CREATION_FAILED", details=str(exc))


@router.get("")
async def list_patients(user_id: Optional[str] = Query(default=None)):
    """List patients. Pass ?user_id=<id> to filter to a specific account."""
    try:
        patients = await PatientService.list_patients(user_id=user_id)
        return success_response(data=patients, message=f"Retrieved {len(patients)} patient profile(s).")
    except Exception as exc:
        return error_response(message="Failed to retrieve patient profiles.", code="PATIENT_LIST_FAILED", details=str(exc))


@router.get("/{patient_id}/timeline")
async def get_patient_timeline(patient_id: str):
    try:
        patient = await PatientService.require_patient(patient_id)
        sessions = await AnalysisService.list_sessions(patient_id=patient_id)
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
        return success_response(data={"patient": patient, "reports": timeline}, message="Patient timeline retrieved successfully.")
    except HTTPException as exc:
        return error_response(message=exc.detail, code="PATIENT_NOT_FOUND")
    except Exception as exc:
        return error_response(message="Failed to retrieve patient timeline.", code="TIMELINE_LOOKUP_FAILED", details=str(exc))


@router.get("/{patient_id}")
async def get_patient(patient_id: str):
    try:
        patient = await PatientService.require_patient(patient_id)
        return success_response(data=patient, message="Patient profile retrieved successfully.")
    except HTTPException as exc:
        return error_response(message=exc.detail, code="PATIENT_NOT_FOUND")
