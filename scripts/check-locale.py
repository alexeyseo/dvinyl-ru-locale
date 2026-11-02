#!/usr/bin/env python3
"""Проверка локали перед публикацией: паритет ключей, плейсхолдеры, плюрализация.

Сравнивает locales/ru.json с апстримным en.json (тянется с GitHub, если не указан
локальный файл). Этим же скриптом проверяются pull request'ы в CI — поэтому правка
перевода не может молча сломать шаблон.

    python3 scripts/check-locale.py                  # сверить с master апстрима
    python3 scripts/check-locale.py --en ./en.json   # сверить с локальным файлом
    python3 scripts/check-locale.py --offline        # только самопроверка ru.json

Код выхода 1 — есть проблемы, их список печатается.
"""
import argparse
import json
import pathlib
import re
import sys
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
RU = ROOT / "locales" / "ru.json"
RAW_EN = "https://raw.githubusercontent.com/Kyonew/DVinyl/master/locales/en.json"
PLACEHOLDER = re.compile(r"\{\{[^}]+\}\}")
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
    ap.add_argument("--en", help="локальный en.json вместо скачивания")
    ap.add_argument("--offline", action="store_true", help="без сверки с английским")
    args = ap.parse_args()

    russian = dict(flat(json.loads(RU.read_text(encoding="utf-8"))))
    problems = []

    english = {}
    if not args.offline:
        try:
            if args.en:
                text = pathlib.Path(args.en).read_text(encoding="utf-8")
            else:
                with urllib.request.urlopen(RAW_EN, timeout=30) as resp:
                    text = resp.read().decode("utf-8")
            english = dict(flat(json.loads(text)))
        except Exception as exc:
            problems.append(f"не удалось прочитать английскую локаль: {exc}")

    if english:
        plural_bases = {k[: -len(s)] for k in english for s in PLURAL_EN if k.endswith(s)}
        for key in english:
            if key.endswith(PLURAL_EN):
                base = key[: -len(s)] if (s := next(x for x in PLURAL_EN if key.endswith(x))) else key
                if not all(f"{base}{suffix}" in russian for suffix in PLURAL_RU):
                    problems.append(f"нет русских форм для плюральной группы {base}")
            elif key not in russian:
                problems.append(f"нет перевода: {key}")
        for key in russian:
            stripped = None
            for suffix in ("_one", "_few", "_many"):
                if key.endswith(suffix) and key[: -len(suffix)] in plural_bases:
                    stripped = key[: -len(suffix)]
                    break
            if stripped or key in english:
                continue
            problems.append(f"лишний ключ: {key}")
        for key, value in russian.items():
            reference = key
            for suffix in ("_one", "_few", "_many"):
                if key.endswith(suffix):
                    stem = key[: -len(suffix)]
                    for en_suffix in PLURAL_EN:
                        if f"{stem}{en_suffix}" in english:
                            reference = f"{stem}{en_suffix}"
                            break
                    break
            if reference in english:
                if set(PLACEHOLDER.findall(str(value))) != set(PLACEHOLDER.findall(str(english[reference]))):
                    problems.append(f"плейсхолдеры не совпали: {key} — {value!r}")

    for key, value in russian.items():
        if not str(value).strip():
            problems.append(f"пустое значение: {key}")

    if problems:
        print(f"НАЙДЕНО ПРОБЛЕМ: {len(problems)}")
        for item in problems[:50]:
            print("  -", item)
        if len(problems) > 50:
            print(f"  …и ещё {len(problems) - 50}")
        return 1

    print(f"локаль в порядке: {len(russian)} записей"
          + (" (сверка с английской не выполнялась)" if not english else ", сверено с en.json"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
