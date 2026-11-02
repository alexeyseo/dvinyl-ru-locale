// Включает русский язык в DVinyl: три точки регистрации плюс сам файл локали.
//
// Зачем скрипт, а не копии файлов: app.ts и config/constants.ts большие, и копия целиком
// ломается на каждом релизе апстрима. Здесь три точечные замены с проверкой — если апстрим
// переписал строку, сборка падает с понятной ошибкой, а не отдаёт интерфейс без русского.
//
// Запускается из Dockerfile оверлея: node /tmp/apply-ru-locale.js
const fs = require('fs');

// Корень приложения: в образе это /app, а при подготовке PR — клон исходников апстрима.
// Тот же скрипт накладывает одни и те же правки на образ и на дерево репозитория.
const ROOT = process.env.DV_ROOT || '/app';
const at = (rel) => `${ROOT}/${rel}`;

function edit(file, from, to, label) {
  const src = fs.readFileSync(file, 'utf8');
  if (src.includes(to)) {
    console.log(`[ru] ${label}: уже применено`);
    return;
  }
  const hits = src.split(from).length - 1;
  if (hits !== 1) {
    throw new Error(`[ru] ${label}: ожидалась ровно одна замена в ${file}, найдено ${hits}. ` +
      'Апстрим изменился — перенеси правку руками (см. overlay/apply-ru-locale.js).');
  }
  fs.writeFileSync(file, src.replace(from, to));
  console.log(`[ru] ${label}: ok`);
}

function editRe(file, pattern, build, label) {
  const src = fs.readFileSync(file, 'utf8');
  const matches = src.match(new RegExp(pattern, 'g')) || [];
  if (matches.length !== 1) {
    throw new Error(`[ru] ${label}: ожидалось одно совпадение в ${file}, найдено ${matches.length}. ` +
      'Апстрим изменился — перенеси правку руками (см. overlay/apply-ru-locale.js).');
  }
  const replacement = build(matches[0]);
  if (src.includes(replacement) && replacement !== matches[0]) {
    console.log(`[ru] ${label}: уже применено`);
    return;
  }
  fs.writeFileSync(file, src.replace(new RegExp(pattern), replacement));
  console.log(`[ru] ${label}: ok`);
}

// 1. Ресурсы i18next: без этой строки i18next не знает про ru.json.
edit(
  at('app.ts'),
  "      de: { translation: require('./locales/de.json') }\n",
  "      de: { translation: require('./locales/de.json') },\n      ru: { translation: require('./locales/ru.json') }\n",
  'app.ts: ресурсы'
);

// 2. Список поддерживаемых языков: из него i18next берёт supportedLngs и preload.
edit(
  at('config/constants.ts'),
  "export const SUPPORTED_LANGUAGES = ['fr', 'en', 'de', 'es', 'it'] as const;",
  "export const SUPPORTED_LANGUAGES = ['fr', 'en', 'de', 'es', 'it', 'ru'] as const;",
  'constants.ts: SUPPORTED_LANGUAGES'
);

// 3. Формат дат: без своей локали русские даты печатались бы по-американски.
edit(
  at('config/constants.ts'),
  "  es: 'es-ES',\n  it: 'it-IT'\n};",
  "  es: 'es-ES',\n  it: 'it-IT',\n  ru: 'ru-RU'\n};",
  'constants.ts: DATE_LOCALES'
);

// 4. Схема пользователя: значение языка проверяется enum-ом, и без правки Mongo не даст
//    сохранить ru — переключатель в настройках молча ничего не изменит.
edit(
  at('models/User.ts'),
  "        enum: ['fr', 'en', 'de', 'es', 'it'],",
  "        enum: ['fr', 'en', 'de', 'es', 'it', 'ru'],",
  'User.ts: enum языка'
);

// 5. Настройки → выпадающий список языков. Найдено на живом образе 3.3.0: язык выбирается
//    не из SUPPORTED_LANGUAGES, а жёстко перечислен в шаблоне, поэтому без этой правки
//    русский не выбрать в интерфейсе, хотя сервер его уже знает.
editRe(
  at('views/settings.ejs'),
  '<option value="it"[\\s\\S]*?Italiano\\s*</option>',
  (hit) => hit + '\n                                <option value="ru" class="bg-white dark:bg-[#1a1a1a]" ' +
    "<%=currentLng==='ru' ? 'selected' : '' %>>\n                                    Русский\n                                </option>",
  'settings.ejs: пункт «Русский»'
);

// 6. Мастер первичной настройки: подпись активного языка.
edit(
  at('views/setup.ejs'),
  "currentLng === 'it' ? 'Italiano' : 'Français' %>",
  "currentLng === 'it' ? 'Italiano' : currentLng === 'ru' ? 'Русский' : 'Français' %>",
  'setup.ejs: подпись языка'
);

// 7. Мастер первичной настройки: свой дропдаун со ссылками ?lng=…
editRe(
  at('views/setup.ejs'),
  '<a href="\\?lng=it"[\\s\\S]*?</a>',
  (hit) => hit + '\n                            <a href="?lng=ru" class="flex items-center justify-between ' +
    'px-4 py-2 text-xs text-neutral-300 hover:bg-green-500/10 hover:text-white transition-colors" ' +
    'role="menuitem">\n                                <span>Русский</span>\n                                ' +
    "<% if (currentLng === 'ru') { %><i class=\"fa-solid fa-check text-green-500 text-[10px]\"></i><% } %>\n" +
    '                            </a>',
  'setup.ejs: пункт «Русский»'
);

// 8. Сохранённый язык пользователя главнее браузера. Без этой правки выбранный в настройках
//    язык жил только в тексте подписи: i18next определял язык по cookie и заголовку браузера,
//    поэтому интерфейс оставался прежним. changeLanguage вызывается только в маршруте
//    сохранения языка, для одного запроса.
edit(
  at('middleware/settingsMiddleware.ts'),
  "        res.locals.currentLng = res.locals.user?.language || req.language || 'fr';",
  "        res.locals.currentLng = res.locals.user?.language || req.language || 'fr';\n" +
    "        // Язык из профиля применяем к самому i18next, иначе он остаётся на cookie браузера\n" +
    "        if (res.locals.user?.language && req.i18n && req.i18n.language !== res.locals.user.language) {\n" +
    "            await req.i18n.changeLanguage(res.locals.user.language);\n" +
    "        }",
  'settingsMiddleware.ts: язык профиля'
);

const ru = JSON.parse(fs.readFileSync(at('locales/ru.json'), 'utf8'));
console.log(`[ru] локаль на месте, ключей верхнего уровня: ${Object.keys(ru).length}`);
