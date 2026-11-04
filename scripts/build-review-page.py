#!/usr/bin/env python3
"""Собирает страницу ревью русского перевода DVinyl: ключ, английский оригинал, перевод.

Зачем: качество перевода нельзя проверить только скриптом. Скрипт ловит паритет ключей,
плейсхолдеры и пустые значения — а «звучит ли это по-русски» читает человек. Эта страница
даёт владельцу весь перевод списком с поиском и отметками того, что стоит посмотреть первым.

Флаги:
  пусто          — перевода нет;
  как в EN       — значение совпадает с английским (возможно, не переведено);
  латиница       — в переводе остались латинские буквы (незакрытый термин или бренд);
  плейсхолдеры   — набор {{…}} / %COUNT% не совпал с оригиналом (сломает подстановку).

Запуск: python3 scripts/build-review-page.py [--en locales/en.json] [--ru locales/ru.json] \
        [--out review/dvinyl-ru-review.html] [--title "..."]
"""
import argparse
import html
import json
import re
from pathlib import Path

PLACEHOLDER = re.compile(r'\{\{-?\s*[A-Za-z0-9_]+\s*\}\}|%[A-Z_]+%')
CYRILLIC = re.compile(r'[А-Яа-яЁё]')
LATIN = re.compile(r'[A-Za-z]')


def flatten(node, prefix=''):
    out = {}
    for key, value in node.items():
        path = f'{prefix}{key}'
        if isinstance(value, dict):
            out.update(flatten(value, path + '.'))
        else:
            out[path] = value
    return out


def placeholders(value):
    return sorted(PLACEHOLDER.findall(str(value)))


def plural_base(key):
    """Ключ без суффикса формы: для русского это _one/_few/_many, в английском _one/_other."""
    for suffix in ('_zero', '_one', '_two', '_few', '_many', '_other'):
        if key.endswith(suffix):
            return key[: -len(suffix)]
    return None


def covered_by_plural(key, ru):
    """Русскому не нужна форма _other, если есть все три формы множественного числа."""
    base = plural_base(key)
    if not base or not key.endswith('_other'):
        return False
    return all(f'{base}_{suffix}' in ru for suffix in ('one', 'few', 'many'))


def flags(en_value, ru_value, key='', ru=None):
    out = []
    if ru_value is None and not (ru is not None and covered_by_plural(key, ru)):
        out.append('пусто')
    if ru_value is not None and str(ru_value).strip() == str(en_value).strip():
        out.append('как в EN')
    if ru_value and LATIN.search(str(ru_value)) and CYRILLIC.search(str(ru_value)):
        out.append('латиница')
    if ru_value is not None and placeholders(en_value) != placeholders(ru_value):
        out.append('плейсхолдеры')
    return out


def build(en, ru, title):
    rows = []
    for key, en_value in en.items():
        ru_value = ru.get(key)
        marks = flags(en_value, ru_value, key, ru)
        section = key.split('.')[0]
        missing = ru_value is None and not covered_by_plural(key, ru)
        rows.append({
            'key': key,
            'section': section,
            'en': en_value if isinstance(en_value, str) else json.dumps(en_value, ensure_ascii=False),
            'ru': '' if ru_value is None else (ru_value if isinstance(ru_value, str) else json.dumps(ru_value, ensure_ascii=False)),
            'marks': marks,
            'missing': missing,
        })
    sections = sorted({r['section'] for r in rows})
    counts = {
        'всего': len(rows),
        'переведено': sum(1 for r in rows if not r['missing']),
        'не хватает': sum(1 for r in rows if r['missing']),
        'с замечаниями': sum(1 for r in rows if r['marks']),
    }
    return rows, sections, counts, title


def render(rows, sections, counts, title):
    data = json.dumps(rows, ensure_ascii=False).replace('</', '<\\/')
    options = '\n'.join(f'<option value="{html.escape(s)}">{html.escape(s)}</option>' for s in sections)
    return f"""<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<style>
  :root {{ color-scheme: light dark; --line: #d8dde4; --muted: #6b7280; --accent: #0f7b4f; }}
  @media (prefers-color-scheme: dark) {{ :root {{ --line: #333a45; --muted: #9aa4b2; --accent: #4ade80; }} }}
  * {{ box-sizing: border-box; }}
  body {{ margin: 0; font: 15px/1.45 -apple-system, "Segoe UI", Roboto, sans-serif; }}
  header {{ position: sticky; top: 0; backdrop-filter: blur(8px); padding: 12px 16px; border-bottom: 1px solid var(--line); }}
  h1 {{ font-size: 17px; margin: 0 0 6px; }}
  .counts {{ color: var(--muted); font-size: 13px; margin-bottom: 10px; }}
  .controls {{ display: flex; flex-wrap: wrap; gap: 8px; }}
  input[type=search], select {{ font: inherit; padding: 7px 10px; border: 1px solid var(--line); border-radius: 8px; background: transparent; }}
  input[type=search] {{ flex: 1 1 220px; }}
  label.chk {{ display: inline-flex; align-items: center; gap: 6px; font-size: 14px; color: var(--muted); }}
  main {{ padding: 8px 16px 60px; }}
  table {{ width: 100%; border-collapse: collapse; }}
  tr {{ border-bottom: 1px solid var(--line); vertical-align: top; }}
  td {{ padding: 8px 8px 8px 0; }}
  td.key {{ font-family: ui-monospace, "SF Mono", Menlo, monospace; font-size: 12px; color: var(--muted); width: 30%; word-break: break-all; }}
  td.en {{ color: var(--muted); width: 33%; }}
  td.ru {{ font-weight: 500; }}
  .mark {{ display: inline-block; font-size: 11px; padding: 1px 6px; border-radius: 99px; border: 1px solid var(--accent); color: var(--accent); margin-left: 6px; }}
  .hidden {{ display: none; }}
</style>
</head>
<body>
<header>
  <h1>{html.escape(title)}</h1>
  <div class="counts" id="counts"></div>
  <div class="controls">
    <input type="search" id="q" placeholder="Поиск по ключу, английскому или русскому тексту">
    <select id="section"><option value="">Все разделы</option>{options}</select>
    <label class="chk"><input type="checkbox" id="onlyIssues"> только с замечаниями</label>
    <label class="chk"><input type="checkbox" id="onlyMissing"> только непереведённое</label>
  </div>
</header>
<main>
<table>
  <thead><tr><th class="key">ключ</th><th class="en">английский оригинал</th><th class="ru">русский перевод</th></tr></thead>
  <tbody id="rows"></tbody>
</table>
</main>
<script>
const ROWS = {data};
const q = document.getElementById('q');
const section = document.getElementById('section');
const onlyIssues = document.getElementById('onlyIssues');
const onlyMissing = document.getElementById('onlyMissing');
const tbody = document.getElementById('rows');
const counts = document.getElementById('counts');
const LIMIT = 400;

function esc(s) {{ return String(s).replace(/[&<>"]/g, c => ({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}}[c])); }}

// innerHTML ниже безопасен: каждая подстановка идёт через esc(), а данные — локальный
// файл локали, а не пользовательский ввод. Экранирование не убирать.

function draw() {{
  const needle = q.value.trim().toLowerCase();
  const sec = section.value;
  const filtered = ROWS.filter(r =>
    (!sec || r.section === sec) &&
    (!onlyIssues.checked || r.marks.length > 0) &&
    (!onlyMissing.checked || r.missing) &&
    (!needle || (r.key + ' ' + r.en + ' ' + r.ru).toLowerCase().includes(needle))
  );
  const shown = filtered.slice(0, LIMIT);
  tbody.innerHTML = shown.map(r => `
    <tr data-key="${{esc(r.key)}}">
      <td class="key">${{esc(r.key)}}${{r.marks.map(m => `<span class="mark">${{esc(m)}}</span>`).join('')}}</td>
      <td class="en">${{esc(r.en)}}</td>
      <td class="ru">${{esc(r.ru) || '<span style="opacity:.5">—</span>'}}</td>
    </tr>`).join('');
  counts.textContent = `показано ${{shown.length}} из ${{filtered.length}} подходящих · всего строк ${{ROWS.length}}`;
}}

q.addEventListener('input', draw);
section.addEventListener('change', draw);
onlyIssues.addEventListener('change', draw);
onlyMissing.addEventListener('change', draw);
draw();
</script>
</body>
</html>
"""


def main():
    here = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser()
    parser.add_argument('--en', default=str(here / 'locales/en.json'))
    parser.add_argument('--ru', default=str(here / 'locales/ru.json'))
    parser.add_argument('--out', default=str(here / 'review/dvinyl-ru-review.html'))
    parser.add_argument('--title', default='Русский перевод DVinyl — проверка')
    args = parser.parse_args()

    en = flatten(json.loads(Path(args.en).read_text(encoding='utf-8')))
    ru = flatten(json.loads(Path(args.ru).read_text(encoding='utf-8')))

    rows, sections, counts, title = build(en, ru, args.title)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render(rows, sections, counts, title), encoding='utf-8')

    issues = [r for r in rows if r['marks']]
    print(f'страница: {out}')
    print(f'строк: {counts["всего"]}, переведено: {counts["переведено"]}, не хватает: {counts["не хватает"]}, с замечаниями: {counts["с замечаниями"]}')
    for mark in ('плейсхолдеры', 'пусто', 'как в EN', 'латиница'):
        n = sum(1 for r in issues if mark in r['marks'])
        if n:
            print(f'  {mark}: {n}')


if __name__ == '__main__':
    main()
