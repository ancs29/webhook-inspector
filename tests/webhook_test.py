"""
Unit tests for webhook API endpoints using an isolated test database.

These tests validate the functionality of the backend routes: receiving webhooks,
storing them in the database, and retrieving them. It uses an SQLite database
which is cleared automatically before each test.

Attributes:
    SQLALCHEMY_DATABASE_URL: SQLite connection string
    engine: SQLAlchemy engine configured with StaticPool to ensure FastAPI route
        uses the same database connection defined in this module.
    TestingSessionLocal: Object that creates database sessions for the test database.
    client: FastAPI TestClient that responds to HTTP requests in tests using the test database.
"""

import json
import os

# Set the DATABASE_URL environment variable to use SQLite for tests
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.db import Base
from backend.main import app, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """
    Overrides the get_db function to use the test database.

    This function replaces the app's get_db dependency so all database operations
    during tests use the test SQLite database instead of the production
    PostgreSQL database.
    """
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_db():
    """
    Automatically clears the database before each test
    """

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


def test_receive_and_get_webhooks():
    """
    Test the receive route: POST webhook and retrieve it from GET route.

    Validates that:
    - POST /api/webhooks accepts JSON and returns 200 and the webhook's database ID
    - Webhook is stored in database with serialized JSON fields
    - GET /api/webhooks returns the saved webhook
    - Body, headers, and query_params are correctly serialized/deserialized
    """

    test_webhook = {"event": "test", "value": 123}

    response = client.post("/api/webhooks", json=test_webhook)
    assert response.status_code == 200
    assert "id" in response.json()
    assert response.json()["status"] == "saved"

    response = client.get("/api/webhooks")
    assert response.status_code == 200

    webhooks = response.json()
    assert len(webhooks) == 1

    last_webhook = webhooks[-1]

    assert json.loads(last_webhook["body"]) == test_webhook

    headers = json.loads(last_webhook["headers"])
    assert isinstance(headers, dict)

    query_params = json.loads(last_webhook["query_params"])
    assert isinstance(query_params, dict)


def test_invalid_json_webhook():
    """
    Test that invalid JSON is rejected with 400 error.

    Validates that POST /api/webhooks returns 400 when sent
    invalid JSON data, and ensures nothing is saved to the database.
    """

    response = client.post("/api/webhooks", data="invalid json string")
    assert response.status_code == 400

    webhooks = client.get("/api/webhooks").json()
    assert len(webhooks) == 0


def test_invalid_utf8_webhook():
    """
    Test that invalid UTF-8 bytes are rejected with 400 error.

    Validates that POST /api/webhooks returns 400 Bad Request when sent
    data with invalid UTF-8 encoding, and ensures nothing is saved.
    """

    invalid_bytes = b"\xff\xfe\xfd\xfc"
    response = client.post("/api/webhooks", data=invalid_bytes)
    assert response.status_code == 400

    webhooks = client.get("/api/webhooks").json()
    assert len(webhooks) == 0


def test_get_individual_webhook():
    """
    Test retrieving a specific webhook by ID and handling non-existent IDs.

    Validates that:
    - GET /api/webhooks/{id} returns the correct webhook
    - Headers and query_params are returned as dicts, not JSON strings
    - Non-existent webhook IDs return 200 with {"error": "Not found"}
    """

    test_webhook = {"event": "user.created", "user_id": 42}
    response = client.post("/api/webhooks", json=test_webhook)
    assert response.status_code == 200
    webhook_id = response.json()["id"]

    response = client.get(f"/api/webhooks/{webhook_id}")
    assert response.status_code == 200

    webhook = response.json()
    assert webhook["id"] == webhook_id
    assert json.loads(webhook["body"]) == test_webhook
    assert isinstance(webhook["headers"], dict)
    assert isinstance(webhook["query_params"], dict)

    response = client.get("/api/webhooks/99999")
    assert response.status_code == 200
    assert response.json() == {"error": "Not found"}
