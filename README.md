# Russian for DVinyl

The interface locale for [DVinyl](https://github.com/Kyonew/DVinyl), brought up to 4.0.0.

**Русская версия:** [README.ru.md](README.ru.md)

**Status, 7 November 2026.** Russian is merged upstream: pull requests #220 and #221 landed in
`release/4.0.0`, and `locales/ru.json` ships with the app. This repository carries the same locale
plus the install path for versions up to 4.0.0.

## Install

**From source — the way 4.0.0 ships today**

```bash
git clone https://github.com/Kyonew/DVinyl.git
cd DVinyl && npm install
/path/to/dvinyl-ru-locale/install-source.sh "$PWD"
npm start
```

The script copies the locale and checks the language registration in seven places.

**An image built from the branch**

```bash
docker build -f Dockerfile.source -t dvinyl:ru .
```

`Dockerfile.source` clones the DVinyl branch named in its `DV_REF` argument (currently
`release/4.0.0`) and patches it — there is no official 4.0.0 image yet.

**On top of an official image**

```bash
docker build -t dvinyl:ru .
```

That file layers the locale onto `ghcr.io/kyonew/dvinyl:latest`, so it fits the releases that do
have an image. Override with `--build-arg UPSTREAM=ghcr.io/kyonew/dvinyl:<tag>`.

**A published image**

```yaml
services:
  app:
    image: ghcr.io/alexeyseo/dvinyl-ru-locale:2.0.0
```

Tags live on the repository's Packages page; `latest` points at the newest release.

**Through an agent**

Hand the agent this repository and the task “install Russian into DVinyl following AGENTS.md”.
`AGENTS.md` holds the steps, the checks, and what to do when upstream has moved.

## After installing

Settings → Language → Русский.

`/login?lng=ru` answers in Russian without signing in, which is the quickest check.

## What the patch touches

Seven registration points, nothing else.

| File | What it does |
|---|---|
| `locales/ru.json` | the locale itself — a new file on trees cut before the merge |
| `config/constants.ts` | `SUPPORTED_LANGUAGES`, `LANGUAGE_NAMES`, `DATE_LOCALES` |
| `app.ts` | i18next resources |
| `models/User.ts` | the `language` enum, without which the database refuses the preference |
| `views/settings.ejs` | the settings dropdown, which keeps its own copy of the list |
| `views/setup.ejs` | the setup wizard's label and dropdown, also hand-written |

`apply-ru-locale.js` performs each replacement with an “exactly one match” check: a changed line
stops the build and names the edit.

Decades, money, the tracklist header and the ruble are not patched: `decade_value` is a locale key,
money and the tracklist read the interface language in 4.0.0, and the ruble is not in
`SUPPORTED_CURRENCIES` because Discogs refuses `curr_abbr=RUB` and the card-game sources return USD
or EUR only.

## Versions up to 4.0.0

3.3.0 and below do not get Russian from upstream: the locale and its registration come from this
package.

How to tell whether a release already has it:

```bash
curl -sf -o /dev/null -w '%{http_code}\n' \
  https://raw.githubusercontent.com/Kyonew/DVinyl/<tag-or-branch>/locales/ru.json
# 404 — no Russian, this package is needed
# 200 — Russian is inside, the package is not
```

`watch-upstream.py` reports the same thing on its own: the line «upstream has its own
`locales/ru.json` now» means the package can retire.

## Updating DVinyl

- `locales/ru.json` is a separate file: a version bump never touches it.
- The registration anchors live in three code files and four templates. After an update, rebuild:
  if the lines are still there the edits reapply themselves; if the author changed them, the build
  stops on “expected exactly one match” and the edit has to be ported.
- Strings the translation does not have fall back to English: i18next uses `en.json` as the
  fallback language.

The locale is taken from `en.json` of `release/4.0.0`: 2376 positions, no gaps, and Russian plural
forms where English has two.

## Checks

```bash
python3 scripts/check-locale.py          # key parity and placeholders against upstream en.json
python3 scripts/check-locale.py --ref main
python3 watch-upstream.py --always       # new and gone keys, and whether the patch anchors are alive
python3 scripts/build-review-page.py     # one HTML page: key, English, Russian, marks
```

`watch-upstream.py` stays silent when everything is fine. CI runs both checks and the Russian
plural forms on every pull request.

## Translating

Edits to wording, terms and new strings go through a pull request; the order, the style and the
glossary are in [CONTRIBUTING.md](CONTRIBUTING.md). If describing it in an issue is easier than a
pull request, use the “Правка перевода” template.

Two rules worth knowing before editing:

- **Trading-card rules terms stay in the original** (`Planeswalker`, `Tamer`, `Digi-Egg`, `Unit`,
  `Near Mint (NM)`), while field labels are Russian. Digimon, Lorcana, Star Wars Unlimited, One
  Piece, Flesh and Blood and Yu-Gi-Oh! have no official Russian cards, Pokémon had them only in
  2014–2016, and Wizards has kept `Planeswalker` English in every language since 2008.
- **One noun per entity**: item → «запись», collection → «коллекция», location → «место»,
  copy → «экземпляр», release → «издание». A synonym in a label is a defect, not a style.

## License

The scripts are MIT. `locales/ru.json` is a derivative of the upstream `en.json`, and DVinyl ships
under ISC, so the same terms apply.
