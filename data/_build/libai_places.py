"""李白行踪地点 → data/libai/places.json。坐标取自 libai_geocode.py 的 Nominatim 缓存结果。
用法：python3 data/_build/libai_places.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GEO = Path(__file__).resolve().parent / 'cache' / 'libai' / 'geocode_result.json'
OUT = ROOT / 'data' / 'libai' / 'places.json'

# key: (name, modern, kind, confidence, geocode_key, note)
SPEC: dict[str, tuple] = {
    'suiye': ('碎叶', '吉尔吉斯斯坦托克马克西南阿克·贝希姆古城', 'city', 'medium', 'suiye',
              '唐安西都护府碎叶镇城，学界多定于阿克·贝希姆遗址（托克马克西南约8km）；坐标取该村，为出生地主说'),
    'changlong': ('绵州昌隆·青莲乡', '四川江油青莲镇', 'village', 'high', 'changlong',
                  '唐绵州昌隆县（先天元年避讳改昌明）清廉乡，今江油市青莲镇，有李白故里'),
    'kuangshan': ('大匡山（戴天山）', '四川江油大康镇匡山', 'mountain', 'medium', 'kuangshan2',
                  '匡山书院所在；Nominatim 无山体条目，取大康镇匡山隧道，与山体相距数公里'),
    'chengdu': ('益州·成都', '四川成都', 'city', 'high', 'chengdu', None),
    'emei': ('峨眉山', '四川峨眉山金顶', 'mountain', 'high', 'emei2', None),
    'yuzhou': ('渝州', '重庆渝中区', 'city', 'high', 'yuzhou', '唐渝州治巴县，今重庆渝中半岛'),
    'baidi': ('白帝城', '重庆奉节白帝城', 'city', 'high', 'baidi', '夔州奉节县东白帝山上'),
    'wushan': ('巫山', '重庆巫山县', 'town', 'high', 'wushan', '唐夔州巫山县'),
    'huangniu': ('黄牛峡', '湖北宜昌夷陵区黄陵庙', 'pass', 'medium', 'huangniu',
                 '西陵峡中黄牛岩下，黄陵庙即古黄牛庙'),
    'jingmen': ('荆门', '湖北宜都（荆门山）', 'mountain', 'low', 'jingmen_alt',
                '荆门山在宜都西北长江南岸，与虎牙山相对；Nominatim 未检得山体，取宜都市行政中心，偏差约10km'),
    'jiangling': ('江陵', '湖北荆州荆州区', 'city', 'high', 'jiangling', '唐荆州江陵府治，今荆州古城'),
    'yuezhou': ('巴陵·洞庭', '湖南岳阳（岳阳楼）', 'city', 'high', 'yuezhou', '唐岳州巴陵县，临洞庭湖'),
    'lushan': ('庐山', '江西九江庐山牯岭', 'mountain', 'high', 'lushan', '屏风叠在五老峰下，距牯岭约5km'),
    'jinling': ('金陵', '江苏南京', 'city', 'high', 'jinling', '唐润州江宁县/上元县，六朝故都'),
    'yangzhou': ('扬州（广陵）', '江苏扬州', 'city', 'high', 'yangzhou', None),
    'anlu': ('安陆', '湖北安陆', 'city', 'high', 'anlu', '唐安州治安陆县；寿山、白兆山桃花岩均在县境'),
    'jiangxia': ('江夏（黄鹤楼）', '湖北武汉武昌', 'city', 'high', 'jiangxia', '唐鄂州治江夏县，黄鹤楼在城西黄鹄矶'),
    'changan': ('长安', '陕西西安', 'city', 'high', 'changan', None),
    'zhongnan': ('终南山', '陕西西安南终南山', 'mountain', 'medium', 'zhongnan',
                 '玉真公主别馆所在的终南山楼观一带，具体位置不详，取终南山主峰'),
    'binzhou': ('邠州', '陕西彬州', 'city', 'high', 'binzhou', None),
    'fangzhou': ('坊州', '陕西黄陵县', 'city', 'high', 'fangzhou', '唐坊州治中部县，今黄陵县'),
    'songzhou': ('宋州·梁园', '河南商丘睢阳区', 'city', 'high', 'songzhou', '唐宋州宋城县；梁孝王梁园（兔园）故地'),
    'kaifeng': ('汴州（梁）', '河南开封', 'city', 'high', 'kaifeng', None),
    'songshan': ('嵩山', '河南登封嵩山', 'mountain', 'high', 'songshan', '元丹丘嵩山山居；坐标取太室山连天峰'),
    'luoyang': ('洛阳', '河南洛阳', 'city', 'high', 'luoyang', None),
    'nanyang': ('南阳', '河南南阳', 'city', 'high', 'nanyang', None),
    'suizhou': ('随州', '湖北随州', 'city', 'high', 'suizhou', '道士胡紫阳所居'),
    'xiangyang': ('襄阳', '湖北襄阳', 'city', 'high', 'xiangyang', '唐襄州治襄阳县'),
    'taiyuan': ('太原', '山西太原晋源区', 'city', 'high', 'taiyuan', '唐太原府治晋阳，今晋源区古城营一带'),
    'yanmen': ('雁门关', '山西代县雁门关', 'pass', 'high', 'yanmen', None),
    'chenzhou': ('陈州', '河南周口淮阳区', 'city', 'high', 'chenzhou', None),
    'chuzhou': ('楚州', '江苏淮安淮安区', 'city', 'high', 'chuzhou', '唐楚州治山阳县'),
    'anyi': ('安宜', '江苏宝应', 'town', 'high', 'anyi', '唐楚州安宜县，上元三年改宝应'),
    'suzhou': ('吴郡·苏州', '江苏苏州', 'city', 'high', 'suzhou', None),
    'dangtu': ('当涂', '安徽马鞍山当涂县', 'city', 'high', 'dangtu', '唐宣州当涂县（姑孰）；李白墓在县东南青山'),
    'yanzhou': ('东鲁·兖州', '山东济宁兖州区', 'city', 'high', 'yanzhou', '唐兖州（鲁郡）治瑕丘，李白寓家所在'),
    'rencheng': ('任城', '山东济宁任城区', 'city', 'high', 'rencheng', None),
    'culai': ('徂徕山', '山东泰安徂徕山', 'mountain', 'high', 'culai', '竹溪六逸隐居处'),
    'taishan': ('泰山', '山东泰安泰山玉皇顶', 'mountain', 'high', 'taishan2', None),
    'jizhou': ('齐州', '山东济南', 'city', 'high', 'jizhou', '紫极宫受道箓处，天宝五载改济南郡'),
    'kuaiji': ('会稽（越州）', '浙江绍兴越城区', 'city', 'high', 'kuaiji', None),
    'tiantai': ('天台山', '浙江天台县', 'mountain', 'medium', 'tiantai_alt', '取天台县城，距主峰华顶约15km'),
    'lujiang': ('庐江', '安徽庐江县', 'city', 'high', 'lujiang', None),
    'yexian': ('叶县石门山', '河南叶县', 'mountain', 'low', 'yexian', '元丹丘石门山居具体位置不详，取叶县县城'),
    'weijun': ('魏郡', '河北大名县', 'city', 'medium', 'weijun', '唐魏州治贵乡，在今大名县东北'),
    'guangping': ('广平郡', '河北邯郸永年区', 'city', 'high', 'guangping', '唐洺州（广平郡）治永年'),
    'youzhou': ('幽州（范阳）', '北京西城区', 'city', 'high', 'youzhou', '唐幽州城在今北京西城区西南广安门一带'),
    'fenyang': ('西河郡', '山西汾阳', 'city', 'high', 'fenyang', '唐汾州（西河郡）治西河县，今汾阳'),
    'huashan': ('华山', '陕西华阴华山', 'mountain', 'high', 'huashan_alt', '取华阴市，距华山主峰约10km'),
    'liyang': ('历阳·横江', '安徽和县', 'city', 'high', 'liyang', '唐和州历阳县，横江浦在县东南江岸'),
    'xuancheng': ('宣城', '安徽宣城宣州区', 'city', 'high', 'xuancheng', '唐宣州治宣城县'),
    'jingting': ('敬亭山', '安徽宣城敬亭山', 'mountain', 'high', 'jingting', None),
    'qiupu': ('秋浦', '安徽池州贵池区', 'town', 'high', 'qiupu', '唐池州秋浦县，今贵池'),
    'shanzhong': ('剡中', '浙江嵊州', 'town', 'high', 'shanzhong', '唐越州剡县'),
    'xunyang': ('浔阳', '江西九江浔阳区', 'city', 'high', 'xunyang', '唐江州治浔阳县；李白系浔阳狱处'),
    'pengze': ('彭泽', '江西彭泽县', 'town', 'medium', 'pengze', '唐彭泽县治在今县境，今县城为后移'),
    'runzhou': ('丹阳（润州）', '江苏镇江', 'city', 'high', 'runzhou', '润州丹阳郡治丹徒，永王兵败于此'),
    'susong': ('宿松', '安徽宿松县', 'town', 'high', 'susong', None),
    'ezhou': ('武昌', '湖北鄂州', 'town', 'high', 'ezhou', '唐鄂州武昌县，今鄂州市'),
    'yuzhang': ('豫章', '江西南昌', 'city', 'high', 'yuzhang', '唐洪州（豫章郡）治钟陵，宗氏寓居处'),
}


def build() -> dict:
    geo = json.loads(GEO.read_text())
    out = {}
    for key, (name, modern, kind, conf, gk, note) in SPEC.items():
        g = geo[gk]
        rec = {'name': name, 'modern': modern, 'lat': g['lat'], 'lon': g['lon'], 'kind': kind,
               'confidence': conf, 'source': f"OSM Nominatim {g['osm']}（查询：{g['q']}）"}
        if note:
            rec['note'] = note
        out[key] = rec
    return out


if __name__ == '__main__':
    OUT.write_text(json.dumps(build(), ensure_ascii=False, indent=1))
    print(OUT, len(SPEC))
