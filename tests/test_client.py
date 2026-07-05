"""Tests for the shared HTTP client (`_client`).

These use httpx.MockTransport to drive the real request/parse code, covering the
core contract: success, 404 -> None, and every failure mode -> ServiceUnavailable.
"""

import httpx
import pytest

from healthcare_assistant_lib.tools import _client
from healthcare_assistant_lib.tools._client import ServiceUnavailable


def test_get_json_success(mock_transport):
    """Test get json success."""
    mock_transport(lambda request: httpx.Response(200, json={"ok": True}))
    assert _client.get_json("https://example.test") == {"ok": True}


def test_get_json_404_returns_none(mock_transport):
    """Test get json 404 returns none."""
    mock_transport(lambda request: httpx.Response(404, json={"error": "not found"}))
    assert _client.get_json("https://example.test") is None


def test_get_json_500_raises_unavailable(mock_transport):
    """Test get json 500 raises unavailable."""
    mock_transport(lambda request: httpx.Response(500, text="server error"))
    with pytest.raises(ServiceUnavailable):
        _client.get_json("https://example.test")


def test_get_json_non_json_body_raises_unavailable(mock_transport):
    """Test get json non json body raises unavailable."""
    mock_transport(lambda request: httpx.Response(200, text="<html>oops</html>"))
    with pytest.raises(ServiceUnavailable):
        _client.get_json("https://example.test")


def test_network_error_raises_unavailable(mock_transport):
    """Test network error raises unavailable."""

    def handler(request):
        """Test helper: handler."""
        raise httpx.ConnectError("connection refused", request=request)

    mock_transport(handler)
    with pytest.raises(ServiceUnavailable):
        _client.get_json("https://example.test")


def test_get_text_success(mock_transport):
    """Test get text success."""
    mock_transport(lambda request: httpx.Response(200, text="<xml/>"))
    assert _client.get_text("https://example.test") == "<xml/>"


def test_get_text_404_returns_none(mock_transport):
    """Test get text 404 returns none."""
    mock_transport(lambda request: httpx.Response(404))
    assert _client.get_text("https://example.test") is None


def test_unavailable_and_not_found_shapes():
    """Test unavailable and not found shapes."""
    assert _client.unavailable("X") == {
        "status": "unavailable",
        "message": "The X service is temporarily not available. Please try again later.",
    }
    assert _client.not_found("nope") == {"status": "not_found", "message": "nope"}
