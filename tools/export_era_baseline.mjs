// 一次性工具：用迁移前的 src/people.js 导出六人每个半年步的 [年龄, 纪年] 与出生覆盖，存为基线
// 用法（在 lives/ 下）：node tools/export_era_baseline.mjs > tests/fixtures/era_baseline.json
import fs from 'node:fs';
import { PEOPLE } from '../src/people.js';

const out = {};
for (const who of Object.keys(PEOPLE)) {
  const p = PEOPLE[who];
  const steps = JSON.parse(fs.readFileSync(`data/${who}/steps.json`)).steps;
  const rows = {};
  for (const s of steps) {
    const [, y, h] = s.id.match(/^(\d+)H([12])$/);
    rows[s.id] = [p.age(+y, +h), p.era(+y, +h)];
  }
  out[who] = { rows, birth: p.birth || null };
}
console.log(JSON.stringify(out, null, 1));
