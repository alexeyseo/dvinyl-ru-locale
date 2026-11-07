# Changelog

Русская версия: [CHANGELOG.ru.md](CHANGELOG.ru.md)

## 2.1.0 — 7 November 2026

- **Russian is merged upstream.** `Kyonew/DVinyl` took both pull requests into `release/4.0.0`:
  #220 for the locale and the language registration (6 files), #221 for decades, money, the
  tracklist header and the ruble (12 files). `locales/ru.json` now ships with the app, and the
  README lists Russian among the interface languages.
- **The ruble did not survive the merge.** Discogs refuses `curr_abbr=RUB` and the card-game
  sources return USD or EUR only, so every estimate would have been shown as rubles with a wrong
  amount; the author took it out until prices are converted between currencies. The patch no longer
  adds it.
- **Decades are a translation key upstream, not a code map.** `t('collection.decade_value', { year })`
  replaced the per-language pattern table, so a new language needs only a string. The patch no
  longer carries `decadeText`; `collection.decade_value` is `{{year}}-е` in this locale.
- **The locale caught up with the branch, 2376 → 2435 positions** against 2426 English leaves:
  47 strings from the commits of 7 November (vinyl size, speed, release type and disc count;
  purchase price and paid-versus-estimate; wishes of other members; saved views; places no
  furniture holds; the kept-source controls) and 12 from the repeating-rows field
  (`common.add_row`, `create_plugin.type_rows`, runout rows for vinyl). Parity is complete, no
  placeholders broken, no empty values.
- **The patch shrank from nineteen edits to the seven registration points.** Decades, money, the
  tracklist header and the ruble are gone — upstream made them itself or turned them down. On a
  current `release/4.0.0` every edit reports “already applied”, so the script is a guard, not a
  translation carrier: it keeps the package usable on trees cut before the merge and puts a
  registration point back if a later release drops one.
- **`watch-upstream.py` watches the merge instead of the patch:** new English strings, and whether
  Russian is still registered in all seven places. Wordings upstream phrases differently are
  listed only with `--report-wording`, since the package keeps the read-through version.
- **`scripts/check-locale.py` no longer mistakes a lone key for a plural group.** A group is a
  `_one`/`_other` pair; `collection.shelf_move_one` is the single-item action (“Move elsewhere”)
  and used to demand forms that will never exist.
- Fifteen strings are worded differently in this package than upstream, deliberately — for
  example `confirm_vinyl.field_release_type` is “Тип издания”, not “Тип релиза”, and
  `wishes.found_title` reads “Желаемое в ваших коллекциях”. Sending them as a follow-up pull
  request is the owner's call.

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
