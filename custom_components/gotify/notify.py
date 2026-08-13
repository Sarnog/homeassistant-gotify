"""Notify-platform voor Gotify."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant.components.notify import (
    ATTR_DATA,
    ATTR_TITLE,
    ATTR_TITLE_DEFAULT,
    PLATFORM_SCHEMA as NOTIFY_PLATFORM_SCHEMA,
    BaseNotificationService,
)
from homeassistant.config_entries import SOURCE_IMPORT
from homeassistant.const import CONF_TOKEN, CONF_URL, CONF_VERIFY_SSL
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.issue_registry import IssueSeverity, async_create_issue
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .api import (
    GotifyAuthError,
    GotifyClient,
    GotifyConnectionError,
    GotifyError,
    resolve_priority,
)
from .const import (
    ATTR_EXTRAS,
    ATTR_PRIORITY,
    CONF_MSG_BLACKLIST,
    DEFAULT_PRIORITY,
    DOMAIN,
    ISSUE_DEPRECATED_YAML,
)

_LOGGER = logging.getLogger(__name__)

# Blijft bestaan om bestaande `notify:`-blokken in configuration.yaml te kunnen
# blijven inlezen; die worden hieronder eenmalig naar een config entry
# geïmporteerd.
PLATFORM_SCHEMA = NOTIFY_PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_URL): cv.url,
        vol.Required(CONF_TOKEN): cv.string,
        vol.Optional(CONF_VERIFY_SSL, default=True): cv.boolean,
        vol.Optional(CONF_MSG_BLACKLIST, default=[]): vol.All(cv.ensure_list, [cv.string]),
    }
)


async def async_get_service(
    hass: HomeAssistant,
    config: ConfigType,
    discovery_info: DiscoveryInfoType | None = None,
) -> GotifyNotificationService | None:
    """Lever de notify-service voor een config entry, of importeer YAML."""
    if discovery_info is None:
        # YAML-configuratie: eenmalig omzetten naar een config entry. De
        # service zelf wordt niet hier aangemaakt maar door de config entry
        # die de import oplevert, zodat er nooit twee services met dezelfde
        # naam naast elkaar bestaan.
        async_create_issue(
            hass,
            DOMAIN,
            ISSUE_DEPRECATED_YAML,
            is_fixable=False,
            severity=IssueSeverity.WARNING,
            translation_key=ISSUE_DEPRECATED_YAML,
        )
        hass.async_create_task(
            hass.config_entries.flow.async_init(
                DOMAIN,
                context={"source": SOURCE_IMPORT},
                data=dict(config),
            )
        )
        return None

    entry = hass.config_entries.async_get_entry(discovery_info["entry_id"])
    # runtime_data ontbreekt als de config entry intussen weer afgebroken is
    # (de discovery-taak loopt los van async_setup_entry).
    data = getattr(entry, "runtime_data", None) if entry is not None else None
    if entry is None or data is None:
        return None

    service = GotifyNotificationService(
        data.client,
        entry.data.get(CONF_MSG_BLACKLIST, []),
    )
    # Zie async_unload_entry() in __init__.py: die heeft deze referentie nodig
    # om precies deze service weer af te melden.
    data.service = service
    return service


class GotifyNotificationService(BaseNotificationService):
    """Stuurt notificaties naar één Gotify-server."""

    def __init__(self, client: GotifyClient, msg_blacklist: list[str]) -> None:
        """Initialiseer de service."""
        self._client = client
        self._msg_blacklist = msg_blacklist

    async def async_send_message(self, message: str = "", **kwargs: Any) -> None:
        """Stuur een bericht naar Gotify."""
        if message.strip() in self._msg_blacklist:
            _LOGGER.debug("Bericht overgeslagen, staat op de blacklist")
            return

        title = kwargs.get(ATTR_TITLE, ATTR_TITLE_DEFAULT)
        data = kwargs.get(ATTR_DATA) or {}
        priority = resolve_priority(data.get(ATTR_PRIORITY, DEFAULT_PRIORITY))
        extras = data.get(ATTR_EXTRAS)

        try:
            await self._client.async_send_message(message, title, priority, extras)
        except GotifyAuthError as err:
            raise HomeAssistantError(
                translation_domain=DOMAIN, translation_key="invalid_auth"
            ) from err
        except GotifyConnectionError as err:
            raise HomeAssistantError(
                translation_domain=DOMAIN,
                translation_key="send_failed",
                translation_placeholders={"error": str(err)},
            ) from err
        except GotifyError as err:  # pragma: no cover - vangnet
            raise HomeAssistantError(str(err)) from err
