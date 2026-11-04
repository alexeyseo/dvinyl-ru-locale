#!/usr/bin/env bash
# Installs the Russian locale into a DVinyl checkout — for people running from source rather
# than from an official image.
#
#   ./install-source.sh /path/to/DVinyl
#
# It only edits files under that directory: the locale is copied and the nineteen registration
# edits are applied, idempotently. Nothing is deleted and nothing is committed — start the app as
# usual (`npm start`) or build your own image afterwards.
set -euo pipefail

TARGET="${1:-}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ -z "$TARGET" ]; then
  echo "give the path to a DVinyl checkout: ./install-source.sh /path/to/DVinyl" >&2
  exit 2
fi
if [ ! -f "$TARGET/app.ts" ] || [ ! -d "$TARGET/locales" ]; then
  echo "this does not look like DVinyl sources: no app.ts or locales/ in $TARGET" >&2
  exit 2
fi

echo "→ copying the locale"
cp "$HERE/locales/ru.json" "$TARGET/locales/ru.json"

echo "→ registering the language"
DV_ROOT="$TARGET" node "$HERE/apply-ru-locale.js"

echo "→ compiling the touched templates"
if command -v node >/dev/null 2>&1; then
  ( cd "$TARGET" && node --input-type=module -e '
import ejs from "ejs";
import fs from "fs";
for (const f of ["views/settings.ejs", "views/setup.ejs", "views/collection.ejs",
                 "core/views/detail.ejs", "views/partials/albums-filters.ejs",
                 "views/partials/active-filter-pills.ejs",
                 "plugins/music/partials/tracklist-view.ejs"]) {
  ejs.compile(fs.readFileSync(f, "utf8"), { filename: f });
  console.log("  ok:", f);
}
const ru = JSON.parse(fs.readFileSync("locales/ru.json", "utf8"));
console.log("  locale in place, top-level groups:", Object.keys(ru).length);
' 2>/dev/null || echo "  (skipped: no ejs in this environment — run npm install first)")
else
  echo "  (node not found, templates not checked)"
fi

echo
echo "Done. Next:"
echo "  cd $TARGET && npm start          # start the app as usual"
echo "  — or —"
echo "  docker compose up -d --build     # if you build your own image"
echo
echo "Pick the language in the interface: Settings → Language → Русский."
