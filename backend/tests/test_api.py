"""Smoke tests for public, non-NIM application surfaces."""

from fastapi.testclient import TestClient

from backend.main import app


def test_health_and_static_frontend_are_available():
    """The container can answer its health check and serve its web client."""
    client = TestClient(app, base_url="http://localhost")

    assert client.get("/health").json() == {"status": "ok"}
    assert client.get("/").status_code == 200
    assert client.get("/css/style.css").status_code == 200
    assert client.get("/js/app.js").status_code == 200


def test_development_allows_a_local_file_preview_to_call_the_api():
    """A browser preview opened from file:// receives development CORS headers."""
    client = TestClient(app, base_url="http://localhost")
    response = client.options(
        "/api/chat",
        headers={"Origin": "null", "Access-Control-Request-Method": "POST"},
    )

    assert response.headers["access-control-allow-origin"] == "null"
