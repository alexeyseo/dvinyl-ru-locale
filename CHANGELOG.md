# Changelog

Русская версия: [CHANGELOG.ru.md](CHANGELOG.ru.md)

## 2.1.0 — 7 November 2026

- Russian is merged upstream: pull requests #220 (locale and language registration) and #221
  (decades, money, tracklist header, ruble) landed in `release/4.0.0`, and `locales/ru.json` now
  ships with the app.
- The ruble is not part of the merge: Discogs refuses `curr_abbr=RUB`, and the card-game sources
  return USD or EUR only.
- Decades are written through `collection.decade_value`; the Russian value is `{{year}}-е`.
- The locale holds 2435 entries against 2426 English keys. Added: vinyl size, speed, release type,
  disc count and runout rows; purchase price and paid-versus-estimate; wishes of other members;
  saved views; places no furniture holds; repeating-row fields.
- `apply-ru-locale.js` covers the seven language registration points. Decades, money, the
  tracklist header and the ruble are removed from it.
- `check-locale.py` reads a plural group as a `_one`/`_other` pair, so single keys ending in `_one`
  are no longer reported as groups.
- `watch-upstream.py` reports new English keys and missing registration points; `--report-wording`
  adds strings worded differently upstream.

## 2.0.0 — 4 November 2026

- The package moves to DVinyl 4.0.0: the locale holds 2376 positions with no gaps against the
  `release/4.0.0` `en.json`. Registering a language grew to **seven places** — the language list is
  hand-written not only in the settings but also in the setup wizard (`views/setup.ejs`, both the
  label and its own dropdown).
- The patch is now nineteen edits: besides registration it carries decades written the way the
  language writes them (`decadeText` next to `dateLocaleFor`), money formatted by the interface
  language, a fallback currency for when Discogs returns none, the tracklist duration header
  through a locale key, and the ruble in `SUPPORTED_CURRENCIES`.
- The “apply the saved language” edit is gone: 4.0.0 does that in `app.ts` itself.
- New `Dockerfile.source` builds from the `release/4.0.0` branch, since 4.0.0 has no official image
  yet. `Dockerfile` stays for releases that do, defaulting to `ghcr.io/kyonew/dvinyl:latest`.
- Code comments and the steps in `README`/`AGENTS.md` are English now; README and CHANGELOG are
  bilingual.
- `scripts/check-locale.py` takes a branch (`--ref`, `release/4.0.0` by default); `watch-upstream.py`
  checks the new patch anchors and looks there by default. CI builds the image from
  `Dockerfile.source`.

## 1.1.0 — 4 November 2026

- The translation now covers DVinyl 4.0.0: the 899 strings missing against `release/4.0.0`
  are translated, taking the locale from 1478 to 2374 keys. New sections included: the plugin
  studio, requests, notifications, layout, dashboard, and the card-collection modules
  (Pokémon, MTG, Yu-Gi-Oh!, One Piece, Lorcana, Star Wars Unlimited, Digimon, Flesh and Blood).
- Russian plural forms: `_few` and `_many` accompany the English `_one/_other` pair, so the
  locale carries 21 forms the English set does not have.
- Trading-card rules terms stay in the original (`Planeswalker`, `Trainer`, `Digi-Egg`, `Tamer`,
  `Unit`, `Pitch`, `Near Mint (NM)`); field labels remain Russian.
- Sleeve condition: the grading scale stays English (`Mint (M)`, `Very Good Plus (VG+)`), and the
  last option is `Generic Sleeve` again.
- Background types: “Однотонный” and “Изображение” overflowed their tiles, so they became
  “Цвет” and “Картинка” — “Цвет · Градиент · Узор · Картинка”.
- Font names are not translated: “С засечками” and “Моноширинный” are `Serif` and `Mono` again.
  The utility options “Как у текста” and “Системный” stay translated.
- Media type in the add form: “Цифровое издание” stretched the button, so it is “Цифровое”;
  “Физическое”, “Коллекционное” and “Лимитированное” are shortened the same way.
- The tracklist duration header knew only French and English
  (`=== 'Année' ? 'Durée' : 'Duration'`) and printed “Duration” in Russian; the template now
  uses the `tracklist.col_duration` key (value refined to “Длительность”).
- The table column “Данные” became “Сведения”: the source string is `Info`, and the cell holds
  the author or artist.
- Furniture editor: “Раскладка” became “Форма мебели”, which is what the code means by it —
  the shape of a compartment (a cube or a full-width plank). The values stay “Ячейки” and “Ряды”
  because “Полки” already names the list of compartments inside a piece of furniture.
- Collection search placeholder: “Фильтр…” (a calque of `Filter...`) became “Поиск”; the same
  string labels the active-filter chip, where an ellipsis read badly.
- New `scripts/build-review-page.py`: a review page listing the key, the English source, the
  translation, with search and “empty / same as EN / latin / placeholders” marks.

## 1.0.4 — 2 November 2026

- The ruble joined the settings: `RUB` is in the user schema, in the save-route validation, in
  the dropdown and in the locales. Amounts print as “1 234,50 ₽”.

## 1.0.3 — 2 November 2026

- The decade filter no longer prints the English “s”: Russian reads “2020-е”, German “2020er”,
  and the romance languages put a word before the year. With several decades selected the control
  shows a range instead of a count.

## 1.0.2 — 2 November 2026

- Prices in the collection estimate and on the item page follow the interface language; they used
  to be hardwired to `fr-FR` or `en-US`, so Russian printed them the American way.
- When Discogs returned no currency code the item page showed an error instead of a price; it now
  falls back to the currency from the settings.

## 1.0.1 — 2 November 2026

- Fixed the module label in the navigation: `media.comic` reads “Комиксы” instead of “Комикс”.
  The English key is plural, and the singular next to “Книги” read as a mistake. The format
  filter keeps the singular “Комикс”.

## 1.0.0 — 2 November 2026

First release. The Russian interface of DVinyl: the locale file plus the edits that register it
in the app.

Install:

- as an image — clone the repository and point compose at `build: ./dvinyl-ru`;
- from source — `install-source.sh` on a DVinyl clone;
- through an agent — the steps in `AGENTS.md`.

After installing, pick the language in the settings: Settings → Language → Русский. A check
without signing in is `/login?lng=ru`.

Taken from the 3.3.0 `en.json`. Compared with `master` on 2 November 2026: no drift, and the
lines the patch cuts into are in place.
