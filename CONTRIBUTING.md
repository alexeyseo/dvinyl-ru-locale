# Helping with the translation

Wording, terms and new strings go through a pull request. One file is enough: `locales/ru.json`.

**Русская версия:** [CONTRIBUTING.ru.md](CONTRIBUTING.ru.md)

## What to do

1. Fork the repository and create a branch.
2. Edit the values you need in `locales/ru.json`. Do not change the keys, and keep the `{{…}}`
   placeholders exactly as they are.
3. Run the checks — a pull request without them will not pass:
   ```bash
   python3 scripts/check-locale.py
   node .github/scripts/pluralization-check.js
   ```
4. Open the pull request: what it was, what it became, and why. Several places at once — as a list.

## Style

Informational: the verb first, no “please” and no “your”, no officialese. A dangerous action says what
exactly will be lost: “Delete the list “{{name}}”? Its records stay in the collection”.

## Terms

One word per entity, or the interface ends up mixing “plates” and “records”.

- item → запись
- release → издание
- pressing → прессинг
- wishlist → желаемое
- shelf → полка
- track / tracklist → трек / треклист
- cover → обложка
- barcode → штрихкод
- rating → оценка
- publisher → издатель
- location → место

Service names are not translated: Discogs, TMDB, IGDB, ScreenScraper, Rebrickable, BoardGameGeek,
GoodReads, Libib, Hardcover, Open Library, Musik-Sammler.

## Plurals

English has two forms, Russian has three: `_one`, `_few`, `_many`. When you edit such a string, edit all
three. Example: `{{count}} трек` / `{{count}} трека` / `{{count}} треков`.

## New strings from upstream

When DVinyl gains new labels they show up in English — i18next uses `en.json` as the fallback language.
They are closed the same way: add the keys to `locales/ru.json`.
