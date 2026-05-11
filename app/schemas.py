# schemas.py — Pydantic models that define what the API accepts and returns
# These are separate from SQLAlchemy models — one is for the DB, the other for the API layer

from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional

# Used when CREATING a new application — these are the fields the client must/can send
class ApplicationCreate(BaseModel):
    company: str
    role: str
    applied_date: date
    job_url: Optional[str] = None
    platform: Optional[str] = None
    status: str = "applied"
    notes: Optional[str] = None

# Used when UPDATING — every field is optional since you might only update status
class ApplicationUpdate(BaseModel):
    company: Optional[str] = None
    role: Optional[str] = None
    applied_date: Optional[date] = None
    job_url: Optional[str] = None
    platform: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None

# Used in RESPONSES — includes the DB-generated fields like id and created_at
class ApplicationResponse(BaseModel):
    id: int
    company: str
    role: str
    applied_date: date
    job_url: Optional[str] = None
    platform: Optional[str] = None
    status: str
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # This tells Pydantic to read data from SQLAlchemy objects, not just plain dicts
    model_config = {"from_attributes": True}