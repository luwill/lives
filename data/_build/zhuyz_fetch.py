"""抓取朱元璋相关史料原文（维基文库），结果缓存到 data/_build/cache/zhuyz/。
用法：python3 data/_build/zhuyz_fetch.py "明史/卷1" "御製皇陵碑" ...
已缓存的页面不会重复请求；遇到限流（429/非 JSON）按指数退避重试。
"""
import json
import subprocess
import sys
import time
import urllib.parse
from pathlib import Path

CACHE = Path(__file__).resolve().parent / 'cache' / 'zhuyz'
UA = 'lives-doc-research/0.1 (documentary data prep; low volume)'
API = 'https://zh.wikisource.org/w/index.php'
PAUSE_S = 3
MAX_TRIES = 5


def cache_path(title: str) -> Path:
    safe = title.replace('/', '_').replace(' ', '_').replace('(', '').replace(')', '')
    return CACHE / f'ws_{safe}.txt'


def fetch_raw(title: str) -> str:
    """用 index.php?action=raw 取 wikitext（curl，规避 Python 证书问题）。"""
    url = f'{API}?title={urllib.parse.quote(title)}&action=raw'
    delay = 20
    for attempt in range(MAX_TRIES):
        out = subprocess.run(['curl', '-s', '-L', '-A', UA, '-w', '\n%{http_code}', url],
                             capture_output=True, text=True, check=True).stdout
        body, _, code = out.rpartition('\n')
        if code == '200' and 'too many requests' not in body[:300].lower():
            return body
        print(f'  {title}: HTTP {code}, retry {attempt + 1} in {delay}s', file=sys.stderr)
        time.sleep(delay)
        delay *= 2
    raise RuntimeError(f'failed to fetch {title}')


def get(title: str) -> str:
    p = cache_path(title)
    if p.exists() and p.stat().st_size > 0:
        return p.read_text()
    CACHE.mkdir(parents=True, exist_ok=True)
    text = fetch_raw(title)
    p.write_text(text)
    time.sleep(PAUSE_S)
    return text


if __name__ == '__main__':
    for t in sys.argv[1:]:
        txt = get(t)
        print(json.dumps({'title': t, 'chars': len(txt), 'file': str(cache_path(t))}, ensure_ascii=False))
