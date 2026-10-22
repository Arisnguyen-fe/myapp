import json

import httpx
import pytest
from fastapi.testclient import TestClient

from app import chatbot_routes
from main import app


@pytest.fixture
def chat_client():
    return TestClient(app)


@pytest.fixture
def gemini(monkeypatch):
    """Replace the outgoing Gemini call with a fake transport and record requests."""
    calls = []

    def install(status_code=200, body=None):
        def handler(request):
            calls.append(request)
            return httpx.Response(status_code, json=body or {})

        real_client = httpx.AsyncClient
        monkeypatch.setattr(
            chatbot_routes.httpx,
            "AsyncClient",
            lambda **kwargs: real_client(transport=httpx.MockTransport(handler), **kwargs),
        )
        return calls

    return install


def gemini_reply(text):
    return {"candidates": [{"content": {"parts": [{"text": text}]}}]}


def test_chat_returns_reply_and_keeps_key_server_side(chat_client, gemini, monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    calls = gemini(body=gemini_reply("  Hello there!  "))

    response = chat_client.post(
        "/chatbot/chat", json={"messages": [{"role": "user", "text": "Hi"}]}
    )

    assert response.status_code == 200
    assert response.json() == {"reply": "Hello there!"}
    assert calls[0].headers["x-goog-api-key"] == "test-key"
    assert "key=" not in str(calls[0].url)
    assert json.loads(calls[0].content) == {
        "contents": [{"role": "user", "parts": [{"text": "Hi"}]}]
    }


def test_chat_without_api_key_returns_503(chat_client, gemini, monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    calls = gemini(body=gemini_reply("unused"))

    response = chat_client.post(
        "/chatbot/chat", json={"messages": [{"role": "user", "text": "Hi"}]}
    )

    assert response.status_code == 503
    assert calls == []


def test_chat_hides_gemini_errors(chat_client, gemini, monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    gemini(status_code=400, body={"error": {"message": "API key not valid"}})

    response = chat_client.post(
        "/chatbot/chat", json={"messages": [{"role": "user", "text": "Hi"}]}
    )

    assert response.status_code == 502
    assert "API key" not in response.text


@pytest.mark.parametrize(
    "messages",
    [
        [],
        [{"role": "system", "text": "Hi"}],
        [{"role": "user", "text": "x" * 2001}],
        [{"role": "user", "text": "Hi"}] * 31,
    ],
)
def test_chat_rejects_invalid_messages(chat_client, messages):
    response = chat_client.post("/chatbot/chat", json={"messages": messages})
    assert response.status_code == 422
