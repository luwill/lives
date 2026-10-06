"""用 OSM Nominatim 核验李白行踪地点今址坐标，结果缓存到 data/_build/cache/libai/nominatim/。
用法：python3 data/_build/libai_geocode.py     # 已缓存的跳过
输出：data/_build/cache/libai/geocode_result.json   # {key: {q, lat, lon, osm, type, display}}
遵守 Nominatim 使用政策：带 User-Agent、≤1 次/秒、结果缓存；用 curl 子进程。
"""
import json
import subprocess
import time
import urllib.parse
from pathlib import Path

CACHE = Path(__file__).resolve().parent / 'cache' / 'libai' / 'nominatim'
OUT = CACHE.parent / 'geocode_result.json'
UA = 'lives-doc-research/0.1 (documentary data prep; low volume)'
PAUSE_S = 1.2

# key -> (今地名查询串, 国家代码)
QUERIES: dict[str, tuple[str, str]] = {
    'suiye': ('Ak-Beshim', 'kg'), 'suiye_tokmok': ('Tokmok', 'kg'),
    'changlong': ('青莲镇, 江油市', 'cn'), 'kuangshan': ('大匡山', 'cn'), 'kuangshan_alt': ('大康镇, 江油市', 'cn'),
    'chengdu': ('成都市', 'cn'), 'emei': ('峨眉山', 'cn'), 'yuzhou': ('渝中区, 重庆', 'cn'),
    'baidi': ('白帝城, 奉节县', 'cn'), 'wushan': ('巫山县', 'cn'), 'huangniu': ('黄陵庙, 宜昌', 'cn'),
    'jingmen': ('荆门山, 宜都', 'cn'), 'jingmen_alt': ('宜都市', 'cn'), 'jiangling': ('荆州区, 荆州市', 'cn'),
    'yuezhou': ('岳阳楼', 'cn'), 'lushan': ('牯岭镇', 'cn'), 'jinling': ('南京市', 'cn'),
    'yangzhou': ('扬州市', 'cn'), 'anlu': ('安陆市', 'cn'), 'baizhao': ('白兆山', 'cn'),
    'jiangxia': ('黄鹤楼', 'cn'), 'changan': ('西安市', 'cn'), 'zhongnan': ('终南山', 'cn'),
    'binzhou': ('彬州市', 'cn'), 'fangzhou': ('黄陵县', 'cn'), 'songzhou': ('睢阳区, 商丘市', 'cn'),
    'kaifeng': ('开封市', 'cn'), 'songshan': ('嵩山', 'cn'), 'luoyang': ('洛阳市', 'cn'),
    'nanyang': ('南阳市', 'cn'), 'suizhou': ('随州市', 'cn'), 'xiangyang': ('襄阳市', 'cn'),
    'taiyuan': ('晋源区, 太原市', 'cn'), 'yanmen': ('雁门关', 'cn'), 'chenzhou': ('淮阳区, 周口市', 'cn'),
    'chuzhou': ('淮安区, 淮安市', 'cn'), 'anyi': ('宝应县', 'cn'), 'suzhou': ('苏州市', 'cn'),
    'dangtu': ('当涂县', 'cn'), 'yanzhou': ('兖州区, 济宁市', 'cn'), 'rencheng': ('任城区, 济宁市', 'cn'),
    'culai': ('徂徕山', 'cn'), 'taishan': ('泰山', 'cn'), 'jizhou': ('济南市', 'cn'),
    'kuaiji': ('越城区, 绍兴市', 'cn'), 'tiantai': ('天台山', 'cn'), 'tiantai_alt': ('天台县', 'cn'),
    'lujiang': ('庐江县', 'cn'), 'yexian': ('叶县', 'cn'), 'weijun': ('大名县', 'cn'),
    'guangping': ('永年区, 邯郸市', 'cn'), 'youzhou': ('西城区, 北京市', 'cn'), 'fenyang': ('汾阳市', 'cn'),
    'huashan': ('华山', 'cn'), 'huashan_alt': ('华阴市', 'cn'), 'liyang': ('和县', 'cn'),
    'xuancheng': ('宣州区, 宣城市', 'cn'), 'jingting': ('敬亭山', 'cn'), 'qiupu': ('贵池区, 池州市', 'cn'),
    'shanzhong': ('嵊州市', 'cn'), 'xunyang': ('浔阳区, 九江市', 'cn'), 'pengze': ('彭泽县', 'cn'),
    'runzhou': ('镇江市', 'cn'), 'susong': ('宿松县', 'cn'), 'ezhou': ('鄂州市', 'cn'),
    'yuzhang': ('南昌市', 'cn'), 'jiangyou': ('江油市', 'cn'),
    'kuangshan2': ('匡山, 江油', 'cn'), 'jingmen2': ('荆门山', 'cn'), 'tiantai2': ('华顶', 'cn'),
    'huashan2': ('华山, 华阴', 'cn'), 'taishan2': ('玉皇顶, 泰安', 'cn'), 'emei2': ('金顶, 峨眉山', 'cn'),
    'lushan2': ('庐山', 'cn'), 'pingfengdie': ('屏风叠', 'cn'),
}


def query(q: str, cc: str) -> list[dict]:
    url = ('https://nominatim.openstreetmap.org/search?format=jsonv2&limit=3&accept-language=zh'
           f'&countrycodes={cc}&q={urllib.parse.quote(q)}')
    out = subprocess.run(['curl', '-s', '--max-time', '30', '-A', UA, url],
                         capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def main() -> None:
    CACHE.mkdir(parents=True, exist_ok=True)
    result = {}
    for key, (q, cc) in QUERIES.items():
        p = CACHE / f'{key}.json'
        if not p.exists():
            try:
                p.write_text(json.dumps(query(q, cc), ensure_ascii=False))
            except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
                print('ERROR', key, q, e)
            time.sleep(PAUSE_S)
        hits = json.loads(p.read_text()) if p.exists() else []
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
