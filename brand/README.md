🇳🇱 [Nederlands](#merklogo) | 🇬🇧 [English](#brand-logo)

---

# Merklogo

Sinds **Home Assistant 2026.3** levert een custom integratie zijn eigen merklogo
mee in de integratie zelf. Een pull request naar
[home-assistant/brands](https://github.com/home-assistant/brands) is niet alleen
overbodig maar wordt daar ook actief geweigerd: een bot sluit zulke PR's binnen
enkele seconden ("we no longer accept brand icons for custom integrations").
Zie de [aankondiging](https://developers.home-assistant.io/blog/2026/02/24/brands-proxy-api).

Home Assistant leest de afbeeldingen uit een `brand/`-map binnen de integratie en
geeft die voorrang boven de centrale brands-CDN. Er is geen aanpassing in
`manifest.json` of `hacs.json` voor nodig.

De actieve bestanden staan dus in `custom_components/gotify/brand/`:

- `icon.png` (256×256)
- `icon@2x.png` (512×512)

`logo.png` en `logo@2x.png` ontbreken bewust: Home Assistant valt voor een
logo-verzoek automatisch terug op `icon.png`, en het logo en het icoon zijn hier
dezelfde afbeelding.

**Let op bij het uitbrengen:** de `brand/`-map moet ín de release-tag zitten.
Wordt hij later toegevoegd, dan krijgen HACS-gebruikers het icoon pas bij de
volgende versie.

## Herkomst en licentie

De afbeeldingen zijn afgeleid van het officiële Gotify-logo uit
[gotify/logo](https://github.com/gotify/logo), gelicentieerd onder
[CC BY 4.0](http://creativecommons.org/licenses/by/4.0/). De oorspronkelijke
Go-gopher is ontworpen door [Renee French](http://reneefrench.blogspot.com/).

Het bronbestand (`gotify-logo.png`, 578×469) is alleen ontdaan van transparante
randen en verkleind naar een vierkant, transparant canvas — niet hertekend, niet
verkleurd en nooit opgeschaald.

---

# Brand logo

Since **Home Assistant 2026.3**, a custom integration ships its own brand logo
inside the integration itself. A pull request to
[home-assistant/brands](https://github.com/home-assistant/brands) is not merely
unnecessary — it is actively refused there: a bot closes such PRs within seconds
("we no longer accept brand icons for custom integrations"). See the
[announcement](https://developers.home-assistant.io/blog/2026/02/24/brands-proxy-api).

Home Assistant reads the images from a `brand/` folder inside the integration and
gives those priority over the central brands CDN. No change to `manifest.json` or
`hacs.json` is needed.

The active files therefore live in `custom_components/gotify/brand/`:

- `icon.png` (256×256)
- `icon@2x.png` (512×512)

`logo.png` and `logo@2x.png` are deliberately absent: Home Assistant falls back
to `icon.png` for a logo request, and here the logo and the icon are the same
image.

**Watch out when releasing:** the `brand/` folder has to be inside the release
tag. Add it afterwards and HACS users only get the icon with the next version.

## Origin and licence

The images are derived from the official Gotify logo in
[gotify/logo](https://github.com/gotify/logo), licensed under
[CC BY 4.0](http://creativecommons.org/licenses/by/4.0/). The original Go gopher
was designed by [Renee French](http://reneefrench.blogspot.com/).

The source file (`gotify-logo.png`, 578×469) was only trimmed of transparent
edges and scaled down onto a square transparent canvas — not redrawn, not
recoloured and never upscaled.
