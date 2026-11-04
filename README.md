# Russian for DVinyl — Русский язык для DVinyl

The interface locale for [DVinyl](https://github.com/Kyonew/DVinyl), brought up to 4.0.0.
Локаль интерфейса для [DVinyl](https://github.com/Kyonew/DVinyl), обновлённая под 4.0.0.

Russian below the English, section by section. / Русский идёт под английским, раздел за разделом.

## Install / Установка

**From source, the way 4.0.0 ships today / Из исходников, как сейчас выходит 4.0.0**

```bash
git clone https://github.com/Kyonew/DVinyl.git
cd DVinyl && npm install
/path/to/dvinyl-ru-locale/install-source.sh "$PWD"
npm start
```

The script copies the locale and applies the nineteen registration edits; a second run prints
“already applied” and changes nothing.
Скрипт копирует локаль и накладывает девятнадцать правок; повторный запуск печатает «уже
применено» и ничего не меняет.

**An image built from source / Образ, собранный из исходников**

```bash
docker build -f Dockerfile.source -t dvinyl:ru .
```

`Dockerfile.source` clones the DVinyl branch named in its `DV_REF` argument (currently
`release/4.0.0`) and patches it — there is no official 4.0.0 image yet.
`Dockerfile.source` клонирует ветку из аргумента `DV_REF` (сейчас `release/4.0.0`) и накладывает
патч: официального образа 4.0.0 пока нет.

**On top of an official image / Поверх официального образа**

```bash
docker build -t dvinyl:ru .
```

That file layers the locale onto `ghcr.io/kyonew/dvinyl:latest`, so it fits the releases that do
have an image. Override with `--build-arg UPSTREAM=ghcr.io/kyonew/dvinyl:<tag>`.
Этот файл кладёт локаль поверх `ghcr.io/kyonew/dvinyl:latest`, то есть подходит для уже
выпущенных версий. Другая версия — `--build-arg UPSTREAM=ghcr.io/kyonew/dvinyl:<тег>`.

**A published image / Готовый образ**

```yaml
services:
  app:
    image: ghcr.io/alexeyseo/dvinyl-ru-locale:2.0.0
```

Tags live on the repository's Packages page; `latest` points at the newest release.
Теги — на странице Packages репозитория; `latest` указывает на последний выпуск.

**Through an agent / Через агента**

Hand the agent this repository and the task “install Russian into DVinyl following AGENTS.md”.
`AGENTS.md` holds the steps, the checks, and what to do when upstream has moved.
Отдайте агенту этот репозиторий и задачу «поставь русский язык в DVinyl по AGENTS.md»: в файле
шаги, проверки и что делать, если апстрим изменился.

## After installing / После установки

Settings → Language → Русский.
Настройки → Язык → Русский.

`/login?lng=ru` answers in Russian without signing in, which is the quickest check.
`/login?lng=ru` отдаёт русскую страницу без входа — это самая быстрая проверка.

## What the patch touches / Что правит патч

Seven registration points, then the language fixes the package carries.
Семь точек регистрации, затем языковые правки, которые везёт пакет.

| File / Файл | What it does / Что делает |
|---|---|
| `locales/ru.json` | the locale itself — a new file / сама локаль, новый файл |
| `config/constants.ts` | `SUPPORTED_LANGUAGES`, `LANGUAGE_NAMES`, `DATE_LOCALES`, `decadeText`, `SUPPORTED_CURRENCIES` |
| `app.ts` | i18next resources; `app.locals.decadeText` next to `dateLocaleFor` |
| `models/User.ts` | the `language` enum, without which the database refuses the preference / enum языка |
| `views/settings.ejs` | the settings dropdown, which keeps its own copy of the list / свой список языков |
| `views/setup.ejs` | the setup wizard's label and dropdown, also hand-written / тоже свой список |
| `views/collection.ejs`, `core/views/detail.ejs` | money formatted by the interface language, and a currency fallback / деньги по языку интерфейса |
| `views/partials/albums-filters.ejs`, `views/partials/active-filter-pills.ejs` | decades written the way the language writes them / десятилетия по правилам языка |
| `plugins/music/partials/tracklist-view.ejs` | the duration header through a locale key / заголовок длительности через ключ |

`apply-ru-locale.js` performs each replacement with an “exactly one match” check. When the author
rewrites a line, the build stops with a message naming the edit instead of shipping an interface
without Russian.
`apply-ru-locale.js` делает каждую замену с проверкой «ровно одно вхождение». Если автор переписал
строку, сборка остановится с сообщением, в котором названа правка, — вместо интерфейса без языка.

## Updating DVinyl / Обновления DVinyl

- `locales/ru.json` is a separate file: a version bump never touches it.
  `locales/ru.json` — отдельный файл, обновления версии его не затрагивают.
- The registration anchors live in three code files and four templates. After an update, rebuild:
  if the lines are still there the edits reapply themselves; if the author changed them, the build
  stops on “expected exactly one match” and the edit has to be ported.
  Точки регистрации опираются на строки в трёх файлах кода и четырёх шаблонах. После обновления
  пересоберите образ: строки на месте — правки применятся сами; автор их изменил — сборка
  остановится на «ожидалась ровно одна замена», и правку надо переложить.
- Strings the translation does not have fall back to English: i18next uses `en.json` as the
  fallback language.
  Строки, которых нет в переводе, показываются по-английски: i18next берёт `en.json` как запасной.

The locale is taken from `en.json` of `release/4.0.0`: 2376 positions, no gaps, and Russian plural
forms where English has two.
Локаль снята с `en.json` ветки `release/4.0.0`: 2376 позиций, расхождений нет, у плюральных строк
русские формы там, где в английском их две.

## Checks / Проверки

```bash
python3 scripts/check-locale.py          # key parity and placeholders against upstream en.json
python3 scripts/check-locale.py --ref main
python3 watch-upstream.py --always       # new and gone keys, and whether the patch anchors are alive
python3 scripts/build-review-page.py     # one HTML page: key, English, Russian, marks
```

`watch-upstream.py` stays silent when everything is fine. CI runs both checks and the Russian
plural forms on every pull request.
`watch-upstream.py` молчит, когда всё в порядке. CI гоняет обе проверки и русскую плюрализацию
на каждый pull request.

## Translating / Перевод

Edits to wording, terms and new strings go through a pull request; the order, the style and the
glossary are in [CONTRIBUTING.md](CONTRIBUTING.md). If describing it in an issue is easier than a
pull request, use the “Правка перевода” template.
Правки формулировок, терминов и новых строк — через pull request. Порядок, стиль и словарь
терминов — в [CONTRIBUTING.md](CONTRIBUTING.md). Если проще описать словами, откройте issue по
шаблону «Правка перевода».

Two rules worth knowing before editing:

- **Trading-card rules terms stay in the original** (`Planeswalker`, `Tamer`, `Digi-Egg`, `Unit`,
  `Near Mint (NM)`), while field labels are Russian. Digimon, Lorcana, Star Wars Unlimited, One
  Piece, Flesh and Blood and Yu-Gi-Oh! have no official Russian cards, Pokémon had them only in
  2014–2016, and Wizards has kept `Planeswalker` English in every language since 2008.
- **One noun per entity**: item → «запись», collection → «коллекция», location → «место»,
  copy → «экземпляр», release → «издание». A synonym in a label is a defect, not a style.

- **Термины правил карточных игр остаются в оригинале** (`Planeswalker`, `Tamer`, `Digi-Egg`,
  `Unit`, `Near Mint (NM)`), подписи полей — по-русски.
- **Одна сущность — одно слово**: item → «запись», collection → «коллекция», location → «место»,
  copy → «экземпляр», release → «издание». Синоним в подписи — дефект, а не стиль.

## License / Лицензия

The scripts are MIT. `locales/ru.json` is a derivative of the upstream `en.json`, and DVinyl ships
under ISC, so the same terms apply.
Скрипты — MIT. `locales/ru.json` — производная работа от апстримного `en.json`, DVinyl
распространяется по ISC, условия те же.
