"""李白行踪农历→公元（儒略历）换算，复用已安装的 lunar_python（寿星历法，未新装任何包）。
唐代行用麟德历/大衍历，与寿星推算偶有一日之差，月级判断足够；结果写入 steps note。
用法：python3 data/_build/libai_lunar.py 756-12-1 ...      （农历年-月-日 → 公历）
      python3 data/_build/libai_lunar.py --gz 762-11 乙酉   （某农历月内指定干支日 → 公历）
"""
import sys

from lunar_python import Lunar


def lunar_to_solar(y: int, m: int, d: int) -> str:
    return Lunar.fromYmd(y, m, d).getSolar().toYmd()


def find_ganzhi_day(y: int, m: int, gz: str) -> list[str]:
    hits = []
    for d in range(1, 31):
        try:
            lu = Lunar.fromYmd(y, m, d)
        except Exception:
            break
        if lu.getDayInGanZhi() == gz:
            hits.append(f'{y}年{m}月{d}日 {gz} -> {lu.getSolar().toYmd()}')
    return hits


if __name__ == '__main__':
    a = sys.argv[1:]
    if a and a[0] == '--gz':
        y, m = (int(x) for x in a[1].split('-'))
        print(find_ganzhi_day(y, m, a[2]) or f'{a[1]} 月内无 {a[2]} 日')
    else:
        for s in a:
            y, m, d = (int(x) for x in s.split('-'))
            print(s, '->', lunar_to_solar(y, m, d))
