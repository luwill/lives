// 相机路径：按时间轴生成关键帧 → 逐帧采样 → 前后向指数平滑（零相位，无滞后）
// renderAt(t) 只查表，保证同一 t 永远得到同一画面
import { positionAt } from './journey.js';

const FPS = 30;
const OVERVIEW = { lon: 106.5, lat: 33.0, dist: 4800 };
const MS_DIST = 260;
const MIN_D = 520, MAX_D = 3600;

function bboxDist(pts) {
  const lons = pts.map(p => p[0]), lats = pts.map(p => p[1]);
  const lon = (Math.min(...lons) + Math.max(...lons)) / 2, lat = (Math.min(...lats) + Math.max(...lats)) / 2;
  const w = (Math.max(...lons) - Math.min(...lons)) * 111.32 * Math.cos(lat * Math.PI / 180);
  const h = (Math.max(...lats) - Math.min(...lats)) * 110.57;
  return { lon, lat, ext: Math.max(w / 1.78, h) };
}

export function buildCamera(tl, journey) {
  const { verts } = journey;
  const steps = tl.steps;
  // 每一步的“取景”：前后约 ±4 秒内经过的位置的包围盒
  const frame = steps.map(s => {
    const mid = (s.t0 + s.t1) / 2, pts = [];
    for (let dt = -4; dt <= 4; dt += 0.5) pts.push(positionAt(verts, mid + dt));
    const b = bboxDist(pts);
    return { lon: b.lon, lat: b.lat, dist: Math.min(MAX_D, Math.max(MIN_D, b.ext * 2.3 + 380)) };
  });
  const lifeBox = bboxDist(verts.map(v => [v[0], v[1]]));
  const outro = { lon: lifeBox.lon, lat: lifeBox.lat - 1.5, dist: Math.min(5200, lifeBox.ext * 2.1 + 600) };
  const first = positionAt(verts, steps[0].t0);

  function raw(t) {
    if (t < tl.intro.t0) return OVERVIEW;
    if (t < tl.intro.t1) {   // 片头：全国俯瞰缓慢推向出生地
      const f = (t - tl.intro.t0) / (tl.intro.t1 - tl.intro.t0);
      const k = Math.max(0, (f - 0.55) / 0.45);
      return { lon: OVERVIEW.lon + (first[0] - OVERVIEW.lon) * k, lat: OVERVIEW.lat + (first[1] - OVERVIEW.lat) * k,
        dist: OVERVIEW.dist * Math.pow(1500 / OVERVIEW.dist, k) };
    }
    if (t >= tl.outro.t0) return outro;
    let i = 0;
    while (i + 1 < steps.length && steps[i + 1].t0 <= t) i++;
    const s = steps[i];
    if (s.ms && t <= s.ms.t1) {
      // 抵达途中：镜头跟随人物并逐渐推近；抵达后定在里程碑地点
      const p = positionAt(verts, Math.min(t, s.ms.t0));
      const k = Math.min(1, (t - s.t0) / (s.ms.t0 - s.t0));
      const from = i > 0 ? frame[i - 1].dist : frame[i].dist;
      return { lon: p[0], lat: p[1], dist: Math.exp(Math.log(from) + (Math.log(MS_DIST) - Math.log(from)) * k * k) };
    }
    return frame[i];
  }

  const n = Math.ceil(tl.total * FPS) + 1;
  const ch = { lon: new Float64Array(n), lat: new Float64Array(n), ld: new Float64Array(n) };
  for (let f = 0; f < n; f++) {
    const r = raw(f / FPS);
    ch.lon[f] = r.lon; ch.lat[f] = r.lat; ch.ld[f] = Math.log(r.dist);
  }
  const smooth = (arr, tau) => {
    const a = 1 - Math.exp(-1 / (FPS * tau));
    for (let f = 1; f < n; f++) arr[f] += (arr[f - 1] - arr[f]) * (1 - a);
    for (let f = n - 2; f >= 0; f--) arr[f] += (arr[f + 1] - arr[f]) * (1 - a);
  };
  smooth(ch.lon, 0.55); smooth(ch.lat, 0.55); smooth(ch.ld, 0.7);

  return t => {
    const f = Math.max(0, Math.min(n - 1, t * FPS));
    const i = Math.floor(f), j = Math.min(n - 1, i + 1), u = f - i;
    const L = k => ch[k][i] * (1 - u) + ch[k][j] * u;
    const dist = Math.exp(L('ld'));
    const z = Math.max(0, Math.min(1, (Math.log(dist) - Math.log(MS_DIST)) / (Math.log(OVERVIEW.dist) - Math.log(MS_DIST))));
    return { lon: L('lon'), lat: L('lat'), dist, pitch: 40 + 22 * z, heading: 6 * Math.sin(t / 37), zoom: z };
  };
}
