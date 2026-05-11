# routers/applications.py — all CRUD route handlers for job applications

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from app.database import get_db
from app.models import Application
from app.schemas import ApplicationCreate, ApplicationUpdate, ApplicationResponse

# APIRouter groups related routes — main.py registers this whole router at once
router = APIRouter(prefix="/applications", tags=["applications"])

# POST /applications — create a new application
@router.post("/", response_model=ApplicationResponse)
def create_application(data: ApplicationCreate, db: Session = Depends(get_db)):
    # Convert the Pydantic schema into a SQLAlchemy model instance
    app = Application(**data.model_dump())
    db.add(app)
    db.commit()
    db.refresh(app)  # reload from DB so we get the generated id and created_at
    return app

# GET /applications — list all, with optional filter by status
@router.get("/", response_model=list[ApplicationResponse])
def list_applications(status: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Application)
    if status:
        query = query.filter(Application.status == status)
    return query.order_by(Application.applied_date.desc()).all()

# GET /applications/stats — summary counts by status
@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    # Group by status and count — like SELECT status, COUNT(*) GROUP BY status
    results = db.query(Application.status, func.count(Application.id)).group_by(Application.status).all()
    total = db.query(func.count(Application.id)).scalar()
    return {
        "total": total,
        "by_status": {status: count for status, count in results}
    }

# GET /applications/{id} — get a single application
@router.get("/{app_id}", response_model=ApplicationResponse)
def get_application(app_id: int, db: Session = Depends(get_db)):
    app = db.query(Application).filter(Application.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    return app

# PATCH /applications/{id} — update status or any field
@router.patch("/{app_id}", response_model=ApplicationResponse)
def update_application(app_id: int, data: ApplicationUpdate, db: Session = Depends(get_db)):
    app = db.query(Application).filter(Application.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    # Only update fields that were actually sent — ignore None values
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(app, field, value)
    db.commit()
    db.refresh(app)
    return app

# DELETE /applications/{id} — remove an application
@router.delete("/{app_id}")
def delete_application(app_id: int, db: Session = Depends(get_db)):
    app = db.query(Application).filter(Application.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    db.delete(app)
    db.commit()
    return {"message": f"Application {app_id} deleted"}