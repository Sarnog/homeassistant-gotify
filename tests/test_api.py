"""Tests voor custom_components/gotify/api.py (geen HA-runtime nodig).

HTTP-aanroepen worden gemockt door `session.get`/`session.post` direct te
vervangen door een object met dezelfde async-contextmanager-vorm als aiohttp's
echte `_RequestContextManager` - geen externe mocking-library nodig, en de test
faalt hard als de mock niet gebruikt wordt in plaats van stilletjes een echte
request te doen.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

import aiohttp
import pytest

from custom_components.gotify import api


class _FakeResponse:
    """Bootst aiohttp's async-contextmanager response-object na."""

    def __init__(self, *, status: int = 200, json_data: Any = None) -> None:
        self.status = status
        self._json_data = json_data

    def raise_for_status(self) -> None:
        if self.status >= 400:
            raise aiohttp.ClientResponseError(
                request_info=MagicMock(),
                history=(),
                status=self.status,
            )

    async def json(self, content_type: str | None = None) -> Any:  # noqa: ARG002
        if self._json_data is _INVALID_JSON:
            raise ValueError("geen JSON")
        return self._json_data

    async def __aenter__(self) -> _FakeResponse:
        return self

    async def __aexit__(self, *_args: object) -> None:
        return None


_INVALID_JSON = object()


class _FakeSession:
    """Fake `aiohttp.ClientSession` die vaste antwoorden teruggeeft."""

    def __init__(
        self,
        *,
        get_response: _FakeResponse | None = None,
        post_response: _FakeResponse | None = None,
    ) -> None:
        self._get_response = get_response
        self._post_response = post_response
        self.get_calls: list[tuple[str, dict[str, Any]]] = []
        self.post_calls: list[tuple[str, dict[str, Any]]] = []

    def get(self, url: str, **kwargs: Any) -> _FakeResponse:
        self.get_calls.append((url, kwargs))
        assert self._get_response is not None, f"Onverwachte GET in test: {url}"
        return self._get_response

    def post(self, url: str, **kwargs: Any) -> _FakeResponse:
        self.post_calls.append((url, kwargs))
        assert self._post_response is not None, f"Onverwachte POST in test: {url}"
        return self._post_response


def _client(session: Any, url: str = "https://gotify.example.com") -> api.GotifyClient:
    return api.GotifyClient(session, url, "token123")


def test_normalize_url_strips_whitespace_and_trailing_slashes() -> None:
    assert api.normalize_url("  https://gotify.example.com/  ") == "https://gotify.example.com"
    assert api.normalize_url("https://gotify.example.com///") == "https://gotify.example.com"
    assert api.normalize_url("https://example.com/gotify") == "https://example.com/gotify"


async def test_check_server_accepts_a_gotify_version_response() -> None:
    session = _FakeSession(get_response=_FakeResponse(json_data={"version": "2.6.3"}))

    await _client(session).async_check_server()

    assert session.get_calls[0][0] == "https://gotify.example.com/version"


async def test_check_server_rejects_a_non_gotify_response() -> None:
    session = _FakeSession(get_response=_FakeResponse(json_data={"hello": "world"}))

    with pytest.raises(api.GotifyConnectionError):
        await _client(session).async_check_server()


async def test_check_server_rejects_non_json() -> None:
    session = _FakeSession(get_response=_FakeResponse(json_data=_INVALID_JSON))

    with pytest.raises(api.GotifyConnectionError):
        await _client(session).async_check_server()


async def test_check_server_rejects_an_error_status() -> None:
    session = _FakeSession(get_response=_FakeResponse(status=404))

    with pytest.raises(api.GotifyConnectionError):
        await _client(session).async_check_server()


async def test_check_token_accepts_the_expected_bad_request() -> None:
    # Een leeg bericht wordt door Gotify geweigerd met 400 - dat betekent dat
    # het token de auth-middleware wel gepasseerd is.
    session = _FakeSession(post_response=_FakeResponse(status=400))

    await _client(session).async_check_token()

    url, kwargs = session.post_calls[0]
    assert url == "https://gotify.example.com/message"
    assert kwargs["headers"] == {"X-Gotify-Key": "token123"}
    assert kwargs["json"] == {}


@pytest.mark.parametrize("status", [401, 403])
async def test_check_token_rejects_an_unauthorized_response(status: int) -> None:
    session = _FakeSession(post_response=_FakeResponse(status=status))

    with pytest.raises(api.GotifyAuthError):
        await _client(session).async_check_token()


async def test_send_message_posts_the_full_payload() -> None:
    session = _FakeSession(post_response=_FakeResponse(status=200))
    extras = {"client::notification": {"click": {"url": "https://example.com"}}}

    await _client(session).async_send_message("bericht", "titel", 10, extras)

    url, kwargs = session.post_calls[0]
    assert url == "https://gotify.example.com/message"
    assert kwargs["json"] == {
        "title": "titel",
        "message": "bericht",
        "priority": 10,
        "extras": extras,
    }


async def test_send_message_omits_empty_extras() -> None:
    session = _FakeSession(post_response=_FakeResponse(status=200))

    await _client(session).async_send_message("bericht", "titel", 5, None)

    assert "extras" not in session.post_calls[0][1]["json"]


async def test_send_message_raises_auth_error_on_401() -> None:
    session = _FakeSession(post_response=_FakeResponse(status=401))

    with pytest.raises(api.GotifyAuthError):
        await _client(session).async_send_message("bericht", "titel", 5)


async def test_send_message_raises_connection_error_on_server_error() -> None:
    session = _FakeSession(post_response=_FakeResponse(status=500))

    with pytest.raises(api.GotifyConnectionError):
        await _client(session).async_send_message("bericht", "titel", 5)


async def test_send_message_wraps_client_errors() -> None:
    session = MagicMock(spec=aiohttp.ClientSession)
    session.post.side_effect = aiohttp.ClientConnectorError(MagicMock(), OSError("boem"))

    with pytest.raises(api.GotifyConnectionError):
        await _client(session).async_send_message("bericht", "titel", 5)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (10, 10),
        (0, 0),
        ("8", 8),
        ("high", 10),
        ("HIGH", 10),
        ("low", 2),
        ("none", 0),
        ("onbekend", 5),
        (None, 5),
        (True, 5),
        ({"nonsense": 1}, 5),
    ],
)
def test_resolve_priority(value: Any, expected: int) -> None:
    assert api.resolve_priority(value) == expected
