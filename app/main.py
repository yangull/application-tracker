# main.py — the FastAPI app entry point, ties everything together

from fastapi import FastAPI
from app.routers import applications
from app.database import engine
from app import models

# Create all tables in the database on startup if they don't exist yet
# This is the simple approach — later projects will use Alembic migrations instead
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Application Tracker",
    description="Track your job applications",
    version="1.0.0"
)

# Register the applications router — all its routes will be available under /applications
app.include_router(applications.router)

# Simple health check route
@app.get("/")
def root():
    return {"status": "Application Tracker is running"}