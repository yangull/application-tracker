# test_applications.py — tests for all application routes
# pytest finds this file automatically because it starts with "test_"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db

# ── TEST DATABASE SETUP ────────────────────────────────────────────────────────

# We use a separate SQLite database just for testing
# SQLite is a lightweight database that lives in a single file
# We don't want tests touching our real PostgreSQL database
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"

# Create a test engine pointing to the SQLite test database
test_engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
    # check_same_thread=False is required for SQLite when used with FastAPI
)

# Create a test session factory
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# ── FIXTURES ───────────────────────────────────────────────────────────────────
# Fixtures are functions that set up and tear down resources for tests
# pytest runs them automatically before and after each test

@pytest.fixture()
def db_session():
    # Create all tables in the test database before each test
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Drop all tables after each test — gives every test a clean slate
        Base.metadata.drop_all(bind=test_engine)

@pytest.fixture()
def client(db_session):
    # This fixture overrides the get_db dependency in FastAPI
    # Instead of using the real PostgreSQL database, tests use the SQLite test database
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    # Tell FastAPI to use our test database instead of the real one
    app.dependency_overrides[get_db] = override_get_db
    
    # TestClient is a fake HTTP client that sends requests to your app
    # without needing a running server — everything runs in memory
    with TestClient(app) as test_client:
        yield test_client
    
    # Clean up the override after the test
    app.dependency_overrides.clear()

# ── TESTS ──────────────────────────────────────────────────────────────────────

def test_create_application(client):
    # Send a POST request to create a new application
    response = client.post("/applications/", json={
        "company": "Test Company",
        "role": "Backend Engineer",
        "applied_date": "2026-05-16",
        "status": "applied"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["company"] == "Test Company"
    assert data["role"] == "Backend Engineer"
    assert data["status"] == "applied"
    assert "id" in data  # DB generated the id

def test_list_applications(client):
    # First create an application
    client.post("/applications/", json={
        "company": "Test Company",
        "role": "Backend Engineer",
        "applied_date": "2026-05-16",
        "status": "applied"
    })
    # Then list all applications
    response = client.get("/applications/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1  # only one application exists
    assert data[0]["company"] == "Test Company"

def test_get_application(client):
    # Create an application first
    create_response = client.post("/applications/", json={
        "company": "Test Company",
        "role": "Backend Engineer",
        "applied_date": "2026-05-16",
        "status": "applied"
    })
    app_id = create_response.json()["id"]  # grab the generated id

    # Now get it by id
    response = client.get(f"/applications/{app_id}")
    assert response.status_code == 200
    assert response.json()["company"] == "Test Company"

def test_get_application_not_found(client):
    # Try to get an application that doesn't exist
    response = client.get("/applications/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Application not found"

def test_update_application(client):
    # Create an application first
    create_response = client.post("/applications/", json={
        "company": "Test Company",
        "role": "Backend Engineer",
        "applied_date": "2026-05-16",
        "status": "applied"
    })
    app_id = create_response.json()["id"]

    # Update just the status
    response = client.patch(f"/applications/{app_id}", json={
        "status": "interviewing"
    })
    assert response.status_code == 200
    assert response.json()["status"] == "interviewing"
    # Other fields should be unchanged
    assert response.json()["company"] == "Test Company"

def test_delete_application(client):
    # Create an application first
    create_response = client.post("/applications/", json={
        "company": "Test Company",
        "role": "Backend Engineer",
        "applied_date": "2026-05-16",
        "status": "applied"
    })
    app_id = create_response.json()["id"]

    # Delete it
    response = client.delete(f"/applications/{app_id}")
    assert response.status_code == 200
    assert response.json()["message"] == f"Application {app_id} deleted"

    # Confirm it's gone
    response = client.get(f"/applications/{app_id}")
    assert response.status_code == 404

def test_get_stats(client):
    # Create two applications with different statuses
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