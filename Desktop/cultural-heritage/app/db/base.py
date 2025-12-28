# app/db/base.py
from sqlalchemy.orm import declarative_base

# shared Base for SQLAlchemy models
Base = declarative_base()
