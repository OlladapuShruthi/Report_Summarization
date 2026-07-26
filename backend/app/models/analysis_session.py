from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict

class PipelineStatus(str, Enum):
    CREATED = "created"
    UPLOADED = "uploaded"
    PARSING = "parsing"
    PARSED = "parsed"
    ANALYZING = "analyzing"
    VALIDATED = "validated"
    COMPLETED = "completed"
    FAILED = "failed"

class AnalysisSessionBase(BaseModel):
    patient_id: Optional[str] = None
    title: Optional[str] = "Clinical Analysis Session"

class AnalysisSessionCreate(AnalysisSessionBase):
    analysis_id: str
    status: PipelineStatus = PipelineStatus.CREATED
    created_at: datetime = Field(default_factory=datetime.utcnow)

class AnalysisSessionResponse(AnalysisSessionBase):
    analysis_id: str
    status: str
    document_info: Optional[Dict[str, Any]] = None
    raw_text: Optional[str] = None
    cleaned_text: Optional[str] = None
    parsed_json: Optional[Dict[str, Any]] = None
    parser_metadata: Optional[Dict[str, Any]] = None
    abnormal_findings: Optional[List[Dict[str, Any]]] = None
    risk_assessment: Optional[Dict[str, Any]] = None
    consultation_advice: Optional[str] = None
    summary_report: Optional[str] = None
    validation_status: Optional[Dict[str, Any]] = None
    retry_count: int = 0
    created_at: str
    updated_at: Optional[str] = None

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )
