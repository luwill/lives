// 帧渲染入口：window.renderAt(t) —— 纯时间函数（相机查表、叠加层按 t 计算）
import { createWorld, setCamera, setExag } from './engine.js';
import { makePerson, parseStepId } from './person.js';
import { buildJourney, stepIndexAt } from './journey.js';
import { buildCamera } from './camera.js';
import { makeTrail, makeMarkers } from './mapfx.js';
import { makeHud } from './hud.js';

const who = new URLSearchParams(location.search).get('who');
if (!who || !/^[a-z0-9_]+$/.test(who)) throw new Error(`bad person key: ${who}`);

const getJson = async url => {
  const r = await fetch(url);
  if (!r.ok) throw new Error(`fetch ${url}: ${r.status}`);
  return r.json();
};
const [cfg, data, places, tl, geo] = await Promise.all([
  getJson(`../data/${who}/person.json`),
  getJson(`../data/${who}/steps.json`), getJson(`../data/${who}/places.json`),
  getJson(`${who}/timeline.json`), getJson('../data/common/labels.json'),
]);
const person = makePerson(cfg);
document.title = `${person.name} · 人生轨迹`;

const world = await createWorld(document.getElementById('gl'), person.levels);
const journey = buildJourney(data.steps, tl.steps, places);
const camAt = buildCamera(tl, journey);
const trail = makeTrail(world.scene, journey, person, tl);
const markers = makeMarkers(person, data, places, journey, tl, geo.labels);
const hud = makeHud(person, data, places, tl, journey);
const fade = document.getElementById('fade');
const labelsEl = document.getElementById('labels');

// 垂直夸张：近景 3.5 倍，全国俯瞰 14 倍
const exagFor = zoom => 3.5 + 10.5 * zoom * zoom;

window.renderAt = t => {
  const cam = camAt(t);
  setExag(world, exagFor(cam.zoom));
  setCamera(world.camera, cam);
  world.scene.fog.near = cam.dist * 1.6;
  world.scene.fog.far = cam.dist * 5;
  const stepIdx = stepIndexAt(tl.steps, t);
  const [y, h] = parseStepId(data.steps[stepIdx].id);
  const s = tl.steps[stepIdx];
  const ms = s.ms && t >= s.t0 && t <= s.t1 + 0.6 ? s.ms : null;
  const chapter = tl.chapters.find(c => t >= c.t0 && t < c.t1) || null;
  const inTitle = t < tl.title.t1;
  const beforeLife = t < tl.steps[0].t0;
  const ctx = { stepIdx, halfIdx: +y * 2 + +h - 1, ms, chapter, inTitle, hideMap: beforeLife };
  trail(beforeLife ? -1 : t, cam, t > tl.end.t0 ? 1 - Math.min(1, (t - tl.end.t0) / 1.5) * 0.4 : 1);
  markers(t, world.camera, cam, ctx);
  // 章节卡、片尾卡出现时，地图注记淡出
  const cover = Math.max(chapter ? Math.min(1, (t - chapter.t0) / 0.45, (chapter.t1 - t) / 0.45) : 0, Math.min(1, Math.max(0, (t - tl.end.t0) / 0.9)));
  labelsEl.style.opacity = 1 - cover;
  world.renderer.render(world.scene, world.camera);
  hud(t, ctx);
  // 片头片尾淡入淡出
  fade.style.opacity = Math.max(1 - Math.min(1, t / 0.8), Math.min(1, Math.max(0, (t - (tl.total - 1.5)) / 1.2)));
};
window.TOTAL = tl.total;
window.ready = true;
