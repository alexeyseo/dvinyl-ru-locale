#!/usr/bin/env python3
"""Сторож русской локали DVinyl: следит, не устарел ли перевод относительно апстрима.

Что проверяет:
  1. появились ли в апстримном en.json новые ключи (значит, в интерфейсе будут
     непереведённые надписи, пока их не дописать);
  2. исчезли ли ключи, которые у нас есть (апстрим переименовал или убрал строки);
  3. живы ли восемь точек, в которые врезается apply-ru-locale.js — если апстрим
     переписал строку, установка сломается на проверке «ожидалась ровно одна замена»;
  4. не появился ли русский язык в апстриме сам (тогда пакет можно снимать с учёта).

Молчит, когда всё в порядке: пустой stdout = сообщение не отправляется.

Запуск:
  watch-upstream.py                  # сравнить с master
  watch-upstream.py --ref 3.4.0      # сравнить с конкретным тегом
  watch-upstream.py --always         # печатать отчёт даже при норме
"""
import argparse
import json
import re
import sys
import urllib.request
from pathlib import Path

REPO = "Kyonew/DVinyl"
RAW = f"https://raw.githubusercontent.com/{REPO}/"
LOCAL_RU = Path(__file__).resolve().parent / "locales" / "ru.json"
PLURAL = ("_one", "_other", "_plural")

# Те же строки поиска, что в apply-ru-locale.js. Меняются только вместе с ним.
ANCHORS = {
    "app.ts": ["de: { translation: require('./locales/de.json') }"],
    "config/constants.ts": [
        "export const SUPPORTED_LANGUAGES = ['fr', 'en', 'de', 'es', 'it'] as const;",
        "es: 'es-ES',\n  it: 'it-IT'\n};",
    ],
    "models/User.ts": ["enum: ['fr', 'en', 'de', 'es', 'it'],"],
    "views/settings.ejs": ['<option value="it"'],
    "views/setup.ejs": [
        "currentLng === 'it' ? 'Italiano' : 'Français' %>",
        '<a href="?lng=it"',
    ],
    "middleware/settingsMiddleware.ts": [
        "res.locals.currentLng = res.locals.user?.language || req.language || 'fr';",
    ],
}


def fetch(path, ref):
    url = f"{RAW}{ref}/{path}"
    try:
        with urllib.request.urlopen(url, timeout=30) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except Exception:
        return None


def flat(obj, prefix=""):
    for key, value in obj.items():
        if isinstance(value, dict):
            yield from flat(value, f"{prefix}{key}.")
        else:
            yield f"{prefix}{key}", value


def upstream_plural_bases(keys):
    """Базы плюральных групп по английскому файлу: он использует только _one/_other."""
    bases = set()
    for key in keys:
        for suffix in ("_one", "_other", "_plural"):
            if key.endswith(suffix):
                bases.add(key[: -len(suffix)])
                break
    return bases


def normalize(keys, plural_bases):
    """Свести плюральные формы к базе, не тронув одиночные ключи вроде images_too_many.

    Русские формы _few/_many отрезаются только там, где в английском действительно
    есть плюральная группа; иначе «collection_info.images_too_many» превратился бы
    в «images_too» и выглядел бы лишним ключом.
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
    ap.add_argument("--ref", default="master")
    ap.add_argument("--always", action="store_true")
    args = ap.parse_args()

    problems, notes = [], []

    upstream_text = fetch("locales/en.json", args.ref)
    if upstream_text is None:
        print(f"**Локаль DVinyl: не удалось прочитать апстрим** ({REPO}, {args.ref}). "
              "Проверь доступ к raw.githubusercontent.com.")
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
            f"новых строк в апстриме: **{len(new_keys)}** — нужен доперевод, "
            + ", ".join(f"`{k}`" for k in new_keys[:8])
            + (f" и ещё {len(new_keys) - 8}" if len(new_keys) > 8 else ""))
    if gone_keys:
        problems.append(f"строк, которых больше нет в апстриме: {len(gone_keys)} — "
                        + ", ".join(f"`{k}`" for k in gone_keys[:8]))

    broken = []
    for path, anchors in ANCHORS.items():
        text = fetch(path, args.ref)
        if text is None:
            broken.append(f"{path}: файл не читается")
            continue
        for anchor in anchors:
            if anchor not in text:
                broken.append(f"{path}: не найдена строка {anchor!r}")
    if broken:
        problems.append("патч локали не ляжет на эту версию:\n  - " + "\n  - ".join(broken))

    if fetch("locales/ru.json", args.ref) is not None:
        notes.append("в апстриме появился свой `locales/ru.json` — пакет можно снимать "
                     "с сопровождения, локаль приезжает с обновлением")

    if not problems and not notes and not args.always:
        return 0

    lines = [f"**Русская локаль DVinyl — проверка {args.ref}**", ""]
    if problems:
        lines += [f"- {item}" for item in problems]
    else:
        lines.append("- перевод совпадает с апстримом, точки патча на месте")
    if notes:
        lines += [f"- {item}" for item in notes]
    lines += ["", f"Пакет: locales/ru.json ({len(local)} позиций). Источник: {REPO}@{args.ref}."]
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
