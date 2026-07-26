import re
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator, model_validator


class ReferenceRange(BaseModel):
    low: Optional[float] = None
    high: Optional[float] = None
    text: Optional[str] = None

    @model_validator(mode="after")
    def validate_range_order(self):
        if self.low is not None and self.high is not None and self.low > self.high:
            raise ValueError("reference_range.low cannot be greater than reference_range.high")
        return self


class ConfidenceModel(BaseModel):
    text_extraction: float = 0.0
    classification: float = 0.0
    entity_extraction: float = 0.0
    overall: float = 0.5

    @model_validator(mode="after")
    def validate_confidence_bounds(self):
        for field_name in ("text_extraction", "classification", "entity_extraction", "overall"):
            value = getattr(self, field_name)
            if value < 0.0 or value > 1.0:
                raise ValueError(f"confidence.{field_name} must be between 0 and 1")
        return self


class LabResultModel(BaseModel):
    test_name: str
    value: float
    unit: Optional[str] = None
    reference_range: Optional[ReferenceRange] = None
    category: Optional[str] = None
    is_outside_reference: Optional[bool] = None
    raw_line: Optional[str] = None

    @field_validator("value")
    @classmethod
    def validate_non_negative_value(cls, value: float) -> float:
        if value < 0:
            raise ValueError("lab result value cannot be negative")
        return value

    @field_validator("unit")
    @classmethod
    def validate_unit_format(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value

        normalized = value.strip()
        if not re.fullmatch(r"[A-Za-z0-9%./^+-]+(?:\s*[A-Za-z0-9%./^+-]+)*", normalized):
            raise ValueError("lab result unit contains invalid characters")
        return normalized

    @model_validator(mode="after")
    def validate_outside_reference_flag(self):
        if self.reference_range is None:
            return self
        if self.reference_range.low is None or self.reference_range.high is None:
            return self

        expected = self.value < self.reference_range.low or self.value > self.reference_range.high
        if self.is_outside_reference is not None and self.is_outside_reference != expected:
            raise ValueError("is_outside_reference does not match value and reference_range")
        return self


class NarrativeImpressionModel(BaseModel):
    section: str = "narrative"
    text: str


class MedicalJSONModel(BaseModel):
    schema_version: str = "1.0"
    report_type: str
    patient_metadata: Dict[str, Any] = Field(default_factory=dict)
    lab_results: List[LabResultModel] = Field(default_factory=list)
    narrative_impressions: List[NarrativeImpressionModel] = Field(default_factory=list)
    confidence: ConfidenceModel = Field(default_factory=ConfidenceModel)
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

    @model_validator(mode="after")
    def validate_structured_content(self):
        if not self.lab_results and not self.narrative_impressions:
            raise ValueError("medical JSON must include lab_results or narrative_impressions")

        seen_tests = set()
        for result in self.lab_results:
            key = (result.test_name.lower(), result.value, result.unit)
            if key in seen_tests:
                raise ValueError(f"duplicate lab result detected: {result.test_name}")
            seen_tests.add(key)

        return self


class MedicalJSONValidator:
    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return MedicalJSONModel(**data).model_dump()
