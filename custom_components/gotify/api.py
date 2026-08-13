"""Asynchrone client voor de Gotify HTTP-API.

Bevat geen Home Assistant-imports, zodat dit los te testen is. De aanroeper
levert de `aiohttp`-sessie aan (in Home Assistant is dat de gedeelde sessie,
eventueel met SSL-verificatie uit).
"""

from __future__ import annotations

import logging
from typing import Any

import aiohttp

from .const import DEFAULT_PRIORITY, PRIORITIES

_LOGGER = logging.getLogger(__name__)

REQUEST_TIMEOUT = aiohttp.ClientTimeout(total=10)

# Gotify antwoordt met 401 zodra de token-middleware het token afwijst; 403 komt
# voor als een reverse proxy ervoor zit.
AUTH_ERROR_STATUSES = (401, 403)


class GotifyError(Exception):
    """Basisfout voor alles wat er met de Gotify-server mis kan gaan."""


class GotifyConnectionError(GotifyError):
    """De server is niet bereikbaar, of het is geen Gotify-server."""


class GotifyAuthError(GotifyError):
    """De server wees het applicatietoken af."""


def normalize_url(url: str) -> str:
    """Haalt spaties en afsluitende slashes weg, zodat paden aan te plakken zijn."""
    return url.strip().rstrip("/")


class GotifyClient:
    """Praat met één Gotify-server met één applicatietoken."""

    def __init__(self, session: aiohttp.ClientSession, url: str, token: str) -> None:
        self._session = session
        self._url = normalize_url(url)
        self._token = token

    @property
    def url(self) -> str:
        """De genormaliseerde basis-URL van de server."""
        return self._url

    def _endpoint(self, path: str) -> str:
        return f"{self._url}/{path}"

    async def async_check_server(self) -> None:
        """Controleert of er op deze URL echt een Gotify-server draait.

        `/version` is het enige endpoint dat zonder token te benaderen is en
        iets teruggeeft waaraan Gotify te herkennen is - zo levert een typefout
        in de URL (of een verwijzing naar een willekeurige andere website) een
        duidelijke foutmelding op in plaats van een vage 404 bij het versturen.
        """
        try:
            async with self._session.get(
                self._endpoint("version"), timeout=REQUEST_TIMEOUT
            ) as response:
                if response.status != 200:
                    raise GotifyConnectionError(
                        f"Onverwachte statuscode {response.status} van /version"
                    )
                try:
                    payload = await response.json(content_type=None)
                except ValueError as err:
                    raise GotifyConnectionError("/version gaf geen JSON terug") from err
        except aiohttp.ClientError as err:
            raise GotifyConnectionError(str(err)) from err
        except TimeoutError as err:
            raise GotifyConnectionError("Time-out bij het benaderen van /version") from err

        if not isinstance(payload, dict) or "version" not in payload:
            raise GotifyConnectionError("Dit lijkt geen Gotify-server te zijn")

    async def async_check_token(self) -> None:
        """Controleert het applicatietoken zonder een melding te versturen.

        Gotify heeft geen endpoint om een applicatietoken te valideren: zo'n
        token mag alleen `POST /message` aanroepen. De tokencontrole zit echter
        in middleware die vóór de handler draait, terwijl de handler zelf een
        leeg bericht weigert. Een POST met een lege body geeft daardoor 401 bij
        een ongeldig token en 400 bij een geldig token - en er wordt in beide
        gevallen niets verstuurd.
        """
        try:
            async with self._session.post(
                self._endpoint("message"),
                headers={"X-Gotify-Key": self._token},
                json={},
                timeout=REQUEST_TIMEOUT,
            ) as response:
                if response.status in AUTH_ERROR_STATUSES:
                    raise GotifyAuthError("Gotify wees het applicatietoken af")
        except aiohttp.ClientError as err:
            raise GotifyConnectionError(str(err)) from err
        except TimeoutError as err:
            raise GotifyConnectionError("Time-out bij het controleren van het token") from err

    async def async_verify(self) -> None:
        """Volledige controle: is dit een Gotify-server en klopt het token."""
        await self.async_check_server()
        await self.async_check_token()

    async def async_send_message(
        self,
        message: str,
        title: str,
        priority: int,
        extras: dict[str, Any] | None = None,
    ) -> None:
        """Verstuurt één bericht naar de Gotify-server."""
        payload: dict[str, Any] = {
            "title": title,
            "message": message,
            "priority": priority,
        }
        if extras:
            payload["extras"] = extras

        _LOGGER.debug("Bericht naar Gotify sturen: %s", payload)

        try:
            async with self._session.post(
                self._endpoint("message"),
                headers={"X-Gotify-Key": self._token},
                json=payload,
                timeout=REQUEST_TIMEOUT,
            ) as response:
                if response.status in AUTH_ERROR_STATUSES:
                    raise GotifyAuthError("Gotify wees het applicatietoken af")
                response.raise_for_status()
        except aiohttp.ClientError as err:
            raise GotifyConnectionError(str(err)) from err
        except TimeoutError as err:
            raise GotifyConnectionError("Time-out bij het versturen van het bericht") from err


def resolve_priority(value: Any) -> int:
    """Zet een prioriteit uit een serviceaanroep om naar het getal dat Gotify wil.

    Accepteert zowel een getal (0-10) als een naam uit `PRIORITIES`; alles wat
    niet te herleiden is, valt terug op de standaardprioriteit.
    """
    if isinstance(value, bool):
        # bool is een subklasse van int, maar True als prioriteit is onzin.
        return DEFAULT_PRIORITY
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        stripped = value.strip()
        if stripped.lstrip("-").isdigit():
            return int(stripped)
        return PRIORITIES.get(stripped.lower(), DEFAULT_PRIORITY)
    return DEFAULT_PRIORITY
