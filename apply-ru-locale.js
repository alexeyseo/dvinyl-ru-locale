// Adds Russian to DVinyl: the locale file plus every place a language has to be registered.
//
// Why a script and not copied files: app.ts, config/constants.ts and the two templates that
// carry a language list are large and drift on every upstream release. A wholesale copy would
// break each time; targeted replacements fail loudly instead, naming the edit and the file, so
// the interface never ships half-translated. Every edit is idempotent: a second run reports
// "already applied" and changes nothing.
//
// Since Russian is merged upstream (PRs #220 and #221, branch release/4.0.0), every edit here
// reports "already applied" on a current build. The script stays for older trees — a tag or a
// branch cut before the merge — and as a guard: if a future upstream release drops one of the
// registration points, the edit puts it back instead of shipping a half-registered language.
//
// Behaviour the upstream author chose differently, and which this script therefore no longer
// touches: decades go through the translation key `collection.decade_value` (not a code map),
// money and the tracklist header are already locale-aware, and the ruble was taken out of
// SUPPORTED_CURRENCIES on purpose — Discogs refuses curr_abbr=RUB and the card-game sources
// return USD or EUR only, so every estimate would have been shown as rubles with a wrong amount.
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

function edit(file, from, to, label, alreadyIf) {
  const src = fs.readFileSync(file, 'utf8');
  // `alreadyIf` marks a file that upstream now ships with Russian: the anchor text is gone
  // because the edit was merged, not because upstream moved.
  if (src.includes(to) || (alreadyIf && src.includes(alreadyIf))) {
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

function editRe(file, pattern, build, label, alreadyIf) {
  const src = fs.readFileSync(file, 'utf8');
  if (alreadyIf && src.includes(alreadyIf)) {
    console.log(`[ru] ${label}: already applied`);
    return;
  }
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
  'app.ts: i18n resources',
  "ru: { translation: require('./locales/ru.json') }"
);

// 2. The language list i18next derives supportedLngs and preload from.
edit(
  at('config/constants.ts'),
  "export const SUPPORTED_LANGUAGES = ['fr', 'en', 'de', 'es', 'it'] as const;",
  "export const SUPPORTED_LANGUAGES = ['fr', 'en', 'de', 'es', 'it', 'ru'] as const;",
  'constants.ts: SUPPORTED_LANGUAGES',
  "SUPPORTED_LANGUAGES = ['fr', 'en', 'de', 'es', 'it', 'ru']"
);

// 3. The names shown in the picker. Typed Record<SupportedLanguage, string>, so the project
//    does not compile until Russian is here as well.
edit(
  at('config/constants.ts'),
  "  es: 'Español',\n  it: 'Italiano'\n};",
  "  es: 'Español',\n  it: 'Italiano',\n  ru: 'Русский'\n};",
  'constants.ts: LANGUAGE_NAMES',
  "ru: 'Русский'"
);

// 4. The regional tag dates are printed with; without it Russian dates read the American way.
edit(
  at('config/constants.ts'),
  "  es: 'es-ES',\n  it: 'it-IT'\n};",
  "  es: 'es-ES',\n  it: 'it-IT',\n  ru: 'ru-RU'\n};",
  'constants.ts: DATE_LOCALES',
  "ru: 'ru-RU'"
);

// 5. The user schema validates the stored preference against this enum, so without it the
//    settings switch looks like it works and saves nothing.
edit(
  at('models/User.ts'),
  "        enum: ['fr', 'en', 'de', 'es', 'it'],",
  "        enum: ['fr', 'en', 'de', 'es', 'it', 'ru'],",
  'User.ts: language enum',
  "enum: ['fr', 'en', 'de', 'es', 'it', 'ru']"
);

// 6. Settings → language dropdown, which keeps its own copy of the list.
editRe(
  at('views/settings.ejs'),
  '<option value="it"[\\s\\S]*?Italiano\\s*</option>',
  (hit) =>
    hit +
    '\n                                <option value="ru" class="bg-white dark:bg-[#1a1a1a]" ' +
    "<%=currentLng==='ru' ? 'selected' : '' %>>\n                                    Русский\n                                </option>",
  'settings.ejs: Russian option',
  'value="ru"'
);

// 7. Setup wizard: the label of the active language, then its own dropdown of ?lng= links.
edit(
  at('views/setup.ejs'),
  "currentLng === 'it' ? 'Italiano' : 'Français' %>",
  "currentLng === 'it' ? 'Italiano' : currentLng === 'ru' ? 'Русский' : 'Français' %>",
  'setup.ejs: language label',
  "currentLng === 'ru' ? 'Русский'"
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
  'setup.ejs: Russian entry',
  'href="?lng=ru"'
);

const ru = JSON.parse(fs.readFileSync(at('locales/ru.json'), 'utf8'));
console.log(`[ru] locale in place, top-level groups: ${Object.keys(ru).length}`);
