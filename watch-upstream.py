#!/usr/bin/env python3
"""Watchdog for the Russian locale: is the translation behind upstream?

What it checks:
  1. keys that appeared upstream in en.json (the interface shows untranslated strings until they
     are written);
  2. keys we have that upstream no longer has (renamed or removed there);
  3. whether the anchors apply-ru-locale.js cuts into are still alive — a rewritten line upstream
     makes the install fail on "expected exactly one match";
  4. whether upstream grew its own Russian locale (then this package can retire).

Silent when everything is fine: empty stdout means no message is sent.

Usage:
  watch-upstream.py                  # compare with release/4.0.0
  watch-upstream.py --ref 4.1.0      # compare with a specific tag or branch
  watch-upstream.py --always         # print the report even when nothing is wrong
"""
import argparse
import json
import sys
import urllib.request
from pathlib import Path

REPO = "Kyonew/DVinyl"
RAW = f"https://raw.githubusercontent.com/{REPO}/"
LOCAL_RU = Path(__file__).resolve().parent / "locales" / "ru.json"
DEFAULT_REF = "release/4.0.0"
PLURAL = ("_one", "_other", "_plural")

# The same search strings apply-ru-locale.js replaces. They change only together with it.
ANCHORS = {
    "app.ts": [
        "de: { translation: require('./locales/de.json') }",
        "normalizeLanguage, dateLocaleFor } from './config/constants.js';",
        "// Dates read the same way wherever a view prints one",
    ],
    "config/constants.ts": [
        "export const SUPPORTED_LANGUAGES = ['fr', 'en', 'de', 'es', 'it'] as const;",
        "es: 'Español',\n  it: 'Italiano'\n};",
        "es: 'es-ES',\n  it: 'it-IT'\n};",
        "export function dateLocaleFor(value: any): string {",
        "export const SUPPORTED_CURRENCIES = ['EUR', 'USD', 'GBP'] as const;",
    ],
    "models/User.ts": ["enum: ['fr', 'en', 'de', 'es', 'it'],"],
    "views/settings.ejs": ['<option value="it"'],
    "views/setup.ejs": [
        "currentLng === 'it' ? 'Italiano' : 'Français' %>",
        '<a href="?lng=it"',
    ],
    "views/partials/albums-filters.ejs": [
        "currentDecadeArr[0] + 's'",
        "<%= y %>s</span>",
    ],
    "views/partials/active-filter-pills.ejs": ["map(d => d + 's')"],
    "views/collection.ejs": ['currentLng === "fr" ? "fr-FR" : "en-US"'],
    "core/views/detail.ejs": [
        'currentLng === "fr" ? "fr-FR" : "en-US"',
        "const currency = data.price.currency;",
    ],
    "plugins/music/partials/tracklist-view.ejs": ["=== 'Année' ? 'Durée' : 'Duration'"],
}


def fetch(path, ref):
    url = f"{RAW}{ref}/{path}"
    try:
        with urllib.request.urlopen(url, timeout=30) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except Exception:  # noqa: BLE001 - a missing file is a finding, not a crash
        return None


def flat(obj, prefix=""):
    for key, value in obj.items():
        if isinstance(value, dict):
            yield from flat(value, f"{prefix}{key}.")
        else:
            yield f"{prefix}{key}", value


def upstream_plural_bases(keys):
    """Plural group bases from the English file, which carries only _one/_other."""
    bases = set()
    for key in keys:
        for suffix in PLURAL:
            if key.endswith(suffix):
                bases.add(key[: -len(suffix)])
                break
    return bases


def normalize(keys, plural_bases):
    """Collapse plural forms onto their base without touching single keys.

    Russian `_few`/`_many` are stripped only where English really has a plural group,
    otherwise `collection_info.images_too_many` would become `images_too` and read as an extra
    key.
    """
    out = set()
    for key in keys:
        stripped = None
        for suffix in ("_one", "_few", "_many", "_other", "_plural"):
            if key.endswith(suffix) and key[: -len(suffix)] in plural_bases:
                stripped = key[: -len(suffix)]
                break
        out.add(stripped or key)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref", default=DEFAULT_REF)
    ap.add_argument("--always", action="store_true")
    args = ap.parse_args()

    problems, notes = [], []

    upstream_text = fetch("locales/en.json", args.ref)
    if upstream_text is None:
        print(
            f"**DVinyl Russian locale: upstream is unreadable** ({REPO}, {args.ref}). "
            "Check access to raw.githubusercontent.com."
        )
        return 0

    upstream_keys = list(dict(flat(json.loads(upstream_text))).keys())
    local_keys = list(dict(flat(json.loads(LOCAL_RU.read_text(encoding="utf-8")))).keys())
    plural_bases = upstream_plural_bases(upstream_keys)
    upstream = normalize(upstream_keys, plural_bases)
    local = normalize(local_keys, plural_bases)

    new_keys = sorted(set(upstream) - set(local))
    gone_keys = sorted(set(local) - set(upstream))
    if new_keys:
        problems.append(
            f"new strings upstream: **{len(new_keys)}** — needs translating, "
            + ", ".join(f"`{k}`" for k in new_keys[:8])
            + (f" and {len(new_keys) - 8} more" if len(new_keys) > 8 else "")
        )
    if gone_keys:
        # Keys this package brings along itself (labels for currencies the patch adds and the
        # like): upstream has no such keys until the patch lands, and losing the signal over
        # them would be wrong.
        notes.append(
            f"our own keys outside upstream: {len(gone_keys)} — "
            + ", ".join(f"`{k}`" for k in gone_keys[:8])
        )

    broken = []
    for path, anchors in ANCHORS.items():
        text = fetch(path, args.ref)
        if text is None:
            broken.append(f"{path}: file is unreadable")
            continue
        for anchor in anchors:
            if anchor not in text:
                broken.append(f"{path}: anchor not found {anchor!r}")
    if broken:
        problems.append("the locale patch will not apply to this version:\n  - " + "\n  - ".join(broken))

    if fetch("locales/ru.json", args.ref) is not None:
        notes.append(
            "upstream has its own `locales/ru.json` now — this package can retire, the locale "
            "arrives with the update"
        )

    if not problems and not notes and not args.always:
        return 0

    lines = [f"**DVinyl Russian locale — check {args.ref}**", ""]
    if problems:
        lines += [f"- {item}" for item in problems]
    else:
        lines.append("- the translation matches upstream, every patch anchor is in place")
    if notes:
        lines += [f"- {item}" for item in notes]
    lines += ["", f"Package: locales/ru.json ({len(local)} positions). Source: {REPO}@{args.ref}."]
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
