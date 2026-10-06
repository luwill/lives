// 逐帧渲染：内置静态服务器 + Playwright 截图
// 用法：node render.mjs <who> frames <from> <to>   （秒，含 from 不含 to，输出 out/<who>/frames/%05d.jpg）
//       node render.mjs <who> still <t> [t...]      （输出 out/<who>/still_<t>.jpg）
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { chromium } from 'playwright-core';

const ROOT = path.dirname(new URL(import.meta.url).pathname);
const FPS = 30;
export const CHROME = path.join(process.env.HOME, 'Library/Caches/ms-playwright/chromium-1243/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing');
const MIME = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.json': 'application/json', '.jpg': 'image/jpeg', '.png': 'image/png', '.bin': 'application/octet-stream', '.geojson': 'application/json' };

export function serve() {
  const srv = http.createServer((req, res) => {
    const p = path.join(ROOT, decodeURIComponent(req.url.split('?')[0]));
    if (!p.startsWith(ROOT) || !fs.existsSync(p) || fs.statSync(p).isDirectory()) { res.writeHead(404); res.end(); return; }
    res.writeHead(200, { 'Content-Type': MIME[path.extname(p)] || 'application/octet-stream' });
    fs.createReadStream(p).pipe(res);
  });
  return new Promise(r => srv.listen(0, () => r(srv)));
}

export async function openPage(who, onError) {
  const srv = await serve();
  const browser = await chromium.launch({ executablePath: CHROME, args: ['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist', '--enable-webgl'] });
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  page.setDefaultTimeout(180000);   // 高负载时截图可能超过默认 30 s
  page.on('pageerror', e => onError(`pageerror: ${e.message}`));
  page.on('console', m => { if (m.type() === 'error') onError(`console: ${m.text()}`); });
  await page.goto(`http://localhost:${srv.address().port}/src/index.html?who=${who}`);
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

if (process.argv[1] === new URL(import.meta.url).pathname) main();
