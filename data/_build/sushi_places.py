"""由 Nominatim 缓存结果 + 古今地名对照，生成 data/sushi/places.json。
先运行 sushi_geocode.py，再运行本脚本：python3 data/_build/sushi_places.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GEO = ROOT / 'data' / '_build' / 'cache' / 'sushi' / 'geocode_result.json'
OUT = ROOT / 'data' / 'sushi' / 'places.json'

# key: (当时称谓, 今地名, kind, confidence, note)
META: dict[str, tuple[str, str, str, str, str]] = {
    'meishan': ('眉山', '四川眉山东坡区', 'city', 'high', '宋眉州治眉山县，今眉山市东坡区；纱縠行故居即今三苏祠'),
    'chengdu': ('成都', '四川成都', 'city', 'high', ''),
    'langzhong': ('阆中', '四川阆中', 'city', 'high', ''),
    'baoxie': ('褒斜道', '陕西汉中石门（褒谷口）', 'pass', 'medium',
               '褒斜道南口褒谷口石门，今为石门水库；取谷口代表整条栈道'),
    'fengxiang': ('凤翔', '陕西宝鸡凤翔区', 'city', 'high', '宋凤翔府治天兴县，即今凤翔区'),
    'changan': ('长安', '陕西西安', 'city', 'high', '宋京兆府'),
    'mianchi': ('渑池', '河南渑池', 'town', 'high', ''),
    'kaifeng': ('汴京', '河南开封', 'city', 'high', '北宋东京开封府'),
    'jiazhou': ('嘉州', '四川乐山', 'city', 'high', ''),
    'rongzhou': ('戎州', '四川宜宾', 'city', 'high', ''),
    'yuzhou': ('渝州', '重庆渝中', 'city', 'high', '宋恭州（旧称渝州），苏轼诗题仍称渝州'),
    'zhongzhou': ('忠州', '重庆忠县', 'city', 'high', ''),
    'kuizhou': ('夔州', '重庆奉节', 'city', 'high', '白帝城、永安宫、八阵碛均在奉节'),
    'xiazhou': ('峡州', '湖北宜昌', 'city', 'high', '治夷陵县，即今宜昌'),
    'jiangling': ('江陵', '湖北荆州荆州区', 'city', 'high', '宋江陵府（荆州）'),
    'xiangyang': ('襄阳', '湖北襄阳', 'city', 'high', ''),
    'zhengzhou': ('郑州', '河南郑州', 'city', 'high', ''),
    'zhouzhi': ('盩厔', '陕西西安周至县', 'town', 'high', '楼观、仙游潭所在'),
    'chenzhou': ('陈州', '河南周口淮阳区', 'city', 'high', '宛丘，苏辙时任陈州学官'),
    'yingzhou': ('颍州', '安徽阜阳颍州区', 'city', 'high', '汝阴，欧阳修致仕居此'),
    'shouzhou': ('寿州', '安徽寿县', 'city', 'high', ''),
    'haozhou': ('濠州', '安徽滁州凤阳县', 'city', 'medium', '宋濠州治钟离县，在今凤阳县临淮关一带；坐标取凤阳县'),
    'chuzhou': ('楚州', '江苏淮安淮安区', 'city', 'high', '治山阳县'),
    'yangzhou': ('扬州', '江苏扬州', 'city', 'high', '广陵'),
    'runzhou': ('润州', '江苏镇江', 'city', 'high', '金山、焦山、甘露寺所在'),
    'hangzhou': ('杭州', '浙江杭州', 'city', 'high', ''),
    'huzhou': ('湖州', '浙江湖州', 'city', 'high', '吴兴'),
    'changzhou': ('常州', '江苏常州', 'city', 'high', '毗陵；宜兴（阳羡）属常州'),
    'suzhou': ('苏州', '江苏苏州', 'city', 'high', ''),
    'haizhou': ('海州', '江苏连云港海州区', 'city', 'high', ''),
    'mizhou': ('密州', '山东潍坊诸城', 'city', 'high', '超然台所在'),
    'weizhou': ('潍州', '山东潍坊潍城区', 'city', 'high', ''),
    'qingzhou': ('青州', '山东青州', 'city', 'high', ''),
    'jinan': ('齐州', '山东济南', 'city', 'high', '宋齐州（历城），苏辙时任齐州掌书记'),
    'xuzhou': ('徐州', '江苏徐州', 'city', 'high', '彭城'),
    'sizhou': ('泗州', '江苏淮安盱眙县', 'city', 'medium', '宋泗州城在淮河北岸与盱眙相对，清代没入洪泽湖；坐标取盱眙县'),
    'wuxi': ('无锡', '江苏无锡', 'city', 'high', '惠山所在'),
    'caizhou': ('蔡州', '河南驻马店汝南县', 'city', 'high', '宋蔡州治汝阳县，即今汝南'),
    'qiting': ('岐亭', '湖北麻城歧亭镇', 'town', 'high', '陈慥（季常）隐居处'),
    'huangzhou': ('黄州', '湖北黄冈黄州区', 'city', 'high', '东坡、雪堂、赤壁（东坡赤壁）所在'),
    'lushan': ('庐山', '江西九江庐山（牯岭）', 'mountain', 'medium', '取山中牯岭镇为代表点；东林寺、西林寺在山北麓'),
    'yunzhou': ('筠州', '江西宜春高安', 'city', 'high', '苏辙时监筠州盐酒税'),
    'hukou': ('湖口', '江西九江湖口县', 'town', 'high', '石钟山在县城鄱阳湖口'),
    'jinling': ('金陵', '江苏南京', 'city', 'high', '宋江宁府'),
    'zhenzhou': ('真州', '江苏扬州仪征', 'city', 'high', ''),
    'nandu': ('南都', '河南商丘睢阳区', 'city', 'high', '宋南京应天府'),
    'dengzhou': ('登州', '山东烟台蓬莱区', 'city', 'high', ''),
    'laizhou': ('莱州', '山东莱州', 'city', 'high', ''),
    'dingzhou': ('定州', '河北定州', 'city', 'high', '中山府'),
    'lincheng': ('临城', '河北邢台临城县', 'town', 'high', ''),
    'ruzhou': ('汝州', '河南汝州', 'city', 'high', '苏辙时知汝州'),
    'ganzhou': ('虔州', '江西赣州', 'city', 'high', '郁孤台所在'),
    'dayuling': ('大庾岭', '江西大余与广东南雄交界梅关', 'pass', 'high', '梅关古道'),
    'guangzhou': ('广州', '广东广州', 'city', 'high', ''),
    'huizhou': ('惠州', '广东惠州', 'city', 'high', '合江楼、白鹤峰所在'),
    'tengzhou': ('藤州', '广西梧州藤县', 'city', 'high', ''),
    'leizhou': ('雷州', '广东湛江雷州', 'city', 'high', '渡海前与苏辙分别处'),
    'qiongzhou': ('琼州', '海南海口琼山区', 'city', 'high', ''),
    'danzhou': ('儋州', '海南儋州中和镇', 'city', 'high', '宋昌化军（故儋耳）治宜伦，今中和镇，东坡书院所在'),
    'lianzhou': ('廉州', '广西北海合浦县', 'city', 'high', ''),
    'shaozhou': ('韶州', '广东韶关', 'city', 'high', ''),
}


def build() -> dict:
    geo = json.loads(GEO.read_text())
    places = {}
    for key, (name, modern, kind, conf, note) in META.items():
        g = geo[key]
        p = {'name': name, 'modern': modern, 'lat': g['lat'], 'lon': g['lon'], 'kind': kind,
             'confidence': conf, 'source': f"OSM Nominatim {g['osm']}（查询：{g['q']}）"}
        if note:
            p['note'] = note
        places[key] = p
    return places


if __name__ == '__main__':
    data = build()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1) + '\n')
    print(len(data), 'places ->', OUT)
