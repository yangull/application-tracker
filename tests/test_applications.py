import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db

SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"

test_engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
    # check_same_thread=False is required for SQLite in a multi-threaded context like FastAPI
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

@pytest.fixture()
def db_session():
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=test_engine)

@pytest.fixture()
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

def test_create_application(client):
    response = client.post("/applications/", json={
        "company": "Test Company",
        "role": "Backend Engineer",
        "applied_date": "2026-05-16",
        "status": "applied"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["company"] == "Test Company"
    assert data["role"] == "Backend Engineer"
    assert data["status"] == "applied"
    assert "id" in data

def test_list_applications(client):
    client.post("/applications/", json={
        "company": "Test Company",
        "role": "Backend Engineer",
        "applied_date": "2026-05-16",
        "status": "applied"
    })
    response = client.get("/applications/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["company"] == "Test Company"

def test_get_application(client):
    create_response = client.post("/applications/", json={
        "company": "Test Company",
        "role": "Backend Engineer",
        "applied_date": "2026-05-16",
        "status": "applied"
    })
    app_id = create_response.json()["id"]
    response = client.get(f"/applications/{app_id}")
    assert response.status_code == 200
    assert response.json()["company"] == "Test Company"

def test_get_application_not_found(client):
    response = client.get("/applications/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Application not found"

def test_update_application(client):
    create_response = client.post("/applications/", json={
        "company": "Test Company",
        "role": "Backend Engineer",
        "applied_date": "2026-05-16",
        "status": "applied"
    })
    app_id = create_response.json()["id"]
    response = client.patch(f"/applications/{app_id}", json={"status": "interviewing"})
    assert response.status_code == 200
    assert response.json()["status"] == "interviewing"
    assert response.json()["company"] == "Test Company"

def test_delete_application(client):
    create_response = client.post("/applications/", json={
        "company": "Test Company",
        "role": "Backend Engineer",
        "applied_date": "2026-05-16",
        "status": "applied"
    })
    app_id = create_response.json()["id"]
    response = client.delete(f"/applications/{app_id}")
    assert response.status_code == 200
    assert response.json()["message"] == f"Application {app_id} deleted"
    response = client.get(f"/applications/{app_id}")
    assert response.status_code == 404

def test_get_stats(client):
    client.post("/applications/", json={
        "company": "Company A",
        "role": "Backend Engineer",
        "applied_date": "2026-05-16",
        "status": "applied"
    })
    client.post("/applications/", json={
        "company": "Company B",
        "role": "Frontend Engineer",
        "applied_date": "2026-05-16",
        "status": "interviewing"
    })
    response = client.get("/applications/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert data["by_status"]["applied"] == 1
    assert data["by_status"]["interviewing"] == 1
