"""
E2E API 測試：以 FastAPI TestClient 對 main:app 發請求，mock rag_service 不啟動 Chroma/Ollama。
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi.testclient import TestClient
from unittest.mock import patch

from main import app

client = TestClient(app)


class TestE2EApi(unittest.TestCase):
    """全系統 API 層 E2E 測試。"""

    def test_get_root(self):
        r = client.get("/")
        assert r.status_code == 200
        data = r.json()
        assert "status" in data
        assert "message" in data

    def test_get_health(self):
        r = client.get("/health")
        assert r.status_code == 200
        assert r.json() == {"status": "healthy"}

    @patch("app.api.v1.endpoints.chat.rag_service.query")
    def test_post_chat_success(self, mock_query):
        mock_query.return_value = {
            "response": "Hello, traveler.",
            "emotion": "neutral",
            "animation_trigger": None,
            "rag_context": [],
        }
        r = client.post(
            "/api/v1/chat/",
            json={
                "user_id": "player_001",
                "message": "Hi",
                "character_id": "elf_ranger",
            },
        )
        assert r.status_code == 200
        data = r.json()
        assert "response" in data and isinstance(data["response"], str)
        assert "emotion" in data and isinstance(data["emotion"], str)
        assert "animation_trigger" in data
        assert "rag_context" in data and isinstance(data["rag_context"], list)

    def test_post_chat_empty_message(self):
        r = client.post(
            "/api/v1/chat/",
            json={"user_id": "u", "message": "", "character_id": "c"},
        )
        assert r.status_code == 422
        detail = r.json().get("detail", [])
        if isinstance(detail, str):
            assert "empty" in detail.lower() or "message" in detail.lower()
        else:
            assert any("empty" in str(d).lower() or "message" in str(d).lower() for d in detail)

    def test_post_chat_whitespace_only_message(self):
        r = client.post(
            "/api/v1/chat/",
            json={"user_id": "u", "message": "   ", "character_id": "c"},
        )
        assert r.status_code == 422

    def test_post_chat_message_too_long(self):
        r = client.post(
            "/api/v1/chat/",
            json={
                "user_id": "u",
                "message": "x" * 4001,
                "character_id": "c",
            },
        )
        assert r.status_code == 422
        detail = r.json().get("detail", [])
        if isinstance(detail, str):
            assert "long" in detail.lower() or "message" in detail.lower()
        else:
            assert any("long" in str(d).lower() or "message" in str(d).lower() for d in detail)

    @patch("app.api.v1.endpoints.chat.rag_service.query")
    def test_post_chat_503_on_connection_error(self, mock_query):
        mock_query.side_effect = Exception("Connection refused to Ollama")
        r = client.post(
            "/api/v1/chat/",
            json={"user_id": "u", "message": "Hi", "character_id": "c"},
        )
        assert r.status_code == 503
        data = r.json()
        assert "detail" in data
        assert "unavailable" in data["detail"].lower() or "temporarily" in data["detail"].lower()

    @patch("app.api.v1.endpoints.chat.rag_service.query")
    def test_post_chat_500_on_generic_error(self, mock_query):
        mock_query.side_effect = Exception("Something went wrong")
        r = client.post(
            "/api/v1/chat/",
            json={"user_id": "u", "message": "Hi", "character_id": "c"},
        )
        assert r.status_code == 500
        data = r.json()
        assert "detail" in data
        assert "internal" in data["detail"].lower() or "error" in data["detail"].lower()
