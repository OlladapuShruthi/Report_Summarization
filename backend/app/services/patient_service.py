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
    async def list_patients(user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List patients. If user_id provided, filter to that account only."""
        db = get_database()
        if db is not None:
            try:
                patients: List[Dict[str, Any]] = []
                query = {"user_id": user_id} if user_id else {}
                cursor = db.patients.find(query).sort("created_at", -1)
                async for patient in cursor:
                    patient["_id"] = str(patient["_id"])
                    patients.append(patient)
                return patients
            except Exception:
                pass
        # In-memory fallback — filter by user_id if provided
        all_patients = list(in_memory_patients.values())
        if user_id:
            all_patients = [p for p in all_patients if p.get("user_id") == user_id]
        return sorted(all_patients, key=lambda item: item["created_at"], reverse=True)
