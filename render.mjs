// 逐帧渲染：内置静态服务器 + Playwright 截图
// 用法：node render.mjs <who> frames <from> <to>   （秒，含 from 不含 to，输出 out/<who>/frames/%05d.jpg）
//       node render.mjs <who> still <t> [t...]      （输出 out/<who>/still_<t>.jpg）
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { chromium } from 'playwright-core';

const ROOT = path.dirname(fileURLToPath(import.meta.url));
const FPS = 30;
// Chromium：优先环境变量 LTV_CHROME，否则在 Playwright 缓存里取版本号最大的 chromium-*
export function findChrome() {
  if (process.env.LTV_CHROME) {
    if (!fs.existsSync(process.env.LTV_CHROME)) throw new Error(`LTV_CHROME not found: ${process.env.LTV_CHROME}`);
    return process.env.LTV_CHROME;
  }
  const caches = [path.join(process.env.HOME, 'Library/Caches/ms-playwright'), path.join(process.env.HOME, '.cache/ms-playwright')];
  const rel = ['chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing',
    'chrome-mac-x64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing',
    'chrome-mac/Chromium.app/Contents/MacOS/Chromium', 'chrome-linux/chrome', 'chrome-linux64/chrome'];
  for (const cache of caches) {
    const dirs = fs.existsSync(cache) ? fs.readdirSync(cache).filter(d => /^chromium-\d+$/.test(d))
      .sort((a, b) => +b.split('-')[1] - +a.split('-')[1]) : [];
    for (const d of dirs) for (const r of rel) { const p = path.join(cache, d, r); if (fs.existsSync(p)) return p; }
  }
  throw new Error('Chromium not found: set LTV_CHROME or run `npx playwright install chromium`');
}
const MIME = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.json': 'application/json', '.jpg': 'image/jpeg', '.png': 'image/png', '.bin': 'application/octet-stream', '.geojson': 'application/json' };

export function serve() {
  const srv = http.createServer((req, res) => {
    let p;
    try { p = path.join(ROOT, decodeURIComponent(req.url.split('?')[0])); } catch { res.writeHead(400); res.end(); return; }
    if (!(p === ROOT || p.startsWith(ROOT + path.sep)) || !fs.existsSync(p) || fs.statSync(p).isDirectory()) { res.writeHead(404); res.end(); return; }
    res.writeHead(200, { 'Content-Type': MIME[path.extname(p)] || 'application/octet-stream' });
    fs.createReadStream(p).pipe(res);
  });
  return new Promise(r => srv.listen(0, '127.0.0.1', () => r(srv)));
}

export async function openPage(who, onError) {
  const srv = await serve();
  const browser = await chromium.launch({ executablePath: findChrome(), args: ['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist', '--enable-webgl'] });
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  page.setDefaultTimeout(180000);   // 高负载时截图可能超过默认 30 s
  page.on('pageerror', e => onError(`pageerror: ${e.message}`));
  page.on('console', m => { if (m.type() === 'error') onError(`console: ${m.text()}`); });
  await page.goto(`http://127.0.0.1:${srv.address().port}/src/index.html?who=${who}`);
  await page.waitForFunction(() => window.ready === true, null, { timeout: 180000 });
  return { page, close: async () => { await browser.close(); srv.close(); } };
}

async function main() {
  const [who, mode, ...args] = process.argv.slice(2);
  if (!who || !['frames', 'still'].includes(mode)) { console.error('usage: node render.mjs <who> frames <from> <to> | still <t...>'); process.exit(1); }
  const { page, close } = await openPage(who, msg => { console.error(msg); process.exit(2); });
  const outDir = path.join(ROOT, 'out', who);
  fs.mkdirSync(outDir, { recursive: true });
  if (mode === 'still') {
    for (const t of args.map(Number)) {
      await page.evaluate(t => window.renderAt(t), t);
      await page.screenshot({ path: path.join(outDir, `still_${t}.jpg`), quality: 90 });
      console.log('still', t);
    }
  } else {
    const [from, to] = args.map(Number);
    const dir = path.join(outDir, 'frames');
    fs.mkdirSync(dir, { recursive: true });
    const t0 = Date.now();
    for (let f = Math.round(from * FPS); f < Math.round(to * FPS); f++) {
      await page.evaluate(t => window.renderAt(t), f / FPS);
      await page.screenshot({ path: path.join(dir, `${String(f).padStart(5, '0')}.jpg`), quality: 92 });
      if (f % 300 === 0) console.log(`${who} frame ${f} (${((Date.now() - t0) / 1000).toFixed(0)}s)`);
    }
  }
  await close();
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) main();
