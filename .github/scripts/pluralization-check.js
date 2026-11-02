// Проверка русских форм множественного числа. Запускается из CI и из pre-push.
// Ожидания взяты из правил русского языка: 1 — «трек», 2–4 — «трека», 5+ — «треков»,
// при этом 11–14 и числа на 11–14 всегда «треков» (22 — «двадцать два трека»).
const locale = require("../../locales/ru.json");

function pluralKey(n) {
  const n10 = n % 10;
  const n100 = n % 100;
  if (n10 === 1 && n100 !== 11) return "_one";
  if (n10 >= 2 && n10 <= 4 && (n100 < 12 || n100 > 14)) return "_few";
  return "_many";
}

function translate(base, n) {
  const form = locale.lists[base + pluralKey(n)];
  if (!form) throw new Error(`нет формы ${base}${pluralKey(n)}`);
  return String(form).replace("{{count}}", n);
}

const cases = [
  [1, "1 трек"],
  [3, "3 трека"],
  [5, "5 треков"],
  [11, "11 треков"],
  [22, "22 трека"],
  [25, "25 треков"],
];

let failed = 0;
for (const [count, want] of cases) {
  const got = translate("tracks_count", count);
  if (got !== want) {
    console.error(`  ${count}: получили «${got}», ждали «${want}»`);
    failed += 1;
  }
}
if (failed) process.exit(1);
console.log(`  формы в порядке: ${cases.length} проверок`);
