from fastapi import APIRouter, HTTPException

from app.core.response import error_response, success_response
from app.models.user import UserCreate, UserLogin
from app.services.user_service import UserService

router = APIRouter()


@router.post("/register")
async def register(user_data: UserCreate):
    """Create a new user account."""
    try:
        user = await UserService.register(
            full_name=user_data.full_name,
            email=user_data.email,
            password=user_data.password,
        )
        return success_response(data=user, message="Account created successfully. Welcome!")
    except HTTPException as exc:
        return error_response(message=exc.detail, code="REGISTER_FAILED")
    except Exception as exc:
        return error_response(message="Registration failed. Please try again.", code="REGISTER_ERROR", details=str(exc))


@router.post("/login")
async def login(credentials: UserLogin):
    """Authenticate user and return account data."""
    try:
        user = await UserService.login(
            email=credentials.email,
            password=credentials.password,
        )
        return success_response(data=user, message="Login successful. Welcome back!")
    except HTTPException as exc:
        # Pass through 404 (not found) and 401 (wrong password) with correct status codes
        return error_response(
            message=exc.detail,
            code="AUTH_FAILED" if exc.status_code == 401 else "USER_NOT_FOUND",
        )
    except Exception as exc:
        return error_response(message="Login failed. Please try again.", code="LOGIN_ERROR", details=str(exc))
