from fastapi import FastAPI
from app.routers import applications
from app.database import engine
from app import models

# Simple schema-creation approach; no Alembic migrations
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Application Tracker",
    description="Track your job applications",
    version="1.0.0"
)

app.include_router(applications.router)

@app.get("/")
def root():
    return {"status": "Application Tracker is running"}
