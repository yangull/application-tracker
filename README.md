# Application Tracker API

A FastAPI + PostgreSQL REST API for tracking job applications.

## Features
- Log job applications with company, role, status, platform, and notes
- Filter applications by status
- Stats endpoint with aggregated counts by status
- Full CRUD: create, read, update, delete

## Stack
- FastAPI
- PostgreSQL + SQLAlchemy
- Python 3.12

## Run locally
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
EOF
