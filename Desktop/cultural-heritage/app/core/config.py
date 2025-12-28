"""
Configuration settings for the Cultural Heritage project.
This file defines database connection URLs and environment-level constants.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # --------------------------------------------------------------------------
    # Application Metadata
    # --------------------------------------------------------------------------
    PROJECT_NAME: str = "Cultural Heritage Management System"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = (
        "A DBMS project demonstrating polyglot persistence — "
        "PostgreSQL for structured data and MongoDB for unstructured heritage data."
    )

    # --------------------------------------------------------------------------
    # PostgreSQL Configuration (Async)
    # --------------------------------------------------------------------------
    POSTGRES_USER: str = "heritage_app_user"               # ← replace if your username differs
    POSTGRES_PASSWORD: str = "anuj0528"           # ← replace if your password differs
    POSTGRES_HOST: str = "127.0.0.1"              # ← 127.0.0.1 avoids DNS lookup errors
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "cultural_heritage"

    @property
    def POSTGRES_URL(self) -> str:
        """
        Build async SQLAlchemy connection URL for PostgreSQL.
        """
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    # --------------------------------------------------------------------------
    # MongoDB Configuration
    # --------------------------------------------------------------------------
    MONGO_USER: str | None = None  # optional — skip if no auth
    MONGO_PASSWORD: str | None = None
    MONGO_HOST: str = "127.0.0.1"
    MONGO_PORT: int = 27017
    MONGO_DB_NAME: str = "heritage_mongo"

    @property
    def MONGO_URL(self) -> str:
        """
        Construct MongoDB URI.
        """
        if self.MONGO_USER and self.MONGO_PASSWORD:
            return f"mongodb://{self.MONGO_USER}:{self.MONGO_PASSWORD}@{self.MONGO_HOST}:{self.MONGO_PORT}"
        return f"mongodb://{self.MONGO_HOST}:{self.MONGO_PORT}"

    # --------------------------------------------------------------------------
    # Misc Settings
    # --------------------------------------------------------------------------
    DEBUG: bool = True


# Singleton settings instance for app-wide use
@lru_cache()
def get_settings() -> Settings:
    return Settings()


# Expose settings directly for import convenience
settings = get_settings()
