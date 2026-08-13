"""Tests voor de berichtlogica in notify.py (zonder draaiende Home Assistant).

Alleen de service-klasse wordt getest; `async_get_service` heeft een echte
`hass` nodig - zie tests/README.md.
"""

from __future__ import annotations

from typing import Any

import pytest
from homeassistant.exceptions import HomeAssistantError

from custom_components.gotify import api
from custom_components.gotify.notify import GotifyNotificationService


class _FakeClient:
    """Vangt op wat de service naar Gotify zou sturen."""

    def __init__(self, error: Exception | None = None) -> None:
        self.error = error
        self.calls: list[tuple[str, str, int, dict[str, Any] | None]] = []

    async def async_send_message(
        self,
        message: str,
        title: str,
        priority: int,
        extras: dict[str, Any] | None = None,
    ) -> None:
        self.calls.append((message, title, priority, extras))
        if self.error is not None:
            raise self.error


async def test_default_title_and_priority_are_used() -> None:
    client = _FakeClient()

    await GotifyNotificationService(client, []).async_send_message("hallo")

    assert client.calls == [("hallo", "Home Assistant", 5, None)]


async def test_title_priority_and_extras_from_the_data_block() -> None:
    client = _FakeClient()
    extras = {"client::notification": {"bigImageUrl": "https://example.com/kat.jpg"}}

    await GotifyNotificationService(client, []).async_send_message(
        "hallo",
        title="Test",
        data={"priority": "high", "extras": extras},
    )

    assert client.calls == [("hallo", "Test", 10, extras)]


async def test_blacklisted_message_is_not_sent() -> None:
    client = _FakeClient()

    await GotifyNotificationService(client, ["TTS"]).async_send_message("  TTS  ")

    assert client.calls == []


async def test_a_message_that_only_contains_a_blacklisted_word_is_still_sent() -> None:
    client = _FakeClient()

    await GotifyNotificationService(client, ["TTS"]).async_send_message("TTS werkt niet")

    assert len(client.calls) == 1


@pytest.mark.parametrize(
    "error",
    [api.GotifyAuthError("nee"), api.GotifyConnectionError("weg"), api.GotifyError("?")],
)
async def test_errors_are_reported_as_home_assistant_errors(error: Exception) -> None:
    client = _FakeClient(error=error)

    with pytest.raises(HomeAssistantError):
        await GotifyNotificationService(client, []).async_send_message("hallo")
