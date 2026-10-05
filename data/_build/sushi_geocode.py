"""用 OSM Nominatim 核验苏轼行踪地点的今址坐标，结果缓存到 data/_build/cache/sushi/nominatim/。
用法：python3 data/_build/sushi_geocode.py          # 查询 QUERIES 中全部条目（已缓存的跳过）
输出：data/_build/cache/sushi/geocode_result.json   # {key: {lat, lon, osm, display}}
遵守 Nominatim 使用政策：带 User-Agent、≤1 次/秒、结果缓存；用 curl 规避 Python 证书问题。
"""
import json
import subprocess
import time
import urllib.parse
from pathlib import Path

CACHE = Path(__file__).resolve().parent / 'cache' / 'sushi' / 'nominatim'
OUT = CACHE.parent / 'geocode_result.json'
UA = 'lives-doc-research/0.1 (documentary data prep; low volume)'
PAUSE_S = 1.2

# key -> 今地名查询串（古地名取学界公认今址）
QUERIES: dict[str, str] = {
    'meishan': '东坡区, 眉山市', 'chengdu': '成都市', 'langzhong': '阆中市',
    'baoxie': '褒河镇, 汉中', 'fengxiang': '凤翔区, 宝鸡', 'changan': '西安市',
    'mianchi': '渑池县', 'kaifeng': '开封市', 'jiazhou': '乐山市', 'rongzhou': '宜宾市',
    'yuzhou': '渝中区, 重庆', 'zhongzhou': '忠县', 'kuizhou': '奉节县', 'xiazhou': '宜昌市',
    'jiangling': '荆州区, 荆州市', 'xiangyang': '襄阳市', 'zhengzhou': '郑州市',
    'zhouzhi': '周至县', 'chenzhou': '淮阳区', 'yingzhou': '颍州区, 阜阳', 'shouzhou': '寿县',
    'haozhou': '凤阳县', 'chuzhou': '淮安区, 淮安', 'yangzhou': '扬州市', 'runzhou': '镇江市',
    'hangzhou': '杭州市', 'huzhou': '湖州市', 'changzhou': '常州市', 'suzhou': '苏州市',
    'haizhou': '海州区, 连云港', 'mizhou': '诸城市', 'weizhou': '潍城区, 潍坊', 'qingzhou': '青州市',
    'jinan': '济南市', 'xuzhou': '徐州市', 'sizhou': '盱眙县', 'wuxi': '无锡市',
    'caizhou': '汝南县', 'qiting': '岐亭镇, 麻城', 'huangzhou': '黄州区, 黄冈', 'lushan': '庐山',
    'yunzhou': '高安市', 'hukou': '湖口县', 'jinling': '南京市', 'zhenzhou': '仪征市',
    'nandu': '睢阳区, 商丘', 'dengzhou': '蓬莱区, 烟台', 'laizhou': '莱州市', 'dingzhou': '定州市',
    'lincheng': '临城县', 'ruzhou': '汝州市', 'ganzhou': '赣州市', 'dayuling': '梅关',
    'guangzhou': '广州市', 'huizhou': '惠州市', 'tengzhou': '藤县', 'leizhou': '雷州市',
    'qiongzhou': '琼山区, 海口', 'danzhou': '中和镇, 儋州', 'lianzhou': '合浦县', 'shaozhou': '韶关市',
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
