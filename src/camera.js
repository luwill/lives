// 相机路径：按时间轴生成关键帧 → 逐帧采样 → 前后向指数平滑（零相位，无滞后）
// renderAt(t) 只查表，保证同一 t 永远得到同一画面
import { positionAt } from './journey.js';

const FPS = 30;
const OVERVIEW = { lon: 106.5, lat: 33.0, dist: 4800 };
const MS_DIST = 260;
const CARD_SHIFT = 0.17;   // 里程碑停留时目标点东移（×距离），把地点让到信息卡左边
const MIN_D = 520, MAX_D = 3600;
const OFF_MIN_D = 3200, OFF_MAX_D = 5400;   // 图外行程的取景范围

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
    // 到过图外地点的一步：放宽视距上限，让图外代理点和它的标注一起进画面（否则镜头只跟着人物小点横穿西部）
    const off = journey.offSteps && journey.offSteps[steps.indexOf(s)];
    return { lon: b.lon, lat: b.lat, dist: Math.min(off ? OFF_MAX_D : MAX_D, Math.max(off ? OFF_MIN_D : MIN_D, b.ext * 2.3 + 380)) };
  });
  // 远途里程碑：整段路线的取景
  const travelFrame = steps.map(s => {
    if (!s.ms || !s.ms.travel) return null;
    const pts = [];
    for (let k = 0; k <= 40; k++) pts.push(positionAt(verts, s.t0 + s.move * k / 40));
    const b = bboxDist(pts);
    // 底部 HUD 遮住画面下缘：取景中心南移、视距放宽
    return { lon: b.lon, lat: b.lat - b.ext * 0.18 / 110.57, dist: Math.min(MAX_D * 1.2, Math.max(MIN_D, b.ext * 2.5 + 300)) };
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
    if (s.ms && s.ms.travel && t <= s.ms.t1) {
      // 先俯瞰整段路线，走到终点后推近
      const arrive = s.t0 + s.move;
      if (t < arrive) return travelFrame[i];
      const p = positionAt(verts, arrive), k = Math.min(1, (t - arrive) / 1.5);
      const tf = travelFrame[i];
      return { lon: tf.lon + (p[0] - tf.lon) * k, lat: tf.lat + (p[1] - tf.lat) * k, dist: Math.exp(Math.log(tf.dist) + (Math.log(MS_DIST * 1.6) - Math.log(tf.dist)) * k) };
    }
    if (s.after && t > s.ms.t1) {   // 讲完后继续行程：镜头跟随
      const p = positionAt(verts, t);
      return { lon: p[0], lat: p[1], dist: Math.max(frame[i].dist, 900) };
    }
    if (s.ms && t <= s.ms.t1) {
      // 抵达途中：镜头跟随人物并逐渐推近；抵达后定在里程碑地点
      const p = positionAt(verts, Math.min(t, s.ms.t0));
      const k = Math.max(0, Math.min(1, (t - s.t0) / (s.ms.t0 - s.t0)));
      const from = i > 0 ? frame[i - 1].dist : frame[i].dist;
      const d = Math.exp(Math.log(from) + (Math.log(MS_DIST) - Math.log(from)) * k * k);
      return { lon: p[0] + CARD_SHIFT * d * k / (111.32 * Math.cos(p[1] * Math.PI / 180)), lat: p[1], dist: d };
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
