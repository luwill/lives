"""诸葛亮行踪地点的今址核验：逐条查询 OSM Nominatim，结果缓存到 data/_build/cache/nominatim/。
用法：python3 data/_build/geocode_zhuge.py [key ...]
- 限速：每次网络请求后 sleep 1.1 秒（Nominatim 使用政策 ≤1 次/秒），带 User-Agent。
- 用 curl 发请求（避免本机 Python 缺 CA 证书的问题）。
- 只打印候选结果，最终坐标由 places.json 人工确认填写（古城址需结合考证）。
"""
import hashlib
import json
import subprocess
import sys
import time
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CACHE = ROOT / 'data' / '_build' / 'cache' / 'nominatim'
UA = 'lives-documentary-data/1.0 (historical geocoding; contact: local research script)'
ENDPOINT = 'https://nominatim.openstreetmap.org/search'

# key -> 查询串（今地名）
QUERIES = {
    'yangdu': '砖埠镇, 沂南县',
    'yinan': '沂南县',
    'nanchang': '南昌市',
    'xiangyang': '襄城区, 襄阳市',
    'longzhong': '古隆中',
    'wolonggang': '武侯祠, 卧龙区, 南阳市',
    'xinye': '新野县',
    'fancheng': '樊城区',
    'dangyang': '长坂坡',
    'dangyang_city': '当阳市',
    'xiakou': '汉阳区, 武汉市',
    'chaisang': '柴桑区',
    'chibi': '赤壁古战场',
    'chibi_city': '赤壁市',
    'linzheng': '衡阳市',
    'gongan': '公安县',
    'baidi': '白帝城',
    'jiangzhou': '渝中区',
    'chengdu': '成都市',
    'xichang': '西昌市',
    'lazha': '拉鲊',
    'huili': '会理市',
    'jinning': '晋城街道, 晋宁区',
    'dianchi': '滇池',
    'mianxian': '勉县',
    'qishan': '祁山镇, 礼县',
    'qishanbao': '祁山堡',
    'sanguan': '大散关',
    'chencang': '陈仓区',
    'xihe': '西和县',
    'chenggu': '城固县',
    'yangxian': '洋县',
    'shanggui': '秦州区, 天水市',
    'lucheng': '盐官镇, 礼县',
    'huangsha': '黄沙镇, 勉县',
    'xiegu': '斜峪关',
    'meixian': '眉县',
    'wuzhangyuan': '五丈原镇',
    'wuzhangyuan2': '五丈原',
    'dingjunshan': '定军山镇',
    'wuhoumu': '武侯墓, 勉县',
    'yangdu2': '砖埠镇',
    'yangdu3': '诸葛亮故里',
    'wolonggang2': '卧龙岗',
    'dangyang2': '长坂坡公园',
    'huangsha2': '黄沙镇',
    'guishan': '龟山, 汉阳区',
    'longting': '龙亭镇, 洋县',
    'wuzhangyuan3': '诸葛亮庙, 岐山县',
    'mianyang_old': '武侯镇, 勉县',
    'huangsha3': '黄沙, 汉中市',
    'dangyang3': '长坂坡, 当阳市',
    'dangyang4': '玉阳街道, 当阳市',
    'nanchang_old': '东湖区, 南昌市',
    'hengyang_old': '石鼓区, 衡阳市',
    'tianshui_xixian': '红河镇, 礼县',
}


def cache_path(q: str) -> Path:
    return CACHE / (hashlib.sha1(q.encode()).hexdigest()[:16] + '.json')


def query(q: str) -> list:
    p = cache_path(q)
    if p.exists():
        return json.loads(p.read_text())['results']
    url = ENDPOINT + '?' + urllib.parse.urlencode(
        {'q': q, 'format': 'jsonv2', 'limit': 3, 'accept-language': 'zh', 'countrycodes': 'cn'})
    out = subprocess.run(['curl', '-sS', '--max-time', '30', '-A', UA, url],
                         capture_output=True, text=True, check=False)
    time.sleep(1.1)
    if out.returncode != 0:
        raise RuntimeError(f'curl failed for {q!r}: {out.stderr.strip()}')
    try:
        res = json.loads(out.stdout)
    except json.JSONDecodeError as e:
        raise RuntimeError(f'non-JSON response for {q!r}: {out.stdout[:200]}') from e
    CACHE.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({'query': q, 'results': res}, ensure_ascii=False, indent=1))
    return res


def main(keys: list[str]) -> None:
    for k in keys or QUERIES:
        q = QUERIES[k]
        try:
            res = query(q)
        except RuntimeError as e:
            print(f'{k}\tERROR\t{e}')
            continue
        if not res:
            print(f'{k}\t{q}\t(no result)')
        for r in res[:2]:
            print(f"{k}\t{q}\t{float(r['lat']):.4f},{float(r['lon']):.4f}\t"
                  f"{r['osm_type']} {r['osm_id']}\t{r.get('display_name', '')[:70]}")


if __name__ == '__main__':
    main(sys.argv[1:])
