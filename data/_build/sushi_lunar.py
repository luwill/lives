"""农历→公元（儒略历，1582 年前）换算，用于判定苏轼行踪落在哪个半年。
依赖：pip install lunar_python（寿星天文历算法）。已用生卒两个锚点校验：
景祐三年十二月十九日 → 1037-01-08；建中靖国元年七月二十八日 → 1101-08-24。
用法：python3 data/_build/sushi_lunar.py 1079-7-28 1097-6-11 ...（负月份表示闰月，如 1094--4-1）
      python3 data/_build/sushi_lunar.py --solar 1084-6-30   （公历→农历）
"""
import sys

from lunar_python import Lunar, Solar


def lunar_to_solar(spec: str) -> str:
    y, rest = spec.split('-', 1)
    if rest.startswith('-'):
        m, d = rest[1:].split('-')
        m = -int(m)
    else:
        m, d = rest.split('-')
    return Lunar.fromYmd(int(y), int(m), int(d)).getSolar().toYmd()


def solar_to_lunar(spec: str) -> str:
    y, m, d = (int(x) for x in spec.split('-'))
    lu = Solar.fromYmd(y, m, d).getLunar()
    return f'{lu.getYear()}年{lu.getMonthInChinese()}月{lu.getDayInChinese()}'


if __name__ == '__main__':
    args = sys.argv[1:]
    solar_mode = bool(args) and args[0] == '--solar'
    for a in args[1:] if solar_mode else args:
        print(a, '->', solar_to_lunar(a) if solar_mode else lunar_to_solar(a))
