from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator


class ReferenceRange(BaseModel):
    low: Optional[float] = None
    high: Optional[float] = None


class LabResultModel(BaseModel):
    test_name: str
    value: float
    unit: Optional[str] = None
    reference_range: Optional[ReferenceRange] = None
    raw_line: Optional[str] = None


class NarrativeImpressionModel(BaseModel):
    section: str = "narrative"
    text: str


class MedicalJSONModel(BaseModel):
    schema_version: str = "1.0"
    report_type: str
    patient_metadata: Dict[str, Any] = Field(default_factory=dict)
    lab_results: List[LabResultModel] = Field(default_factory=list)
    narrative_impressions: List[NarrativeImpressionModel] = Field(default_factory=list)
    confidence: Dict[str, float] = Field(default_factory=dict)
    parser_metadata: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("schema_version")
    @classmethod
    def validate_schema_version(cls, value: str) -> str:
        if value != "1.0":
            raise ValueError("Medical JSON schema_version must be 1.0")
        return value

    @field_validator("report_type")
    @classmethod
    def validate_report_type(cls, value: str) -> str:
        allowed = {
            "LAB_REPORT_CBC",
            "LAB_REPORT_THYROID",
            "LAB_REPORT_LIPID",
            "LAB_REPORT_LFT",
            "LAB_REPORT_KFT",
            "RADIOLOGY_REPORT",
            "DISCHARGE_SUMMARY",
            "UNKNOWN",
        }
        if value not in allowed:
            raise ValueError(f"Unsupported report_type: {value}")
        return value


class MedicalJSONValidator:
    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return MedicalJSONModel(**data).model_dump()
