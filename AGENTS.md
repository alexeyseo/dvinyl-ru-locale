# Instructions for an AI agent: install the Russian interface into DVinyl
#
# Task: add a Russian interface to a self-hosted DVinyl so that a version update does not wipe
# it. The source is this directory (`locales/ru.json` plus `apply-ru-locale.js`).

## 1. Work out how DVinyl runs for this person

- A directory with `docker-compose.yml` and a service on `ghcr.io/kyonew/dvinyl` → **the image
  route**. Note that 4.0.0 has no official image yet; if they run 4.0.0, they build from source
  and the source route below applies.
- A source checkout (`app.ts`, `locales/`) → **the source route**.
- Unclear → ask once, do not guess.

## 2. Image route

```bash
cp -r <this directory> <compose directory>/dvinyl-ru
```

In the DVinyl service of `docker-compose.yml`:

```yaml
    build: ./dvinyl-ru
    image: dvinyl:ru
    # image: ghcr.io/kyonew/dvinyl:3.3.0   ← remove or comment this line out
```

If the service is declared with `image:` and no `build:`, add `build` next to it and touch nothing
else.

```bash
docker compose up -d --build
```

For the branch with no published image, build from source instead:

```bash
docker build -f Dockerfile.source -t dvinyl:ru .
```

## 3. Source route

```bash
./install-source.sh /path/to/DVinyl
```

The script copies the locale and applies the edits; it does not commit — leave that decision to the
person.

## 4. Check the result (for real, not from build logs)

```bash
# the app accepts the language: before the patch this answered fr
curl -s -i "http://127.0.0.1:<port>/login?lng=ru" | grep -i 'content-language'
# expect: Content-Language: ru

# the strings and the plural forms
docker exec <container> node --input-type=module -e "
import i18next from 'i18next';
import ru from './locales/ru.json' with { type: 'json' };
await i18next.init({ lng: 'ru', fallbackLng: 'ru', resources: { ru: { translation: ru } } });
console.log(i18next.t('lists.tracks_count', { count: 3 }));  // 3 трека
"
```

Expect `Content-Language: ru` and «3 трека». If you get `fr`, the edits did not apply — see step 5.

A second, template-level check that catches a missed registration point:

```bash
curl -s "http://127.0.0.1:<port>/setup?lng=ru" | grep -c 'Русский'
```

The setup wizard keeps its own language list, so a zero here means that point was skipped.

## 5. If the build stops on “expected exactly one match”

Upstream has rewritten a line the patch cuts into. Work through it:

1. Find the failing edit in `apply-ru-locale.js` — the message names the file and the match count.
2. Look at the file in the image or checkout:
   `docker run --rm -it <image> sh -lc 'grep -n "<fragment>" /app/<file>'`.
3. Update the search string so that it matches exactly once.
4. Rebuild and repeat the check from step 4.

Do not copy whole upstream files into the project: `app.ts` is large and changes with every
release.

## 6. What to tell the person

- Pick the language in the interface: Settings → Language → Русский. If it stays English, the
  browser still carries the old cookie; the settings switch applies to every subsequent request.
- Strings that appeared upstream after this version stay English until translated: the fallback is
  `en.json`.
- Updating DVinyl: `docker compose build` (or `docker build`) first, then `up -d`. If upstream moved
  a patch anchor the build stops with a readable error, and that is not a breakage.

## Limits worth remembering

- Upstream's `DEFAULT_LANGUAGE` is `'fr'`: a visitor with no Russian in their browser sees French.
  That is upstream behaviour, not a locale bug.
- Source metadata languages (TMDB, Discogs and the rest) do not follow the interface language.
- Trading-card rules terms stay in the original (`Planeswalker`, `Digi-Egg`, `Near Mint (NM)`);
  field labels are Russian. Do not “finish” those translations.
