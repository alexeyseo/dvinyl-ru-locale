#!/usr/bin/env python3
"""Pre-publication check of the locale: key parity, placeholders, plural forms.

Compares locales/ru.json with the upstream en.json (fetched from GitHub unless a local file is
given). The same script runs in CI, so a translation edit cannot silently break a template.

    python3 scripts/check-locale.py                    # check against release/4.0.0
    python3 scripts/check-locale.py --ref main         # against another branch or tag
    python3 scripts/check-locale.py --en ./en.json     # against a local file
    python3 scripts/check-locale.py --offline          # self-check of ru.json only

Exit code 1 means problems were found and listed.
"""
import argparse
import json
import pathlib
import re
import sys
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
RU = ROOT / "locales" / "ru.json"
RAW = "https://raw.githubusercontent.com/Kyonew/DVinyl/{ref}/locales/en.json"
DEFAULT_REF = "release/4.0.0"
PLACEHOLDER = re.compile(r"\{\{[^}]+\}\}")
# English carries two plural forms; Russian needs three, and `_other` is deliberately absent —
# i18next falls back to `_many` for fractions, which is the correct Russian reading anyway.
PLURAL_EN = ("_one", "_other", "_plural")
PLURAL_RU = ("_one", "_few", "_many")


def flat(obj, prefix=""):
    for key, value in obj.items():
        if isinstance(value, dict):
            yield from flat(value, f"{prefix}{key}.")
        else:
            yield f"{prefix}{key}", value


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--en", help="local en.json instead of downloading it")
    ap.add_argument("--ref", default=DEFAULT_REF, help=f"upstream branch or tag (default: {DEFAULT_REF})")
    ap.add_argument("--offline", action="store_true", help="skip the comparison with English")
    args = ap.parse_args()

    russian = dict(flat(json.loads(RU.read_text(encoding="utf-8"))))
    problems = []

    english = {}
    if not args.offline:
        try:
            if args.en:
                text = pathlib.Path(args.en).read_text(encoding="utf-8")
            else:
                with urllib.request.urlopen(RAW.format(ref=args.ref), timeout=30) as resp:
                    text = resp.read().decode("utf-8")
            english = dict(flat(json.loads(text)))
        except Exception as exc:  # noqa: BLE001 - the message is what the caller needs
            problems.append(f"could not read the English locale: {exc}")

    extra_keys = []
    if english:
        plural_bases = {k[: -len(s)] for k in english for s in PLURAL_EN if k.endswith(s)}
        for key in english:
            suffix = next((s for s in PLURAL_EN if key.endswith(s)), None)
            if suffix:
                base = key[: -len(suffix)]
                if not all(f"{base}{form}" in russian for form in PLURAL_RU):
                    problems.append(f"no Russian forms for the plural group {base}")
            elif key not in russian:
                problems.append(f"missing translation: {key}")

        for key in russian:
            if any(key.endswith(s) and key[: -len(s)] in plural_bases for s in PLURAL_RU):
                continue
            if key in english:
                continue
            # An extra key does not break rendering (i18next simply finds no counterpart), and
            # some of them are legitimate: the locale ships keys the patch brings along.
            extra_keys.append(key)

        for key, value in russian.items():
            reference = key
            for suffix in PLURAL_RU:
                if key.endswith(suffix):
                    stem = key[: -len(suffix)]
                    reference = next((f"{stem}{s}" for s in PLURAL_EN if f"{stem}{s}" in english), key)
                    break
            if reference in english:
                if set(PLACEHOLDER.findall(str(value))) != set(PLACEHOLDER.findall(str(english[reference]))):
                    problems.append(f"placeholders differ: {key} — {value!r}")

    for key, value in russian.items():
        if not str(value).strip():
            problems.append(f"empty value: {key}")

    if extra_keys:
        print(
            f"note: {len(extra_keys)} keys that English does not have "
            f"({', '.join(extra_keys[:5])})",
            file=sys.stderr,
        )

    if problems:
        print(f"PROBLEMS FOUND: {len(problems)}")
        for item in problems[:50]:
            print("  -", item)
        if len(problems) > 50:
            print(f"  …and {len(problems) - 50} more")
        return 1

    print(
        f"locale is fine: {len(russian)} entries"
        + (" (English not compared)" if not english else f", compared with en.json @ {args.ref}")
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
