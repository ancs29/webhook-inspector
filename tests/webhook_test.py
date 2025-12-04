from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_receive_and_get_webhooks():
    test_webhook = {"event": "test", "value": 123}
    response = client.post("/receive", json=test_webhook)
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

    response = client.get("/webhooks")
    assert response.status_code == 200

    webhooks = response.json()
    assert len(webhooks) >= 1

    last_webhook = webhooks[-1]
    assert last_webhook["body"] == test_webhook
    assert "headers" in last_webhook
    assert "query_params" in last_webhook


def test_invalid_json_webhook():
    response = client.post("/receive", data="invalid json string")
    assert response.status_code == 400

    webhooks = client.get("/webhooks").json()
    if webhooks:
        assert webhooks[-1]["body"] != "invalid json string"
