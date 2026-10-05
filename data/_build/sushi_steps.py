"""苏轼半年粒度行踪 → data/sushi/steps.json。
数据按人生阶段分块写在本文件 STAGE_STEPS 中，逐阶段补充、逐阶段落盘：
    python3 data/_build/sushi_steps.py
日期换算见 sushi_lunar.py（农历→儒略历），史料原文缓存见 cache/sushi/。
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'data' / 'sushi' / 'steps.json'
WS = 'https://zh.wikisource.org/wiki/'

META = {
    'person': '苏轼',
    'birth': '1037-01-08',
    'birth_note': '景祐三年十二月十九日（王宗稷《东坡先生年谱》；换算为儒略历 1037-01-08）',
    'death': '1101-08-24',
    'death_note': '建中靖国元年七月二十八日卒于常州（《宋史》本传、苏辙《墓志铭》）',
    'calendar_note': ('H1=公历1–6月，H2=7–12月（儒略历）。史料为农历：有确切日期的用 lunar_python（寿星历法）'
                      '换算后归半年（脚本 data/_build/sushi_lunar.py，已用生卒两锚点校验）；只知月份的按'
                      '农历1–6月→H1、7–12月→H2 近似，并在 note 中注明。农历岁末事件常落入次年公历，'
                      '如乌台诗案出狱（元丰二年十二月二十九日→1080-01-23）。'),
    'sources': [
        {'id': 'S1', 'title': '《宋史·苏轼传》（卷三百三十八）', 'url': WS + '宋史/卷338', 'kind': 'primary'},
        {'id': 'S2', 'title': '苏辙《亡兄子瞻端明墓志铭》（《栾城后集》卷二十二）',
         'url': WS + '亡兄子瞻端明墓誌銘', 'kind': 'primary'},
        {'id': 'S3', 'title': '查慎行《苏诗补注》各卷卷首编年（四库全书本，卷1–45）',
         'url': WS + '蘇詩補註_(四庫全書本)', 'kind': 'scholarly'},
        {'id': 'S4', 'title': '苏轼诗词文原文（维基文库：江城子、水调歌头、念奴娇、定风波、前赤壁赋等；诗据《苏诗补注》）',
         'url': WS + '作者:蘇軾', 'kind': 'primary'},
        {'id': 'S5', 'title': '王宗稷《东坡先生年谱》（维基文库残本，止于庆历三年）',
         'url': WS + '東坡先生年譜', 'kind': 'scholarly'},
        {'id': 'S6', 'title': '王文诰《苏文忠公诗编注集成》卷一总案（转引自川观新闻《三苏出川路线》）',
         'url': 'https://cbgc.scol.com.cn/news/5014034', 'kind': 'secondary'},
        {'id': 'S7', 'title': '维基百科「苏轼」条（含孔凡礼《苏轼年谱》引文）',
         'url': 'https://zh.wikipedia.org/wiki/苏轼', 'kind': 'secondary'},
    ],
}

STAGES = [
    {'id': 'st1', 'title': '眉山少年', 'from': '1037H1', 'to': '1055H2',
     'summary': '生于眉山纱縠行，母程氏亲授以书，读《范滂传》而有当世之志。',
     'mood_hint': '蜀中山水间的童年与少年，聪颖好学、天真意气，温暖明亮，带一点川西田园的悠扬。'},
    {'id': 'st2', 'title': '名动京师', 'from': '1056H1', 'to': '1070H2',
     'summary': '随父出川，进士高第、制科三等，签判凤翔；丧母、丧妻、丧父，两度往返蜀中与汴京。',
     'mood_hint': '少年得志、锋芒毕露，意气风发中夹着亲人相继离世的悲恸；旅途辽阔，雄健而有起伏。'},
    {'id': 'st3', 'title': '外任州郡', 'from': '1071H1', 'to': '1079H1',
     'summary': '与新法不合请外，通判杭州，历知密、徐、湖三州，诗酒风流亦勤于民事。',
     'mood_hint': '江南湖山的清丽与北方边郡的豪放交替：西湖的潇洒、密州的出猎狂放与中秋怀人、徐州抗洪的担当。'},
    {'id': 'st4', 'title': '乌台与黄州', 'from': '1079H2', 'to': '1084H1',
     'summary': '因诗下御史台狱一百三十日，贬黄州团练副使，躬耕东坡，赤壁三咏。',
     'mood_hint': '由惊惧、生死未卜的低谷，转入苦中作乐、竹杖芒鞋的超然；深沉内省而终归旷达。'},
    {'id': 'st5', 'title': '元祐沉浮', 'from': '1084H2', 'to': '1093H2',
     'summary': '量移北上，元祐还朝骤至翰林学士；不安于朝，屡请外放，再守杭州筑苏堤，历颍、扬、定三州。',
     'mood_hint': '重返庙堂的荣光与党争的倦意并存，宦海浮沉中的从容与自嘲；杭州段明丽开阔。'},
    {'id': 'st6', 'title': '岭海万里', 'from': '1094H1', 'to': '1100H1',
     'summary': '绍圣贬惠州，再贬儋州，渡海居昌化军，与黎民为伍，著书为乐。',
     'mood_hint': '年近六旬，万里投荒而泊然无所芥蒂；南国荔枝、海天苍茫，豁达、幽默、苍凉而坚韧。'},
    {'id': 'st7', 'title': '北归', 'from': '1100H2', 'to': '1101H2',
     'summary': '徽宗即位遇赦北归，渡海、度岭、经虔州金陵真州，卒于常州。',
     'mood_hint': '“九死南荒吾不恨”的释然与归途的疲惫，夕照般温暖而苍茫的终章。'},
]


def S(sid, places, event, conf, sources, **extra):
    """构造一条半年步。"""
    d = {'id': sid, 'places': places, 'event': event, 'confidence': conf, 'sources': sources}
    d.update(extra)
    return d


def MS(title, subtitle, importance, quote=None, quote_src=None):
    m = {'title': title, 'subtitle': subtitle, 'importance': importance}
    if quote:
        m['quote'] = {'text': quote, 'source': quote_src}
    return m


def meishan_years() -> list[dict]:
    """1037H2–1055H2 居眉山读书，大多无逐年行程记载。"""
    known = {
        '1043H1': ('入乡校，以道士张易简为师（王宗稷年谱引《志林》“吾八岁入小学”）', 'documented', ['S5']),
        '1047H1': ('父苏洵游学四方，母程氏亲授以书，读《范滂传》', 'inferred', ['S1', 'S2']),
        '1054H1': ('娶青神王弗（至和元年，月份不详）', 'inferred', ['S7']),
    }
    out = []
    for y in range(1037, 1056):
        for h in (1, 2):
            sid = f'{y}H{h}'
            if sid == '1037H1':
                continue
            ev, conf, src = known.get(sid, ('居眉山读书，无行程记载', 'inferred', ['S1']))
            step = S(sid, ['meishan'], ev, conf, src, stage='st1')
            if sid == '1047H1':
                step['note'] = '本传“生十年，父洵游学四方”，十岁约在庆历六至七年，具体年份为推断'
            if sid == '1054H1':
                step['note'] = '王弗十六岁归苏轼，至和元年（1054）；月份不详，暂系上半年'
            out.append(step)
    return out


STAGE_STEPS: dict[str, list[dict]] = {}

STAGE_STEPS['st1'] = [
    S('1037H1', ['meishan'], '景祐三年十二月十九日生于眉州眉山县（公历1037年1月8日）', 'documented',
      ['S5', 'S2'], stage='st1',
      milestone=MS('眉山出生', '生于蜀中眉山纱縠行，父苏洵、母程氏', 1)),
    *meishan_years(),
]


STAGE_STEPS['st2'] = [
    S('1056H1', ['meishan', 'chengdu', 'langzhong', 'baoxie', 'fengxiang', 'changan', 'mianchi', 'kaifeng'],
      '三月随父谒张方平于成都，经阆中出褒斜，过长安、渑池，五月抵京', 'documented', ['S6', 'S3', 'S7'],
      stage='st2',
      note='路线据王文诰总案“自阆中出褒斜，发横渠镇入凤翔，过长安，五月抵京师”；渑池据《和子由渑池怀旧》自注“往岁马死于二陵，骑驴至渑池”'),
    S('1056H2', ['kaifeng'], '寓居汴京兴国寺，秋应开封府解试中举', 'inferred', ['S7'], stage='st2',
      note='嘉祐元年秋举人试（月份据宋制推断）'),
    S('1057H1', ['kaifeng'], '正月礼部试，欧阳修得《刑赏忠厚论》置第二；殿试中乙科，进士及第；四月母程氏卒于眉山',
      'documented', ['S1', 'S2'], stage='st2',
      milestone=MS('进士及第', '欧阳修读其文惊喜，欲避此人出一头地', 1,
                   '老夫當避此人，放出一頭地！', '苏辙《亡兄子瞻端明墓志铭》引欧阳修语'),
      note='程夫人卒于嘉祐二年四月八日（≈1057-05-14）'),
    S('1057H2', ['kaifeng', 'meishan'], '闻母丧，父子三人仓促离京返蜀奔丧', 'documented', ['S1', 'S2'], stage='st2',
      note='“丁母忧”见本传；离京与抵家的具体月份不详，按常理系于下半年'),
    S('1058H1', ['meishan'], '在眉山守母丧', 'inferred', ['S1'], stage='st2'),
    S('1058H2', ['meishan'], '在眉山守母丧', 'inferred', ['S1'], stage='st2'),
    S('1059H1', ['meishan'], '守丧期满，居眉山', 'inferred', ['S1', 'S3'], stage='st2'),
    S('1059H2', ['meishan', 'jiazhou', 'rongzhou', 'yuzhou', 'zhongzhou', 'kuizhou', 'xiazhou'],
      '十月侍父携弟舟行出川：发嘉州，经戎、渝、忠、夔诸州下三峡，父子唱和成《南行集》', 'documented', ['S3'],
      stage='st2',
      note='查注卷一“自眉州…经戎泸渝涪忠夔诸州下峡抵荆州度岁”；抵江陵在农历十二月（已入1060年公历），故本半年末取峡州'),
    S('1060H1', ['jiangling', 'xiangyang', 'kaifeng'], '在江陵度岁；正月自荆门陆行，经襄阳、唐、许，二月至汴京',
      'documented', ['S3'], stage='st2',
      note='查注卷二“嘉祐五年庚子春自荆州陆行赴京师”'),
    S('1060H2', ['kaifeng'], '授河南府福昌县主簿，未赴；在京准备制科', 'documented', ['S1', 'S2'], stage='st2'),
    S('1061H1', ['kaifeng'], '寓居汴京怀远驿，欧阳修荐应制科，进《进策》《进论》', 'inferred', ['S1', 'S2'],
      stage='st2'),
    S('1061H2', ['kaifeng', 'zhengzhou', 'mianchi', 'changan'],
      '八月制科入三等，除签书凤翔府判官；十一月与子由别于郑州西门，西行赴任', 'documented', ['S1', 'S2', 'S3', 'S7'],
      stage='st2',
      milestone=MS('制科三等·签判凤翔', '宋兴以来制策入三等者唯吴育与苏轼', 2,
                   '人生到處知何似，應似飛鴻踏雪泥。', '《和子由渑池怀旧》'),
      note='十二月十四日到凤翔（≈1062-01-27，已入次年公历），故本半年末取长安一带'),
    S('1062H1', ['fengxiang', 'zhouzhi', 'fengxiang'], '到凤翔签判任；二月奉诏减决囚禁，历宝鸡、虢、郿、盩厔诸县',
      'documented', ['S3'], stage='st2'),
    S('1062H2', ['fengxiang'], '在凤翔签判任，修衙规以减衙前木筏之害', 'inferred', ['S1', 'S2', 'S3'], stage='st2'),
    S('1063H1', ['fengxiang'], '在凤翔任，与太守陈希亮不睦，作《凌虚台记》', 'inferred', ['S3', 'S7'], stage='st2'),
    S('1063H2', ['fengxiang'], '在凤翔签判任', 'inferred', ['S3'], stage='st2'),
    S('1064H1', ['fengxiang'], '在凤翔签判任，游终南、楼观', 'inferred', ['S3'], stage='st2'),
    S('1064H2', ['fengxiang'], '十二月罢凤翔任', 'documented', ['S3', 'S2'], stage='st2',
      note='罢任在农历十二月，启程已入1065年公历'),
    S('1065H1', ['fengxiang', 'changan', 'kaifeng'], '自凤翔还朝，判登闻鼓院；试二论入三等，直史馆', 'documented',
      ['S1', 'S2', 'S3'], stage='st2'),
    S('1065H2', ['kaifeng'], '五月二十八日妻王弗卒于京师，年二十七', 'documented', ['S7'], stage='st2',
      milestone=MS('王弗卒', '结发之妻早逝，十年后密州梦中作悼亡词', 2,
                   '十年生死兩茫茫，不思量，自難忘。', '《江城子·乙卯正月二十日夜记梦》（1075年作于密州）'),
      note='治平二年五月二十八日换算为1065-07-04，落入下半年'),
    S('1066H1', ['kaifeng'], '四月二十五日父苏洵卒于京师；辞赙金，求赠一官', 'documented', ['S1', 'S2'], stage='st2'),
    S('1066H2', ['kaifeng', 'jiangling'], '六月护父柩，与子由舟行自汴入淮、溯江西归', 'documented', ['S1', 'S7'],
      stage='st2',
      note='英宗诏官船载丧；沿途具体停留史无详载，本半年末位置取江陵为推定'),
    S('1067H1', ['meishan'], '四月抵眉山，守父丧', 'documented', ['S7'], stage='st2',
      note='抵家月份据孔凡礼年谱（转引），存疑'),
    S('1067H2', ['meishan'], '十月葬父于彭山安镇乡可龙里，与母合葬；守丧', 'inferred', ['S7'], stage='st2'),
    S('1068H1', ['meishan'], '在眉山守父丧', 'inferred', ['S2'], stage='st2'),
    S('1068H2', ['meishan'], '七月服除，续娶王弗堂妹王闰之；十二月携家离蜀北上，此后终身未再回乡', 'documented',
      ['S2', 'S7'], stage='st2',
      note='离蜀为熙宁元年十二月（≈1068年12月末至1069年1月）；路线史无详载'),
    S('1069H1', ['kaifeng'], '二月还朝，王安石变法方兴，判官告院', 'documented', ['S1', 'S2', 'S3'], stage='st2',
      note='自眉山至汴京的陆路行程未见明载'),
    S('1069H2', ['kaifeng'], '在京判官告院，议论与新法不合', 'inferred', ['S1', 'S2'], stage='st2'),
    S('1070H1', ['kaifeng'], '在京判官告院；参与本年进士考校，所拟上官均第一被吕惠卿改为第二', 'documented',
      ['S7'], stage='st2'),
    S('1070H2', ['kaifeng'], '在京任职，与新党议论日左；谢景温诬其居丧贩运，查无实据', 'inferred', ['S1', 'S7'],
      stage='st2'),
]


STAGE_STEPS['st3'] = [
    S('1071H1', ['kaifeng'], '上书论新法，议学校贡举蒙神宗召对，权开封府推官；为人诬奏，请外任', 'documented',
      ['S1', 'S2'], stage='st3'),
    S('1071H2', ['kaifeng', 'chenzhou', 'yingzhou', 'shouzhou', 'haozhou', 'chuzhou', 'yangzhou', 'runzhou',
                 'hangzhou'],
      '通判杭州：七月离京，过陈州会子由，颍州谒欧阳修，经淮、扬、润，十一月到杭', 'documented', ['S1', 'S3', 'S7'],
      stage='st3',
      milestone=MS('通判杭州', '与新法不合请外，初到湖山之地', 2),
      note='路线据查注卷六、卷七诗题（宛丘、陪欧阳公燕西湖、出颍口至寿州、濠州、山阳、金山）；到杭十一月二十八日≈1071-12-22'),
    S('1072H1', ['hangzhou'], '在杭州通判任，游西湖、孤山、吉祥寺赏牡丹', 'documented', ['S3'], stage='st3'),
    S('1072H2', ['hangzhou', 'huzhou', 'hangzhou'], '在杭州通判任；冬往湖州相度堤岸，与知州孙觉唱和', 'documented',
      ['S3', 'S7'], stage='st3'),
    S('1073H1', ['hangzhou'], '在杭州通判任，作《饮湖上初晴后雨》', 'documented', ['S3'], stage='st3',
      note='查注卷九“熙宁六年正月尽六月在杭州通守任作”'),
    S('1073H2', ['hangzhou', 'changzhou'], '秋在杭；十一月奉命往常、润赈济，除夜野宿常州城外', 'documented', ['S3'],
      stage='st3',
      note='查注卷十一“癸丑冬合甲寅春夏往返常润苏秀道中作”'),
    S('1074H1', ['changzhou', 'runzhou', 'suzhou', 'hangzhou'], '往返常、润、苏、秀诸州赈灾，游金山、惠山，六月回杭',
      'documented', ['S3'], stage='st3'),
    S('1074H2', ['hangzhou', 'runzhou', 'yangzhou', 'haizhou', 'mizhou'],
      '九月移知密州，经润州、扬州、海州北上，十二月到密州任', 'documented', ['S1', 'S3', 'S7'], stage='st3',
      note='到任约十二月初（≈1074年12月下旬），仍在本半年'),
    S('1075H1', ['mizhou'], '在密州任，正月二十日夜梦亡妻王弗作《江城子》；治蝗、捕盗、罢手实法', 'documented',
      ['S1', 'S2', 'S4'], stage='st3'),
    S('1075H2', ['mizhou'], '在密州任，修超然台；冬作《江城子·密州出猎》', 'documented', ['S3', 'S4'], stage='st3'),
    S('1076H1', ['mizhou'], '在密州任', 'inferred', ['S3'], stage='st3'),
    S('1076H2', ['mizhou'], '丙辰中秋欢饮达旦作《水调歌头》兼怀子由；冬受命移知河中府，十二月离密州', 'documented',
      ['S3', 'S4'], stage='st3',
      milestone=MS('密州·明月几时有', '出猎的少年狂与中秋的怀弟之思', 2,
                   '但願人長久，千里共嬋娟。', '《水调歌头·丙辰中秋》'),
      note='离密州在农历十二月，已近1077年公历'),
    S('1077H1', ['weizhou', 'qingzhou', 'jinan', 'kaifeng', 'xuzhou'],
      '除夜大雪留潍州，经青、齐至京城外，改知徐州；四月与子由同赴徐州，二十一日到任', 'documented', ['S3', 'S7'],
      stage='st3',
      note='查注卷十五“丁巳正月自密州至京师四月后赴徐州任”；到徐州四月二十一日≈1077-05-15'),
    S('1077H2', ['xuzhou'], '七月河决澶州曹村，八月水围徐州城，苏轼庐于城上、率军民筑堤，十月水退', 'documented',
      ['S1', 'S2'], stage='st3',
      milestone=MS('徐州抗洪', '过家不入，率禁军筑东南长堤，全城得保', 2,
                   '吾在，是水決不能敗城！', '苏辙《亡兄子瞻端明墓志铭》引苏轼语')),
    S('1078H1', ['xuzhou'], '在徐州任，请调夫增筑故城、为木岸', 'documented', ['S1', 'S3'], stage='st3'),
    S('1078H2', ['xuzhou'], '在徐州任，东门黄楼落成，重九大会宾客；子由作《黄楼赋》', 'documented', ['S3', 'S7'],
      stage='st3'),
    S('1079H1', ['xuzhou', 'sizhou', 'wuxi', 'huzhou'], '三月移知湖州，经泗州过淮、游惠山，四月下旬到湖州任',
      'documented', ['S1', 'S3', 'S7'], stage='st3',
      note='到任日期有四月二十日、四月二十九日两说（维基百科取后者），换算均为1079年5月下旬'),
]


STAGE_STEPS['st4'] = [
    S('1079H2', ['huzhou', 'kaifeng'], '七月二十八日在湖州被皇甫遵逮捕，八月十八日下御史台狱，鞫治百余日', 'documented',
      ['S1', 'S2', 'S7'], stage='st4',
      milestone=MS('乌台诗案', '以诗托讽获罪，下御史台狱，几至于死', 1,
                   '是處青山可埋骨，他年夜雨獨傷神。',
                   '《予以事系御史台狱……以遗子由二首》其一'),
      note='被捕日≈1079-08-27；出狱为十二月二十九日≈1080-01-23，已入次年公历，故本半年末仍在狱中'),
    S('1080H1', ['kaifeng', 'chenzhou', 'caizhou', 'qiting', 'huangzhou'],
      '出狱责授黄州团练副使；正月初一离京，经陈、蔡、新息、岐亭，二月一日到黄州，寓定惠院', 'documented',
      ['S1', 'S2', 'S3'], stage='st4',
      milestone=MS('贬谪黄州', '检校水部员外郎、黄州团练副使，本州安置', 2,
                   '長江繞郭知魚美，好竹連山覺筍香。', '《初到黄州》'),
      note='查注卷二十“元丰三年庚申正月赴黄州”；到黄州二月一日≈1080-02-24'),
    S('1080H2', ['huangzhou'], '在黄州安置，渡江游武昌寒溪西山寺', 'documented', ['S3'], stage='st4'),
    S('1081H1', ['huangzhou'], '马正卿为请故营地数十亩，躬耕其中，名曰“东坡”', 'documented', ['S1', 'S2', 'S7'],
      stage='st4'),
    S('1081H2', ['huangzhou'], '在黄州躬耕东坡', 'inferred', ['S3'], stage='st4'),
    S('1082H1', ['huangzhou'], '筑雪堂，自号东坡居士；三月七日沙湖道中遇雨作《定风波》', 'documented',
      ['S1', 'S4', 'S7'], stage='st4'),
    S('1082H2', ['huangzhou'], '七月既望泛舟赤壁作《赤壁赋》，十月再游作《后赤壁赋》；《念奴娇·赤壁怀古》亦系本年',
      'documented', ['S4', 'S7'], stage='st4',
      milestone=MS('赤壁三咏', '前、后《赤壁赋》与《念奴娇·赤壁怀古》', 1,
                   '惟江上之清風，與山間之明月，耳得之而為聲，目遇之而成色，取之無禁，用之不竭。', '《赤壁赋》'),
      note='《念奴娇》维基文库系于1082年，具体月份不详'),
    S('1083H1', ['huangzhou'], '在黄州，与张怀民、陈慥等往还', 'inferred', ['S3'], stage='st4'),
    S('1083H2', ['huangzhou'], '十月十二日夜访张怀民于承天寺，作《记承天寺夜游》', 'documented', ['S4'], stage='st4',
      note='《记承天寺夜游》作于元丰六年十月十二日'),
    S('1084H1', ['huangzhou', 'lushan', 'yunzhou'],
      '量移汝州团练副使：四月离黄州，游庐山作《题西林壁》，五月至筠州探子由', 'documented', ['S1', 'S3', 'S7'],
      stage='st4',
      note='查注卷二十三“先生于四月初离黄州，先游庐山后至筠州”；离黄州≈1084-05-13，公历6月末（农历五月廿五）约在筠州或返程'),
]


STAGE_STEPS['st5'] = [
    S('1084H2', ['hukou', 'jinling', 'zhenzhou', 'runzhou', 'yangzhou', 'sizhou'],
      '六月过湖口探石钟山；七月至金陵见王安石，幼子遁夭；八月寓真州，历润、扬，泗州度岁', 'documented',
      ['S1', 'S3', 'S7'], stage='st5',
      note='石钟山之游在六月丁丑（≈7月中旬）；查注卷二十四“自金陵历真润扬淮，在泗州度岁”'),
    S('1085H1', ['sizhou', 'nandu', 'changzhou'], '上书乞居常州获准；正月自泗州往南都，三月神宗崩，五月抵常州',
      'documented', ['S1', 'S2', 'S3'], stage='st5',
      note='查注卷二十五“元丰八年乙丑正月自泗州往南都，得请归阳羡，五月抵常州”'),
    S('1085H2', ['changzhou', 'runzhou', 'yangzhou', 'chuzhou', 'haizhou', 'mizhou', 'dengzhou', 'laizhou', 'kaifeng'],
      '起知登州，经扬、楚、海、密诸州北上，十月到任五日即以礼部郎中召还，经莱州，十二月至京', 'documented',
      ['S1', 'S2', 'S3'], stage='st5',
      note='查注卷二十六“五月后起知登州，十月到任，十一月以礼部郎还朝”；途经据卷二十六诗题（金山妙高台、斗野亭、怀仁、再过超然台、过莱州）'),
    S('1086H1', ['kaifeng'], '元祐元年迁起居舍人，以七品服入侍延和殿，三月迁中书舍人', 'documented', ['S1', 'S2', 'S3'],
      stage='st5'),
    S('1086H2', ['kaifeng'], '与司马光争免役差役；秋除翰林学士、知制诰', 'documented', ['S1', 'S2', 'S3'],
      stage='st5',
      milestone=MS('元祐还朝', '十年之间由黄州罪人骤至翰林学士', 2,
                   '此先帝意也。先帝每誦卿文章，必歎曰：「奇才，奇才！」', '《宋史·苏轼传》载宣仁太后语'),
      note='除翰林学士月份：查注卷二十七作十月，另有九月说，均在本半年'),
    S('1087H1', ['kaifeng'], '在京任翰林学士，兼侍读', 'documented', ['S1', 'S3'], stage='st5'),
    S('1087H2', ['kaifeng'], '在京任翰林学士；洛蜀党争渐起', 'inferred', ['S3', 'S7'], stage='st5'),
    S('1088H1', ['kaifeng'], '权知礼部贡举，大雪中宽舍人禁约', 'documented', ['S1'], stage='st5'),
    S('1088H2', ['kaifeng'], '在京任翰林学士，屡遭台谏攻讦，乞外', 'inferred', ['S1', 'S2'], stage='st5'),
    S('1089H1', ['kaifeng'], '春除龙图阁学士、知杭州，四月后出京南下', 'documented', ['S1', 'S3'], stage='st5',
      note='途中行程未见明载，本半年末位置取汴京为保守处理'),
    S('1089H2', ['hangzhou'], '七月三日到杭州任，“江山故国，所至如归”；大旱饥疫，请免上供米、设病坊', 'documented',
      ['S1', 'S3'], stage='st5'),
    S('1090H1', ['hangzhou'], '四月起开浚西湖，浚茅山、盐桥二河，取葑泥筑长堤，杭人名为苏公堤', 'documented',
      ['S1', 'S7'], stage='st5',
      milestone=MS('再守杭州·筑苏堤', '浚西湖、复六井，南北长堤成，植芙蓉杨柳', 1,
                   '欲把西湖比西子，淡粧濃抹總相宜。', '《饮湖上初晴后雨》（熙宁六年通判杭州时作）'),
      note='《宋史》载堤成植芙蓉杨柳；开湖时间据维基百科（元祐五年）'),
    S('1090H2', ['hangzhou'], '在杭州知州任，议开石门运河避浮山之险', 'inferred', ['S1', 'S3'], stage='st5'),
    S('1091H1', ['hangzhou', 'kaifeng'], '三月罢杭州召还，以弟辙除右丞改翰林学士承旨，入京', 'documented',
      ['S1', 'S3', 'S7'], stage='st5'),
    S('1091H2', ['kaifeng', 'yingzhou'], '在翰林数月，复以谗请外，八月以龙图阁学士知颍州，闰八月到任', 'documented',
      ['S1', 'S3', 'S7'], stage='st5'),
    S('1092H1', ['yingzhou', 'yangzhou'], '在颍州擒剧盗尹遇；正月诏移知扬州，三月到任', 'documented', ['S1', 'S3', 'S7'],
      stage='st5'),
    S('1092H2', ['yangzhou', 'kaifeng'], '九月以兵部尚书召还；十一月为南郊卤簿使，迁礼部尚书、端明殿学士', 'documented',
      ['S1', 'S3', 'S7'], stage='st5'),
    S('1093H1', ['kaifeng'], '在京任礼部尚书', 'documented', ['S1', 'S3'], stage='st5'),
    S('1093H2', ['kaifeng', 'dingzhou'], '继室王闰之卒于京师；九月宣仁太后崩，出知定州，十月到任整顿军政', 'documented',
      ['S1', 'S3', 'S7'], stage='st5',
      note='王闰之卒年据维基百科，通行说为八月，未见一手史料核对；查注卷三十七“癸酉九月出知定州”'),
]


STAGE_STEPS['st6'] = [
    S('1094H1', ['dingzhou', 'lincheng', 'ruzhou'],
      '绍圣元年以“讥斥先朝”落职知英州；闰四月自定州南下，过临城，至汝州与子由相会', 'documented',
      ['S1', 'S3'], stage='st6',
      note='查注卷三十七收《临城道中作》《子由新修汝州龙兴寺吴画壁》；公历6月末约当农历五月中，位置取汝州为推定'),
    S('1094H2', ['jinling', 'lushan', 'ganzhou', 'dayuling', 'guangzhou', 'huizhou'],
      '途中再贬宁远军节度副使、惠州安置；过金陵、庐山下，八月入赣过惶恐滩，度大庾岭，十月二日到惠州',
      'documented', ['S1', 'S3'], stage='st6',
      milestone=MS('谪居惠州', '年近六旬投荒岭南，泊然无所芥蒂', 2,
                   '日噉荔支三百顆，不辭長作嶺南人。', '《食荔支二首》其二（作于惠州）'),
      note='查注卷三十八“绍圣元年甲戌秋自江西赴岭外十月到惠州”；到惠州≈1094-11-12'),
    S('1095H1', ['huizhou'], '在惠州，三月自嘉祐寺迁居合江楼', 'documented', ['S3', 'S7'], stage='st6'),
    S('1095H2', ['huizhou'], '在惠州安置；虔州王原（子直）不远千里来访', 'inferred', ['S3'], stage='st6',
      note='王子直来访据查注卷四十四引年谱，月份不详'),
    S('1096H1', ['huizhou'], '在惠州，捐犀带助修东、西新桥', 'inferred', ['S7'], stage='st6',
      note='修桥事系绍圣三年，月份不详'),
    S('1096H2', ['huizhou'], '七月五日侍妾王朝云病卒于惠州，葬栖禅寺松林', 'documented', ['S3'],
      stage='st6', note='据《悼朝云诗》引“绍圣三年七月五日朝云病亡于惠州”'),
    S('1097H1', ['huizhou', 'tengzhou'], '二月十四日白鹤峰新居落成；四月责授琼州别驾、昌化军安置，十九日离惠州，五月于藤州追及子由',
      'documented', ['S1', 'S3', 'S7'], stage='st6',
      note='告下四月十七日≈1097-05-30；藤州相遇五月十一日≈1097-06-23'),
    S('1097H2', ['leizhou', 'qiongzhou', 'danzhou'], '与子由同至雷州，六月十一日渡琼州海峡，经琼州，七月抵儋州昌化军',
      'documented', ['S1', 'S3', 'S7'], stage='st6',
      milestone=MS('渡海居儋', '六十二岁贬至海南，与幼子苏过相依', 1,
                   '四州環一島，百洞蟠其中。', '《行琼儋间肩舆坐睡……戏作此数句》'),
      note='渡海六月十一日≈1097-07-22，故归下半年；抵儋日期有七月二日、七月十三日两说'),
    S('1098H1', ['danzhou'], '初僦官屋，有司逐之，遂买地筑室（桄榔庵），儋人运甓畚土相助', 'documented',
      ['S1', 'S7'], stage='st6', note='逐出官舍事系元符元年，月份不详'),
    S('1098H2', ['danzhou'], '在儋州，著书为乐，作和陶诗', 'inferred', ['S1', 'S3'], stage='st6'),
    S('1099H1', ['danzhou'], '琼州士子姜唐佐来从学', 'inferred', ['S7'], stage='st6', note='系元符二年，月份不详'),
    S('1099H2', ['danzhou'], '在儋州，时从父老游', 'inferred', ['S1', 'S3'], stage='st6'),
    S('1100H1', ['danzhou'], '正月哲宗崩、徽宗即位，大赦；五月告下移廉州安置', 'documented', ['S1', 'S2', 'S3'],
      stage='st6'),
]


STAGE_STEPS['st7'] = [
    S('1100H2', ['danzhou', 'qiongzhou', 'leizhou', 'lianzhou', 'tengzhou', 'guangzhou', 'shaozhou'],
      '六月二十日夜渡海北归，七月至廉州；改舒州团练副使永州居住，八月末离廉，经藤、梧、广州，复提举玉局观，韶州度岁',
      'documented', ['S1', 'S3', 'S7'], stage='st7',
      milestone=MS('遇赦北归', '徽宗即位，三度大赦，渡海北还', 2,
                   '九死南荒吾不恨，茲遊奇絕冠平生。', '《六月二十日夜渡海》'),
      note='渡海≈1100-07-28。永州实未到：途中即复朝奉郎、提举成都玉局观，任便居住；查注卷四十四“是冬在韶州度岁”'),
    S('1101H1', ['dayuling', 'ganzhou', 'hukou', 'jinling', 'zhenzhou'],
      '正月度大庾岭，至虔州停留；四月过湖口，五月经金陵至真州，登金山自题画像，暑中病作', 'documented',
      ['S1', 'S3', 'S7'], stage='st7',
      note='查注卷四十五“建中靖国元年辛巳春自南安归常州”；公历6月末≈农历六月初三，仍在真州一带'),
    S('1101H2', ['zhenzhou', 'changzhou'], '六月渡江至常州，病笃，七月二十八日卒于常州孙氏馆，年六十六', 'documented',
      ['S1', 'S2', 'S7'], stage='st7',
      milestone=MS('常州病逝', '北归途中卒于毗陵，吴越之民相与哭于市', 1,
                   '心似已灰之木，身如不繫之舟。問汝平生功業，黃州惠州儋州。',
                   '《自题金山画像》（北归途经金山时作）'),
      note='卒日≈1101-08-24；至常州约六月中旬（≈7月中）。“孙氏馆”据维基百科引地方文献'),
]

CONTESTED = [
    {'topic': '1056年出川路线',
     'views': ['自阆中出褒斜，发横渠镇入凤翔，过长安至京（王文诰总案，S6）',
               '部分通俗读物写作经剑门、金牛道入关中（无一手史料）'],
     'adopted': '采用王文诰说，并以《和子由渑池怀旧》自注佐证经渑池'},
    {'topic': '到湖州日期（1079）',
     'views': ['四月二十日（通行年谱说）', '四月二十九日（维基百科）'],
     'adopted': '两说均落在1079H1，事件表述为“四月下旬”'},
    {'topic': '到儋州日期（1097）',
     'views': ['七月二日（通行说）', '七月十三日（维基百科）'],
     'adopted': '两说均在1097H2，不影响分步'},
    {'topic': '北归途经永州',
     'views': ['任务书提示“经廉州、永州一带”', '《宋史》“移廉州，改舒州团练副使，徙永州。更三大赦，遂提举玉局观”，查注卷四十四行程为廉→藤→梧→广→韶'],
     'adopted': '苏轼并未到永州，行程按查注取廉州—藤州—广州—韶州'},
    {'topic': '密州/凤翔等农历岁末事件的半年归属',
     'views': ['按农历月份直接归半年', '按儒略历换算后归半年'],
     'adopted': '有确切日期者一律换算（如王弗卒1065-07-04归H2，出狱1080-01-23归1080H1，赴凤翔到任1062-01-27归1062H1）'},
    {'topic': '《念奴娇·赤壁怀古》文本',
     'views': ['“浪淘尽……三国周郎赤壁”（通行本）', '“浪声沉……三国孙吴赤壁”（《容斋随笔》引黄庭坚手书本）'],
     'adopted': '本数据未引用该词原文作 quote，赤壁里程碑改用《赤壁赋》，避免文本分歧'},
]


def build() -> dict:
    steps = [s for st in STAGES for s in STAGE_STEPS.get(st['id'], [])]
    done = {s['stage'] for s in steps}
    stages = [st for st in STAGES if st['id'] in done]
    return {'meta': META, 'stages': stages, 'steps': steps, 'contested': CONTESTED}


if __name__ == '__main__':
    data = build()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1) + '\n')
    print(len(data['steps']), 'steps,', len(data['stages']), 'stages ->', OUT)
