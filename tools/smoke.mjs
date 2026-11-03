// 冒烟测试：六个人物页面都能加载，并在抽样时间点 renderAt(t) 无报错，画面非空
// 用法：node tools/smoke.mjs [who...]
import fs from 'node:fs';
import { openPage } from '../render.mjs';

const DATA = new URL('../data/', import.meta.url);
const all = fs.readdirSync(DATA).filter(d => fs.existsSync(new URL(`${d}/person.json`, DATA))).sort();
const people = process.argv.slice(2).length ? process.argv.slice(2) : all;
if (!people.length) { console.error('no people found (data/*/person.json)'); process.exit(1); }
let failed = 0;
for (const who of people) {
  const errors = [];
  let page, close;
  try {
    ({ page, close } = await openPage(who, msg => errors.push(msg)));
    const total = await page.evaluate(() => window.TOTAL);
    const ts = Array.from({ length: 24 }, (_, i) => +(total * (i + 0.5) / 24).toFixed(2));
    for (const t of ts) await page.evaluate(t => window.renderAt(t), t);
    // 中段一帧的画面方差：地形应当渲染出来（不是纯色）
    await page.evaluate(t => window.renderAt(t), total / 2);
    const std = await page.evaluate(() => {
      const c = document.getElementById('gl'), g = c.getContext('webgl2') || c.getContext('webgl');
      // 整帧抽样（每 16 像素取一点）：地形应有明暗变化
      const px = new Uint8Array(4 * 1920 * 1080);
      g.readPixels(0, 0, 1920, 1080, g.RGBA, g.UNSIGNED_BYTE, px);
      let s = 0, s2 = 0, n = 0;
      for (let i = 0; i < px.length; i += 4 * 16) { s += px[i]; s2 += px[i] * px[i]; n++; }
      return Math.sqrt(s2 / n - (s / n) ** 2);
    });
    if (std < 2) errors.push(`terrain looks blank (std=${std.toFixed(2)})`);
    console.log(`${who}: total ${total.toFixed(1)}s, ${ts.length} samples, frame std ${std.toFixed(1)}, errors ${errors.length}`);
  } catch (e) {
    errors.push(`load failed: ${e.message}`);
  }
  if (close) await close();
  if (errors.length) { failed++; errors.slice(0, 10).forEach(e => console.error(`  ${who}: ${e}`)); }
}
process.exit(failed ? 1 : 0);
