"""Test cases for the API endpoints."""

from http import HTTPStatus
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from src.main import app


@pytest.fixture
def client() -> TestClient:
    """Fixture to create a test client."""
    return TestClient(app)


def test_health_check(client: TestClient) -> None:
    """Test the health check endpoint."""
    response = client.get("/")
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"message": "Welcome to the FastAPI LangGraph Agent!"}


def test_chat_endpoint(client: TestClient) -> None:
    """Test the chat endpoint."""
    test_message = {"message": "Hello"}
    response = client.post("/chat", json=test_message)
    assert response.status_code == HTTPStatus.OK
    assert response.headers["content-type"] == "text/event-stream; charset=utf-8"
    content = b"".join(response.iter_bytes()).decode()
    assert content


def test_minute_endpoint(client: TestClient) -> None:
    """Test the minute writing endpoint with audio file upload."""
    # Use the existing test.wav file in the tests directory
    with Path("tests/test.wav").open("rb") as audio_file:
        test_audio_content = audio_file.read()

    # Create test file data with correct MIME type
    files = {"audio_file": ("test.wav", test_audio_content, "audio/wav")}

    response = client.post("/minute-writer/process", files=files)
    assert response.status_code == HTTPStatus.OK
    assert response.json()["success"]
    assert "summary" in response.json()["data"]
