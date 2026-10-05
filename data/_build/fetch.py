"""抓取网页到 cache/mao/，用 curl 子进程（避免 urllib 证书问题），输出纯文本。
用法：python3 fetch.py <url> [name]
"""
import hashlib, html, re, subprocess, sys
from pathlib import Path

CACHE = Path(__file__).resolve().parent / 'cache' / 'mao'


def fetch(url: str, name: str | None = None) -> Path:
    CACHE.mkdir(parents=True, exist_ok=True)
    name = name or hashlib.md5(url.encode()).hexdigest()[:10]
    raw, txt = CACHE / f'{name}.html', CACHE / f'{name}.txt'
    if not raw.exists():
        subprocess.run(['curl', '-sL', '-A', 'Mozilla/5.0', '--max-time', '40', url, '-o', str(raw)], check=False)
    b = raw.read_bytes()
    m = re.search(rb'charset=["\']?([\w-]+)', b[:3000])
    enc = (m.group(1).decode() if m else 'utf-8').lower()
    enc = 'gb18030' if enc in ('gb2312', 'gbk') else enc
    t = b.decode(enc, 'replace')
    t = re.sub(r'<(script|style).*?</\1>', '', t, flags=re.S | re.I)
    t = html.unescape(re.sub(r'<[^>]+>', '\n', t))
    lines = [l.strip() for l in t.split('\n') if l.strip()]
    txt.write_text(f'URL: {url}\n' + '\n'.join(lines))
    return txt


if __name__ == '__main__':
    p = fetch(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
    print(p, p.stat().st_size)
