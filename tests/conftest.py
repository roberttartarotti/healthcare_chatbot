"""Shared pytest fixtures for the tool tests.

The tools reach the network through ``healthcare_assistant_lib.tools._client``.
These fixtures replace that layer so tests are deterministic and offline:

- ``patch_json`` / ``patch_text``: stub the client's parsed-body helpers to return
  canned data, ``None`` (upstream 404 / no data), or raise ServiceUnavailable.
- ``mock_transport``: install an ``httpx.MockTransport`` to exercise the real
  ``_client`` request/parse logic without a live server.
"""

import httpx
import pytest
from langchain_core.messages import AIMessage

from healthcare_assistant_lib.tools import _client
from healthcare_assistant_lib.tools._client import ServiceUnavailable


@pytest.fixture
def patch_json(monkeypatch):
    """Stub ``_client.get_json``. Call with a result, or raises=True to fail."""

    def _patch(result=None, *, raises: bool = False):
        """Test helper: patch."""

        def fake(url, params=None, **kwargs):
            """Test helper: fake."""
            if raises:
                raise ServiceUnavailable("stubbed failure")
            return result

        monkeypatch.setattr(_client, "get_json", fake)

    return _patch


@pytest.fixture
def patch_text(monkeypatch):
    """Stub ``_client.get_text``. Call with a result, or raises=True to fail."""

    def _patch(result=None, *, raises: bool = False):
        """Test helper: patch."""

        def fake(url, params=None, **kwargs):
            """Test helper: fake."""
            if raises:
                raise ServiceUnavailable("stubbed failure")
            return result

        monkeypatch.setattr(_client, "get_text", fake)

    return _patch


@pytest.fixture
def mock_transport():
    """Install an httpx.MockTransport into the client, cleaned up afterwards."""
    original = _client._TRANSPORT

    def _install(handler):
        """Test helper: install."""
        _client._TRANSPORT = httpx.MockTransport(handler)

    yield _install
    _client._TRANSPORT = original


class _StructuredFake:
    """Stands in for ``llm.with_structured_output(RouteDecision)``."""

    def __init__(self, route: str):
        """Store the test double's configuration."""
        self._route = route

    def invoke(self, messages):
        """Test helper: invoke."""
        from healthcare_assistant_lib.agent.router import RouteDecision

        return RouteDecision(specialty=self._route)


class FakeLLM:
    """A scriptable stand-in for the agent LLM (no API key, deterministic).

    - ``with_structured_output`` (router) returns a fixed ``route``.
    - ``bind_tools`` (specialists) returns self; ``invoke`` yields the next scripted
      AIMessage, or a plain answer once the script is exhausted.
    - ``invoke`` (summarize) also draws from the script / falls back to summary text.
    """

    def __init__(self, route: str = "general", script=None, summary_text: str = "Concise summary."):
        """Store the test double's configuration."""
        self.route = route
        self.script = list(script or [])
        self.summary_text = summary_text

    def with_structured_output(self, schema):
        """Test helper: with structured output."""
        return _StructuredFake(self.route)

    def bind_tools(self, tools):
        """Test helper: bind tools."""
        return self

    def invoke(self, messages):
        """Test helper: invoke."""
        if self.script:
            return self.script.pop(0)
        return AIMessage(content=self.summary_text)


@pytest.fixture
def patch_agent_llm(monkeypatch):
    """Point the router, specialist and summarize nodes at one FakeLLM instance."""

    def _patch(fake: FakeLLM):
        """Test helper: patch."""
        for module in ("router", "nodes", "summarize"):
            monkeypatch.setattr(f"healthcare_assistant_lib.agent.{module}.get_llm", lambda: fake)
        return fake

    return _patch
