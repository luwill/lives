// 行程：把半年步 + 时间轴展开为带时间戳的路径点（纯函数，不依赖 three.js）
// 地图可见范围（之外的地点投到边缘）。东界放到 146°E：世界底图铺到 178°E，日本本州在画面里，东京、高田应按真实坐标标注
export const MAP_BOX = { lon0: 72, lon1: 146, lat0: 16, lat1: 54 };
const CENTER = [105, 35];

export function isOffMap(p) {
  return p.lon < MAP_BOX.lon0 || p.lon > MAP_BOX.lon1 || p.lat < MAP_BOX.lat0 || p.lat > MAP_BOX.lat1;
}

// 图外地点 → 从北京朝它的方向延伸到地图边缘（留 3° 边距）的固定代理点：方向正确，且同一地点每次都落在同一处
const ANCHOR = [116.4, 39.9];
export function proxyOf(p) {
  if (!isOffMap(p)) return [p.lon, p.lat];
  const m = 3, [cx, cy] = ANCHOR, dx = p.lon - cx, dy = p.lat - cy;
  let s = 1;
  if (dx < 0) s = Math.min(s, (MAP_BOX.lon0 + m - cx) / dx);
  if (dx > 0) s = Math.min(s, (MAP_BOX.lon1 - m - cx) / dx);
  if (dy < 0) s = Math.min(s, (MAP_BOX.lat0 + m - cy) / dy);
  if (dy > 0) s = Math.min(s, (MAP_BOX.lat1 - m - cy) / dy);
  return [cx + dx * s, cy + dy * s];
}

const KM = (a, b) => Math.hypot((b[0] - a[0]) * 111.32 * Math.cos((a[1] + b[1]) / 2 * Math.PI / 180), (b[1] - a[1]) * 110.57);

// steps: data steps；tlSteps: 时间轴步（同序）；places: 地点表
export function buildJourney(steps, tlSteps, places, stepKm = 12) {
  const verts = [];          // [lon, lat, t]
  const arrivals = [];       // {key, t, step, pos}
  let prev = null;
  const kmTrue = [];          // 每个路径点相对上一点的“真实”公里数（图外段按真实坐标折算）
  // 一段行程：keys 依次经过，在 [t0, t1] 内按距离匀速（首尾缓动）走完
  function leg(keys, t0, t1, i) {
    const seq = (prev ? [prev] : []).concat(keys).filter((k, j, a) => j === 0 || k !== a[j - 1]);
    // 第一个点就是上一段的终点：直接沿用（图外代理点不能重复外推）
    const pts = [];
    seq.forEach((k, j) => {
      if (j === 0 && prev) { pts.push(verts[verts.length - 1].slice(0, 2)); return; }
      pts.push(proxyOf(places[k]));
    });
    if (!prev) {
      verts.push([...pts[0], t0]);
      kmTrue.push(0);
      arrivals.push({ key: seq[0], t: t0, step: i, pos: pts[0] });
    }
    const lens = pts.slice(1).map((p, j) => KM(pts[j], p));
    const total = lens.reduce((a, b) => a + b, 0);
    const real = seq.map(k => [places[k].lon, places[k].lat]);
    const scale = lens.map((l, j) => (l > 0 ? KM(real[j], real[j + 1]) / l : 0));
    let acc = 0;
    for (let j = 0; j < pts.length - 1; j++) {
      const a = pts[j], b = pts[j + 1], n = Math.max(1, Math.ceil(lens[j] / stepKm));
      for (let k = 1; k <= n; k++) {
        const f = k / n, d = acc + lens[j] * f;
        const u = total > 0 ? d / total : 1;
        const e = u < 0.5 ? 2 * u * u : 1 - (-2 * u + 2) ** 2 / 2;
        verts.push([a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f, t0 + (t1 - t0) * e]);
        kmTrue.push(lens[j] / n * scale[j]);
      }
      acc += lens[j];
      arrivals.push({ key: seq[j + 1], t: t0 + (t1 - t0) * (total > 0 ? acc / total : 1), step: i, pos: pts[j + 1] });
    }
    prev = keys[keys.length - 1];
  }
  steps.forEach((st, i) => {
    const ts = tlSteps[i];
    const cut = ts.split ?? st.places.length;
    leg(st.places.slice(0, cut), ts.t0, ts.t0 + ts.move, i);
    if (ts.after) leg(st.places.slice(cut), ts.after.t0, ts.after.t0 + ts.after.move, i);
  });
  const cum = [0];
  for (let i = 1; i < verts.length; i++) cum.push(cum[i - 1] + kmTrue[i]);
  // 每一步是否到过图外地点（镜头据此拉远，让图外标注落在画面里）
  const offSteps = steps.map(st => st.places.some(k => isOffMap(places[k])));
  return { verts, arrivals, cum, totalKm: cum[cum.length - 1], offSteps };
}

// 二分查找：t 时刻已走过的路径点下标（verts[i].t <= t 的最大 i）
export function vertIndexAt(verts, t) {
  let lo = 0, hi = verts.length - 1;
  if (t < verts[0][2]) return -1;
  while (lo < hi) {
    const mid = (lo + hi + 1) >> 1;
    if (verts[mid][2] <= t) lo = mid; else hi = mid - 1;
  }
  return lo;
}

export function positionAt(verts, t) {
  const i = vertIndexAt(verts, t);
  if (i < 0) return [verts[0][0], verts[0][1]];
  if (i >= verts.length - 1) return [verts[i][0], verts[i][1]];
  const a = verts[i], b = verts[i + 1], f = b[2] > a[2] ? (t - a[2]) / (b[2] - a[2]) : 1;
  return [a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f];
}

// 已走过的路径（含插值的当前点），可选只取 [tFrom, t] 一段
export function trailUpTo(verts, t, tFrom = -Infinity) {
  const i = vertIndexAt(verts, t);
  if (i < 0) return [];
  let s = tFrom === -Infinity ? 0 : Math.max(0, vertIndexAt(verts, tFrom));
  const out = verts.slice(s, i + 1).map(v => [v[0], v[1]]);
  if (i < verts.length - 1) out.push(positionAt(verts, t));
  return out;
}

export function stepIndexAt(tlSteps, t) {
  let k = 0;
  for (let i = 0; i < tlSteps.length; i++) if (t >= tlSteps[i].t0) k = i;
  return k;
}

export function kmAt(journey, t) {
  const i = vertIndexAt(journey.verts, t);
  return i < 0 ? 0 : journey.cum[i];
}

// 轨迹亮度：走过越久越暗（指数衰减到 floor），近景里多年前的长直线不再抢眼
// 旧轨迹的亮度下限随镜头远近变化：近景压到 0.08，避免多年前的长直线横穿近景、两端都不在画内；全景回到 0.3
export function trailFloor(zoom) {
  return 0.08 + 0.22 * Math.max(0, Math.min(1, zoom));
}

// 旧轨迹衰减的时间常数（单位：半年步）：近景 3 步，全景 12 步。按人生年岁而不是视频秒数衰减——
// 早年每步只占 0.55 s，按秒算时“三年前”的长途路线在近景里几乎不变暗（粟裕 1927 南下潮汕的南北直线）
export function trailTau(zoom) {
  return 3 + 9 * Math.max(0, Math.min(1, zoom));
}

export function trailFade(age, tau = 90, floor = 0.3) {
  return floor + (1 - floor) * Math.exp(-Math.max(0, age) / tau);
}

// 片尾回放：f∈[0,1] 按“人生半年步”匀速映射到时间轴时刻（跳过里程碑讲解的停留，回放速度与年岁成正比）
// 每步内：有后续行程（after）时前后两半各走一段；无移动的步停在原地
export function replayTime(tlSteps, f) {
  const n = tlSteps.length, x = Math.max(0, Math.min(1, f)) * n;
  const i = Math.min(n - 1, Math.floor(x)), u = x - i, s = tlSteps[i];
  if (s.after) return u < 0.5 ? s.t0 + s.move * u * 2 : s.after.t0 + s.after.move * (u - 0.5) * 2;
  return s.t0 + s.move * u;
}
