// 人物配置（data/<who>/person.json）→ 运行时对象：年龄、纪年、政权注记、地形层
const NUM = '〇一二三四五六七八九';
export function cnNum(n) {
  if (!Number.isInteger(n) || n < 1 || n > 199) throw new Error('cnNum out of range: ' + n);
  if (n >= 100) {
    const r = n - 100;
    if (r === 0) return '一百';
    if (r < 10) return '一百〇' + NUM[r];
    return '一百' + NUM[Math.floor(r / 10)] + '十' + (r % 10 ? NUM[r % 10] : '');
  }
  if (n === 1) return '元';
  if (n < 10) return NUM[n];
  if (n < 20) return '十' + (n % 10 ? NUM[n % 10] : '');
  return NUM[Math.floor(n / 10)] + '十' + (n % 10 ? NUM[n % 10] : '');
}

// 步 id "-221H2" → [-221, 2]（年可为负：公元前）
export function parseStepId(id) {
  const m = /^(-?\d+)H([12])$/.exec(id);
  if (!m) throw new Error(`bad step id: ${id}`);
  return [+m[1], +m[2]];
}

// "744H1" → 半年序号 744*2+0
export function halfIdx(key) {
  const m = /^(-?\d+)H([12])$/.exec(key);
  if (!m) throw new Error(`bad half-year key: ${key}`);
  return +m[1] * 2 + +m[2] - 1;
}

// 共享高清层（z10，约 150 m/像素，卫星底色），同级按先后让位；再往下是粗层
const HI = [['zhuge_hi', 0], ['hi_north', 0], ['hi_east', 0], ['hi_south', 0]];
const BASE = [['east', -0.03], ['china', -0.06], ['world', -0.15]];

// 年龄：古人按虚岁（农历出生年记为一岁），近人按周岁（以半年中点 4/1、10/1 计）
function ageFn(a) {
  if (a.kind === 'xusui') return y => `虚岁 ${y - a.lunar_birth_year + 1}`;
  if (a.kind === 'zhousui') {
    const [by, bm, bd] = a.birth.split('-').map(Number);
    return (y, h) => {
      const [m, d] = h === 1 ? [4, 1] : [10, 1];
      return `${Math.max(0, y - by - (m < bm || (m === bm && d < bd) ? 1 : 0))} 岁`;
    };
  }
  throw new Error(`unknown age kind: ${a.kind}`);
}

// 纪年：年号表取最后一个已生效的行；覆盖规则命中时整串替换，{n:Y} → cnNum(当年 − Y + 1)
function eraFn(rows, overrides = []) {
  const table = rows.map(([prefix, name, first, eff]) => ({ prefix, name, first, k: halfIdx(eff) }));
  const ovs = overrides.map(o => ({ a: o.from ? halfIdx(o.from) : -Infinity, b: o.to ? halfIdx(o.to) : Infinity, t: o.template }));
  return (y, h) => {
    const k = y * 2 + h - 1;
    const o = ovs.find(v => k >= v.a && k <= v.b);
    if (o) return o.t.replace(/\{n:(-?\d+)\}/g, (_, base) => cnNum(y - +base + 1));
    let e = null;
    for (const r of table) if (k >= r.k) e = r;
    return e ? `${e.prefix}${e.name}${cnNum(y - e.first + 1)}年` : '';
  };
}

export function makePerson(cfg) {
  return {
    name: cfg.name, life: cfg.life, tagline: cfg.tagline, color: cfg.color, glow: cfg.glow,
    birth: cfg.birth_override || undefined,
    age: ageFn(cfg.age),
    era: eraFn(cfg.eras, cfg.era_overrides),
    regions: (cfg.regions || []).map(r => ({
      name: r.name, lon: r.lon, lat: r.lat,
      from: r.from ? halfIdx(r.from) : -Infinity, to: r.to ? halfIdx(r.to) : Infinity,
    })),
    levels: [...HI, ...(cfg.extra_levels || []), ...BASE],
  };
}
