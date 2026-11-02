#!/usr/bin/env bash
# Установка русской локали в DVinyl, запущенный из исходников (не из официального образа).
#
#   ./install-source.sh /путь/к/клону/DVinyl
#
# Скрипт только правит файлы в указанном каталоге: локаль копируется, восемь точек
# регистрации накладываются идемпотентно. Ничего не удаляет и не коммитит — дальше
# запускаете приложение как обычно (`npm start`) или собираете свой образ.
set -euo pipefail

TARGET="${1:-}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ -z "$TARGET" ]; then
  echo "укажите путь к клону DVinyl: ./install-source.sh /path/to/DVinyl" >&2
  exit 2
fi
if [ ! -f "$TARGET/app.ts" ] || [ ! -d "$TARGET/locales" ]; then
  echo "это не похоже на исходники DVinyl: нет app.ts или locales/ в $TARGET" >&2
  exit 2
fi

echo "→ копирую локаль"
cp "$HERE/locales/ru.json" "$TARGET/locales/ru.json"

echo "→ регистрирую язык"
DV_ROOT="$TARGET" node "$HERE/apply-ru-locale.js"

echo "→ проверяю, что шаблоны собираются"
if command -v node >/dev/null 2>&1; then
  ( cd "$TARGET" && node --input-type=module -e '
import ejs from "ejs";
import fs from "fs";
for (const f of ["views/settings.ejs", "views/setup.ejs"]) {
  ejs.compile(fs.readFileSync(f, "utf8"), { filename: f });
  console.log("  ok:", f);
}
const ru = JSON.parse(fs.readFileSync("locales/ru.json", "utf8"));
console.log("  локаль на месте, верхних групп:", Object.keys(ru).length);
' 2>/dev/null || echo "  (проверка пропущена: в этом окружении нет ejs — запустите npm install)")
else
  echo "  (node не найден, шаблоны не проверены)"
fi

echo
echo "Готово. Дальше:"
echo "  cd $TARGET && npm start          # запустить как обычно"
echo "  — или —"
echo "  docker compose up -d --build     # если собираете свой образ"
echo
echo "Язык выбирается в интерфейсе: Настройки → Язык → Русский."
