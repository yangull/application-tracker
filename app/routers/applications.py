from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from app.database import get_db
from app.models import Application
from app.schemas import ApplicationCreate, ApplicationUpdate, ApplicationResponse

router = APIRouter(prefix="/applications", tags=["applications"])

@router.post("/", response_model=ApplicationResponse)
def create_application(data: ApplicationCreate, db: Session = Depends(get_db)):
    app = Application(**data.model_dump())
    db.add(app)
    db.commit()
    db.refresh(app)
    return app

@router.get("/", response_model=list[ApplicationResponse])
def list_applications(status: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Application)
    if status:
        query = query.filter(Application.status == status)
    return query.order_by(Application.applied_date.desc()).all()

@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    results = db.query(Application.status, func.count(Application.id)).group_by(Application.status).all()
    total = db.query(func.count(Application.id)).scalar()
    return {
        "total": total,
        "by_status": {status: count for status, count in results}
    }

@router.get("/{app_id}", response_model=ApplicationResponse)
def get_application(app_id: int, db: Session = Depends(get_db)):
    app = db.query(Application).filter(Application.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    return app

@router.patch("/{app_id}", response_model=ApplicationResponse)
def update_application(app_id: int, data: ApplicationUpdate, db: Session = Depends(get_db)):
    app = db.query(Application).filter(Application.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    # exclude_unset=True means fields absent from the request body are not overwritten
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(app, field, value)
    db.commit()
    db.refresh(app)
    return app

@router.delete("/{app_id}")
def delete_application(app_id: int, db: Session = Depends(get_db)):
    app = db.query(Application).filter(Application.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    db.delete(app)
    db.commit()
    return {"message": f"Application {app_id} deleted"}
