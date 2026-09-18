from typing import Optional

from fastapi import APIRouter, Depends, HTTPException

from app.core.security import get_current_user_id as get_optional_user_id
from app.services.patient_service import PatientService
from app.core.response import success_response, error_response
from app.database.mongodb import get_database

router = APIRouter()

@router.delete("/{patient_id}/reports/{report_id}")
async def delete_report(
    patient_id: str,
    report_id: str,
    authenticated_user_id: Optional[str] = Depends(get_optional_user_id),
):
    """Delete a specific report (analysis session) for a patient.

    The `report_id` corresponds to the analysis session identifier.
    Only the owner of the patient profile may delete the report.
    """
    try:
        # Verify patient ownership
        await PatientService.require_patient_access(patient_id, authenticated_user_id)
        db = get_database()
        if db is None:
            return error_response(message="Database not available", code="DB_UNAVAILABLE", status_code=503)
        # Delete the analysis session (report)
        result = await db.analysis_sessions.delete_one({"analysis_id": report_id, "patient_id": patient_id})
        if result.deleted_count == 0:
            return error_response(message="Report not found or already deleted", code="REPORT_NOT_FOUND", status_code=404)
        return success_response(data=None, message="Report deleted successfully.")
    except HTTPException as exc:
        return error_response(message=exc.detail, code="ACCESS_DENIED" if exc.status_code == 403 else "REPORT_DELETE_FAILED", status_code=exc.status_code)
    except Exception as exc:
        return error_response(message="Failed to delete report", code="REPORT_DELETE_FAILED", details=str(exc))
