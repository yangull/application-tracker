# models.py — defines the database table as a Python class

from sqlalchemy import Column, Integer, String, Text, Date, DateTime
from sqlalchemy.sql import func
from app.database import Base

# This class maps directly to the "applications" table in PostgreSQL
class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)  # auto-increment PK
    company = Column(String, nullable=False)             # e.g. "Taktile"
    role = Column(String, nullable=False)                # e.g. "Junior Backend Engineer"
    job_url = Column(Text, nullable=True)                # link to the job posting
    platform = Column(String, nullable=True)             # "LinkedIn", "careers page", etc.
    status = Column(String, nullable=False, default="applied")  # current stage
    applied_date = Column(Date, nullable=False)          # when you submitted
    notes = Column(Text, nullable=True)                  # freeform notes

    # These two are set automatically by the database, you never pass them manually
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())