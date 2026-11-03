// HUD：片名、身份卡、年份/纪年、事件条、人生进度条、里程碑卡、章节卡、字幕、片尾
import { clamp01, win } from './mapfx.js';
import { kmAt } from './journey.js';
import { kmBetween } from './engine.js';
import { parseStepId } from './person.js';

const hud = () => document.getElementById('hud');
function mk(cls, html = '') {
  const d = document.createElement('div');
  d.className = cls;
  d.innerHTML = html;
  hud().appendChild(d);
  return d;
}
const show = (d, op, tf = '') => {
  d.style.display = op > 0.005 ? '' : 'none';
  d.style.opacity = op;
  if (tf) d.style.transform = tf;
};
const easeOut = x => 1 - Math.pow(1 - clamp01(x), 3);
const esc = s => String(s).replace(/[&<>]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]));
const CONF = { documented: ['史载', 'c-doc'], inferred: ['推断', 'c-inf'], traditional: ['传说', 'c-tra'] };
const parse = parseStepId;

export function makeHud(person, data, places, tl, journey) {
  const steps = data.steps, stages = data.stages;
  const stageOf = Object.fromEntries(stages.map(s => [s.id, s]));
  const [by] = parse(steps[0].id);
  const n = steps.length;

  // 片名
  const title = mk('title-card', `<div class="nm">${esc(person.name)}</div><div class="life">${esc(person.life)}</div><div class="tag">${esc(person.tagline)}</div>`);
  // 身份卡 + 年份
  // 左上角压成三行：姓名 · 阶段 / 纪年 / 年份 + 半年 + 年龄（生卒年已在片名和进度条两端）
  const idc = mk('idcard', `<b>${esc(person.name)}</b><span class="stage"></span>`);
  const stageEl = idc.querySelector('.stage');
  const year = mk('year', '<div class="era"></div><div class="row"><b class="y"></b><span class="h"></span><span class="age"></span></div>');
  const [eraEl, yEl, hEl, ageEl] = ['.era', '.y', '.h', '.age'].map(s => year.querySelector(s));
  const stats = mk('stats', '<div><b class="km"></b><em>累计行程（公里）</em></div><div><b class="np"></b><em>足迹所至</em></div>');
  const [kmEl, npEl] = ['.km', '.np'].map(s => stats.querySelector(s));
  // 事件条
  const ev = mk('event', '<i class="badge"></i><span class="tx"></span><em class="pl"></em>');
  const [evBadge, evTx, evPl] = ['.badge', '.tx', '.pl'].map(s => ev.querySelector(s));
  // 进度条
  const BAR_W = 1700;
  const bar = mk('lifebar', `<div class="track">${stages.map(s => {
    const a = steps.findIndex(x => x.stage === s.id), b = steps.length - 1 - [...steps].reverse().findIndex(x => x.stage === s.id);
    const w = (b - a + 1) / n * BAR_W;
    // 太短的阶段放不下名字：不显示（章节卡和身份卡里仍有阶段名）
    return `<div class="seg" style="left:${a / n * BAR_W}px;width:${w}px"><span>${w >= s.title.length * 17 + 12 ? esc(s.title) : ''}</span></div>`;
  }).join('')}</div>${steps.map((s, i) => s.milestone ? `<i class="tick${s.milestone.importance === 1 ? ' big' : ''}" style="left:${(i + 0.5) / n * BAR_W}px"></i>` : '').join('')}
    <div class="cursor"></div><div class="fill"></div><span class="y0">${steps[0].id.replace(/H\d/, '')}</span><span class="y1">${steps[n - 1].id.replace(/H\d/, '')}</span>`);
  const cursor = bar.querySelector('.cursor'), fill = bar.querySelector('.fill');
  const segEls = [...bar.querySelectorAll('.seg')], ticks = [...bar.querySelectorAll('.tick')];
  const msIdx = steps.map((s, i) => s.milestone ? i : -1).filter(i => i >= 0);
  // 里程碑卡
  const card = mk('mscard', '<div class="when"></div><h2></h2><div class="where"></div><p class="msub"></p><blockquote></blockquote>');
  const [cWhen, cH, cWhere, cSub, cQ] = ['.when', 'h2', '.where', '.msub', 'blockquote'].map(s => card.querySelector(s));
  // 章节卡
  const chap = mk('chapter', '<div class="no"></div><div class="ti"></div><div class="bar"></div><div class="dt"></div><div class="sm"></div>');
  const [chNo, chTi, chBar, chDt, chSm] = ['.no', '.ti', '.bar', '.dt', '.sm'].map(s => chap.querySelector(s));
  // 字幕
  const sub = mk('sub');
  // 片尾
  // 足迹去重：同一地点改名时 places.json 用 same_as 指向原键（如草山/阳明山），只算一处
  const spot = k => places[k].same_as || k;
  const placesSeen = new Set(journey.arrivals.map(a => spot(a.key)));
  const end = mk('endcard', `<div class="nm">${esc(person.name)}</div><div class="life">${esc(person.life)}</div>
    <div class="nums"><div><b>${(Math.round(journey.totalKm / 100) * 100).toLocaleString('en-US')}</b><em>公里行程（直线距离累计）</em></div><div><b>${placesSeen.size}</b><em>处足迹</em></div><div><b>${msIdx.length}</b><em>个人生节点</em></div></div>
    <div class="src">史料：${data.meta.sources.filter(s => s.kind === 'primary' || s.kind === 'scholarly').slice(0, 6).map(s => esc(s.title)).join(' · ')}</div>
    <div class="note">地图仅示意地形与行迹，不表示任何行政或国家界线<br>卫星影像：EOxCloudless by EOX IT Services GmbH（含经修改的 Copernicus Sentinel 2022 数据）· 高程：AWS Terrain Tiles</div>`);
  const flash = mk('flash');

  let lastStep = -1, lastCh = null, lastMs = null;
  return (t, ctx) => {
    const { stepIdx: i, inTitle, chapter, ms } = ctx;
    const st = steps[i], [y, h] = parse(st.id);
    // 片名卡
    show(title, win(t, tl.title.t0, tl.title.t1 + 0.3, 0.8), `translateY(${(1 - easeOut((t - tl.title.t0) / 1.2)) * 20}px)`);
    const mainOp = clamp01((t - tl.intro.t0 - 0.3) / 0.8) * (1 - clamp01((t - tl.end.t0) / 0.8));
    const lifeOp = clamp01((t - tl.steps[0].t0 + 0.4) / 0.6) * mainOp;
    // 身份卡 / 年份 / 统计
    show(idc, mainOp);
    stageEl.textContent = t >= tl.steps[0].t0 ? stageOf[st.stage].title : '';
    show(year, lifeOp);
    if (i !== lastStep) {
      eraEl.textContent = i === 0 && person.birth ? person.birth.era : person.era(y, h);
      yEl.textContent = `${y}`;
      hEl.textContent = h === 1 ? '上半年' : '下半年';
      ageEl.textContent = i === 0 && person.birth ? person.birth.age : person.age(y, h);
      const [lab, cls] = CONF[st.confidence];
      evBadge.textContent = lab;
      evBadge.className = `badge ${cls}`;
      evTx.textContent = st.event;
      lastStep = i;
    }
    // 里程碑讲解期间显示停留地点，其余时候显示本半年的终点
    const stopKey = st.milestone?.place && !(tl.steps[i].after && t > tl.steps[i].after.t0) ? st.milestone.place : st.places[st.places.length - 1];
    if (evPl.dataset.k !== stopKey) {
      const end = places[stopKey];
      evPl.textContent = `📍 ${end.name}${end.modern && end.modern !== end.name ? `（今${end.modern}）` : ''}`;
      evPl.dataset.k = stopKey;
    }
    year.classList.toggle('pulse', t - tl.steps[i].t0 < 0.25);
    show(stats, lifeOp);
    const np = new Set();
    for (const a of journey.arrivals) if (a.t <= t) np.add(spot(a.key));
    kmEl.textContent = Math.round(kmAt(journey, t)).toLocaleString('en-US');
    npEl.textContent = np.size;
    // 里程碑卡与事件条内容重复：卡片在时事件条完全让开
    show(ev, lifeOp * (chapter ? 0 : 1) * (1 - (ms ? win(t, ms.t0 - 0.3, ms.t1 + 0.3, 0.5) : 0)));
    // 进度条
    show(bar, lifeOp);
    const stepT = tl.steps[i], frac = (i + clamp01((t - stepT.t0) / (stepT.t1 - stepT.t0))) / n;
    cursor.style.transform = `translateX(${(frac * BAR_W).toFixed(1)}px)`;
    fill.style.width = `${(frac * BAR_W).toFixed(1)}px`;
    const stIdx = stages.findIndex(s => s.id === st.stage);
    segEls.forEach((e, k) => e.classList.toggle('on', k === stIdx));
    ticks.forEach((e, k) => { e.classList.toggle('done', msIdx[k] <= i); e.classList.toggle('now', ms && msIdx[k] === i); });
    // 里程碑卡
    if (ms) {
      if (lastMs !== i) {
        const m = st.milestone, pl = places[m.place || st.places[st.places.length - 1]];
        const b0 = i === 0 && person.birth;
        cWhen.textContent = [`${y} 年${h === 1 ? '上半年' : '下半年'}`, b0 ? b0.era : person.era(y, h), b0 ? b0.age : person.age(y, h)].filter(Boolean).join(' · ');
        cH.textContent = m.title;
        // 远途里程碑显示“起点 → 事件地”（未指定 place 时为终点）；起点与事件地相距不到 50 km（同城往返）或非远途时显示停留地点
        const p0 = places[st.places[0]], p1 = pl;
        cWhere.textContent = tl.steps[i].ms.travel && kmBetween([p0.lon, p0.lat], [p1.lon, p1.lat]) > 50 ? `${p0.name} → ${p1.name}（今${p1.modern}）`
          : `${pl.name}${pl.modern && pl.modern !== pl.name ? ` · 今${pl.modern}` : ''}`;
        cSub.textContent = m.subtitle || '';
        cQ.innerHTML = m.quote ? `${esc(m.quote.text)}<cite>—— ${esc(m.quote.source)}</cite>` : '';
        cQ.style.display = m.quote ? '' : 'none';
        card.classList.toggle('lv1', m.importance === 1);
        card.classList.toggle('long', m.title.length > 6);
        lastMs = i;
      }
      const k = win(t, ms.t0, ms.t1, 0.6);
      show(card, k, `translateX(${(1 - easeOut((t - ms.t0) / 0.8)) * 60}px)`);
      show(flash, Math.max(0, 0.5 - (t - ms.t0) * 1.2) * (t >= ms.t0 ? 1 : 0));
    } else { show(card, 0); show(flash, 0); }
    // 章节卡
    if (chapter) {
      if (lastCh !== chapter.stage) {
        const s = stageOf[chapter.stage], k = stages.indexOf(s);
        chNo.textContent = `第 ${'一二三四五六七八'[k]} 章`;
        chTi.textContent = s.title;
        chDt.textContent = `${s.from.replace(/H1/, ' 上半年').replace(/H2/, ' 下半年')} — ${s.to.replace(/H1/, ' 上半年').replace(/H2/, ' 下半年')}`;
        chSm.textContent = s.summary || '';
        lastCh = chapter.stage;
      }
      const k = win(t, chapter.t0, chapter.t1, 0.45);
      show(chap, k);
      chBar.style.width = `${easeOut((t - chapter.t0) / 1.2) * 520}px`;
    } else show(chap, 0);
    // 字幕
    const c = tl.subs.find(([a, b]) => t >= a && t < b);
    if (c && !inTitle) {
      if (sub.textContent !== c[2]) sub.textContent = c[2];
      show(sub, Math.min(clamp01((t - c[0]) / 0.15), clamp01((c[1] - t) / 0.12)));
    } else show(sub, 0);
    // 片尾
    show(end, win(t, tl.end.t0, tl.total + 5, 0.9));
  };
}
