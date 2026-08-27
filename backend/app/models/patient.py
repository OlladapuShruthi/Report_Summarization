from typing import Optional
from pydantic import BaseModel, Field


class PatientCreate(BaseModel):
    display_name: str = Field(min_length=1, max_length=120)
    date_of_birth: Optional[str] = None
    sex: Optional[str] = Field(default=None, pattern="^(MALE|FEMALE|OTHER|UNKNOWN)$")
    user_id: Optional[str] = None  # Owning user account


class PatientResponse(PatientCreate):
    patient_id: str
    created_at: str
    updated_at: str
