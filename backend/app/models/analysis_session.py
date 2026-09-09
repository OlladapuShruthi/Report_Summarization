from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, List, Literal
from pydantic import BaseModel, Field, ConfigDict

class PipelineStatus(str, Enum):
    CREATED = "created"
    UPLOADED = "uploaded"
    PARSING = "parsing"
    PARSED = "parsed"
    NEEDS_REVIEW = "needs_review"
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
    review_required: bool = False
    review_reasons: Optional[List[str]] = None
    review_questions: Optional[List[Dict[str, Any]]] = None
    review_policy: Optional[Dict[str, Any]] = None
    comparison_context: Optional[Dict[str, Any]] = None
    abnormal_findings: Optional[List[Dict[str, Any]]] = None
    risk_assessment: Optional[Dict[str, Any]] = None
    consultation_advice: Optional[Dict[str, Any]] = None
    summary_report: Optional[str] = None
    validation_status: Optional[Dict[str, Any]] = None
    execution_log: Optional[List[Dict[str, Any]]] = None
    retry_count: int = 0
    created_at: str
    updated_at: Optional[str] = None

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )


class ReviewAnswerRequest(BaseModel):
    action: Literal["confirm", "no_report", "dismiss", "defer"]
    response: Optional[str] = None
    finding_id: Optional[str] = None
