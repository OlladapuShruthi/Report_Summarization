from typing import Optional
from pydantic import BaseModel, Field


class PatientCreate(BaseModel):
    # Accept 'name' from frontend as alias for display_name
    display_name: str = Field(..., min_length=1, max_length=120, alias="name")
    date_of_birth: Optional[str] = None
    sex: Optional[str] = Field(default=None, pattern="^(MALE|FEMALE|OTHER|UNKNOWN)$")
    user_id: Optional[str] = None  # Owning user account

    class Config:
        allow_population_by_field_name = True


class PatientResponse(PatientCreate):
    patient_id: str
    created_at: str
    updated_at: str
