"""朱元璋行踪地点 → data/zhuyz/places.json。
坐标来自 zhuyz_geocode.py 的 Nominatim 缓存（cache/zhuyz/geocode_result.json）；
SPEC 里写当时称谓、今地名、类别、可信度与考证说明。
用法：python3 data/_build/zhuyz_geocode.py && python3 data/_build/zhuyz_places.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GEO = Path(__file__).resolve().parent / 'cache' / 'zhuyz' / 'geocode_result.json'
OUT = ROOT / 'data' / 'zhuyz' / 'places.json'

# key: (name 当时称谓, modern 今地名, kind, confidence, geocode 键, note)
SPEC: dict[str, tuple[str, str, str, str, str, str]] = {
    'dongxiang': ('钟离东乡', '安徽凤阳县小溪河镇（燃灯寺村一带）', 'village', 'medium', 'dongxiang',
                  '《皇陵碑记》太祖自述“居鍾離之東鄉，而朕生焉”；维基百科「朱元璋」定为今小溪河镇燃灯寺村，'
                  'OSM 无该村点位，取小溪河镇政区坐标'),
    'guzhuang': ('太平乡孤庄村', '安徽凤阳县（明皇陵一带）', 'village', 'medium', 'zhongli',
                 '《皇陵碑记》：十年后迁钟离西乡，再迁太平乡孤庄村；父母即葬于同里刘大秀（《明史》作刘继祖）'
                 '所与之地，即今明皇陵。村落今址无公认定点，取明皇陵坐标；西乡今址亦不详，一并以此代表'),
    'huangjue': ('皇觉寺', '安徽凤阳县（於皇寺原址，明皇陵附近）', 'village', 'low', 'zhongli',
                 '《皇陵碑记》称“里之皇觉寺”，即同乡之寺；原寺毁于元末兵火，洪武十六年另建龙兴寺于凤阳城北，'
                 '原址无确切定点，暂取明皇陵坐标'),
    'haozhou': ('濠州', '安徽凤阳县临淮关镇', 'city', 'medium', 'haozhou',
                '元濠州治钟离县，城址在今凤阳县东北临淮关一带（明初移治中都）'),
    'hefei': ('合肥', '安徽合肥', 'city', 'high', 'hefei', '元庐州路治合肥；《皇陵碑记》作“南历金斗”'),
    'luan': ('六安', '安徽六安', 'city', 'medium', 'luan',
             '合肥西行至光州的必经之地；史书未明载其到六安，为路线推断'),
    'guangzhou': ('光州', '河南潢川县', 'city', 'high', 'guangzhou', '元光州治定城，即今潢川'),
    'gushi': ('固始', '河南固始县', 'city', 'high', 'gushi', ''),
    'ruzhou': ('汝州', '河南汝州', 'city', 'high', 'ruzhou', ''),
    'yingzhou': ('颍州', '安徽阜阳颍州区', 'city', 'high', 'yingzhou', '元颍州治汝阴，即今阜阳'),
    'dingyuan': ('定远', '安徽定远县', 'city', 'high', 'dingyuan',
                 '驴牌寨（定远张家堡）、横涧山均在定远境内，具体位置无公认今址，以县城代表'),
    'chuzhou': ('滁州', '安徽滁州琅琊区', 'city', 'high', 'chuzhou', ''),
    'liuhe': ('六合（瓦梁垒）', '江苏南京六合区', 'battle', 'medium', 'liuhe',
              '瓦梁垒在六合附近，确切位置不详，取六合城区'),
    'chaohu': ('巢湖', '安徽巢湖', 'lake', 'medium', 'chaohu', '取湖面中心；廖永安、俞通海水军原泊巢湖'),
    'hezhou': ('和州', '安徽和县', 'city', 'high', 'hezhou', '又称和阳'),
    'caishi': ('采石', '安徽马鞍山采石矶（翠螺山）', 'battle', 'high', 'caishi',
               '牛渚矶即采石矶，在翠螺山临江处'),
    'taiping': ('太平', '安徽当涂县姑孰镇', 'city', 'high', 'taiping', '元太平路治当涂（姑孰），改太平府'),
    'yingtian': ('应天（集庆）', '江苏南京', 'city', 'high', 'yingtian',
                 '元集庆路，至正十六年改应天府，洪武元年称南京；1356 年以前不出现于行程'),
    'zhenjiang': ('镇江', '江苏镇江', 'city', 'high', 'zhenjiang', ''),
    'ningguo': ('宁国', '安徽宣城宣州区', 'city', 'high', 'ningguo', '元宁国路治宣城，非今宁国市'),
    'wuzhou': ('婺州', '浙江金华婺城区', 'city', 'high', 'wuzhou', '克后改宁越府，后称金华府'),
    'longwan': ('龙湾（卢龙山）', '江苏南京狮子山（阅江楼）', 'battle', 'medium', 'longwan',
                '太祖“亲督军卢龙山”，卢龙山即今狮子山；龙湾在其西北江岸，取阅江楼代表'),
    'anqing': ('安庆', '安徽安庆迎江区', 'city', 'high', 'anqing', ''),
    'hukou': ('湖口', '江西湖口县', 'city', 'high', 'hukou', '鄱阳湖入江口'),
    'jiangzhou': ('江州', '江西九江', 'city', 'high', 'jiangzhou', '元江州路治德化，即今九江'),
    'hongdu': ('洪都（龙兴）', '江西南昌', 'city', 'high', 'hongdu', '元龙兴路，至正二十二年改洪都府'),
    'anfeng': ('安丰', '安徽寿县', 'city', 'high', 'anfeng', '元安丰路治寿春，即今寿县'),
    'kanglangshan': ('康郎山', '江西余干县康山', 'battle', 'medium', 'kanglangshan',
                     '鄱阳湖东南湖中之山，今余干县康山乡；取乡政区坐标'),
    'zuoli': ('左蠡', '江西都昌县左里镇', 'battle', 'medium', 'zuoli', '鄱阳湖西北岸，太祖移军扼左蠡'),
    'wuchang': ('武昌', '湖北武汉武昌区', 'city', 'high', 'wuchang', ''),
    'kaifeng': ('汴梁', '河南开封', 'city', 'high', 'kaifeng', '洪武元年八月以开封为北京'),
    'zhongdu': ('中都', '安徽凤阳县府城镇（明中都皇故城）', 'city', 'high', 'zhongdu',
                '洪武二年以临濠为中都，营建于凤阳城北；八年罢营'),
    'xiaoling': ('孝陵', '江苏南京钟山明孝陵', 'mountain', 'high', 'xiaoling', '洪武十五年马皇后先葬于此'),
}


def build() -> dict:
    geo = json.loads(GEO.read_text())
    out = {}
    for key, (name, modern, kind, conf, gkey, note) in SPEC.items():
        g = geo[gkey]
        rec = {'name': name, 'modern': modern, 'lat': g['lat'], 'lon': g['lon'], 'kind': kind,
               'confidence': conf, 'source': f"OSM Nominatim {g['osm']}（查询：{g['q']}）"}
        if note:
            rec['note'] = note
        out[key] = rec
    return out


if __name__ == '__main__':
    OUT.parent.mkdir(parents=True, exist_ok=True)
    places = build()
    OUT.write_text(json.dumps(places, ensure_ascii=False, indent=1) + '\n')
    print(f'{len(places)} places -> {OUT}')
