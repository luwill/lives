// 3D 地形引擎：地形网格、经纬度↔世界坐标、贴地线、标注投影
import * as THREE from 'three';
import { Line2 } from 'three/addons/lines/Line2.js';
import { LineGeometry } from 'three/addons/lines/LineGeometry.js';
import { LineMaterial } from 'three/addons/lines/LineMaterial.js';

export const W = 1920, H = 1080;
export const EXAG = 4.5;              // 垂直夸张（辽西多平原丘陵，比黔北夸张更多）
const LON_C = 121.75, LAT_C = 41.55;  // 投影中心（main 区域中心）
const KX = 111.32 * Math.cos(LAT_C * Math.PI / 180), KZ = 110.57;

export function toWorld(lon, lat, lift = 0) {
  return new THREE.Vector3((lon - LON_C) * KX, heightAt(lon, lat) + lift, -(lat - LAT_C) * KZ);
}
export function toLonLat(x, z) {
  return [x / KX + LON_C, -z / KZ + LAT_C];
}

const grids = {};   // name -> {meta, data:Uint16Array}

function sampleGrid(g, lon, lat) {
  const m = g.meta;
  if (lon < m.lon0 || lon > m.lon1 || lat < m.lat0 || lat > m.lat1) return null;
  const fx = (lon - m.lon0) / (m.lon1 - m.lon0) * (m.gw - 1);
  const fy = (m.lat1 - lat) / (m.lat1 - m.lat0) * (m.gh - 1);
  const x0 = Math.floor(fx), y0 = Math.floor(fy), x1 = Math.min(x0 + 1, m.gw - 1), y1 = Math.min(y0 + 1, m.gh - 1);
  const ax = fx - x0, ay = fy - y0, d = g.data, gw = m.gw;
  const v = (d[y0 * gw + x0] * (1 - ax) + d[y0 * gw + x1] * ax) * (1 - ay) + (d[y1 * gw + x0] * (1 - ax) + d[y1 * gw + x1] * ax) * ay;
  return (m.hmin + v / 65535 * (m.hmax - m.hmin)) / 1000 * EXAG;
}

// 多级地形：精细层优先，macro（东北—华北全域）兜底
const LEVELS = [['main', 0], ['wide', -0.35], ['macro', -0.8]];
export function heightAt(lon, lat) {
  for (const [name] of LEVELS) {
    const h = grids[name] && sampleGrid(grids[name], lon, lat);
    if (h != null) return h;
  }
  return 0.0;
}

async function loadGrid(name) {
  const meta = await (await fetch(`../assets/terrain/${name}.json`)).json();
  const data = new Uint16Array(await (await fetch(`../assets/terrain/${name}_h.bin`)).arrayBuffer());
  grids[name] = { meta, data };
  return grids[name];
}

function terrainMesh(g, tex, yOffset) {
  const m = g.meta;
  const geo = new THREE.BufferGeometry();
  const n = m.gw * m.gh, pos = new Float32Array(n * 3), uv = new Float32Array(n * 2);
  for (let j = 0; j < m.gh; j++) {
    for (let i = 0; i < m.gw; i++) {
      const k = j * m.gw + i;
      const lon = m.lon0 + (m.lon1 - m.lon0) * i / (m.gw - 1), lat = m.lat1 - (m.lat1 - m.lat0) * j / (m.gh - 1);
      pos[k * 3] = (lon - LON_C) * KX;
      pos[k * 3 + 1] = (m.hmin + g.data[k] / 65535 * (m.hmax - m.hmin)) / 1000 * EXAG + yOffset;
      pos[k * 3 + 2] = -(lat - LAT_C) * KZ;
      uv[k * 2] = i / (m.gw - 1);
      uv[k * 2 + 1] = 1 - j / (m.gh - 1);
    }
  }
  const idx = new Uint32Array((m.gw - 1) * (m.gh - 1) * 6);
  let p = 0;
  for (let j = 0; j < m.gh - 1; j++) {
    for (let i = 0; i < m.gw - 1; i++) {
      const a = j * m.gw + i, b = a + 1, c = a + m.gw, d = c + 1;
      idx[p++] = a; idx[p++] = c; idx[p++] = b; idx[p++] = b; idx[p++] = c; idx[p++] = d;
    }
  }
  geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  geo.setAttribute('uv', new THREE.BufferAttribute(uv, 2));
  geo.setIndex(new THREE.BufferAttribute(idx, 1));
  tex.colorSpace = THREE.SRGBColorSpace;
  tex.anisotropy = 8;
  const mat = new THREE.MeshBasicMaterial({ map: tex, transparent: true });
  mat.userData.baseOpacity = 1;
  return new THREE.Mesh(geo, mat);
}

export async function createWorld(canvas) {
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, preserveDrawingBuffer: true });
  renderer.setPixelRatio(1);
  renderer.setSize(W, H, false);
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  const scene = new THREE.Scene();
  scene.background = new THREE.Color('#1b1a17');
  scene.fog = new THREE.Fog('#1b1a17', 400, 1400);
  const camera = new THREE.PerspectiveCamera(32, W / H, 1, 12000);
  const loader = new THREE.TextureLoader();
  const loaded = await Promise.all(LEVELS.map(([name]) => Promise.all([loadGrid(name), loader.loadAsync(`../assets/terrain/${name}_tex.jpg`)])));
  const terrain = {};
  LEVELS.forEach(([name, off], i) => {
    const mesh = terrainMesh(loaded[i][0], loaded[i][1], off);
    mesh.renderOrder = LEVELS.length - i;
    terrain[name] = mesh;
    scene.add(mesh);
  });
  return { renderer, scene, camera, terrain };
}

// ---------- 相机：target 经纬度 + 距离/俯仰/方位 ----------
export function setCamera(camera, { lon, lat, dist, pitch, heading }) {
  const tgt = new THREE.Vector3((lon - LON_C) * KX, heightAt(lon, lat) * 0.6, -(lat - LAT_C) * KZ);
  const p = pitch * Math.PI / 180, h = heading * Math.PI / 180;
  camera.position.set(tgt.x + dist * Math.cos(p) * Math.sin(h), tgt.y + dist * Math.sin(p), tgt.z + dist * Math.cos(p) * Math.cos(h));
  camera.up.set(0, 1, 0);
  camera.lookAt(tgt);
  camera.updateMatrixWorld();
}

// ---------- 贴地线 ----------
export function densify(lonlats, stepKm = 0.8) {
  const out = [];
  for (let i = 0; i < lonlats.length - 1; i++) {
    const [a, b] = [lonlats[i], lonlats[i + 1]];
    const d = Math.hypot((b[0] - a[0]) * KX, (b[1] - a[1]) * KZ);
    const n = Math.max(1, Math.ceil(d / stepKm));
    for (let k = 0; k < n; k++) out.push([a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n]);
  }
  out.push(lonlats[lonlats.length - 1]);
  return out;
}

// 平滑折线（Catmull-Rom），用于行军路线
export function smoothPath(lonlats, samples = 12) {
  if (lonlats.length < 3) return lonlats;
  const v = lonlats.map(([lo, la]) => new THREE.Vector3((lo - LON_C) * KX, 0, -(la - LAT_C) * KZ));
  const curve = new THREE.CatmullRomCurve3(v, false, 'centripetal', 0.5);
  return curve.getPoints((lonlats.length - 1) * samples).map(p => toLonLat(p.x, p.z));
}

export function cumulative(lonlats) {
  const c = [0];
  for (let i = 1; i < lonlats.length; i++) {
    c.push(c[i - 1] + Math.hypot((lonlats[i][0] - lonlats[i - 1][0]) * KX, (lonlats[i][1] - lonlats[i - 1][1]) * KZ));
  }
  return c;
}

export function makeLine(color, widthPx, opts = {}) {
  const mat = new LineMaterial({
    color, linewidth: widthPx, transparent: true, opacity: 1, depthTest: opts.depthTest ?? false,
    dashed: !!opts.dashed, dashSize: opts.dashSize ?? 3, gapSize: opts.gapSize ?? 2, worldUnits: false,
  });
  mat.resolution.set(W, H);
  const line = new Line2(new LineGeometry(), mat);
  line.renderOrder = opts.renderOrder ?? 10;
  line.frustumCulled = false;
  return line;
}

// 把线设为 lonlats 的前 frac 部分（按长度）
export function setLinePartial(line, pts, cum, frac, lift = 0.25) {
  const total = cum[cum.length - 1], L = total * Math.max(0, Math.min(1, frac));
  const arr = [];
  let tip = null, dir = null;
  for (let i = 0; i < pts.length; i++) {
    if (cum[i] <= L) { const w = toWorld(pts[i][0], pts[i][1], lift); arr.push(w.x, w.y, w.z); tip = w; continue; }
    const a = pts[i - 1], b = pts[i], f = (L - cum[i - 1]) / (cum[i] - cum[i - 1] || 1);
    const w = toWorld(a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f, lift);
    arr.push(w.x, w.y, w.z);
    tip = w;
    break;
  }
  if (arr.length < 6) { line.visible = false; return null; }
  line.visible = true;
  line.geometry.dispose();
  line.geometry = new LineGeometry();
  line.geometry.setPositions(arr);
  if (line.material.dashed) line.computeLineDistances();
  const n = arr.length;
  dir = new THREE.Vector3(arr[n - 3] - arr[n - 6], arr[n - 2] - arr[n - 5], arr[n - 1] - arr[n - 4]);
  return { tip, dir };
}

// 世界坐标 → 屏幕像素
const _v = new THREE.Vector3();
export function project(camera, p) {
  _v.copy(p).project(camera);
  return { x: (_v.x + 1) / 2 * W, y: (1 - _v.y) / 2 * H, visible: _v.z < 1 && Math.abs(_v.x) < 1.3 && Math.abs(_v.y) < 1.3 };
}

export { THREE };
