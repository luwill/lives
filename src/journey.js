// 行程：把半年步 + 时间轴展开为带时间戳的路径点（纯函数，不依赖 three.js）
export const MAP_BOX = { lon0: 72, lon1: 136, lat0: 16, lat1: 54 };   // 地图可见范围（境外地点投到边缘）
const CENTER = [105, 35];

export function isOffMap(p) {
  return p.lon < MAP_BOX.lon0 || p.lon > MAP_BOX.lon1 || p.lat < MAP_BOX.lat0 || p.lat > MAP_BOX.lat1;
}

// 图外地点 → 从出发点朝它的方向前进 OFF_KM 公里处（画面内可见的“出图”箭头位置）
const OFF_KM = 900;
const ANCHOR = [116.4, 39.9];   // 北京：同一图外地点每次都落在同一代理点
export function proxyOf(p) {
  if (!isOffMap(p)) return [p.lon, p.lat];
  const [fx, fy] = ANCHOR;
  const kx = 111.32 * Math.cos(fy * Math.PI / 180), dx = (p.lon - fx) * kx, dy = (p.lat - fy) * 110.57;
  const d = Math.hypot(dx, dy), s = Math.min(1, OFF_KM / d);
  return [fx + dx * s / kx, fy + dy * s / 110.57];
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
  return { verts, arrivals, cum, totalKm: cum[cum.length - 1] };
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
