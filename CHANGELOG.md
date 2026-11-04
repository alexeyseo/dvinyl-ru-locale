# История версий / Changelog

Каждая запись дана дважды: по-русски и по-английски. / Every entry is given twice: in Russian and in English.

## 2.0.0 — 4 ноября 2026 / 4 November 2026

**RU**

- Пакет переведён на DVinyl 4.0.0: локаль — 2376 позиций, паритет с `en.json` ветки
  `release/4.0.0` полный. Регистрация языка выросла до **семи точек**: список языков вписан руками
  не только в настройках, но и в мастере первичной настройки (`views/setup.ejs` — подпись и
  отдельный выпадающий список).
- Патч стал девятнадцатью правками: к регистрации добавились десятилетия по правилам языка
  (`decadeText` рядом с `dateLocaleFor`), формат денег по языку интерфейса, запасная валюта,
  когда Discogs не вернул код, заголовок длительности в треклисте через ключ локали и рубль
  в `SUPPORTED_CURRENCIES`.
- Правка «применять сохранённый язык» убрана: в 4.0.0 это делает сам апстрим в `app.ts`.
- Появился `Dockerfile.source` — сборка из ветки `release/4.0.0`, потому что официального образа
  4.0.0 ещё нет. `Dockerfile` остаётся для версий с опубликованным образом, база по умолчанию
  `ghcr.io/kyonew/dvinyl:latest`.
- Комментарии в коде и шаги в `README`/`AGENTS.md` переведены на английский, README и CHANGELOG
  двуязычные.
- `scripts/check-locale.py` знает ветку (`--ref`, по умолчанию `release/4.0.0`); `watch-upstream.py`
  проверяет новые точки патча и по умолчанию смотрит туда же. CI собирает образ из
  `Dockerfile.source`.

**EN**

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

## 1.1.0 — 4 ноября 2026 / 4 November 2026

**RU**

- Перевод доведён до DVinyl 4.0.0: 899 недостающих строк против ветки `release/4.0.0`
  переведены, локаль выросла с 1478 до 2374 ключей. Закрыты новые разделы: студия плагинов,
  запросы, уведомления, вёрстка, главная, коллекционные модули (Pokémon, MTG, Yu-Gi-Oh!,
  One Piece, Lorcana, Star Wars Unlimited, Digimon, Flesh and Blood).
- Плюрализация русская: к английской паре `_one/_other` добавлены `_few/_many`, поэтому
  в локали 21 форма сверх английского набора.
- Термины правил карточных игр оставлены в оригинале (`Planeswalker`, `Trainer`, `Digi-Egg`,
  `Tamer`, `Unit`, `Pitch`, `Near Mint (NM)`), подписи полей — по-русски.
- Состояние конверта: шкала оценки остаётся английской (`Mint (M)`, `Very Good Plus (VG+)`),
  последний пункт списка вернулся к `Generic Sleeve`.
- Типы фона: «Однотонный» и «Изображение» не влезали в плитки, стало «Цвет» и «Картинка» —
  «Цвет · Градиент · Узор · Картинка».
- В выборе шрифта названия не переводятся: «С засечками» и «Моноширинный» вернулись к
  `Serif` и `Mono`. Служебные пункты «Как у текста» и «Системный» оставлены переведёнными.
- Тип носителя в форме: «Цифровое издание» раздувало кнопку, стало «Цифровое». Так же
  сокращены «Физическое», «Коллекционное», «Лимитированное».
- Заголовок колонки длительности в треклисте знал только французский и английский
  (`=== 'Année' ? 'Durée' : 'Duration'`) и по-русски писал «Duration»; шаблон переведён на
  ключ `tracklist.col_duration` (значение уточнено до «Длительность»).
- Колонка таблицы «Данные» стала «Сведения»: в оригинале `Info`, а внутри автор или исполнитель.
- Редактор мебели: «Раскладка» стала «Форма мебели» — по коду это форма отделения (кубик или
  планка во всю ширину). Значения остались «Ячейки» и «Ряды», потому что «Полки» занято
  списком отделений внутри мебели.
- Плейсхолдер поиска в коллекции: было «Фильтр…» (калька с `Filter...`), стало «Поиск» —
  строка служит ещё и подписью чипа активного фильтра.
- Появился `scripts/build-review-page.py`: страница ревью с ключом, английским оригиналом,
  переводом, поиском и отметками «пусто / как в EN / латиница / плейсхолдеры».

**EN**

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

## 1.0.4 — 2 ноября 2026 / 2 November 2026

**RU**

- В настройках появился рубль: `RUB` добавлен в схему пользователя, в проверку маршрута
  сохранения, в выпадающий список и в локали. Суммы печатаются как «1 234,50 ₽».

**EN**

- The ruble joined the settings: `RUB` is in the user schema, in the save-route validation, in
  the dropdown and in the locales. Amounts print as “1 234,50 ₽”.

## 1.0.3 — 2 ноября 2026 / 2 November 2026

**RU**

- Фильтр по десятилетиям больше не пишет английское «s»: в русском «2020-е», в немецком «2020er»,
  во французском и испанском слово перед годом. При нескольких выбранных десятилетиях вместо
  числа показывается диапазон.

**EN**

- The decade filter no longer prints the English “s”: Russian reads “2020-е”, German “2020er”,
  and the romance languages put a word before the year. With several decades selected the control
  shows a range instead of a count.

## 1.0.2 — 2 ноября 2026 / 2 November 2026

**RU**

- Цены в оценке коллекции и на карточке записи форматируются по языку интерфейса: было жёстко
  `fr-FR` или `en-US`, поэтому по-русски сумма печаталась по-американски.
- Если Discogs не вернул код валюты, на карточке вместо цены показывалась ошибка: теперь
  подставляется валюта из настроек.

**EN**

- Prices in the collection estimate and on the item page follow the interface language; they used
  to be hardwired to `fr-FR` or `en-US`, so Russian printed them the American way.
- When Discogs returned no currency code the item page showed an error instead of a price; it now
  falls back to the currency from the settings.

## 1.0.1 — 2 ноября 2026 / 2 November 2026

**RU**

- Исправлена подпись модуля в навигации: `media.comic` теперь «Комиксы», а не «Комикс» —
  в английском ключ во множественном числе, и рядом с «Книгами» единственное число читалось
  как ошибка. Формат издания в фильтрах остался «Комикс».

**EN**

- Fixed the module label in the navigation: `media.comic` reads “Комиксы” instead of “Комикс”.
  The English key is plural, and the singular next to “Книги” read as a mistake. The format
  filter keeps the singular “Комикс”.

## 1.0.0 — 2 ноября 2026 / 2 November 2026

**RU**

Первый выпуск. Русский язык интерфейса DVinyl: файл локали и правки, которые добавляют
его в приложение.

Установка:

- образ — склонировать репозиторий и указать в compose `build: ./dvinyl-ru`;
- из исходников — `install-source.sh` на клоне DVinyl;
- через агента — шаги в `AGENTS.md`.

После установки язык выбирается в настройках: Настройки → Язык → Русский. Проверка без
входа — `/login?lng=ru`.

Снято с `en.json` версии 3.3.0. Сверка с `master` 2 ноября 2026: расхождений нет, строки,
в которые врезается патч, на месте.

**EN**

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
