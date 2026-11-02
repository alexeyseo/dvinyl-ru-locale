# Русский язык для DVinyl

Локаль интерфейса для [DVinyl](https://github.com/Kyonew/DVinyl).

## Установка

### Готовый образ

```yaml
services:
  app:
    image: ghcr.io/alexeyseo/dvinyl-ru-locale:1.0.0
```

```bash
docker compose up -d
```

Собирать ничего не нужно. Список тегов — на странице Packages репозитория; `latest`
указывает на последний выпуск.

### Сборка образа поверх официального

```bash
git clone https://github.com/alexeyseo/dvinyl-ru-locale.git dvinyl-ru
```

В `docker-compose.yml` замените образ на сборку из этого каталога:

```yaml
services:
  app:
    build: ./dvinyl-ru
    image: dvinyl:ru
```

```bash
docker compose up -d --build
```

### Запуск из исходников

```bash
git clone https://github.com/Kyonew/DVinyl.git
cd DVinyl && npm install
/path/to/dvinyl-ru-locale/install-source.sh "$PWD"
npm start
```

Скрипт копирует локаль и накладывает правки. Повторный запуск печатает «уже применено»
и ничего не меняет.

### Через агента

Отдайте агенту этот репозиторий и задачу «поставь русский язык в DVinyl по AGENTS.md».
В файле — шаги, проверки и что делать, если апстрим изменился.

## После установки

Настройки → Язык → Русский.

Проверка без входа: `/login?lng=ru` отдаёт русскую страницу. Если при входе язык остался
прежним, смените его в настройках.

## Что правится в коде

| Файл | Что делается |
|---|---|
| `locales/ru.json` | новый файл, сама локаль |
| `config/constants.ts` | `SUPPORTED_LANGUAGES` += `'ru'`, `DATE_LOCALES.ru = 'ru-RU'` |
| `app.ts` | `resources: { ru: require('./locales/ru.json') }` |
| `models/User.ts` | enum поля `language` += `'ru'` — без этого база не сохранит язык |
| `views/settings.ejs` | пункт «Русский» в выпадающем списке (список жёсткий, не из константы) |
| `views/setup.ejs` | пункт «Русский» в мастере первичной настройки |
| `middleware/settingsMiddleware.ts` | сохранённый язык применяется к i18next на каждом запросе |

`apply-ru-locale.js` делает эти замены с проверкой «ровно одно вхождение». Если автор
переписал строку, скрипт падает с сообщением, а не оставляет интерфейс без языка.

## Обновления DVinyl

- `locales/ru.json` — отдельный файл, обновления версии его не затрагивают.
- Регистрация опирается на строки в трёх файлах кода и двух шаблонах. После обновления версии
  пересоберите образ: если строки на месте, правки применятся сами; если автор их изменил,
  сборка остановится на проверке «ожидалась ровно одна замена» и правку надо переложить.
- Строки, которых нет в переводе, показываются по-английски: i18next берёт `en.json`
  как запасной язык.

Локаль снята с `en.json` версии 3.3.0; сверка с `master` на 2 ноября 2026 — расхождений нет.

## Проверки

```bash
python3 scripts/check-locale.py   # паритет ключей с апстримным en.json, плейсхолдеры
python3 watch-upstream.py         # новые и пропавшие ключи, живость точек патча
```

`watch-upstream.py` молчит, когда всё в порядке. CI гоняет обе проверки и русскую
плюрализацию на каждый pull request.

## Перевод

Правки формулировок, терминов и новых строк — через pull request. Порядок, стиль и словарь
терминов — в [CONTRIBUTING.md](CONTRIBUTING.md). Если проще описать словами, чем делать
pull request, откройте issue по шаблону «Правка перевода».

## English

Russian UI locale for DVinyl: `locales/ru.json` plus the eight registration edits the app
needs. Install by building the provided `Dockerfile` on top of the official image, or run
`install-source.sh` on a source checkout. `AGENTS.md` holds step-by-step instructions for
an AI agent.

## Лицензия

Скрипты — MIT. `locales/ru.json` — производная работа от `en.json` апстрима, DVinyl
распространяется по ISC, условия те же.
