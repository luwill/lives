// 3D 地形引擎：多级地形网格、经纬度↔世界坐标、动态垂直夸张、贴地线、屏幕投影
// 世界单位 = km；地形高度按 km 存入网格，mesh.scale.y = 垂直夸张倍数
import * as THREE from 'three';
import { Line2 } from 'three/addons/lines/Line2.js';
import { LineGeometry } from 'three/addons/lines/LineGeometry.js';
import { LineMaterial } from 'three/addons/lines/LineMaterial.js';

export const W = 1920, H = 1080;
const LON_C = 108, LAT_C = 32;        // 全国统一投影中心
const KX = 111.32 * Math.cos(LAT_C * Math.PI / 180), KZ = 110.57;
let EXAG = 6;

export const getExag = () => EXAG;
export function lonLatToXZ(lon, lat) { return [(lon - LON_C) * KX, -(lat - LAT_C) * KZ]; }
export function toWorld(lon, lat, lift = 0) {
  return new THREE.Vector3((lon - LON_C) * KX, heightAt(lon, lat) + lift, -(lat - LAT_C) * KZ);
}

const grids = [];   // [{name, meta, data, off}]，精细层在前

function sampleGrid(g, lon, lat) {
  const m = g.meta;
  if (lon < m.lon0 || lon > m.lon1 || lat < m.lat0 || lat > m.lat1) return null;
  const fx = (lon - m.lon0) / (m.lon1 - m.lon0) * (m.gw - 1);
  const fy = (m.lat1 - lat) / (m.lat1 - m.lat0) * (m.gh - 1);
  const x0 = Math.floor(fx), y0 = Math.floor(fy), x1 = Math.min(x0 + 1, m.gw - 1), y1 = Math.min(y0 + 1, m.gh - 1);
  const ax = fx - x0, ay = fy - y0, d = g.data, gw = m.gw;
  const v = (d[y0 * gw + x0] * (1 - ax) + d[y0 * gw + x1] * ax) * (1 - ay) + (d[y1 * gw + x0] * (1 - ax) + d[y1 * gw + x1] * ax) * ay;
  return (m.hmin + v / 65535 * (m.hmax - m.hmin)) / 1000;
}

// 当前夸张倍数下的地面高度（世界单位）
export function heightAt(lon, lat) {
  for (const g of grids) {
    const h = sampleGrid(g, lon, lat);
    if (h != null) return (h + g.off) * EXAG;
  }
  return 0;
}

async function loadGrid(name) {
  const meta = await (await fetch(`../assets/terrain/${name}.json`)).json();
  const data = new Uint16Array(await (await fetch(`../assets/terrain/${name}_h.bin`)).arrayBuffer());
  return { name, meta, data };
}

// holes：更精细各层的范围。粗层落在其内（向内缩两格）的顶点压到地下，
// 否则粗层平滑过的谷底比精细层高，会从深谷里“冒”出来
function terrainMesh(g, tex, order, holes = []) {
  const m = g.meta;
  const mx = 2 * (m.lon1 - m.lon0) / (m.gw - 1), my = 2 * (m.lat1 - m.lat0) / (m.gh - 1);
  const inHole = (lon, lat) => holes.some(h => lon > h.lon0 + mx && lon < h.lon1 - mx && lat > h.lat0 + my && lat < h.lat1 - my);
  const geo = new THREE.BufferGeometry();
  const n = m.gw * m.gh, pos = new Float32Array(n * 3), uv = new Float32Array(n * 2);
  for (let j = 0; j < m.gh; j++) {
    for (let i = 0; i < m.gw; i++) {
      const k = j * m.gw + i;
      const lon = m.lon0 + (m.lon1 - m.lon0) * i / (m.gw - 1), lat = m.lat1 - (m.lat1 - m.lat0) * j / (m.gh - 1);
      pos[k * 3] = (lon - LON_C) * KX;
      pos[k * 3 + 1] = inHole(lon, lat) ? -50 : (m.hmin + g.data[k] / 65535 * (m.hmax - m.hmin)) / 1000 + g.off;
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
  tex.generateMipmaps = true;
  // 粗层整体后推，避免与精细层争深度
  const mat = new THREE.MeshBasicMaterial({ map: tex, polygonOffset: order > 0, polygonOffsetFactor: order * 2, polygonOffsetUnits: order * 8 });
  const mesh = new THREE.Mesh(geo, mat);
  mesh.frustumCulled = false;
  return mesh;
}

// levels: [[name, offsetKm], ...] 精细层在前
export async function createWorld(canvas, levels) {
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, preserveDrawingBuffer: true });
  renderer.setPixelRatio(1);
  renderer.setSize(W, H, false);
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  const scene = new THREE.Scene();
  scene.background = new THREE.Color('#141a20');
  scene.fog = new THREE.Fog('#141a20', 4000, 16000);
  const camera = new THREE.PerspectiveCamera(32, W / H, 2, 40000);
  const loader = new THREE.TextureLoader();
  const loaded = await Promise.all(levels.map(([name]) => Promise.all([loadGrid(name), loader.loadAsync(`../assets/terrain/${name}_tex.jpg`)])));
  const meshes = [];
  levels.forEach(([, off], i) => {
    const g = loaded[i][0];
    g.off = off;
    grids.push(g);
    const mesh = terrainMesh(g, loaded[i][1], i, loaded.slice(0, i).map(l => l[0].meta));
    mesh.renderOrder = -i;
    meshes.push(mesh);
    scene.add(mesh);
  });
  return { renderer, scene, camera, meshes };
}

export function setExag(world, e) {
  EXAG = e;
  for (const m of world.meshes) m.scale.y = e;
}

// ---------- 相机：target 经纬度 + 距离/俯仰/方位 ----------
export function setCamera(camera, { lon, lat, dist, pitch, heading }) {
  const tgt = new THREE.Vector3((lon - LON_C) * KX, heightAt(lon, lat) * 0.7, -(lat - LAT_C) * KZ);
  const p = pitch * Math.PI / 180, h = heading * Math.PI / 180;
  camera.position.set(tgt.x + dist * Math.cos(p) * Math.sin(h), tgt.y + dist * Math.sin(p), tgt.z + dist * Math.cos(p) * Math.cos(h));
  camera.up.set(0, 1, 0);
  camera.lookAt(tgt);
  camera.near = Math.max(1, dist * 0.02);
  camera.far = dist * 12 + 2000;
  camera.updateProjectionMatrix();
  camera.updateMatrixWorld();
}

// ---------- 线 ----------
export function makeLine(color, widthPx, opts = {}) {
  const mat = new LineMaterial({ color, linewidth: widthPx, transparent: true, opacity: opts.opacity ?? 1, depthTest: false, worldUnits: false,
    vertexColors: !!opts.vertexColors });
  mat.resolution.set(W, H);
  const line = new Line2(new LineGeometry(), mat);
  line.renderOrder = opts.renderOrder ?? 10;
  line.frustumCulled = false;
  return line;
}

// 用经纬度点列（贴地 + lift）设置线几何；少于 2 点则隐藏。colors：可选逐点 RGB（线性空间，长度 = 点数 × 3）
export function setLinePts(line, lonlats, lift, colors = null) {
  if (lonlats.length < 2) { line.visible = false; return; }
  const arr = new Float32Array(lonlats.length * 3);
  lonlats.forEach(([lo, la], i) => {
    arr[i * 3] = (lo - LON_C) * KX;
    arr[i * 3 + 1] = heightAt(lo, la) + lift;
    arr[i * 3 + 2] = -(la - LAT_C) * KZ;
  });
  line.visible = true;
  line.geometry.dispose();
  line.geometry = new LineGeometry();
  line.geometry.setPositions(arr);
  if (colors) line.geometry.setColors(colors);
}

// 世界坐标 → 屏幕像素
const _v = new THREE.Vector3();
export function project(camera, p) {
  _v.copy(p).project(camera);
  return { x: (_v.x + 1) / 2 * W, y: (1 - _v.y) / 2 * H, front: _v.z < 1, visible: _v.z < 1 && Math.abs(_v.x) < 1.15 && Math.abs(_v.y) < 1.15 };
}

export function kmBetween(a, b) {
  const R = 6371, r = Math.PI / 180;
  const dlat = (b[1] - a[1]) * r, dlon = (b[0] - a[0]) * r;
  const h = Math.sin(dlat / 2) ** 2 + Math.cos(a[1] * r) * Math.cos(b[1] * r) * Math.sin(dlon / 2) ** 2;
  return 2 * R * Math.asin(Math.sqrt(h));
}

export { THREE };
