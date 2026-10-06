"""抓取李白相关史料到 cache/libai/（curl 子进程，维基系页面取 action=raw 原始 wikitext）。
用法：python3 data/_build/libai_fetch.py <name> <url>
"""
import subprocess
import sys
from pathlib import Path

CACHE = Path(__file__).resolve().parent / 'cache' / 'libai'


def fetch(name: str, url: str) -> Path:
    CACHE.mkdir(parents=True, exist_ok=True)
    out = CACHE / f'{name}.txt'
    if not out.exists() or out.stat().st_size < 200:
        subprocess.run(['curl', '-sL', '-A', 'lives-doc-research/0.1', '--max-time', '60', url, '-o', str(out)],
                       check=False)
    return out


if __name__ == '__main__':
    p = fetch(sys.argv[1], sys.argv[2])
    print(p, p.stat().st_size if p.exists() else 'MISSING')
