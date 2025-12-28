# app/models/oral_model.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class OralHistoryIn(BaseModel):
    title: str = Field(..., max_length=255)
    narrator: str = Field(..., max_length=255)
    year: Optional[int] = None
    region: Optional[str] = None
    description: Optional[str] = None
    audio_url: Optional[str] = None  # NEW: Audio support

class OralHistoryOut(OralHistoryIn):
    _id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None