"""Shared HTTP client for the open-API tools.

Every tool calls one open, no-registration public API. Networks and third-party
services fail, so this module centralises that concern: one place decides what
"the service is temporarily not available" means, so every tool degrades the same
way instead of raising and crashing a graph run.

Contract:

- ``get_json`` / ``get_text`` return the parsed body on success.
- They return ``None`` when the upstream reports *not found* (HTTP 404) — a normal
  "no data" result, not a failure.
- They raise ``ServiceUnavailable`` for anything else (network error, timeout,
  5xx, non-JSON body). Tools catch it and return ``unavailable(...)``.

``_TRANSPORT`` is a test seam: set it to an ``httpx.MockTransport`` to exercise
this module without real network access (see ``tests/test_client.py``).
"""

import httpx

USER_AGENT = "healthcare-assistant-hobby-project/0.1 (LangGraph demo; not for medical use)"
DEFAULT_TIMEOUT = 15.0

_TRANSPORT: httpx.BaseTransport | None = None


class ServiceUnavailable(Exception):
    """Raised when an upstream open API cannot be reached or returns bad data."""


def _request(
    url: str,
    params: dict | None = None,
    *,
    timeout: float = DEFAULT_TIMEOUT,
    headers: dict | None = None,
) -> httpx.Response | None:
    """GET a URL. Return the response, ``None`` on 404, or raise ServiceUnavailable."""
    hdrs = {"User-Agent": USER_AGENT}
    if headers:
        hdrs.update(headers)
    try:
        with httpx.Client(
            timeout=timeout, headers=hdrs, follow_redirects=True, transport=_TRANSPORT
        ) as client:
            response = client.get(url, params=params)
    except httpx.HTTPError as exc:
        raise ServiceUnavailable(str(exc)) from exc

    if response.status_code == 404:
        return None
    if response.status_code >= 400:
        raise ServiceUnavailable(f"HTTP {response.status_code} from {url}")
    return response


def get_json(url: str, params: dict | None = None, **kwargs) -> object | None:
    """GET and parse JSON. ``None`` on 404; raises ServiceUnavailable on failure."""
    response = _request(url, params, **kwargs)
    if response is None:
        return None
    try:
        return response.json()
    except ValueError as exc:
        raise ServiceUnavailable(f"invalid JSON from {url}") from exc


def get_text(url: str, params: dict | None = None, **kwargs) -> str | None:
    """GET raw text (e.g. XML). ``None`` on 404; raises ServiceUnavailable on failure."""
    response = _request(url, params, **kwargs)
    return None if response is None else response.text


def unavailable(service: str) -> dict:
    """The standard 'service temporarily not available' result every tool returns."""
    return {
        "status": "unavailable",
        "message": f"The {service} service is temporarily not available. Please try again later.",
    }


def not_found(message: str) -> dict:
    """The standard 'no data found' result (distinct from a service failure)."""
    return {"status": "not_found", "message": message}
