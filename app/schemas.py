from pydantic import BaseModel
from datetime import date, datetime
from typing import Dict, Optional

class ApplicationCreate(BaseModel):
    company: str
    role: str
    applied_date: date
    job_url: Optional[str] = None
    platform: Optional[str] = None
    status: str = "applied"
    notes: Optional[str] = None

class ApplicationUpdate(BaseModel):
    company: Optional[str] = None
    role: Optional[str] = None
    applied_date: Optional[date] = None
    job_url: Optional[str] = None
    platform: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None

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

    model_config = {"from_attributes": True}

class StatsResponse(BaseModel):
    total: int
    by_status: Dict[str, int]
