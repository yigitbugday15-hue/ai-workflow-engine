from fastapi.testclient import TestClient
from app.main import app
client = TestClient(app)

def test_run():
    r = client.post("/run", json={"steps": [{"type": "transform", "op": "uppercase"}, {"type": "notify", "message": "done"}], "context": {"text": "hello"}})
    assert r.status_code == 200
    assert r.json()["data"]["text"] == "HELLO"

def test_if_and_webhook():
    r = client.post("/run", json={"steps": [{"type": "if", "field": "plan", "equals": "pro", "then": "premium", "else": "basic"}], "context": {"plan": "pro"}})
    assert r.json()["data"]["if_branch"] == "premium"
    r2 = client.post("/webhook", json={"steps": [{"type": "notify", "message": "hi"}], "context": {}})
    assert r2.json()["trigger"] == "webhook"

def test_validate_and_history():
    assert client.post("/validate", json={"steps": [{"type": "unknown"}]}).json()["valid"] is False
    assert client.get("/history").status_code == 200

def test_health():
    assert client.get("/health").status_code == 200
