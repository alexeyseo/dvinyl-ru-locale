#!/usr/bin/env python3
"""Reports how the Russian locale compares with upstream.

Checks: new English keys, keys upstream dropped, the seven places a language has to be registered,
and (with --report-wording) strings upstream words differently. Silent when nothing is wrong.

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

# Russian has to stay registered in seven places. Two of them are templates that spell the
# language list out by hand instead of reading LANGUAGE_NAMES, which is how a language ends up
# supported in code and invisible in the interface. These are the strings apply-ru-locale.js
# writes, so the two files move together: change one, change the other.
PRESENT = {
    "locales/ru.json": [],  # the file itself; a 404 is a finding
    "app.ts": ["ru: { translation: require('./locales/ru.json') }"],
    "config/constants.ts": [
        "'fr', 'en', 'de', 'es', 'it', 'ru'",
        "ru: 'Русский'",
        "ru: 'ru-RU'",
    ],
    "models/User.ts": ["'fr', 'en', 'de', 'es', 'it', 'ru'"],
    "views/settings.ejs": ['value="ru"'],
    "views/setup.ejs": ["currentLng === 'ru' ? 'Русский'", 'href="?lng=ru"'],
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


def plural_bases_of(keys):
    """Plural groups only: a `_one`/`_other` pair.

    A lone key can end in a plural suffix without being a group — `collection.shelf_move_one` is
    the single-item action ("Move elsewhere"), and counting it as a group makes the report claim
    forms are missing that will never exist.
    """
    present = set(keys)
    bases = set()
    for key in keys:
        for suffix in PLURAL:
            if key.endswith(suffix):
                base = key[: -len(suffix)]
                if f"{base}_one" in present and f"{base}_other" in present:
                    bases.add(base)
                break
    return bases


def normalize(keys, plural_bases):
    """Collapse plural forms onto their base without touching single keys."""
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
    ap.add_argument(
        "--report-wording",
        action="store_true",
        help="also list strings upstream words differently",
    )
    args = ap.parse_args()

    problems, notes = [], []

    upstream_text = fetch("locales/en.json", args.ref)
    if upstream_text is None:
        print(
            f"**DVinyl Russian locale: upstream is unreadable** ({REPO}, {args.ref}). "
            "Check access to raw.githubusercontent.com."
        )
        return 0

    upstream_flat = dict(flat(json.loads(upstream_text)))
    local_flat = dict(flat(json.loads(LOCAL_RU.read_text(encoding="utf-8"))))
    plural_bases = plural_bases_of(list(upstream_flat))
    upstream = normalize(upstream_flat, plural_bases)
    local = normalize(local_flat, plural_bases)

    new_keys = sorted(set(upstream) - set(local))
    gone_keys = sorted(set(local) - set(upstream))
    if new_keys:
        problems.append(
            f"new strings upstream: **{len(new_keys)}** — needs translating, "
            + ", ".join(f"`{k}`" for k in new_keys[:8])
            + (f" and {len(new_keys) - 8} more" if len(new_keys) > 8 else "")
        )
    if gone_keys:
        notes.append(
            f"our own keys outside upstream: {len(gone_keys)} — "
            + ", ".join(f"`{k}`" for k in gone_keys[:8])
        )

    missing = []
    for path, anchors in PRESENT.items():
        text = fetch(path, args.ref)
        if text is None:
            missing.append(f"{path}: file is unreadable or gone")
            continue
        for anchor in anchors:
            if anchor not in text:
                missing.append(f"{path}: {anchor!r} not found")
    if missing:
        problems.append(
            "Russian is no longer fully registered upstream — a release from this branch would "
            "ship it invisible or with American dates:\n  - " + "\n  - ".join(missing)
        )

    # The merged locale is the source of truth for the keys themselves; a different string only
    # means the two copies were worded apart. Not a problem, and noisy on every run, so it is
    # reported on request.
    upstream_ru_text = fetch("locales/ru.json", args.ref)
    if upstream_ru_text is not None and args.report_wording:
        upstream_ru = dict(flat(json.loads(upstream_ru_text)))
        changed = sorted(
            key
            for key, value in upstream_ru.items()
            if key in local_flat and local_flat[key] != value and key in local
        )
        if changed:
            notes.append(
                f"upstream words {len(changed)} string(s) differently: "
                + ", ".join(f"`{k}`" for k in changed[:8])
                + (f" and {len(changed) - 8} more" if len(changed) > 8 else "")
            )

    if not problems and not notes and not args.always:
        return 0

    lines = [f"**DVinyl Russian locale — check {args.ref}**", ""]
    if problems:
        lines += [f"- {item}" for item in problems]
    else:
        lines.append("- translation matches upstream, Russian is registered everywhere it needs to be")
    if notes:
        lines += [f"- {item}" for item in notes]
    lines += ["", f"Package: locales/ru.json ({len(local)} positions). Source: {REPO}@{args.ref}."]
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
