# Tests

## NL

Deze tests draaien op gewone `pytest` + een normale `homeassistant`-package-installatie
(voor type-imports en om echte Home Assistant API-signaturen te kunnen verifieren),
maar **niet** tegen een echte draaiende `hass`-testinstantie.

**Waarom niet:** de gangbare testomgeving voor custom components,
[`pytest-homeassistant-custom-component`](https://github.com/MatthewFlamm/pytest-homeassistant-custom-component),
importeert bij het laden `homeassistant.runner`, dat op module-niveau Unix-only
stdlib-modules gebruikt (`fcntl`, `resource`). Op het Windows-ontwikkelsysteem
waarop dit project gebouwd is, bestaan die simpelweg niet - er is geen WSL of
Docker beschikbaar om dit te omzeilen.

**Wat dit wel/niet dekt:**

- `test_api.py` - volledig getest, inclusief de HTTP-aanroepen (gemockt met een eigen
  minimale async-contextmanager-nabootsing van `aiohttp.ClientSession`, zie de
  docstring bovenin dat bestand), plus `normalize_url()` en `resolve_priority()`.
- `test_config_flow_helpers.py` - test het schema en `_clean()` uit `config_flow.py`
  zonder een draaiende `hass`.
- `test_notify.py` - test `GotifyNotificationService`: blacklist, standaardtitel en
  -prioriteit, `data`-blok met prioriteit en extras, en het vertalen van fouten naar
  een `HomeAssistantError`.
- **Niet automatisch getest:** de daadwerkelijke `ConfigFlow`-stappen
  (`async_step_user`, `async_step_import`, `async_step_reauth`,
  `async_step_reconfigure`), `async_setup_entry`/`async_unload_entry` en het opzetten
  van het notify-platform via discovery - die hebben een echte `hass`-instantie nodig.
  Deze zijn wel zorgvuldig gereviewd tegen de daadwerkelijk geïnstalleerde
  `homeassistant`-broncode (methode-signaturen zijn stuk voor stuk geverifieerd, niet
  alleen uit het geheugen aangenomen). Test dit gedrag in de praktijk door de
  integratie in een echte Home Assistant-instantie te installeren.

Als je dit project op Linux/macOS ontwikkelt (of via WSL), kun je wel de volledige
`pytest-homeassistant-custom-component`-suite gebruiken voor config-flow- en
setup-tests.

## EN

These tests run on plain `pytest` plus a regular `homeassistant` package install
(for type imports and to verify real Home Assistant API signatures), but **not**
against a real running `hass` test instance.

**Why not:** the standard test harness for custom components,
[`pytest-homeassistant-custom-component`](https://github.com/MatthewFlamm/pytest-homeassistant-custom-component),
imports `homeassistant.runner` on load, which uses Unix-only stdlib modules at module
level (`fcntl`, `resource`). On the Windows development machine this project was built
on, those simply don't exist - and no WSL or Docker is available to work around it.

**What this does/doesn't cover:**

- `test_api.py` - fully tested, including the HTTP calls (mocked with a small
  hand-rolled async-context-manager stand-in for `aiohttp.ClientSession`, see that
  file's docstring), plus `normalize_url()` and `resolve_priority()`.
- `test_config_flow_helpers.py` - tests the schema and `_clean()` from
  `config_flow.py` without a running `hass`.
- `test_notify.py` - tests `GotifyNotificationService`: the blacklist, the default
  title and priority, the `data` block with priority and extras, and the translation of
  errors into a `HomeAssistantError`.
- **Not automatically tested:** the actual `ConfigFlow` steps (`async_step_user`,
  `async_step_import`, `async_step_reauth`, `async_step_reconfigure`),
  `async_setup_entry`/`async_unload_entry` and setting up the notify platform via
  discovery - those need a real `hass` instance. These were carefully reviewed against
  the actually-installed `homeassistant` source (method signatures were verified one by
  one, not assumed from memory). Verify this behavior in practice by installing the
  integration on a real Home Assistant instance.

If you develop this project on Linux/macOS (or via WSL), you can use the full
`pytest-homeassistant-custom-component` suite for config-flow and setup tests.
