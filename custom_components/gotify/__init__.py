"""De Gotify-integratie voor Home Assistant."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from homeassistant.components.notify import BaseNotificationService
from homeassistant.components.notify.legacy import NOTIFY_SERVICES
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME, CONF_TOKEN, CONF_URL, CONF_VERIFY_SSL, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady
from homeassistant.helpers import config_validation as cv, discovery
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.typing import ConfigType

from .api import GotifyAuthError, GotifyClient, GotifyConnectionError
from .const import DATA_HASS_CONFIG, DOMAIN

_LOGGER = logging.getLogger(__name__)

# De integratie zelf wordt niet via YAML geconfigureerd (het `notify:`-blok
# wordt door notify.py geïmporteerd naar een config entry).
CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


@dataclass
class GotifyData:
    """Wat er tijdens de levensduur van een config entry bewaard wordt."""

    client: GotifyClient
    # Wordt door notify.py gevuld zodra de notify-service is aangemaakt; die
    # referentie is bij het afsluiten nodig om precies díe service weer op te
    # ruimen (en niet die van een andere config entry).
    service: BaseNotificationService | None = field(default=None)


type GotifyConfigEntry = ConfigEntry[GotifyData]


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Bewaar de YAML-configuratie voor het opzetten van het notify-platform."""
    hass.data[DATA_HASS_CONFIG] = config
    return True


async def async_setup_entry(hass: HomeAssistant, entry: GotifyConfigEntry) -> bool:
    """Zet een Gotify-config entry op."""
    session = async_get_clientsession(hass, verify_ssl=entry.data.get(CONF_VERIFY_SSL, True))
    client = GotifyClient(session, entry.data[CONF_URL], entry.data[CONF_TOKEN])

    try:
        await client.async_check_token()
    except GotifyAuthError as err:
        raise ConfigEntryAuthFailed(
            translation_domain=DOMAIN, translation_key="invalid_auth"
        ) from err
    except GotifyConnectionError as err:
        raise ConfigEntryNotReady(
            translation_domain=DOMAIN,
            translation_key="cannot_connect",
            translation_placeholders={"url": client.url},
        ) from err

    entry.runtime_data = GotifyData(client=client)

    # De notify-service wordt via de discovery-route aangemaakt (hetzelfde
    # patroon als de officiële Pushover-integratie). Dat levert een klassieke
    # notify.<naam>-service op, die - anders dan een notify-entiteit - het
    # volledige `data`-blok met priority en extras ondersteunt.
    hass.async_create_task(
        discovery.async_load_platform(
            hass,
            Platform.NOTIFY,
            DOMAIN,
            {CONF_NAME: entry.data[CONF_NAME], "entry_id": entry.entry_id},
            hass.data.get(DATA_HASS_CONFIG, {}),
        )
    )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: GotifyConfigEntry) -> bool:
    """Ruim de notify-service van deze config entry op.

    Legacy notify-services zitten niet in het platform-register van config
    entries, dus `async_unload_platforms` ziet ze niet: ze moeten hier met de
    hand afgemeld worden. Zonder dit zou de integratie helemaal niet
    ontlaadbaar zijn en zou elke wijziging een herstart van Home Assistant
    vragen.
    """
    service = entry.runtime_data.service
    if service is None:
        # De discovery-taak was nog niet klaar; er is dan ook niets aangemeld.
        _LOGGER.debug("Geen notify-service om op te ruimen voor %s", entry.title)
        return True

    await service.async_unregister_services()

    registered = hass.data.get(NOTIFY_SERVICES, {}).get(DOMAIN)
    if registered and service in registered:
        registered.remove(service)

    entry.runtime_data.service = None
    return True
