"""Tests for the FastAPI endpoints (stubbed LLM, offline)."""

from fastapi.testclient import TestClient
from langchain_core.messages import AIMessage

from fastapi_app.main import app
from tests.conftest import FakeLLM

client = TestClient(app)


def test_health():
    """Test health."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_chat_endpoint_returns_reply(patch_agent_llm):
    """Test chat endpoint returns reply."""
    patch_agent_llm(FakeLLM(route="general", script=[AIMessage(content="Some general info.")]))
    response = client.post("/api/v1/chat", json={"user_id": "api-1", "message": "hello"})
    assert response.status_code == 200
    body = response.json()
    assert "Some general info." in body["reply"]
    assert body["specialty"] == "general"
    assert body["blocked"] is False
    assert "PLEASE READ FIRST" in body["reply"]


def test_chat_endpoint_blocks_emergency(patch_agent_llm):
    """Test chat endpoint blocks emergency."""
    patch_agent_llm(FakeLLM())
    response = client.post(
        "/api/v1/chat", json={"user_id": "api-2", "message": "I'm having a heart attack"}
    )
    assert response.status_code == 200
    assert response.json()["blocked"] is True


def test_chat_endpoint_validates_body():
    """Test chat endpoint validates body."""
    response = client.post("/api/v1/chat", json={"user_id": "api-3"})
    assert response.status_code == 422
