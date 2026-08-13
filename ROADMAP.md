# ROADMAP.md

## NL

Dit bestand is de ideeënbus van deze Gotify-integratie: toekomstige aanpassingen,
verbeteringen en uitbreidingen die nog **niet** gebouwd zijn - geordend als *should
have* (waarschijnlijk waardevol), *could have* (leuk, situationeel) en *would have*
(later, apart traject). Nog niet alles is besproken of goedgekeurd; het is een
verzamelplek om uit te kiezen, te prioriteren of af te wijzen.

De geschiedenis van wat er al gebouwd en gewijzigd is, staat **niet** hier maar in de
[release notes](https://github.com/Sarnog/homeassistant-gotify/releases) van elke versie.

### Should have

- **De YAML-import in de praktijk beproeven.** Toevoegen via de UI en het versturen met
  prioriteiten zijn in een draaiende Home Assistant bevestigd, maar het overnemen van een
  bestaand `notify:`-blok is alleen tegen de Home Assistant-broncode geverifieerd. De
  beheerder van deze fork kwam pas bij versie 2.0.0 binnen en heeft dus nooit een
  YAML-configuratie gehad om mee te testen; bevestiging moet daarom van een gebruiker
  komen die vanaf het origineel overstapt. Werkt het bij jou (of juist niet), meld het
  dan via een issue.
- **Ondersteuning voor `target`.** Een Gotify-server kan meerdere applicaties hebben,
  elk met een eigen token. Met `targets` in de notify-service zou één integratie-entry
  naar meerdere applicaties kunnen sturen (`notify.gotify_werk` naast
  `notify.gotify_thuis`), in plaats van per applicatie een aparte entry.

### Could have

- **Een notify-entiteit náást de service.** Sinds Home Assistant 2024.6 bestaat
  `NotifyEntity`, die in de UI selecteerbaar is. Die kent alleen bericht en titel (geen
  prioriteit of extras), dus het zou puur een gemak zijn bovenop de bestaande service.
- **Afbeeldingen vanuit Home Assistant meesturen.** Nu kan `bigImageUrl` alleen naar een
  publiek bereikbare URL wijzen; een lokale camera-snapshot vraagt om uploaden naar
  Gotify of om een tijdelijke, extern bereikbare URL.
- **Standaardprioriteit per server.** Een instelling in de config flow zodat een entry
  bijvoorbeeld standaard op prioriteit 8 verstuurt zonder dat elke automation dat
  hoeft mee te geven.
- **Serverstatus als sensor.** Een `binary_sensor` die aangeeft of de Gotify-server
  bereikbaar is, zodat je mislukte meldingen kunt zien aankomen.

### Would have

- **Berichten ontvangen.** Gotify heeft een WebSocket-stream van binnenkomende
  berichten. Daarmee zou Home Assistant op meldingen van andere applicaties kunnen
  reageren - een compleet andere richting dan alleen versturen, en een apart traject.
- **Opname in de standaard HACS-store.** Nu te installeren als custom repository. Een
  aanvraag bij [hacs/default](https://github.com/hacs/default) is pas zinvol nadat deze
  fork zich in de praktijk bewezen heeft.
- **Automatisch een Gotify-server op het netwerk vinden.** *Onderzocht op 2026-08-13 en
  voorlopig afgeschreven.* Home Assistant kan alleen ontdekken wat zichzelf aankondigt,
  en de broncode van `gotify/server` bevat geen enkele verwijzing naar mDNS, zeroconf,
  Bonjour, Avahi, SSDP of UPnP - een Gotify-server laat dus niets van zich horen.
  DHCP-discovery valt af omdat die op MAC-adressen en hostnames van fysieke apparaten
  matcht. Blijven over: discovery via de Supervisor (alleen als Gotify als HA-app
  draait én die app zich aanmeldt) of zelf het subnet afscannen op `/version`, wat Home
  Assistant afraadt. Bovendien moet het applicatietoken hoe dan ook met de hand uit
  Gotify gehaald worden, dus discovery zou alleen het intypen van de URL besparen.

## EN

This file is the idea box for this Gotify integration: future changes, improvements and
additions that have **not** been built yet - grouped as *should have* (likely
valuable), *could have* (nice, situational) and *would have* (later, separate track).
Not everything here has been discussed or approved; it is a place to pick from,
prioritize or reject.

The history of what has already been built and changed is **not** here but in the
[release notes](https://github.com/Sarnog/homeassistant-gotify/releases) of each version.

### Should have

- **Try the YAML import in practice.** Adding a server through the UI and sending with
  priorities are confirmed in a running Home Assistant, but importing an existing
  `notify:` block has only been verified against the Home Assistant source. This fork's
  maintainer only came aboard at version 2.0.0 and so never had a YAML configuration to
  test with; confirmation therefore has to come from a user migrating from the original.
  If it works for you (or doesn't), please open an issue.
- **Support for `target`.** A Gotify server can have multiple applications, each with
  its own token. With `targets` on the notify service a single integration entry could
  send to several applications (`notify.gotify_work` next to `notify.gotify_home`)
  instead of needing a separate entry per application.

### Could have

- **A notify entity alongside the service.** Home Assistant has had `NotifyEntity` since
  2024.6, which is selectable in the UI. It only knows message and title (no priority or
  extras), so it would purely be a convenience on top of the existing service.
- **Sending images from Home Assistant.** Right now `bigImageUrl` can only point at a
  publicly reachable URL; a local camera snapshot would require uploading to Gotify or a
  temporary, externally reachable URL.
- **A default priority per server.** A setting in the config flow so an entry sends at
  priority 8 by default, without every automation having to pass that along.
- **Server status as a sensor.** A `binary_sensor` showing whether the Gotify server is
  reachable, so you can see failing notifications coming.

### Would have

- **Receiving messages.** Gotify has a WebSocket stream of incoming messages. That would
  let Home Assistant react to notifications from other applications - a completely
  different direction from only sending, and a separate track.
- **Inclusion in the default HACS store.** Currently installable as a custom repository.
  A request at [hacs/default](https://github.com/hacs/default) only makes sense once this
  fork has proven itself in practice.
- **Automatically finding a Gotify server on the network.** *Investigated on 2026-08-13
  and shelved for now.* Home Assistant can only discover what announces itself, and the
  `gotify/server` source contains no reference to mDNS, zeroconf, Bonjour, Avahi, SSDP or
  UPnP at all - a Gotify server stays silent. DHCP discovery is out because it matches on
  MAC addresses and hostnames of physical devices. That leaves discovery via the
  Supervisor (only if Gotify runs as a HA app and that app registers itself) or scanning
  the subnet for `/version` yourself, which Home Assistant advises against. On top of
  that, the application token has to be copied from Gotify by hand regardless, so
  discovery would only save typing the URL.
