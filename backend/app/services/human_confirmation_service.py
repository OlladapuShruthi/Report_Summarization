from datetime import datetime
from typing import Any, Dict, List, Optional

from app.database.mongodb import get_database


in_memory_human_confirmations: List[Dict[str, Any]] = []


class HumanConfirmationService:
    @staticmethod
    async def record(
        patient_id: Optional[str],
        analysis_id: str,
        question_id: str,
        action: str,
        response: Optional[str],
        finding_id: Optional[str],
        evidence_type: str,
    ) -> Dict[str, Any]:
        confirmation = {
            "confirmation_id": f"{analysis_id}:{question_id}",
            "patient_id": patient_id,
            "analysis_id": analysis_id,
            "question_id": question_id,
            "finding_id": finding_id,
            "action": action,
            "response": response,
            "evidence_type": evidence_type,
            "created_at": datetime.utcnow().isoformat(),
        }
        db = get_database()
        if db is not None:
            try:
                await db.human_confirmations.update_one(
                    {"confirmation_id": confirmation["confirmation_id"]},
                    {"$set": confirmation},
                    upsert=True,
                )
                return confirmation
            except Exception:
                pass

        for index, existing in enumerate(in_memory_human_confirmations):
            if existing.get("confirmation_id") == confirmation["confirmation_id"]:
                in_memory_human_confirmations[index] = confirmation
                return confirmation
        in_memory_human_confirmations.append(confirmation)
        return confirmation

    @staticmethod
    async def list_for_finding(patient_id: str, finding_id: str) -> List[Dict[str, Any]]:
        db = get_database()
        if db is not None:
            try:
                cursor = db.human_confirmations.find({"patient_id": patient_id, "finding_id": finding_id}).sort("created_at", 1)
                confirmations = []
                async for item in cursor:
                    item["_id"] = str(item["_id"])
                    confirmations.append(item)
                return confirmations
            except Exception:
                pass
        return [
            item
            for item in in_memory_human_confirmations
            if item.get("patient_id") == patient_id and item.get("finding_id") == finding_id
        ]

    @staticmethod
    async def list_for_patient(patient_id: str) -> List[Dict[str, Any]]:
        db = get_database()
        if db is not None:
            try:
                cursor = db.human_confirmations.find({"patient_id": patient_id}).sort("created_at", 1)
                confirmations = []
                async for item in cursor:
                    item["_id"] = str(item["_id"])
                    confirmations.append(item)
                return confirmations
            except Exception:
                pass
        return [
            item for item in in_memory_human_confirmations if item.get("patient_id") == patient_id
        ]
