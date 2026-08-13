# ARCHITECTURE.md

## NL

Technisch ontwerpdocument voor wie aan de code werkt (geen gebruikershandleiding —
dat is [`README.md`](README.md)). Elke laag heeft precies één verantwoordelijkheid.

### Overzicht

```
Home Assistant UI
   config_flow.py   toevoegen / herconfigureren / opnieuw inloggen;
        │           valideert de server live en schrijft de config entry
        ▼
   __init__.py      config entry opzetten: client bouwen, token controleren,
        │           notify-platform laden via discovery, opruimen bij unload
        ▼
   notify.py        notify.<naam>-service: blacklist, titel, prioriteit,
        │           extras; importeert daarnaast oude YAML-configuratie
        ▼
   api.py           HTTP-aanroepen naar Gotify (pure aiohttp, geen
        │           Home Assistant-imports)
        ▼
   Gotify-server    GET /version, POST /message
```

### api.py — API-client

Uitsluitend verantwoordelijk voor het praten met de Gotify-server; bevat **geen**
Home Assistant-imports en is los te testen.

- `normalize_url()` — haalt spaties en afsluitende slashes weg, zodat paden veilig
  aan te plakken zijn.
- `GotifyClient.async_check_server()` — controleert via `GET /version` of hier echt
  een Gotify-server draait (het enige endpoint dat zonder token bruikbaar is).
- `GotifyClient.async_check_token()` — controleert het applicatietoken zonder een
  melding te versturen. Gotify kent geen endpoint om zo'n token te valideren, maar de
  tokencontrole zit in middleware vóór de handler van `POST /message`, terwijl die
  handler een leeg bericht weigert: een POST met een lege body geeft daardoor 401 bij
  een ongeldig token en 400 bij een geldig token.
- `GotifyClient.async_send_message()` — bouwt de payload (`title`, `message`,
  `priority`, optioneel `extras`) en verstuurt die.
- `resolve_priority()` — pure functie die zowel een getal als een naam (`high`,
  `low`, ...) omzet naar het getal dat Gotify verwacht.
- Fouten worden vertaald naar `GotifyAuthError` (token afgewezen) of
  `GotifyConnectionError` (onbereikbaar, time-out, geen Gotify-server).

### const.py — Constanten

Domeinnaam, standaardnaam, de eigen configuratiesleutel (`msg_blacklist`), de
`data`-sleutels van een serviceaanroep, de prioriteitstabel en de issue-ID's. Geen
logica.

### config_flow.py — Configuratie

De stappen voor toevoegen (`user`), overnemen uit YAML (`import`), opnieuw inloggen
(`reauth`) en wijzigen (`reconfigure`). `_clean()` normaliseert de invoer (haalt de
YAML-sleutel `platform` weg, trimt de URL en het token, vult standaardwaarden aan) en
`async_validate_input()` test de server en het token live voordat er iets opgeslagen
wordt. `_name_in_use()` bewaakt dat er geen twee entries dezelfde servicenaam
opleveren: die naam is de "geslugificeerde" naam, dus "Mijn Gotify" en "mijn gotify"
botsen met elkaar.

### __init__.py — Setup

`async_setup()` bewaart de YAML-configuratie, omdat `discovery.async_load_platform()`
die nodig heeft. `async_setup_entry()` bouwt de `GotifyClient` (met de gedeelde
aiohttp-sessie van Home Assistant, eventueel zonder SSL-verificatie), controleert het
token — een afgewezen token wordt `ConfigEntryAuthFailed` en start dus de
reauth-flow, een onbereikbare server wordt `ConfigEntryNotReady` en dus een nieuwe
poging — en laadt daarna het notify-platform via discovery. `GotifyData` is wat er per
config entry in `runtime_data` leeft: de client, en de notify-service zodra die bestaat.

`async_unload_entry()` meldt die notify-service weer af. Dat moet met de hand: legacy
notify-services staan niet in het platformregister van config entries, dus
`async_unload_platforms()` ziet ze niet. Zonder dit zou de integratie helemaal niet
ontlaadbaar zijn en zou elke wijziging een herstart van Home Assistant vragen.

### notify.py — Notify-platform

`async_get_service()` heeft twee kanten:

- **Met `discovery_info`** (de normale route, vanuit een config entry): bouwt de
  `GotifyNotificationService` en hangt die in `runtime_data` zodat het opruimen bij
  unload precies deze service raakt.
- **Zonder `discovery_info`** (een oud `notify:`-blok in `configuration.yaml`): maakt
  een reparatiemelding aan, start eenmalig een import-flow en geeft bewust géén
  service terug — die komt van de config entry die de import oplevert, zodat er nooit
  twee services met dezelfde naam naast elkaar bestaan.

`GotifyNotificationService.async_send_message()` past de blacklist toe, kiest titel en
prioriteit en vertaalt fouten uit `api.py` naar een `HomeAssistantError`, zodat een
mislukte melding zichtbaar wordt in de automation in plaats van alleen in het logboek.

### Waarom een klassieke notify-service en geen notify-entiteit

Home Assistant heeft sinds 2024.6 een moderne `NotifyEntity`, maar die kent alleen
`message` en `title`. Prioriteit en `extras` — precies waar Gotify om draait — passen
daar niet in. Daarom gebruikt deze integratie de klassieke notify-service, opgezet
vanuit een config entry via de discovery-route: hetzelfde patroon als de officiële
Pushover-integratie in Home Assistant zelf.

## EN

Technical design document for people working on the code (not a user manual — that is
[`README.md`](README.md)). Each layer has exactly one responsibility.

### Overview

```
Home Assistant UI
   config_flow.py   add / reconfigure / re-authenticate; validates the
        │           server live and writes the config entry
        ▼
   __init__.py      set up the config entry: build the client, check the
        │           token, load the notify platform via discovery, clean up
        ▼
   notify.py        notify.<name> service: blacklist, title, priority,
        │           extras; also imports old YAML configuration
        ▼
   api.py           HTTP calls to Gotify (pure aiohttp, no Home Assistant
        │           imports)
        ▼
   Gotify server    GET /version, POST /message
```

### api.py — API client

Solely responsible for talking to the Gotify server; contains **no** Home Assistant
imports and can be tested standalone.

- `normalize_url()` — strips whitespace and trailing slashes so paths can safely be
  appended.
- `GotifyClient.async_check_server()` — uses `GET /version` to check that a Gotify
  server really is running here (the only endpoint usable without a token).
- `GotifyClient.async_check_token()` — checks the application token without sending a
  notification. Gotify has no endpoint for validating such a token, but the token check
  sits in middleware ahead of the `POST /message` handler, while that handler rejects an
  empty message: a POST with an empty body therefore returns 401 for an invalid token
  and 400 for a valid one.
- `GotifyClient.async_send_message()` — builds the payload (`title`, `message`,
  `priority`, optionally `extras`) and sends it.
- `resolve_priority()` — pure function converting both a number and a name (`high`,
  `low`, ...) into the number Gotify expects.
- Errors are translated into `GotifyAuthError` (token rejected) or
  `GotifyConnectionError` (unreachable, timeout, not a Gotify server).

### const.py — Constants

Domain name, default name, the integration's own config key (`msg_blacklist`), the
`data` keys of a service call, the priority table and the issue IDs. No logic.

### config_flow.py — Configuration

The steps for adding (`user`), importing from YAML (`import`), re-authenticating
(`reauth`) and changing (`reconfigure`). `_clean()` normalizes the input (drops the
YAML `platform` key, trims the URL and token, fills in defaults) and
`async_validate_input()` tests the server and token live before anything is stored.
`_name_in_use()` makes sure no two entries produce the same service name: that name is
the slugified name, so "My Gotify" and "my gotify" collide.

### __init__.py — Setup

`async_setup()` stores the YAML configuration, because
`discovery.async_load_platform()` needs it. `async_setup_entry()` builds the
`GotifyClient` (using Home Assistant's shared aiohttp session, optionally without SSL
verification), checks the token — a rejected token becomes `ConfigEntryAuthFailed` and
so starts the reauth flow, an unreachable server becomes `ConfigEntryNotReady` and so a
retry — and then loads the notify platform via discovery. `GotifyData` is what lives in
`runtime_data` per config entry: the client, and the notify service once it exists.

`async_unload_entry()` unregisters that notify service again. This has to be done by
hand: legacy notify services are not in the config entry platform registry, so
`async_unload_platforms()` does not see them. Without this the integration would not be
unloadable at all and every change would require a Home Assistant restart.

### notify.py — Notify platform

`async_get_service()` has two sides:

- **With `discovery_info`** (the normal route, from a config entry): builds the
  `GotifyNotificationService` and stores it in `runtime_data` so that cleanup on unload
  targets exactly this service.
- **Without `discovery_info`** (an old `notify:` block in `configuration.yaml`):
  creates a repair notification, starts a one-off import flow and deliberately returns
  no service — that comes from the config entry the import produces, so two services
  with the same name never exist side by side.

`GotifyNotificationService.async_send_message()` applies the blacklist, picks the title
and priority and translates errors from `api.py` into a `HomeAssistantError`, so a
failed notification surfaces in the automation instead of only in the log.

### Why a classic notify service and not a notify entity

Home Assistant has had a modern `NotifyEntity` since 2024.6, but it only knows
`message` and `title`. Priority and `extras` — exactly what Gotify is about — do not
fit in there. That is why this integration uses the classic notify service, set up from
a config entry via the discovery route: the same pattern as the official Pushover
integration in Home Assistant itself.
