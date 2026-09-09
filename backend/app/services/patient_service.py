import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import HTTPException

from app.database.mongodb import get_database

# Mirrors the analysis-session fallback so patient scoping also works without Atlas.
in_memory_patients: Dict[str, Dict[str, Any]] = {}

class PatientService:
    @staticmethod
    async def create_patient(
        display_name: str,
        date_of_birth: Optional[str] = None,
        sex: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        now = datetime.utcnow().isoformat()
        patient = {
            "patient_id": str(uuid.uuid4()),
            "display_name": display_name.strip(),
            "date_of_birth": date_of_birth,
            "sex": sex,
            "user_id": user_id,  # associate with logged-in user account
            "created_at": now,
            "updated_at": now,
        }
        db = get_database()
        if db is not None:
            try:
                await db.patients.insert_one(dict(patient))
            except Exception:
                in_memory_patients[patient["patient_id"]] = patient
        else:
            in_memory_patients[patient["patient_id"]] = patient
        return patient

    @staticmethod
    async def get_patient(patient_id: str) -> Optional[Dict[str, Any]]:
        db = get_database()
        if db is not None:
            try:
                patient = await db.patients.find_one({"patient_id": patient_id})
                if patient:
                    patient["_id"] = str(patient["_id"])
                    return patient
            except Exception:
                pass
        return in_memory_patients.get(patient_id)

    @staticmethod
    async def require_patient(patient_id: str) -> Dict[str, Any]:
        patient = await PatientService.get_patient(patient_id)
        if not patient:
            raise HTTPException(status_code=404, detail=f"Patient '{patient_id}' was not found.")
        return patient

    @staticmethod
    async def require_patient_access(patient_id: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        patient = await PatientService.require_patient(patient_id)
        owner_id = patient.get("user_id")
        if owner_id is not None:
            if not user_id or owner_id != user_id:
                raise HTTPException(status_code=403, detail="You do not have access to this patient record.")
        return patient

    @staticmethod
    async def list_patients(user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List patients. If user_id provided, filter to that account only."""
        db = get_database()
        if db is not None:
            try:
                patients: List[Dict[str, Any]] = []
                # If user_id is provided, return only patients for that user.
                # If user_id is None, return only unassigned/dev patients to prevent cross-user leakage.
                query = {"user_id": user_id} if user_id else {"$or": [{"user_id": None}, {"user_id": {"$exists": False}}]}
                cursor = db.patients.find(query).sort("created_at", -1)
                async for patient in cursor:
                    patient["_id"] = str(patient["_id"])
                    patients.append(patient)
                return patients
            except Exception:
                pass
        # In-memory fallback — filter by user_id
        all_patients = list(in_memory_patients.values())
        if user_id:
            all_patients = [p for p in all_patients if p.get("user_id") == user_id]
        else:
            all_patients = [p for p in all_patients if not p.get("user_id")]
        return sorted(all_patients, key=lambda item: item["created_at"], reverse=True)

    @staticmethod
    async def delete_patient(patient_id: str) -> None:
        """Delete a patient and cascade delete all associated analysis sessions.
        This operates against both MongoDB (if available) and the in‑memory fallback.
        """
        # Local import to avoid circular dependency.
        from app.services.analysis_service import in_memory_sessions
        db = get_database()
        # Delete associated analysis sessions first.
        if db is not None:
            try:
                await db.analysis_sessions.delete_many({"patient_id": patient_id})
            except Exception as e:
                from app.core.logger import logger
                logger.warning(f"MongoDB cascade delete of analysis sessions for patient {patient_id} failed: {e}")
        # In‑memory sessions cleanup.
        sessions_to_delete = [sid for sid, sess in in_memory_sessions.items() if sess.get("patient_id") == patient_id]
        for sid in sessions_to_delete:
            del in_memory_sessions[sid]
        # Delete patient record.
        if db is not None:
            try:
                await db.patients.delete_one({"patient_id": patient_id})
            except Exception as e:
                from app.core.logger import logger
                logger.warning(f"MongoDB delete of patient {patient_id} failed: {e}")
        else:
            in_memory_patients.pop(patient_id, None)
