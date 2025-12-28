# app/db/postgres.py
import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.db.base import Base

logger = logging.getLogger("postgres")

DATABASE_URL = (
    f"postgresql+asyncpg://{settings.POSTGRES_USER}:"
    f"{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:"
    f"{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
)

# Create async engine
engine = create_async_engine(DATABASE_URL, echo=False, future=True)

# Session factory
AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def init_postgres():
    """
    Create tables if they don't exist and test connection.
    """
    try:
        async with engine.begin() as conn:
            # create tables based on Base metadata (models import will register tables)
            await conn.run_sync(Base.metadata.create_all)
        logger.info("✅ PostgreSQL tables created (if not existed).")
    except Exception as e:
        logger.error(f"❌ init_postgres failed: {e}")
        raise


# Dependency for routes
async def get_postgres_session():
    """
    Async dependency that yields a SQLAlchemy session.
    """
    async with AsyncSessionLocal() as session:
        yield session
