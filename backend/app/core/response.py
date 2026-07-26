from typing import Any, Optional
from pydantic import BaseModel

class ErrorDetail(BaseModel):
    code: str
    details: Optional[Any] = None

class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None
    error: Optional[ErrorDetail] = None

def success_response(data: Any = None, message: str = "Operation successful") -> dict:
    return APIResponse(
        success=True,
        message=message,
        data=data,
        error=None
    ).model_dump()

def error_response(message: str = "Operation failed", code: str = "BAD_REQUEST", details: Any = None) -> dict:
    return APIResponse(
        success=False,
        message=message,
        data=None,
        error=ErrorDetail(code=code, details=details)
    ).model_dump()
