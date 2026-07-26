import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import UploadFile, HTTPException

from app.database.mongodb import get_database
from app.models.analysis_session import PipelineStatus
from app.utils.file_handler import save_uploaded_file
from app.core.logger import logger

# In-memory session store fallback if Mongo Atlas connection is degraded
in_memory_sessions: Dict[str, Dict[str, Any]] = {}

class AnalysisService:

    @staticmethod
    async def create_session(patient_id: Optional[str] = None, title: Optional[str] = "Clinical Analysis Session") -> Dict[str, Any]:
        analysis_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        
        session_data = {
            "analysis_id": analysis_id,
            "patient_id": patient_id,
            "title": title or "Clinical Analysis Session",
            "status": PipelineStatus.CREATED.value,
            "document_info": None,
            "parsed_json": None,
            "abnormal_findings": None,
            "risk_assessment": None,
            "consultation_advice": None,
            "summary_report": None,
            "validation_status": None,
            "retry_count": 0,
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

        doc_record = {
            "analysis_id": analysis_id,
            "file_id": saved_file["file_id"],
            "original_filename": saved_file["original_filename"],
            "stored_filename": saved_file["stored_filename"],
            "file_path": saved_file["file_path"],
            "file_size": saved_file["file_size"],
            "content_type": saved_file["content_type"],
            "status": "uploaded",
            "created_at": now
        }

        # 2. Update session
        update_fields = {
            "document_info": doc_record,
            "status": PipelineStatus.UPLOADED.value,
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
    async def quick_start_session(file: UploadFile, patient_id: Optional[str] = None, title: Optional[str] = None) -> Dict[str, Any]:
        # Convenience endpoint: create workspace & upload document in one step
        title = title or f"Analysis - {file.filename}"
        new_session = await AnalysisService.create_session(patient_id=patient_id, title=title)
        updated_session = await AnalysisService.upload_document_to_session(new_session["analysis_id"], file)
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
    async def list_sessions() -> List[Dict[str, Any]]:
        db = get_database()
        sessions = []
        if db is not None:
            try:
                cursor = db.analysis_sessions.find().sort("created_at", -1)
                async for doc in cursor:
                    doc["_id"] = str(doc["_id"])
                    sessions.append(doc)
                return sessions
            except Exception as e:
                logger.warning(f"MongoDB list sessions failed: {e}")

        # Fallback in-memory sessions
        return sorted(list(in_memory_sessions.values()), key=lambda x: x["created_at"], reverse=True)
