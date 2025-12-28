# app/db/mongo.py
import logging
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

logger = logging.getLogger("mongo")

MONGO_CLIENT: Optional[AsyncIOMotorClient] = None
MONGO_DB = None


async def init_mongo():
    """
    Initialize motor client and test connection.
    """
    global MONGO_CLIENT, MONGO_DB
    try:
        logger.info(f"🔗 Connecting to MongoDB: {settings.MONGO_URL}")
        MONGO_CLIENT = AsyncIOMotorClient(settings.MONGO_URL)
        MONGO_DB = MONGO_CLIENT[settings.MONGO_DB_NAME]
        # ping to ensure connection (motor command is async)
        await MONGO_CLIENT.admin.command("ping")
        logger.info("✅ MongoDB connected and ping succeeded.")
    except Exception as e:
        MONGO_CLIENT = None
        MONGO_DB = None
        logger.error(f"❌ MongoDB init failed: {e}")
        raise


def get_mongo_db():
    """
    Return the motor DB object (or None if not connected).
    """
    return MONGO_DB


async def close_mongo_client():
    global MONGO_CLIENT
    try:
        if MONGO_CLIENT:
            MONGO_CLIENT.close()
            MONGO_CLIENT = None
            logger.info("🧹 MongoDB client closed.")
    except Exception as e:
        logger.warning(f"Error closing Mongo client: {e}")
