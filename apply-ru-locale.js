// Adds Russian to DVinyl: the locale file plus every place a language has to be registered.
//
// Why a script and not copied files: app.ts, config/constants.ts and the two templates that
// carry a language list are large and drift on every upstream release. A wholesale copy would
// break each time; targeted replacements fail loudly instead, naming the edit and the file, so
// the interface never ships half-translated. Every edit is idempotent: a second run reports
// "already applied" and changes nothing.
//
// Used from three places, all with the same edits:
//   - Dockerfile / Dockerfile.source — patching an image at build time;
//   - install-source.sh — patching a DVinyl clone;
//   - pull requests to upstream — the same edits, made in the fork.
//
// Set DV_ROOT to point at anything other than /app.
//
// Written against DVinyl 4.0.0 (branch `release/4.0.0`).
'use strict';

const fs = require('fs');

const ROOT = process.env.DV_ROOT || '/app';
const at = (rel) => `${ROOT}/${rel}`;

function edit(file, from, to, label) {
  const src = fs.readFileSync(file, 'utf8');
  if (src.includes(to)) {
    console.log(`[ru] ${label}: already applied`);
    return;
  }
  const hits = src.split(from).length - 1;
  if (hits !== 1) {
    throw new Error(
      `[ru] ${label}: expected exactly one match in ${file}, found ${hits}. ` +
        'Upstream has changed — port the edit by hand (see CHANGELOG.md for the anchor).'
    );
  }
  fs.writeFileSync(file, src.replace(from, to));
  console.log(`[ru] ${label}: ok`);
}

function editRe(file, pattern, build, label) {
  const src = fs.readFileSync(file, 'utf8');
  const matches = src.match(new RegExp(pattern, 'g')) || [];
  const replacement = matches.length === 1 ? build(matches[0]) : null;
  if (replacement && src.includes(replacement)) {
    console.log(`[ru] ${label}: already applied`);
    return;
  }
  if (matches.length !== 1) {
    throw new Error(
      `[ru] ${label}: expected exactly one match in ${file}, found ${matches.length}. ` +
        'Upstream has changed — port the edit by hand (see CHANGELOG.md for the anchor).'
    );
  }
  fs.writeFileSync(file, src.replace(new RegExp(pattern), replacement));
  console.log(`[ru] ${label}: ok`);
}

// ─── Registering the language ───────────────────────────────────────────────────────────────
// Seven places. Two of them are templates that spell the language list out by hand instead of
// reading LANGUAGE_NAMES, which is why a language can be "supported" in code and invisible in
// the interface: the settings page and the setup wizard each keep their own copy.

// 1. i18next resources: without this line i18next has no ru.json to read.
edit(
  at('app.ts'),
  "      de: { translation: require('./locales/de.json') }\n",
  "      de: { translation: require('./locales/de.json') },\n      ru: { translation: require('./locales/ru.json') }\n",
  'app.ts: i18n resources'
);

// 2. The language list i18next derives supportedLngs and preload from.
edit(
  at('config/constants.ts'),
  "export const SUPPORTED_LANGUAGES = ['fr', 'en', 'de', 'es', 'it'] as const;",
  "export const SUPPORTED_LANGUAGES = ['fr', 'en', 'de', 'es', 'it', 'ru'] as const;",
  'constants.ts: SUPPORTED_LANGUAGES'
);

// 3. The names shown in the picker. Typed Record<SupportedLanguage, string>, so the project
//    does not compile until Russian is here as well.
edit(
  at('config/constants.ts'),
  "  es: 'Español',\n  it: 'Italiano'\n};",
  "  es: 'Español',\n  it: 'Italiano',\n  ru: 'Русский'\n};",
  'constants.ts: LANGUAGE_NAMES'
);

// 4. The regional tag dates are printed with; without it Russian dates read the American way.
edit(
  at('config/constants.ts'),
  "  es: 'es-ES',\n  it: 'it-IT'\n};",
  "  es: 'es-ES',\n  it: 'it-IT',\n  ru: 'ru-RU'\n};",
  'constants.ts: DATE_LOCALES'
);

// 5. The user schema validates the stored preference against this enum, so without it the
//    settings switch looks like it works and saves nothing.
edit(
  at('models/User.ts'),
  "        enum: ['fr', 'en', 'de', 'es', 'it'],",
  "        enum: ['fr', 'en', 'de', 'es', 'it', 'ru'],",
  'User.ts: language enum'
);

// 6. Settings → language dropdown, which keeps its own copy of the list.
editRe(
  at('views/settings.ejs'),
  '<option value="it"[\\s\\S]*?Italiano\\s*</option>',
  (hit) =>
    hit +
    '\n                                <option value="ru" class="bg-white dark:bg-[#1a1a1a]" ' +
    "<%=currentLng==='ru' ? 'selected' : '' %>>\n                                    Русский\n                                </option>",
  'settings.ejs: Russian option'
);

// 7. Setup wizard: the label of the active language, then its own dropdown of ?lng= links.
edit(
  at('views/setup.ejs'),
  "currentLng === 'it' ? 'Italiano' : 'Français' %>",
  "currentLng === 'it' ? 'Italiano' : currentLng === 'ru' ? 'Русский' : 'Français' %>",
  'setup.ejs: language label'
);

editRe(
  at('views/setup.ejs'),
  '<a href="\\?lng=it"[\\s\\S]*?</a>',
  (hit) =>
    hit +
    '\n                            <a href="?lng=ru" class="flex items-center justify-between ' +
    'px-4 py-2 text-xs text-neutral-300 hover:bg-green-500/10 hover:text-white transition-colors" ' +
    'role="menuitem">\n                                <span>Русский</span>\n                                ' +
    "<% if (currentLng === 'ru') { %><i class=\"fa-solid fa-check text-green-500 text-[10px]\"></i><% } %>\n" +
    '                            </a>',
  'setup.ejs: Russian entry'
);

// ─── Decades ────────────────────────────────────────────────────────────────────────────────
// The filter appended a hardcoded "s" to every year, so a Russian interface read "2020s". The
// rule lives next to dateLocaleFor and reaches the views the same way, because two places print
// a decade and they have to agree: the filter's own label and list, and the active-filter pill.

edit(
  at('config/constants.ts'),
  `export function dateLocaleFor(value: any): string {
  return DATE_LOCALES[normalizeLanguage(value)];
}`,
  `export function dateLocaleFor(value: any): string {
  return DATE_LOCALES[normalizeLanguage(value)];
}

// Keyed by language code: a language this map does not know keeps the English "s".
const DECADE_PATTERNS: Record<string, string> = {
  ru: '{year}-е',
  de: '{year}er',
  fr: 'Années {year}',
  es: 'Años {year}'
};

/**
 * A decade written the way its language writes it: "2020s", "2020-е", "2020er", "Années 2020",
 * "Años 2020". The code is read off the tag directly rather than through normalizeLanguage(),
 * which clamps an unknown code to the default language and would undo the Russian form.
 */
export function decadeText(decade: number | string, language: any): string {
  const year = String(decade);
  const code = String(language || '').toLowerCase().split('-')[0] ?? '';
  const pattern = DECADE_PATTERNS[code];
  return pattern ? pattern.replace('{year}', year) : year + 's';
}`,
  'constants.ts: decadeText'
);

edit(
  at('app.ts'),
  "import { BASE_URL, SUPPORTED_LANGUAGES, DEFAULT_LANGUAGE, LANGUAGE_NAMES, normalizeLanguage, dateLocaleFor } from './config/constants.js';",
  "import { BASE_URL, SUPPORTED_LANGUAGES, DEFAULT_LANGUAGE, LANGUAGE_NAMES, normalizeLanguage, dateLocaleFor, decadeText } from './config/constants.js';",
  'app.ts: decadeText import'
);

edit(
  at('app.ts'),
  '// Dates read the same way wherever a view prints one\napp.locals.dateLocaleFor = dateLocaleFor;',
  '// Dates read the same way wherever a view prints one\napp.locals.dateLocaleFor = dateLocaleFor;\n' +
    '// Decades too: the filter bar and the active-filter pill must agree on "2020-е" against "2020s".\napp.locals.decadeText = decadeText;',
  'app.ts: decadeText in locals'
);

edit(
  at('views/partials/albums-filters.ejs'),
  "currentDecadeArr[0] + 's'",
  'decadeText(currentDecadeArr[0], currentLng)',
  'albums-filters.ejs: selected decade'
);

edit(
  at('views/partials/albums-filters.ejs'),
  '<span class="group-hover:translate-x-0.5 transition-transform"><%= y %>s</span>',
  '<span class="group-hover:translate-x-0.5 transition-transform"><%= decadeText(y, currentLng) %></span>',
  'albums-filters.ejs: decade list'
);

edit(
  at('views/partials/active-filter-pills.ejs'),
  "locals.queryDecade.split(',').map(d => d + 's').join(', ')",
  "locals.queryDecade.split(',').map(d => decadeText(d, currentLng)).join(', ')",
  'active-filter-pills.ejs: decade pill'
);

// ─── Money and the tracklist header ─────────────────────────────────────────────────────────

// Both views built their Intl locale from a two-way guess — French or American English, nothing
// else — so any other language printed sums the American way.
edit(
  at('views/collection.ejs'),
  `const currentLocale = '<%= currentLng === "fr" ? "fr-FR" : "en-US" %>';`,
  'const currentLocale = <%- JSON.stringify(dateLocaleFor(currentLng)) %>;',
  'collection.ejs: money locale'
);

edit(
  at('core/views/detail.ejs'),
  `const currentLocale = '<%= currentLng === "fr" ? "fr-FR" : "en-US" %>';`,
  'const currentLocale = <%- JSON.stringify(dateLocaleFor(currentLng)) %>;',
  'detail.ejs: money locale'
);

// Discogs does not always return a currency code, and Intl throws without one — the price is
// then replaced by an error. Falling back to the user's own currency keeps the page readable.
edit(
  at('core/views/detail.ejs'),
  '                const currency = data.price.currency;',
  '                const currency = data.price.currency || \'<%= user.currency || "USD" %>\';',
  'detail.ejs: fallback currency'
);

// The tracklist header knew French and English only, so a third language got "Duration".
// tracklist.col_duration already exists in every shipped locale.
edit(
  at('plugins/music/partials/tracklist-view.ejs'),
  "t('confirm_vinyl.year_label') === 'Année' ? 'Durée' : 'Duration'",
  "t('tracklist.col_duration')",
  'tracklist-view.ejs: duration header'
);

// ─── The ruble ──────────────────────────────────────────────────────────────────────────────
// SUPPORTED_CURRENCIES is what the schema accepts, what the save route validates against and
// what the settings dropdown lists, so one entry there is the whole code change. Labels are
// keyed settings.currency_<code>, and an English interface would show the raw key without one.

edit(
  at('config/constants.ts'),
  "export const SUPPORTED_CURRENCIES = ['EUR', 'USD', 'GBP'] as const;",
  "export const SUPPORTED_CURRENCIES = ['EUR', 'USD', 'GBP', 'RUB'] as const;",
  'constants.ts: RUB'
);

const CURRENCY_LABELS = {
  en: 'Russian Ruble (₽)',
  de: 'Russischer Rubel (₽)',
  fr: 'Rouble russe (₽)',
  es: 'Rublo ruso (₽)',
  it: 'Rublo russo (₽)'
};

for (const [code, label] of Object.entries(CURRENCY_LABELS)) {
  const file = at(`locales/${code}.json`);
  if (!fs.existsSync(file)) continue;
  const locale = JSON.parse(fs.readFileSync(file, 'utf8'));
  locale.settings = locale.settings || {};
  if (locale.settings.currency_rub === label) {
    console.log(`[ru] ${code}.json: ruble label already there`);
    continue;
  }
  locale.settings.currency_rub = label;
  fs.writeFileSync(file, JSON.stringify(locale, null, 2) + '\n');
  console.log(`[ru] ${code}.json: ruble label added`);
}

const ru = JSON.parse(fs.readFileSync(at('locales/ru.json'), 'utf8'));
console.log(`[ru] locale in place, top-level groups: ${Object.keys(ru).length}`);
