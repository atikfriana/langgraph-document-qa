"""
Integration tests for the FastAPI layer.

Exercises real HTTP request/response cycles via `TestClient`, with the
LangGraph agent and vector store replaced by fakes injected in
`conftest.py`'s `app_client` fixture — this validates routing, schema
validation, and error-handling wiring without depending on OpenAI/FAISS.
"""

from __future__ import annotations

from fastapi.testclient import TestClient


class TestHealthEndpoint:
    def test_liveness_check_always_ok(self, app_client: TestClient) -> None:
        response = app_client.get("/health")

        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "ok"

    def test_readiness_check_ok_when_vector_store_loaded(
        self, app_client: TestClient
    ) -> None:
        response = app_client.get("/health/ready")

        assert response.status_code == 200
        assert response.json()["vector_store_ready"] is True


class TestChatEndpoint:
    def test_send_message_returns_answer_and_new_session_id(
        self, app_client: TestClient
    ) -> None:
        response = app_client.post(
            "/chat", json={"message": "What is the battery life of the Aurora M1?"}
        )

        assert response.status_code == 200
        body = response.json()
        assert body["session_id"]
        assert "Aurora M1" in body["response"] or "battery" in body["response"].lower()
        assert isinstance(body["tool_used"], bool)
        assert isinstance(body["sources"], list)

    def test_send_message_reuses_provided_session_id(
        self, app_client: TestClient
    ) -> None:
        response = app_client.post(
            "/chat",
            json={"message": "Follow up question", "session_id": "existing-session-123"},
        )

        assert response.status_code == 200
        assert response.json()["session_id"] == "existing-session-123"

    def test_blank_message_is_rejected(self, app_client: TestClient) -> None:
        response = app_client.post("/chat", json={"message": "   "})

        assert response.status_code == 422

    def test_missing_message_field_is_rejected(self, app_client: TestClient) -> None:
        response = app_client.post("/chat", json={})

        assert response.status_code == 422

    def test_response_shape_matches_schema(self, app_client: TestClient) -> None:
        response = app_client.post("/chat", json={"message": "Hello"})

        body = response.json()
        assert set(body.keys()) == {"session_id", "response", "tool_used", "sources"}