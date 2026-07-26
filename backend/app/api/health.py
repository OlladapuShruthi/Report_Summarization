from datetime import datetime
from fastapi import APIRouter
from app.database.mongodb import get_database
from app.core.config import settings
from app.core.response import success_response

router = APIRouter()

@router.get("/health")
async def check_health():
    db = get_database()
    db_status = "connected"
    
    if db is not None:
        try:
            await db.command("ping")
        except Exception:
            db_status = "disconnected"
    else:
        db_status = "not_configured_or_down"

    health_data = {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "database": db_status,
        "database_name": settings.DATABASE_NAME,
        "timestamp": datetime.utcnow().isoformat()
    }

    return success_response(
        data=health_data,
        message="System telemetry retrieved successfully."
    )
