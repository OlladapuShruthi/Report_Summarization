from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
from app.core.logger import logger

class Database:
    client: AsyncIOMotorClient = None
    db = None

db_instance = Database()

async def connect_to_mongo():
    if not settings.MONGODB_URL:
        if settings.MONGODB_REQUIRED:
            raise RuntimeError("MONGODB_URL is required but is not configured")
        logger.warning("MONGODB_URL is not configured. Operating in in-memory fallback mode.")
        return
    try:
        logger.info(f"Connecting to MongoDB Atlas (DB: {settings.DATABASE_NAME})...")
        db_instance.client = AsyncIOMotorClient(
            settings.MONGODB_URL,
            serverSelectionTimeoutMS=5000
        )
        db_instance.db = db_instance.client[settings.DATABASE_NAME]
        # Ping check
        await db_instance.client.admin.command('ping')
        logger.info(f"Connected successfully to MongoDB Atlas database '{settings.DATABASE_NAME}'.")
    except Exception as e:
        db_instance.client = None
        db_instance.db = None
        if settings.MONGODB_REQUIRED:
            raise RuntimeError("MongoDB connection failed while MONGODB_REQUIRED=true") from e
        logger.warning(f"MongoDB Atlas connection check warning: {e}. Operating in graceful fallback mode.")

async def close_mongo_connection():
    if db_instance.client:
        db_instance.client.close()
        logger.info("MongoDB connection closed.")

def get_database():
    return db_instance.db

def get_collection(collection_name: str):
    if db_instance.db is not None:
        return db_instance.db[collection_name]
    return None
