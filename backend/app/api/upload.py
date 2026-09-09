from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from app.utils.file_handler import save_uploaded_file
from app.database.mongodb import get_database
from app.models.document import DocumentResponse
from app.core.security import get_optional_user_id

router = APIRouter()

# In-memory document storage fallback if MongoDB is down during early dev
in_memory_documents = []

@router.post("/upload", response_model=DocumentResponse)
async def upload_document(file: UploadFile = File(...), authenticated_user_id: Optional[str] = Depends(get_optional_user_id)):
    saved_file_info = await save_uploaded_file(file)
    
    doc_record = {
        "file_id": saved_file_info["file_id"],
        "user_id": authenticated_user_id,
        "original_filename": saved_file_info["original_filename"],
        "stored_filename": saved_file_info["stored_filename"],
        "file_path": saved_file_info["file_path"],
        "file_size": saved_file_info["file_size"],
        "content_type": saved_file_info["content_type"],
        "status": "uploaded",
        "created_at": datetime.utcnow().isoformat()
    }

    db = get_database()
    if db is not None:
        try:
            await db.documents.insert_one(dict(doc_record))
        except Exception as e:
            # Fallback
            in_memory_documents.append(doc_record)
    else:
        in_memory_documents.append(doc_record)

    return doc_record

@router.get("/documents", response_model=List[DocumentResponse])
async def list_documents(authenticated_user_id: Optional[str] = Depends(get_optional_user_id)):
    db = get_database()
    documents = []

    if db is not None:
        try:
            query = {"user_id": authenticated_user_id} if authenticated_user_id else {"user_id": None}
            cursor = db.documents.find(query).sort("created_at", -1)
            async for doc in cursor:
                doc["_id"] = str(doc["_id"])
                documents.append(doc)
            return documents
        except Exception:
            pass

    # Fallback return in-memory filtered by user_id
    filtered = [d for d in in_memory_documents if d.get("user_id") == authenticated_user_id]
    return sorted(filtered, key=lambda x: x["created_at"], reverse=True)
