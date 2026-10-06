// 人物配置：显示信息、轨迹配色、地形层级、纪年、时代政区注记（无边界，仅文字）
const NUM = '〇一二三四五六七八九';
export function cnNum(n) {
  if (n === 1) return '元';
  if (n < 10) return NUM[n];
  if (n < 20) return '十' + (n % 10 ? NUM[n % 10] : '');
  return NUM[Math.floor(n / 10)] + '十' + (n % 10 ? NUM[n % 10] : '');
}

// 年号表：[年号, 元年(公元), 生效半年序号 year*2+half-1]；同一半年内改元时取占多数月份的年号
const idx = (y, h) => y * 2 + h - 1;
function eraFrom(table, prefix) {
  return (y, h) => {
    const k = idx(y, h);
    let e = null;
    for (const row of table) if (k >= row[2]) e = row;
    return e ? `${prefix(e)}${e[0]}${cnNum(y - e[1] + 1)}年` : '';
  };
}

// 年龄：古人按虚岁（农历出生年记为一岁），近人按周岁（以半年中点 4/1、10/1 计）
const xusui = lunarBirthYear => (y) => `虚岁 ${y - lunarBirthYear + 1}`;
const zhousui = (by, bm, bd) => (y, h) => {
  const [m, d] = h === 1 ? [4, 1] : [10, 1];
  return `${Math.max(0, y - by - (m < bm || (m === bm && d < bd) ? 1 : 0))} 岁`;
};

export const PEOPLE = {
  mao: {
    age: zhousui(1893, 12, 26),
    name: '毛泽东', life: '1893 — 1976', tagline: '一个人的八十二年 · 半年一步', color: '#e8473a', glow: '#ff8a5c',
    levels: [['east', 0], ['china', -0.06], ['world', -0.15]],
    era: (y, h) => {
      if (y < 1909) return `清 · 光绪${cnNum(y - 1874)}年`;
      if (y < 1912) return `清 · 宣统${cnNum(y - 1908)}年`;
      if (y < 1949 || (y === 1949 && h === 1)) return `民国${cnNum(y - 1911)}年`;
      return '中华人民共和国';
    },
    regions: [],
  },
  zhuge: {
    age: xusui(181),
    name: '诸葛亮', life: '181 — 234', tagline: '鞠躬尽瘁 · 半年一步', color: '#4fc1b0', glow: '#9ff0e2',
    levels: [['east', 0], ['china', -0.06], ['world', -0.15]],
    era: eraFrom([
      ['光和', 178, idx(181, 1)], ['中平', 184, idx(185, 1)], ['初平', 190, idx(190, 1)], ['兴平', 194, idx(194, 1)],
      ['建安', 196, idx(196, 1)], ['章武', 221, idx(221, 1)], ['建兴', 223, idx(223, 2)],
    ], e => (e[1] >= 221 ? '蜀汉 · ' : '东汉 · ')),
    // 章武元年四月刘备即位：221H1 按事件记为章武元年
    regions: [
      { name: '曹 魏', lon: 114.2, lat: 35.2, from: idx(220, 2) },
      { name: '蜀 汉', lon: 104.6, lat: 30.9, from: idx(221, 1) },
      { name: '孙 吴', lon: 117.8, lat: 28.4, from: idx(222, 2) },
    ],
  },
  sushi: {
    age: xusui(1036),   // 生于景祐三年十二月（农历 1036 年）
    birth: { era: '北宋 · 景祐三年', age: '虚岁 1' },   // 出生一步按生日所在的农历年显示
    name: '苏轼', life: '1037 — 1101', tagline: '一蓑烟雨任平生 · 半年一步', color: '#f0b84a', glow: '#ffe2a0',
    levels: [['east', 0], ['china', -0.06], ['world', -0.15]],
    era: eraFrom([
      ['景祐', 1034, idx(1037, 1)], ['宝元', 1038, idx(1039, 1)], ['康定', 1040, idx(1040, 1)], ['庆历', 1041, idx(1042, 1)],
      ['皇祐', 1049, idx(1049, 1)], ['至和', 1054, idx(1054, 1)], ['嘉祐', 1056, idx(1056, 2)], ['治平', 1064, idx(1064, 1)],
      ['熙宁', 1068, idx(1068, 1)], ['元丰', 1078, idx(1078, 1)], ['元祐', 1086, idx(1086, 1)], ['绍圣', 1094, idx(1094, 2)],
      ['元符', 1098, idx(1098, 2)], ['建中靖国', 1101, idx(1101, 1)],
    ], () => '北宋 · '),
    regions: [
      { name: '辽', lon: 118.5, lat: 43.6, from: 0 },
      { name: '西 夏', lon: 105.6, lat: 38.9, from: 0 },
      { name: '大 理', lon: 100.4, lat: 25.4, from: 0 },
    ],
  },
};
