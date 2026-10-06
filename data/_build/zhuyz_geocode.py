"""用 OSM Nominatim 核验朱元璋行踪地点的今址坐标，结果缓存到 data/_build/cache/zhuyz/nominatim/。
用法：python3 data/_build/zhuyz_geocode.py          # 查询 QUERIES 中全部条目（已缓存的跳过）
输出：data/_build/cache/zhuyz/geocode_result.json   # {key: {lat, lon, osm, display}}
遵守 Nominatim 使用政策：带 User-Agent、≤1 次/秒、结果缓存；用 curl 规避 Python 证书问题。
"""
import json
import subprocess
import time
import urllib.parse
from pathlib import Path

CACHE = Path(__file__).resolve().parent / 'cache' / 'zhuyz' / 'nominatim'
OUT = CACHE.parent / 'geocode_result.json'
UA = 'lives-doc-research/0.1 (documentary data prep; low volume)'
PAUSE_S = 1.2

# key -> 今地名查询串（古地名取学界公认今址）
QUERIES: dict[str, str] = {
    'zhongli': '明皇陵, 凤阳县', 'dongxiang': '小溪河镇, 凤阳县', 'haozhou': '临淮关镇, 凤阳县', 'zhongdu': '府城镇, 凤阳县',
    'hefei': '合肥市', 'luan': '六安市', 'guangzhou': '潢川县', 'gushi': '固始县',
    'ruzhou': '汝州市', 'yingzhou': '颍州区, 阜阳市', 'dingyuan': '定远县',
    'chuzhou': '琅琊区, 滁州市', 'liuhe': '六合区, 南京市',
    'chaohu': '巢湖', 'hezhou': '和县', 'caishi': '翠螺山', 'taiping': '姑孰镇, 当涂县',
    'yingtian': '南京市', 'zhenjiang': '镇江市', 'ningguo': '宣州区, 宣城市',
    'wuzhou': '婺城区, 金华市', 'longwan': '阅江楼', 'anqing': '迎江区, 安庆市',
    'hukou': '双钟镇, 湖口县', 'jiangzhou': '浔阳区, 九江市', 'hongdu': '东湖区, 南昌市', 'anfeng': '寿县',
    'kanglangshan': '康山, 余干县', 'zuoli': '左里镇, 都昌县', 'wuchang': '武昌区, 武汉市',
    'kaifeng': '龙亭区, 开封市', 'xiaoling': '明孝陵',
}


def query(q: str) -> list[dict]:
    url = ('https://nominatim.openstreetmap.org/search?format=jsonv2&limit=3&accept-language=zh'
           f'&countrycodes=cn&q={urllib.parse.quote(q)}')
    out = subprocess.run(['curl', '-s', '-A', UA, url], capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def main() -> None:
    CACHE.mkdir(parents=True, exist_ok=True)
    result = {}
    for key, q in QUERIES.items():
        p = CACHE / f'{key}.json'
        if not p.exists():
            p.write_text(json.dumps(query(q), ensure_ascii=False))
            time.sleep(PAUSE_S)
        hits = json.loads(p.read_text())
        if not hits:
            print('NO HIT', key, q)
            continue
        h = hits[0]
        result[key] = {'q': q, 'lat': round(float(h['lat']), 4), 'lon': round(float(h['lon']), 4),
                       'osm': f"{h['osm_type']} {h['osm_id']}", 'type': h.get('type'),
                       'display': h.get('display_name', '')[:80]}
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=1))
    for k, v in result.items():
        print(k, v['lat'], v['lon'], v['osm'], v['type'], v['display'])


if __name__ == '__main__':
    main()
