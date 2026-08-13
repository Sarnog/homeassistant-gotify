"""Constanten voor de Gotify-integratie."""

from __future__ import annotations

from typing import Final

DOMAIN: Final = "gotify"
DEFAULT_NAME: Final = "Gotify"

# Eigen configuratiesleutel; url/token/verify_ssl komen uit homeassistant.const.
CONF_MSG_BLACKLIST: Final = "msg_blacklist"

# Hier bewaart async_setup() de volledige YAML-configuratie, omdat
# discovery.async_load_platform() die nodig heeft om het notify-platform
# vanuit een config entry op te zetten.
DATA_HASS_CONFIG: Final = "gotify_hass_config"

# Sleutels binnen het optionele `data`-blok van een notify-serviceaanroep.
ATTR_PRIORITY: Final = "priority"
ATTR_EXTRAS: Final = "extras"

DEFAULT_PRIORITY: Final = 5

# Gotify werkt met numerieke prioriteiten; deze namen zijn een gemak voor
# automations en komen uit de oorspronkelijke YAML-implementatie.
PRIORITIES: Final[dict[str, int]] = {
    "high": 10,
    "normal": 5,
    "default": 5,
    "low": 2,
    "min": 0,
    "none": 0,
}

ISSUE_DEPRECATED_YAML: Final = "deprecated_yaml"
ISSUE_YAML_IMPORT_FAILED: Final = "deprecated_yaml_import_failed"
