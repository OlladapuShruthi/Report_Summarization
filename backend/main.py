from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logger import logger
from app.core.response import success_response
from app.database.mongodb import connect_to_mongo, close_mongo_connection

from app.api.health import router as health_router
from app.api.upload import router as upload_router
from app.api.analysis import router as analysis_router
from app.api.chat import router as chat_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("==================================================================")
    logger.info(f"Starting {settings.PROJECT_NAME} Backend (FastAPI)...")
    logger.info(f"Connecting to MongoDB database: {settings.DATABASE_NAME}")
    await connect_to_mongo()
    logger.info("==================================================================")
    yield
    logger.info("Shutting down Medical Report Assistant Backend...")
    await close_mongo_connection()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Industry-Grade AI Medical Report Assistant API Server",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for Frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(health_router, prefix=settings.API_V1_STR, tags=["Health Telemetry"])
app.include_router(analysis_router, prefix=f"{settings.API_V1_STR}/analysis", tags=["Analysis Workspaces"])
app.include_router(upload_router, prefix=settings.API_V1_STR, tags=["Legacy Uploads"])
app.include_router(chat_router, prefix=f"{settings.API_V1_STR}/chat", tags=["Chat & Q&A"])

@app.get("/")
async def root():
    return success_response(
        data={
            "service": settings.PROJECT_NAME,
            "version": "1.0.0",
            "docs": "/docs",
            "health": f"{settings.API_V1_STR}/health"
        },
        message="Welcome to AI Medical Report Assistant API Server"
    )
