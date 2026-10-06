"""把 cache/libai/<name>.html 转成纯文本 <name>.txt（自动识别 gbk/utf-8）。用法：python3 libai_html2txt.py name..."""
import html
import re
import sys
from pathlib import Path

C = Path(__file__).resolve().parent / 'cache' / 'libai'


def convert(name: str) -> Path:
    b = (C / f'{name}.html').read_bytes()
    m = re.search(rb'charset=["\']?([\w-]+)', b[:5000])
    enc = (m.group(1).decode() if m else 'utf-8').lower()
    enc = 'gb18030' if enc in ('gb2312', 'gbk') else enc
    t = b.decode(enc, 'replace')
    t = re.sub(r'<(script|style).*?</\1>', '', t, flags=re.S | re.I)
    t = html.unescape(re.sub(r'<[^>]+>', '\n', t))
    lines = [l.strip() for l in t.split('\n') if l.strip()]
    out = C / f'{name}.txt'
    out.write_text('\n'.join(lines))
    return out


if __name__ == '__main__':
    for n in sys.argv[1:]:
        print(convert(n))
