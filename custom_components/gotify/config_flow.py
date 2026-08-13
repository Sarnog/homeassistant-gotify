"""Config flow voor de Gotify-integratie."""

from __future__ import annotations

import logging
from collections.abc import Mapping
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_NAME, CONF_TOKEN, CONF_URL, CONF_VERIFY_SSL
from homeassistant.core import HomeAssistant
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.issue_registry import IssueSeverity, async_create_issue
from homeassistant.util import slugify

from .api import GotifyAuthError, GotifyClient, GotifyConnectionError, normalize_url
from .const import (
    CONF_MSG_BLACKLIST,
    DEFAULT_NAME,
    DOMAIN,
    ISSUE_YAML_IMPORT_FAILED,
)

_LOGGER = logging.getLogger(__name__)

# De naam bepaalt hoe de service gaat heten (notify.<naam>), dus die hoort hier
# wél thuis - anders dan bij integraties die alleen entiteiten aanmaken.
DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME, default=DEFAULT_NAME): str,
        vol.Required(CONF_URL): selector.TextSelector(
            selector.TextSelectorConfig(type=selector.TextSelectorType.URL)
        ),
        vol.Required(CONF_TOKEN): selector.TextSelector(
            selector.TextSelectorConfig(type=selector.TextSelectorType.PASSWORD)
        ),
        vol.Optional(CONF_VERIFY_SSL, default=True): bool,
        vol.Optional(CONF_MSG_BLACKLIST, default=list): selector.TextSelector(
            selector.TextSelectorConfig(multiple=True)
        ),
    }
)

TOKEN_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_TOKEN): selector.TextSelector(
            selector.TextSelectorConfig(type=selector.TextSelectorType.PASSWORD)
        ),
    }
)


async def async_validate_input(hass: HomeAssistant, data: Mapping[str, Any]) -> dict[str, str]:
    """Test de opgegeven server en het token; geeft de eventuele fouten terug."""
    session = async_get_clientsession(hass, verify_ssl=data.get(CONF_VERIFY_SSL, True))
    client = GotifyClient(session, data[CONF_URL], data[CONF_TOKEN])

    errors: dict[str, str] = {}
    try:
        await client.async_verify()
    except GotifyAuthError:
        errors[CONF_TOKEN] = "invalid_auth"
    except GotifyConnectionError as err:
        _LOGGER.debug("Gotify-server niet bereikbaar: %s", err)
        errors[CONF_URL] = "cannot_connect"
    return errors


class GotifyConfigFlow(ConfigFlow, domain=DOMAIN):
    """Doorloopt het toevoegen, herstellen en herconfigureren van een server."""

    VERSION = 1

    def _name_in_use(self, name: str, ignore_entry_id: str | None = None) -> bool:
        """Bestaat er al een entry die dezelfde notify-service zou opleveren?

        De servicenaam is de "geslugificeerde" naam, dus "Mijn Gotify" en
        "mijn gotify" botsen met elkaar - zonder deze controle zou de tweede
        entry stilzwijgend geen werkende service opleveren.
        """
        slug = slugify(name)
        return any(
            entry.entry_id != ignore_entry_id
            and slugify(entry.data.get(CONF_NAME, DEFAULT_NAME)) == slug
            for entry in self._async_current_entries()
        )

    @staticmethod
    def _clean(user_input: Mapping[str, Any]) -> dict[str, Any]:
        """Normaliseer de invoer zoals die opgeslagen wordt."""
        data = {key: value for key, value in user_input.items() if key != "platform"}
        data[CONF_NAME] = str(data.get(CONF_NAME) or DEFAULT_NAME).strip()
        data[CONF_URL] = normalize_url(data[CONF_URL])
        data[CONF_TOKEN] = data[CONF_TOKEN].strip()
        data.setdefault(CONF_VERIFY_SSL, True)
        data.setdefault(CONF_MSG_BLACKLIST, [])
        return data

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Handmatig toevoegen via de UI."""
        errors: dict[str, str] = {}

        if user_input is not None:
            data = self._clean(user_input)
            self._async_abort_entries_match(
                {CONF_URL: data[CONF_URL], CONF_TOKEN: data[CONF_TOKEN]}
            )

            if self._name_in_use(data[CONF_NAME]):
                errors[CONF_NAME] = "name_in_use"
            else:
                errors = await async_validate_input(self.hass, data)

            if not errors:
                return self.async_create_entry(title=data[CONF_NAME], data=data)

            user_input = data

        schema = self.add_suggested_values_to_schema(DATA_SCHEMA, user_input or {})
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    async def async_step_import(self, import_data: dict[str, Any]) -> ConfigFlowResult:
        """Neem een bestaand `notify:`-blok uit configuration.yaml over."""
        data = self._clean(import_data)
        self._async_abort_entries_match({CONF_URL: data[CONF_URL], CONF_TOKEN: data[CONF_TOKEN]})

        if self._name_in_use(data[CONF_NAME]):
            return self.async_abort(reason="name_in_use")

        if errors := await async_validate_input(self.hass, data):
            # Bij een importfout is er geen formulier om de fout in te tonen,
            # dus wordt die als reparatiemelding in de UI gezet.
            reason = next(iter(errors.values()))
            async_create_issue(
                self.hass,
                DOMAIN,
                f"{ISSUE_YAML_IMPORT_FAILED}_{reason}",
                is_fixable=False,
                severity=IssueSeverity.ERROR,
                translation_key=f"{ISSUE_YAML_IMPORT_FAILED}_{reason}",
                translation_placeholders={"name": data[CONF_NAME]},
            )
            return self.async_abort(reason=reason)

        return self.async_create_entry(title=data[CONF_NAME], data=data)

    async def async_step_reauth(self, entry_data: Mapping[str, Any]) -> ConfigFlowResult:
        """Het token werd afgewezen; vraag om een nieuw token."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Sla een nieuw applicatietoken op."""
        errors: dict[str, str] = {}
        reauth_entry = self._get_reauth_entry()

        if user_input is not None:
            data = {**reauth_entry.data, CONF_TOKEN: user_input[CONF_TOKEN].strip()}
            errors = await async_validate_input(self.hass, data)
            if not errors:
                return self.async_update_reload_and_abort(reauth_entry, data=data)

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=TOKEN_SCHEMA,
            errors=errors,
            description_placeholders={CONF_NAME: reauth_entry.title},
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Wijzig een bestaande server (URL, token, SSL-controle, blacklist)."""
        errors: dict[str, str] = {}
        reconfigure_entry = self._get_reconfigure_entry()

        if user_input is not None:
            data = self._clean(user_input)

            if self._name_in_use(data[CONF_NAME], ignore_entry_id=reconfigure_entry.entry_id):
                errors[CONF_NAME] = "name_in_use"
            else:
                errors = await async_validate_input(self.hass, data)

            if not errors:
                # Het herladen meldt de oude notify-service af en registreert
                # de nieuwe naam, dus een hernoeming komt meteen goed door.
                return self.async_update_reload_and_abort(
                    reconfigure_entry, title=data[CONF_NAME], data=data
                )

            user_input = data

        schema = self.add_suggested_values_to_schema(
            DATA_SCHEMA, user_input or reconfigure_entry.data
        )
        return self.async_show_form(step_id="reconfigure", data_schema=schema, errors=errors)
