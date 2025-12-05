import json

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
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_db():
    """Clear the database before each test"""
    # Clear all tables
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


def test_receive_and_get_webhooks():
    test_webhook = {"event": "test", "value": 123}

    response = client.post("/receive", json=test_webhook)
    assert response.status_code == 200
    assert "id" in response.json()
    assert response.json()["status"] == "saved"

    # Fetch from DB
    response = client.get("/webhooks")
    assert response.status_code == 200

    webhooks = response.json()
    assert len(webhooks) == 1

    last_webhook = webhooks[-1]

    # BODY stored as string → need json.loads
    assert json.loads(last_webhook["body"]) == test_webhook

    # HEADERS stored as JSON string too
    headers = json.loads(last_webhook["headers"])
    assert isinstance(headers, dict)
    # assert "host" in headers

    query_params = json.loads(last_webhook["query_params"])
    assert isinstance(query_params, dict)


def test_invalid_json_webhook():
    response = client.post("/receive", data="invalid json string")
    assert response.status_code == 400

    webhooks = client.get("/webhooks").json()
    assert len(webhooks) == 0  # nothing should have been saved


def test_invalid_utf8_webhook():
    invalid_bytes = b"\xff\xfe\xfd\xfc"
    response = client.post("/receive", data=invalid_bytes)
    assert response.status_code == 400

    webhooks = client.get("/webhooks").json()
    assert len(webhooks) == 0


def test_get_individual_webhook():

    test_webhook = {"event": "user.created", "user_id": 42}
    response = client.post("/receive", json=test_webhook)
    assert response.status_code == 200
    webhook_id = response.json()["id"]

    # Retrieve the individual webhook
    response = client.get(f"/webhooks/{webhook_id}")
    assert response.status_code == 200

    webhook = response.json()
    assert webhook["id"] == webhook_id
    assert json.loads(webhook["body"]) == test_webhook
    assert isinstance(webhook["headers"], dict)
    assert isinstance(webhook["query_params"], dict)

    # Test non-existent webhook
    response = client.get("/webhooks/99999")
    assert response.status_code == 200
    assert response.json() == {"error": "Not found"}
