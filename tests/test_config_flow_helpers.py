"""Tests voor de pure schema- en normalisatielogica in config_flow.py.

De flow-stappen zelf (`async_step_user`, `async_step_import`, ...) hebben een
draaiende Home Assistant nodig en worden hier niet getest - zie tests/README.md.
"""

from __future__ import annotations

import pytest
import voluptuous as vol

from custom_components.gotify.config_flow import DATA_SCHEMA, GotifyConfigFlow

_clean = GotifyConfigFlow._clean


def test_schema_defaults() -> None:
    result = DATA_SCHEMA({"url": "https://gotify.example.com", "token": "abc"})

    assert result["name"] == "Gotify"
    assert result["verify_ssl"] is True
    assert result["msg_blacklist"] == []


def test_schema_requires_url_and_token() -> None:
    with pytest.raises(vol.Invalid):
        DATA_SCHEMA({"url": "https://gotify.example.com"})

    with pytest.raises(vol.Invalid):
        DATA_SCHEMA({"token": "abc"})


def test_clean_strips_the_yaml_platform_key() -> None:
    result = _clean(
        {
            "platform": "gotify",
            "name": "Mijn Gotify",
            "url": "https://gotify.example.com/",
            "token": "abc",
        }
    )

    assert "platform" not in result
    assert result["name"] == "Mijn Gotify"


def test_clean_normalizes_url_and_token_and_fills_defaults() -> None:
    result = _clean({"url": " https://gotify.example.com// ", "token": " abc "})

    assert result["url"] == "https://gotify.example.com"
    assert result["token"] == "abc"
    assert result["name"] == "Gotify"
    assert result["verify_ssl"] is True
    assert result["msg_blacklist"] == []


def test_clean_keeps_explicit_values() -> None:
    result = _clean(
        {
            "name": "  Werk  ",
            "url": "https://gotify.example.com",
            "token": "abc",
            "verify_ssl": False,
            "msg_blacklist": ["TTS"],
        }
    )

    assert result["name"] == "Werk"
    assert result["verify_ssl"] is False
    assert result["msg_blacklist"] == ["TTS"]


def test_clean_falls_back_to_the_default_name_for_an_empty_name() -> None:
    # Een leeg `name:` in YAML mag geen servicenaam "notify." opleveren.
    result = _clean({"name": "", "url": "https://gotify.example.com", "token": "abc"})

    assert result["name"] == "Gotify"
