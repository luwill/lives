"""在缓存文本中按关键词取上下文。用法：python3 kw.py 'kw1|kw2' file1 [file2 ...] [-w 60]"""
import re, sys
args = sys.argv[1:]
w = 60
if '-w' in args:
    i = args.index('-w'); w = int(args[i + 1]); del args[i:i + 2]
pat = re.compile(args[0])
for f in args[1:]:
    t = open(f, encoding='utf-8', errors='replace').read().replace('\n', ' ')
    hits = [t[max(0, m.start() - w): m.end() + w] for m in pat.finditer(t)]
    print(f'## {f} ({len(hits)})')
    for h in hits[:12]:
        print('  ·', h)
