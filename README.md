  <a href="#nl">NL</a> | <a href="#en">EN</a>

<div align="center">
  <!-- align="center" centreert alles binnen deze div -->
  <h1>
    <!-- h1 = grootste kop, standaard al dikgedrukt en groot -->
    <ins>Gotify Notifications</ins>
    <!-- ins = onderstreepte tekst op GitHub -->
  </h1>
</div>


##### <ins>NL</ins>

Een integratie voor Home Assistant om notificaties te sturen via [Gotify](https://gotify.net/),
met een eigen prioriteit en extra's zoals een klik-URL of een afbeelding.

> **Dit is een fork van [1RandomDev/homeassistant-gotify](https://github.com/1RandomDev/homeassistant-gotify).**
> Het oorspronkelijke notify-platform is het werk van [1RandomDev](https://github.com/1RandomDev);
> deze fork wordt onderhouden door [Sarnog](https://github.com/Sarnog) en voegt daar vanaf
> versie 2.0.0 configuratie via de UI aan toe, in plaats van via `configuration.yaml`.
> Zie [Overstappen vanaf YAML](#overstappen-vanaf-yaml) als je van het origineel komt.

<!-- Tabel zodat de labels en de knoppen in twee nette, uitgelijnde kolommen
     staan die zich op elk scherm aanpassen. -->
<table>
  <tr>
    <td>Integratie toevoegen:</td>
    <td><a href="https://my.home-assistant.io/redirect/hacs_repository/?owner=Sarnog&amp;repository=homeassistant-gotify&amp;category=integration"><img src="https://my.home-assistant.io/badges/hacs_repository.svg" alt="Open your Home Assistant instance and open a repository inside the Home Assistant Community Store."></a></td>
  </tr>
  <tr>
    <td>Integratie instellen:</td>
    <td><a href="https://my.home-assistant.io/redirect/config_flow_start/?domain=gotify"><img src="https://my.home-assistant.io/badges/config_flow_start.svg" alt="Open your Home Assistant instance and start setting up a new integration."></a></td>
  </tr>
</table>

**Te installeren via HACS als custom repository, of handmatig - zie [Installatie](#installatie).**

### Wat doet dit

Je stelt een of meer Gotify-servers in via de Home Assistant-interface. Elke server
levert een notify-service op (`notify.<naam>`) waarmee je vanuit automations,
scripts en scènes berichten naar Gotify stuurt - inclusief prioriteit en de
volledige `extras` die de Gotify-API kent.

Vanaf versie 2.0.0 wordt de integratie **volledig via de UI ingesteld**; een
bestaand `notify:`-blok in `configuration.yaml` wordt automatisch overgenomen.
Zie [Overstappen vanaf YAML](#overstappen-vanaf-yaml).

### Installatie

**Vereist:** Home Assistant **2024.6** of nieuwer. De integratie gebruikt
`entry.runtime_data` met een getypeerde config entry, die sinds 2024.6 bestaat.

**Via HACS** (aanbevolen): klik de HACS-badge bovenaan dit bestand, of voeg deze repository
handmatig toe als **custom repository** in HACS (HACS > drie puntjes > Aangepaste
repositories > deze GitHub-URL, categorie "Integratie").

**Handmatig**, als alternatief:

1. Kopieer de map `custom_components/gotify` naar de `custom_components`-map van
   je Home Assistant-configuratie.
2. Herstart Home Assistant.

### Een server toevoegen

Ga naar **Instellingen > Apparaten en diensten > Integratie toevoegen** en zoek op
"Gotify". Je vult in:

| Veld | Betekenis |
| --- | --- |
| **Naam** | Bepaalt de servicenaam. "Mijn Gotify" wordt `notify.mijn_gotify`. |
| **URL** | De basis-URL van je Gotify-server, bijvoorbeeld `https://gotify.voorbeeld.nl`. |
| **Applicatietoken** | Een *applicatie*token uit Gotify (Apps > applicatie aanmaken). Een clienttoken werkt niet. |
| **SSL-certificaat controleren** | Alleen uitzetten bij een zelfondertekend certificaat. |
| **Geblokkeerde berichten** | Berichten waarvan de tekst hier exact op staat, worden weggegooid in plaats van verstuurd (handig voor bijvoorbeeld `TTS`). |

Bij het opslaan wordt gecontroleerd of er op die URL echt een Gotify-server draait en
of het token geaccepteerd wordt. Daar wordt géén testmelding voor verstuurd: Gotify
weigert een leeg bericht, terwijl de tokencontrole daar al vóór plaatsvindt.

Later wijzigen kan via **Herconfigureren** bij de integratie; wordt je token ongeldig,
dan verschijnt vanzelf een melding om een nieuw token in te vullen. Let op: bij het
wijzigen van de naam verandert ook de naam van de notify-service, dus automations die
de oude naam gebruiken moeten aangepast worden.

### Gebruik

De integratie accepteert dezelfde waarden als de officiële Gotify-API. Een volledige
lijst van mogelijke `extras` staat in de [Gotify-documentatie](https://gotify.net/docs/msgextras).

#### Simpel tekstbericht

```yaml
actions:
  - action: notify.mijn_gotify
    data:
      message: "Dit is een testbericht."
```

#### Bericht met titel en prioriteit

```yaml
actions:
  - action: notify.mijn_gotify
    data:
      message: "Dit is een testbericht."
      title: "Gotify-test"
      data:
        priority: 10
```

Naast een getal (0-10) mag `priority` ook een naam zijn: `high` (10), `normal` /
`default` (5), `low` (2), `min` / `none` (0). Zonder prioriteit wordt 5 gebruikt.

#### Bericht met klik-actie

```yaml
actions:
  - action: notify.mijn_gotify
    data:
      message: "Dit is een testbericht."
      title: "Gotify-test"
      data:
        priority: 10
        extras:
          'client::notification':
            click:
              url: https://www.home-assistant.io/
```

#### Bericht met afbeelding

```yaml
actions:
  - action: notify.mijn_gotify
    data:
      message: "Dit is een testbericht."
      title: "Gotify-test"
      data:
        priority: 10
        extras:
          'client::notification':
            bigImageUrl: https://example.com/foto.jpg
```

### Overstappen vanaf YAML

Had je Gotify eerder via `configuration.yaml` ingesteld, dan hoef je niets voor te
bereiden: bij de eerste start na het bijwerken wordt die configuratie automatisch
overgenomen als integratie in de UI, met dezelfde naam - en dus dezelfde
`notify.<naam>`-service. Je bestaande automations blijven werken.

Daarna verschijnt er een reparatiemelding met het verzoek het oude blok op te ruimen.
Haal het Gotify-gedeelte uit het `notify:`-blok van je `configuration.yaml`:

```yaml
# Deze regels mogen weg na de overstap:
notify:
  - name: "mijn gotify"
    platform: gotify
    url: <gotify_url>
    token: <gotify_token>
```

en herstart Home Assistant.

Eén uitzondering: had je blok géén `name:`, dan heette de service voorheen
`notify.notify`. Die naam is niet te behouden (hij is niet van Gotify), dus na het
overnemen heet de service `notify.gotify` en moeten je automations daarop aangepast
worden.

Lukt het overnemen niet (server onbereikbaar of token afgewezen), dan meldt de
integratie dat als reparatiemelding, zodat je de server handmatig kunt toevoegen.

### Architectuur

De interne structuur van de integratie - de lagen, hun verantwoordelijkheden en de
conventies - staat beschreven in [ARCHITECTURE.md](ARCHITECTURE.md).

### Ideeën en geschiedenis

Toekomstige uitbreidingen en ideeën staan in [`ROADMAP.md`](ROADMAP.md). De
wijzigingsgeschiedenis per versie staat in de
[release notes](https://github.com/Sarnog/homeassistant-gotify/releases).

### Met dank aan

Deze integratie is een fork van
[1RandomDev/homeassistant-gotify](https://github.com/1RandomDev/homeassistant-gotify),
waarop het oorspronkelijke YAML-notify-platform gebouwd is. Deze fork voegt daar
configuratie via de UI, asynchrone HTTP-aanroepen en meertalige teksten aan toe.

Het pictogram is het logo van [Gotify](https://github.com/gotify/logo), gebruikt onder de
[CC BY 4.0-licentie](http://creativecommons.org/licenses/by/4.0/) en alleen bijgesneden en
verkleind. De oorspronkelijke Go-gopher is ontworpen door
[Renee French](http://reneefrench.blogspot.com/).

### Licentie

Het hele project valt onder de [GPL-3-licentie](https://www.gnu.org/licenses/gpl-3.0.html).

### Steun dit project ☕

Vind je deze integratie nuttig? Een kleine bijdrage houdt de koffie warm en de
commits komende. Volledig vrijblijvend, uiteraard!

<!-- Ko-fi badge via shields.io, geen externe tracking -->
[![Koop me een koffie op Ko-fi](https://img.shields.io/badge/Ko--fi-Koop%20me%20een%20koffie-FF5E5B?style=for-the-badge&logo=kofi&logoColor=white)](https://ko-fi.com/sarnog)

<!-- GitHub Sponsors badge, toont live het aantal sponsors -->
[![Sponsor via GitHub](https://img.shields.io/github/sponsors/sarnog?style=for-the-badge&logo=github&label=Sponsors&color=EA4AAA)](https://github.com/sponsors/sarnog)


---



##### <ins>EN</ins>

A Home Assistant integration for sending notifications via [Gotify](https://gotify.net/),
with a custom priority and extras such as a click URL or an image.

> **This is a fork of [1RandomDev/homeassistant-gotify](https://github.com/1RandomDev/homeassistant-gotify).**
> The original notify platform is the work of [1RandomDev](https://github.com/1RandomDev);
> this fork is maintained by [Sarnog](https://github.com/Sarnog) and, as of version 2.0.0,
> adds configuration through the UI instead of through `configuration.yaml`.
> See [Migrating from YAML](#migrating-from-yaml) if you are coming from the original.

<!-- Table so the labels and the buttons sit in two neat, aligned columns
     that adapt to any screen size. -->
<table>
  <tr>
    <td>Add integration:</td>
    <td><a href="https://my.home-assistant.io/redirect/hacs_repository/?owner=Sarnog&amp;repository=homeassistant-gotify&amp;category=integration"><img src="https://my.home-assistant.io/badges/hacs_repository.svg" alt="Open your Home Assistant instance and open a repository inside the Home Assistant Community Store."></a></td>
  </tr>
  <tr>
    <td>Set up integration:</td>
    <td><a href="https://my.home-assistant.io/redirect/config_flow_start/?domain=gotify"><img src="https://my.home-assistant.io/badges/config_flow_start.svg" alt="Open your Home Assistant instance and start setting up a new integration."></a></td>
  </tr>
</table>

**Install via HACS as a custom repository, or manually - see [Installation](#installation).**

### What this does

You configure one or more Gotify servers through the Home Assistant interface. Each
server provides a notify service (`notify.<name>`) for sending messages to Gotify from
automations, scripts and scenes - including the priority and the full `extras` the
Gotify API supports.

As of version 2.0.0 the integration is **configured entirely through the UI**; an
existing `notify:` block in `configuration.yaml` is imported automatically. See
[Migrating from YAML](#migrating-from-yaml).

### Installation

**Requires:** Home Assistant **2024.6** or newer. The integration uses
`entry.runtime_data` with a typed config entry, which exists since 2024.6.

**Via HACS** (recommended): click the HACS badge at the top of this file, or add this
repository manually as a **custom repository** in HACS (HACS > three dots > Custom
repositories > this GitHub URL, category "Integration").

**Manually**, as an alternative:

1. Copy the `custom_components/gotify` folder into the `custom_components` folder of
   your Home Assistant configuration.
2. Restart Home Assistant.

### Adding a server

Go to **Settings > Devices & services > Add integration** and search for "Gotify".
You fill in:

| Field | Meaning |
| --- | --- |
| **Name** | Determines the service name. "My Gotify" becomes `notify.my_gotify`. |
| **URL** | The base URL of your Gotify server, for example `https://gotify.example.com`. |
| **Application token** | An *application* token from Gotify (Apps > create application). A client token will not work. |
| **Verify SSL certificate** | Only turn this off for a self-signed certificate. |
| **Blocked messages** | Messages whose text matches one of these entries exactly are discarded instead of sent (handy for something like `TTS`). |

On save, the integration checks that a Gotify server really is running at that URL and
that the token is accepted. No test notification is sent for this: Gotify rejects an
empty message, while the token check already happens before that.

You can change everything later via **Reconfigure** on the integration; if your token
stops working, a repair notification appears asking for a new one. Note that changing
the name also changes the notify service name, so automations using the old name have
to be updated.

### Usage

This integration accepts the same values as the official Gotify API. For a full list of
extras that can be added to a notification, refer to the
[Gotify docs](https://gotify.net/docs/msgextras).

#### Simple text message

```yaml
actions:
  - action: notify.my_gotify
    data:
      message: "This is a test message."
```

#### Message with title and priority

```yaml
actions:
  - action: notify.my_gotify
    data:
      message: "This is a test message."
      title: "Gotify Test"
      data:
        priority: 10
```

Besides a number (0-10), `priority` also accepts a name: `high` (10), `normal` /
`default` (5), `low` (2), `min` / `none` (0). Without a priority, 5 is used.

#### Message with click event

```yaml
actions:
  - action: notify.my_gotify
    data:
      message: "This is a test message."
      title: "Gotify Test"
      data:
        priority: 10
        extras:
          'client::notification':
            click:
              url: https://www.home-assistant.io/
```

#### Message with image

```yaml
actions:
  - action: notify.my_gotify
    data:
      message: "This is a test message."
      title: "Gotify Test"
      data:
        priority: 10
        extras:
          'client::notification':
            bigImageUrl: https://example.com/photo.jpg
```

### Migrating from YAML

If you configured Gotify through `configuration.yaml` before, there is nothing to
prepare: on the first start after updating, that configuration is imported
automatically as a UI integration, under the same name - and therefore with the same
`notify.<name>` service. Your existing automations keep working.

A repair notification then asks you to clean up the old block. Remove the Gotify part
from the `notify:` block in your `configuration.yaml`:

```yaml
# These lines can go after the migration:
notify:
  - name: "my gotify"
    platform: gotify
    url: <gotify_url>
    token: <gotify_token>
```

and restart Home Assistant.

One exception: if your block had no `name:`, the service used to be called
`notify.notify`. That name cannot be kept (it isn't Gotify's), so after the import the
service is called `notify.gotify` and your automations have to be updated to match.

If the import fails (server unreachable or token rejected), the integration reports
that as a repair notification so you can add the server manually.

### Architecture

The integration's internal structure - the layers, their responsibilities and the
conventions - is documented in [ARCHITECTURE.md](ARCHITECTURE.md).

### Ideas and history

Future additions and ideas live in [`ROADMAP.md`](ROADMAP.md). The per-version change
history is in the [release notes](https://github.com/Sarnog/homeassistant-gotify/releases).

### Credits

This integration is a fork of
[1RandomDev/homeassistant-gotify](https://github.com/1RandomDev/homeassistant-gotify),
which the original YAML notify platform was built on. This fork adds UI configuration,
asynchronous HTTP calls and translated texts on top of that.

The icon is the [Gotify](https://github.com/gotify/logo) logo, used under the
[CC BY 4.0 license](http://creativecommons.org/licenses/by/4.0/) and only cropped and
resized. The original Go gopher was designed by
[Renee French](http://reneefrench.blogspot.com/).

### License

The whole project is under the [GPL-3 license](https://www.gnu.org/licenses/gpl-3.0.html).

### Support this project ☕

Do you find this integration useful? A small contribution keeps the coffee
warm and the commits coming. Entirely optional, of course!

<!-- Ko-fi badge via shields.io, no external tracking -->
[![Buy me a coffee on Ko-fi](https://img.shields.io/badge/Ko--fi-Buy%20me%20a%20coffee-FF5E5B?style=for-the-badge&logo=kofi&logoColor=white)](https://ko-fi.com/sarnog)

<!-- GitHub Sponsors badge, shows the sponsor count live -->
[![Sponsor via GitHub](https://img.shields.io/github/sponsors/sarnog?style=for-the-badge&logo=github&label=Sponsors&color=EA4AAA)](https://github.com/sponsors/sarnog)
