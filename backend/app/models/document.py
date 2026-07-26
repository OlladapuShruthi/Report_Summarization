from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

class DocumentBase(BaseModel):
    original_filename: str
    content_type: str
    file_size: int

class DocumentCreate(DocumentBase):
    analysis_id: str
    file_id: str
    stored_filename: str
    file_path: str
    status: str = "uploaded"
    created_at: datetime = Field(default_factory=datetime.utcnow)

class DocumentResponse(DocumentBase):
    analysis_id: str
    file_id: str
    stored_filename: str
    file_path: str
    status: str
    created_at: str

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )
