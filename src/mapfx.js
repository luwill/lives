// 地图叠加层：轨迹线、当前位置、到访地点、里程碑星标、地理注记（含碰撞避让）
import { makeLine, setLinePts, toWorld, project, kmBetween, THREE } from './engine.js';
import { trailUpTo, positionAt, isOffMap, trailFade, trailFloor, trailTau, replayTime, stepIndexAt } from './journey.js';

export const clamp01 = x => Math.max(0, Math.min(1, x));
export const win = (t, t0, t1, fade = 0.5) => Math.min(clamp01((t - t0) / fade), clamp01((t1 - t) / fade));

const layer = () => document.getElementById('labels');
function el(cls, html) {
  const d = document.createElement('div');
  d.className = cls;
  d.innerHTML = html;
  layer().appendChild(d);
  return d;
}

// ---------- 轨迹线 ----------
// 已走过的轨迹逐点着色：平时按“走过多久”变暗；片尾按人生先后由暗到亮，看得出时间方向
const OUTRO_FLOOR = 0.4;
function shadeColors(pts, ts, base, shade) {
  const out = new Float32Array(pts.length * 3);
  for (let k = 0; k < pts.length; k++) {
    const s = shade(ts[k]) ** 2.2;   // 感知亮度 → 线性空间（顶点色按线性存储）
    out[k * 3] = base.r * s; out[k * 3 + 1] = base.g * s; out[k * 3 + 2] = base.b * s;
  }
  return out;
}

export function makeTrail(scene, journey, person, tl) {
  const past = makeLine('#ffffff', 2.4, { opacity: 0.8, renderOrder: 10, vertexColors: true });
  const glow = makeLine(person.glow, 12, { opacity: 0.22, renderOrder: 11 });
  const recent = makeLine(person.color, 5, { renderOrder: 12 });
  const core = makeLine('#fffaf0', 1.6, { opacity: 0.9, renderOrder: 13 });
  [past, glow, recent, core].forEach(l => scene.add(l));
  const base = new THREE.Color(person.color);
  const RECENT = 7;   // 秒：最近这段路高亮
  const { verts } = journey;
  const vt0 = verts[0][2], vt1 = verts[verts.length - 1][2];
  // 片尾回放占 outro 的 [1 s, 末尾前 2.5 s]
  const rp0 = tl.outro.t0 + 1, rp1 = Math.max(rp0 + 4, tl.outro.t1 - 2.5);
  const REPLAY_VERTS = 70;   // 回放光带长度：约 70 个路径点（≈ 800 km）
  const vStep = verts.map(v => stepIndexAt(tl.steps, v[2]));   // 每个路径点属于哪个半年步
  return (t, cam, fadeAll = 1) => {
    const lift = cam.dist * 0.004;
    const inOutro = t >= tl.outro.t0;
    const all = trailUpTo(verts, t);
    // 每个点的着色依据：片尾按时间轴位置（人生先后），平时按“走过了几个半年步”；trailUpTo 末尾可能多一个插值点（当前时刻）
    let vals, shade;
    if (inOutro) {
      vals = verts.slice(0, all.length).map(v => v[2]);
      if (vals.length < all.length) vals.push(t);
      shade = vt => OUTRO_FLOOR + (1 - OUTRO_FLOOR) * clamp01((vt - vt0) / (vt1 - vt0));
    } else {
      const now = stepIndexAt(tl.steps, t), tau = trailTau(cam.zoom), floor = trailFloor(cam.zoom);
      vals = vStep.slice(0, all.length).map(k => now - k);
      if (vals.length < all.length) vals.push(0);
      shade = age => trailFade(age, tau, floor);
    }
    setLinePts(past, all, lift, shadeColors(all, vals, base, shade));
    let rec;
    if (inOutro) {   // 一生回放：一道光沿全程从出生地走到终点
      const e = clamp01((t - rp0) / (rp1 - rp0)), f = e < 0.5 ? 2 * e * e : 1 - (-2 * e + 2) ** 2 / 2;
      const tr = replayTime(tl.steps, f);
      const head = trailUpTo(verts, tr), k0 = Math.max(0, head.length - REPLAY_VERTS);
      rec = t < rp0 ? [] : head.slice(k0);
    } else rec = trailUpTo(verts, t, t - RECENT);
    setLinePts(glow, rec, lift);
    setLinePts(recent, rec, lift);
    setLinePts(core, rec, lift);
    const outroK = inOutro ? clamp01((t - tl.outro.t0) / 1.5) : 0;
    past.material.linewidth = 2.4 + 1.2 * outroK;
    past.material.opacity = 0.8 * fadeAll;
    glow.material.opacity = 0.22 * fadeAll;
    recent.material.opacity = fadeAll;
    core.material.opacity = 0.85 * fadeAll;
  };
}

// ---------- 碰撞避让：按优先级贪心放置 ----------
// HUD 占用的屏幕区域：地图注记不放进去
const HUD_ZONES = [
  { x0: 30, x1: 640, y0: 24, y1: 250 },        // 身份卡 + 年份
  { x0: 1360, x1: 1900, y0: 24, y1: 120 },     // 行程统计
  { x0: 0, x1: 1920, y0: 845, y1: 1080 },      // 事件条（最多两行）+ 进度条
];
const CARD_ZONE = { x0: 1290, x1: 1890, y0: 160, y1: 700 };
const SUB_ZONE = { x0: 260, x1: 1660, y0: 770, y1: 836 };
// 图外标注可贴边的安全区：避开左上身份块、右上统计、底部字幕与事件条
const EDGE = { x0: 70, x1: 1850, y0: 290, y1: 740 };

function placeLabels(items, reserved) {
  items.sort((a, b) => b.pri - a.pri);
  const boxes = [];
  const overlaps = (r, list) => list.some(b => r.x0 < b.x1 && r.x1 > b.x0 && r.y0 < b.y1 && r.y1 > b.y0);
  for (const it of items) {
    const r = it.rect;
    // HUD 区域对所有注记生效；当前地点可压过其他注记
    // 注记超出画面（如图外代理点落在画面最上缘）时整条隐藏，不显示半截
    const outside = r.x0 < 0 || r.y0 < 0 || r.x1 > 1920 || r.y1 > 1080;
    if (outside || overlaps(r, reserved) || (overlaps(r, boxes) && !it.force)) { it.d.style.display = 'none'; continue; }
    boxes.push(r);
    it.d.style.display = 'block';
    it.d.style.opacity = it.op;
    it.d.style.transform = `translate(${it.x.toFixed(1)}px, ${it.y.toFixed(1)}px)`;
  }
}

// 估算文字框：字号 × 字数（中文等宽）
const rectOf = (x, y, w, h, anchor) => anchor === 'c'
  ? { x0: x - w / 2 - 6, x1: x + w / 2 + 6, y0: y - h / 2 - 4, y1: y + h / 2 + 4 }
  : { x0: x - 10, x1: x + 16 + w, y0: y - h / 2 - 4, y1: y + h / 2 + 4 };

// ---------- 地点与注记 ----------
export function makeMarkers(person, data, places, journey, tl, geoLabels) {
  const steps = data.steps;
  const stayCount = {};
  steps.forEach(s => { const k = s.places[s.places.length - 1]; stayCount[k] = (stayCount[k] || 0) + 1; });
  const msPlace = {};
  const msKey = s => s.milestone.place || s.places[s.places.length - 1];
  steps.forEach((s, i) => { if (s.milestone) msPlace[msKey(s)] = msPlace[msKey(s)] ?? i; });
  const firstAt = {}, firstPos = {};
  journey.arrivals.forEach(a => { if (!(a.key in firstAt)) { firstAt[a.key] = a.t; firstPos[a.key] = a.pos; } });
  const lastAt = {};
  journey.arrivals.forEach(a => { (lastAt[a.key] = lastAt[a.key] || []).push(a.t); });

  const P = Object.entries(places).filter(([k]) => k in firstAt).map(([k, p]) => {
    const [lon, lat] = firstPos[k];
    const off = isOffMap(p);
    const name = off ? `${p.name} ➚` : p.name;
    const sub = off ? `图外 · 距北京约 ${Math.round(kmBetween([116.4, 39.9], [p.lon, p.lat]) / 100) * 100} 公里` : (p.modern !== p.name ? p.modern : '');
    const d = el(`place${off ? ' foreign' : ''}`, `<i></i><span><b>${name}</b>${sub ? `<em>${sub}</em>` : ''}</span>`);
    return { key: k, lon, lat, d, off, w: name.length * 26 + 30, wFull: name.length * 26 + 30 + (sub ? sub.length * 17 + 10 : 0),
      important: stayCount[k] >= 2 || k in msPlace || off, first: firstAt[k], arr: lastAt[k] };
  });
  const stars = Object.keys(msPlace).filter(k => k in firstAt).map(k => {
    const s = steps[msPlace[k]], [lon, lat] = firstPos[k];
    return { lon, lat, t: tl.steps[msPlace[k]].ms ? tl.steps[msPlace[k]].ms.t0 : tl.steps[msPlace[k]].t0, d: el('star', '★'), title: s.milestone.title };
  });
  const G = geoLabels.map(g => ({ ...g, d: el(`geo g-${g.kind}`, `<span>${g.name}</span>`), w: g.name.length * (g.kind === 'region' ? 34 : 26) }));
  const R = person.regions.map(r => ({ ...r, d: el('geo g-era', `<span>${r.name}</span>`), w: r.name.length * 44 }));
  const cur = el('cur', '<i class="r1"></i><i class="r2"></i><i class="dot"></i>');
  cur.style.setProperty('--c', person.color);
  const ring = el('msring', '<i></i><i></i><i></i>');

  return (t, camera, cam, ctx) => {
    const items = [];
    const curPos = positionAt(journey.verts, t);
    // 当前地点（最近到达且未离开）
    let curKey = null;
    for (const a of journey.arrivals) if (a.t <= t) curKey = a.key;
    const stepIdx = ctx.stepIdx;
    for (const p of P) {
      if (t < p.first || ctx.hideMap) { p.d.style.display = 'none'; continue; }
      const sp = project(camera, toWorld(p.lon, p.lat, cam.dist * 0.004));
      const isCur = p.key === curKey;
      // 人在图外时，图外标注贴到画面安全区边缘（代理点常在地图西北角，落进左上 HUD 或画外就会被藏掉）
      if (isCur && p.off && sp.front) {
        sp.x = Math.max(EDGE.x0, Math.min(EDGE.x1 - p.wFull, sp.x));
        sp.y = Math.max(EDGE.y0, Math.min(EDGE.y1, sp.y));
        sp.visible = true;
      }
      if (!sp.visible) { p.d.style.display = 'none'; continue; }
      const lastArr = p.arr.filter(x => x <= t).pop();
      const recent = t - lastArr < 3.5;
      const fresh = clamp01((t - p.first) / 0.4);
      let pri = isCur ? 100 : recent ? 70 : p.important ? 50 : 0;
      p.d.classList.toggle('cur-place', isCur);
      p.d.classList.toggle('minor', !p.important && !isCur && !recent);
      if (pri === 0) {   // 普通地点：只留小点，不显示名字
        p.d.style.display = 'block';
        p.d.style.opacity = 0.75 * fresh;
        p.d.style.transform = `translate(${sp.x.toFixed(1)}px, ${sp.y.toFixed(1)}px)`;
        continue;
      }
      items.push({ d: p.d, x: sp.x, y: sp.y, pri, op: fresh, force: isCur, rect: rectOf(sp.x, sp.y, p.off ? p.wFull : p.w, 34, 'r') });
    }
    for (const s of stars) {
      const on = t >= s.t && !ctx.hideMap;
      if (!on) { s.d.style.display = 'none'; continue; }
      const sp = project(camera, toWorld(s.lon, s.lat, cam.dist * 0.004));
      // 星标落在 HUD 区（年份块、统计、底栏、里程碑卡）里时隐藏，避免压住文字
      const zones = [...HUD_ZONES, ...(ctx.ms ? [CARD_ZONE] : [])];
      const covered = zones.some(z => sp.x >= z.x0 && sp.x <= z.x1 && sp.y >= z.y0 && sp.y <= z.y1);
      s.d.style.display = sp.visible && !covered ? 'block' : 'none';
      s.d.style.opacity = clamp01((t - s.t) / 0.6);
      s.d.style.transform = `translate(${sp.x.toFixed(1)}px, ${sp.y.toFixed(1)}px) scale(${1 + 0.8 * Math.exp(-(t - s.t) * 2)})`;
    }
    for (const g of G) {
      const vis = cam.dist >= g.dmin && cam.dist <= g.dmax && !ctx.hideMap;
      if (!vis) { g.d.style.display = 'none'; continue; }
      const sp = project(camera, toWorld(g.lon, g.lat, 0.5));
      if (!sp.visible) { g.d.style.display = 'none'; continue; }
      const edge = Math.min(clamp01((cam.dist - g.dmin) / (g.dmin * 0.25)), clamp01((g.dmax - cam.dist) / (g.dmax * 0.15)));
      const pri = { region: 30, sea: 25, mountain: 20, river: 18, island: 22, lake: 15 }[g.kind];
      items.push({ d: g.d, x: sp.x, y: sp.y, pri, op: edge, rect: rectOf(sp.x, sp.y, g.w, g.kind === 'region' ? 40 : 30, 'c') });
    }
    for (const r of R) {
      const k = ctx.halfIdx >= r.from && !(ctx.halfIdx > r.to) && !ctx.hideMap && cam.dist > 900;
      if (!k) { r.d.style.display = 'none'; continue; }
      const sp = project(camera, toWorld(r.lon, r.lat, 0.5));
      if (!sp.visible) { r.d.style.display = 'none'; continue; }
      items.push({ d: r.d, x: sp.x, y: sp.y, pri: 35, op: clamp01((cam.dist - 900) / 300), rect: rectOf(sp.x, sp.y, r.w, 56, 'c') });
    }
    placeLabels(items, [...HUD_ZONES, SUB_ZONE, ...(ctx.ms ? [CARD_ZONE] : [])]);
    // 当前位置标记
    const cp = project(camera, toWorld(curPos[0], curPos[1], cam.dist * 0.004));
    // 当前位置落进 HUD 区（图外代理点常在左上角）时不画，避免红点压在姓名、年份上
    const inHud = HUD_ZONES.some(z => cp.x >= z.x0 && cp.x <= z.x1 && cp.y >= z.y0 && cp.y <= z.y1);
    cur.style.display = ctx.hideMap || inHud ? 'none' : 'block';
    cur.style.transform = `translate(${cp.x.toFixed(1)}px, ${cp.y.toFixed(1)}px)`;
    cur.style.setProperty('--ph', ((t * 0.9) % 1).toFixed(3));
    cur.style.setProperty('--ph2', ((t * 0.9 + 0.5) % 1).toFixed(3));
    // 里程碑光环
    const m = ctx.ms;
    if (m) {
      const k = win(t, m.t0, m.t1, 0.6);
      ring.style.display = k > 0 ? 'block' : 'none';
      ring.style.opacity = k;
      ring.style.transform = `translate(${cp.x.toFixed(1)}px, ${cp.y.toFixed(1)}px)`;
      ring.style.setProperty('--ph', (((t - m.t0) * 0.55) % 1).toFixed(3));
    } else ring.style.display = 'none';
    return stepIdx;
  };
}
