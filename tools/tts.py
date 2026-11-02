"""逐段合成旁白（edge-tts），记录时长与逐词时间戳。
用法：python3 tools/tts.py <who> [--force]
输出：narration/<who>/audio/<id>.mp3，narration/<who>/tts.json {id: {dur, words:[[text, t0, t1]]}}
声线按人物区分（见 data/<who>/person.json 的 voice）。
文本变化会自动重合成（按文本哈希缓存）。
"""
import asyncio
import hashlib
import json
import subprocess
import sys
from pathlib import Path

from person import people, voice_of

ROOT = Path(__file__).resolve().parent.parent


def duration(p: Path) -> float:
    out = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(p)],
                         capture_output=True, text=True, check=True).stdout
    return float(out)


async def synth(text: str, path: Path, voice: tuple) -> list:
    import edge_tts  # 延迟导入：测试不需要联网依赖
    comm = edge_tts.Communicate(text, voice[0], rate=voice[1], pitch=voice[2], boundary='WordBoundary')
    words = []
    with path.open('wb') as f:
        async for ch in comm.stream():
            if ch['type'] == 'audio':
                f.write(ch['data'])
            elif ch['type'] == 'WordBoundary':
                t0 = ch['offset'] / 1e7
                words.append([ch['text'], round(t0, 3), round(t0 + ch['duration'] / 1e7, 3)])
    return words


async def main(who: str, force: bool) -> None:
    VOICE, RATE, PITCH = voice_of(who)
    NAR = ROOT / 'narration' / who
    (NAR / 'audio').mkdir(exist_ok=True)
    cache_p = NAR / 'tts.json'
    cache = json.loads(cache_p.read_text()) if cache_p.exists() else {}
    for seg in json.loads((NAR / 'script.json').read_text()):
        if 'text' not in seg:
            continue
        h = hashlib.md5(f"{VOICE}{RATE}{PITCH}{seg['text']}".encode()).hexdigest()[:10]
        mp3 = NAR / 'audio' / f"{seg['id']}.mp3"
        if not force and cache.get(seg['id'], {}).get('hash') == h and mp3.exists():
            continue
        for attempt in range(3):
            try:
                words = await synth(seg['text'], mp3, (VOICE, RATE, PITCH))
                break
            except Exception as e:  # 网络抖动重试
                print('retry', seg['id'], e)
                await asyncio.sleep(2)
        else:
            sys.exit(f"TTS failed: {seg['id']}")
        cache[seg['id']] = {'hash': h, 'dur': round(duration(mp3), 3), 'words': words}
        print(seg['id'], cache[seg['id']]['dur'])
        cache_p.write_text(json.dumps(cache, ensure_ascii=False, indent=0))
    print('total narration', round(sum(v['dur'] for v in cache.values()), 1), 's')


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    if len(args) != 1 or args[0] not in people():
        sys.exit(__doc__)
    asyncio.run(main(args[0], '--force' in sys.argv))
