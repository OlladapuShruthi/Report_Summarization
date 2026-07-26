import os
import uuid
from fastapi import UploadFile, HTTPException
from app.core.config import settings

async def save_uploaded_file(file: UploadFile) -> dict:
    # 1. Validate file extension
    filename = file.filename or "report"
    ext = os.path.splitext(filename)[1].lower()
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format '{ext}'. Allowed formats: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )

    # 2. Generate unique file identifier
    file_id = str(uuid.uuid4())
    stored_filename = f"{file_id}_{filename}"
    file_path = os.path.join(settings.UPLOAD_DIR, stored_filename)

    # 3. Read content
    content = await file.read()
    size_mb = len(content) / (1024 * 1024)
    if size_mb > settings.MAX_FILE_SIZE_MB:
        raise HTTPException(
            status_code=400,
            detail=f"File exceeds maximum allowed size of {settings.MAX_FILE_SIZE_MB}MB."
        )

    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "wb") as out_file:
        out_file.write(content)

    return {
        "file_id": file_id,
        "original_filename": filename,
        "stored_filename": stored_filename,
        "file_path": file_path,
        "file_size": len(content),
        "content_type": file.content_type or "application/octet-stream"
    }
