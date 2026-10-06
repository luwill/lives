"""李白半年粒度行踪 → data/libai/steps.json。
编年骨架：安旗《李白年谱》体系（经江油李白故里网逐年转录，S9），以郁贤皓“两入长安”说、
曾巩《李白诗集后序》、两唐书本传、李阳冰/魏颢/范传正三文校核；无明文的半年标 inferred。
农历换算见 libai_lunar.py。用法：python3 data/_build/libai_steps.py
"""
import json
from pathlib import Path

from libai_steps_data import CONTESTED, STAGE_STEPS

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'data' / 'libai' / 'steps.json'
WS = 'https://zh.wikisource.org/wiki/'

META = {
    'person': '李白',
    'birth': '701',
    'birth_note': ('武后长安元年。据李华《故翰林学士李君墓志》“年六十有二”及卒于宝应元年逆推；'
                   '生月日无一手史料（流行的“正月十六日”说无据）。出生地采碎叶说，见 contested'),
    'death': '762',
    'death_note': ('代宗宝应元年冬卒于当涂。李阳冰《草堂集序》署“宝应元年十一月乙酉”（≈762-11-30），'
                   '时李白“疾亟”，卒当在此前后；宝应元年十一月≈公历762-11-21至12-19，落在762H2'),
    'calendar_note': ('H1=公历1–6月，H2=7–12月（儒略历）。唐代史料为农历：有日期的用 lunar_python（寿星历法）'
                      '换算（脚本 data/_build/libai_lunar.py，已用“天宝十四载十一月甲子安禄山起兵=755-12-16”校验）；'
                      '只知季节或月份的，按农历1–6月→H1、7–12月→H2近似，并在 note 注明。'
                      '关键跨年案例：永王“十二月甲辰擅引舟师东巡”（≈757-01-19），故李白入幕系于757H1；'
                      '乾元二年三月大赦≈759-04；李白年谱多为推定，无明文的半年标 inferred。'),
    'sources': [
        {'id': 'S1', 'title': '李阳冰《草堂集序》（宝应元年）', 'url': WS + '唐李翰林草堂集序', 'kind': 'primary'},
        {'id': 'S2', 'title': '魏颢《李翰林集序》', 'url': WS + '李翰林集序', 'kind': 'primary'},
        {'id': 'S3', 'title': '范传正《唐左拾遗翰林学士李公新墓碑并序》', 'url': WS + '贈左拾遺翰林學士李公新墓碑',
         'kind': 'primary'},
        {'id': 'S4', 'title': '《旧唐书·文苑传下·李白》（卷一百九十下）', 'url': WS + '舊唐書/卷190下', 'kind': 'primary'},
        {'id': 'S5', 'title': '《新唐书·文艺传中·李白》（卷二百二）', 'url': WS + '新唐書/卷202', 'kind': 'primary'},
        {'id': 'S6', 'title': '王琦《李太白年谱》（《李太白集注》卷三十五，四库本）',
         'url': WS + '李太白集注_(四庫全書本)/卷35', 'kind': 'scholarly'},
        {'id': 'S7', 'title': '李白诗文原文（全唐诗/维基文库：上安州裴长史书、与韩荆州书、峨眉山月歌、南陵别儿童入京、'
                              '行路难、将进酒、梦游天姥吟留别、北风行、独坐敬亭山、永王东巡歌、早发白帝城、临路歌等）',
         'url': WS + '作者:李白', 'kind': 'primary'},
        {'id': 'S8', 'title': '曾巩《李白诗集后序》（北宋，最早的李白行迹编次）', 'url': WS + '李白詩集後序',
         'kind': 'scholarly'},
        {'id': 'S9', 'title': '江油李白故里网《李白简介》所附逐年年谱（安旗年谱体系）',
         'url': 'http://libaiguli.com.cn/show.asp?id=1', 'kind': 'popular'},
        {'id': 'S10', 'title': '维基百科「李白」条（引李长之、郁贤皓等）', 'url': 'https://zh.wikipedia.org/wiki/李白',
         'kind': 'secondary'},
        {'id': 'S11', 'title': '郭勉愈《新时期李白生平研究综述》（出生地、出蜀、入长安、卒年诸说）',
         'url': 'https://www.aisixiang.com/data/92617.html', 'kind': 'scholarly'},
        {'id': 'S12', 'title': '李定广《李白出蜀时间及寓居夔州、江陵考实》', 'url': 'https://www.sohu.com/a/821920709_121119369',
         'kind': 'scholarly'},
        {'id': 'S13', 'title': '《资治通鉴》卷二百一十九（至德元载十二月甲辰永王东巡；二载二月戊戌璘败死）',
         'url': WS + '資治通鑑/卷219', 'kind': 'primary'},
        {'id': 'S14', 'title': '李华《故翰林学士李君墓志并序》（《李太白集注》卷三十一附录，“年六十有二不偶，赋临终歌而卒”）',
         'url': WS + '李太白集注_(四庫全書本)/卷31', 'kind': 'primary'},
    ],
}

STAGES = [
    {'id': 'st1', 'title': '碎叶·蜀中少年', 'from': '701H1', 'to': '724H1',
     'summary': '生于西域碎叶，五岁随父潜还绵州昌隆；匡山读书，学剑任侠，谒苏颋于成都，游峨眉。',
     'mood_hint': '西域风沙到蜀中青山：少年任侠、好剑术、慕神仙，天真而有凌云之志，明亮清新带一点异域苍茫。'},
    {'id': 'st2', 'title': '仗剑出蜀', 'from': '724H2', 'to': '726H2',
     'summary': '仗剑去国，辞亲远游：峨眉月下发清溪，出三峡渡荆门，江陵遇司马承祯，洞庭、庐山、金陵、扬州。',
     'mood_hint': '初出夔门的开阔与新奇，“山随平野尽，江入大荒流”，意气风发、挥金如土，间有客中病卧与思乡。'},
    {'id': 'st3', 'title': '酒隐安陆', 'from': '727H1', 'to': '740H1',
     'summary': '入赘许相公家，“酒隐安陆，蹉跎十年”；一入长安无成，谒韩荆州、游太原、访元丹丘于嵩山。',
     'mood_hint': '安居与不甘并存：桃花岩的闲适、干谒的屈辱、一入长安的失意，“行路难”的郁愤与“将进酒”的狂放交替。'},
    {'id': 'st4', 'title': '寓家东鲁', 'from': '740H2', 'to': '742H1',
     'summary': '移家东鲁，与孔巢父等隐徂徕山，号“竹溪六逸”；四月上泰山。',
     'mood_hint': '齐鲁山水间纵酒高歌、求仙访道，疏放闲逸中暗蓄待时而起的雄心。'},
    {'id': 'st5', 'title': '长安待诏', 'from': '742H2', 'to': '744H1',
     'summary': '天宝元年奉诏入京，玄宗降辇步迎，供奉翰林；遭谗见疏，天宝三载赐金放还。',
     'mood_hint': '“仰天大笑出门去”的狂喜，宫廷的华美与醉态的不羁，转而为谗毁中的孤傲与失落。'},
    {'id': 'st6', 'title': '漫游天下', 'from': '744H2', 'to': '755H2',
     'summary': '与杜甫、高适游梁宋，东鲁别杜甫；南游吴越、北上幽州、往来宣城秋浦金陵，十年飘泊。',
     'mood_hint': '狂放飘逸而怀才不遇：天姥梦游的瑰丽、幽州边塞的寒凛、敬亭独坐的孤寂，豪情底下愈见苍凉。'},
    {'id': 'st7', 'title': '乱世浮沉', 'from': '756H1', 'to': '760H2',
     'summary': '安史乱起南奔，隐庐山；入永王幕获罪，系浔阳狱，长流夜郎，溯江至巫山遇赦东还。',
     'mood_hint': '乱离悲慨：避乱的惶急、从军报国的热望、下狱与流放的屈辱；遇赦时“轻舟已过万重山”的狂喜一闪而过。'},
    {'id': 'st8', 'title': '当涂终老', 'from': '761H1', 'to': '762H2',
     'summary': '欲从李光弼军半道病还，依族叔李阳冰于当涂，枕上授简，赋《临路歌》而卒。',
     'mood_hint': '晚年苍凉：老病漂泊，壮志未酬，“大鹏飞兮振八裔，中天摧兮力不济”，悲壮而终归旷远。'},
]


def build() -> dict:
    steps = [s for block in STAGE_STEPS for s in block]
    return {'meta': META, 'stages': STAGES, 'steps': steps, 'contested': CONTESTED}


if __name__ == '__main__':
    d = build()
    OUT.write_text(json.dumps(d, ensure_ascii=False, indent=1))
    print(OUT, len(d['steps']), 'steps,', sum(1 for s in d['steps'] if s.get('milestone')), 'milestones')
