"""Gedeelde test-fixtures voor de Gotify-integratie tests.

Deze tests draaien tegen een gewone `homeassistant`-installatie (voor
type-imports en om echte API-signaturen te kunnen verifieren), maar niet
tegen een draaiende `hass`-testinstantie: `pytest-homeassistant-custom-
component` importeert bij het laden `homeassistant.runner`, dat Unix-only
stdlib-modules (`fcntl`, `resource`) gebruikt en op Windows niet werkt. Zie
tests/README.md voor wat dit wel en niet dekt.
"""

from __future__ import annotations
