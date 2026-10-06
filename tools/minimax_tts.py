"""MiniMax 语音合成（t2a_v2，预置音色；不做声音克隆）。
密钥只从环境变量 MINIMAX_API_KEY 读取，不写入任何文件。
用法（命令行试听）：MINIMAX_API_KEY=... python3 tools/minimax_tts.py <out.mp3> <voice_id> <speed> <pitch> <text>
文本里可用 <#0.5#> 插入 0.5 秒停顿。
"""
import json
import os
import subprocess
import sys
from pathlib import Path

API = 'https://api.minimaxi.com/v1/t2a_v2'
MODELS = ('speech-2.8-hd', 'speech-2.6-hd', 'speech-02-hd')


def synth(out: Path, voice: str, text: str, speed: float = 1.0, pitch: int = 0, model: str | None = None) -> dict:
    """合成一段并写入 out（mp3）；返回 extra_info（含 audio_length 毫秒、usage_characters）。"""
    key = os.environ.get('MINIMAX_API_KEY')
    if not key:
        raise RuntimeError('MINIMAX_API_KEY 未设置')
    last = None
    for m in ([model] if model else MODELS):
        body = {'model': m, 'text': text, 'stream': False,
                'voice_setting': {'voice_id': voice, 'speed': speed, 'vol': 1, 'pitch': pitch},
                'audio_setting': {'sample_rate': 32000, 'bitrate': 128000, 'format': 'mp3', 'channel': 1}}
        # 系统 Python 缺根证书：用 curl 发请求；密钥经 stdin 传入的配置文件，不出现在进程参数里
        cfg = f'header = "Authorization: Bearer {key}"\nheader = "Content-Type: application/json"\n'
        r = subprocess.run(['curl', '-sS', '--retry', '3', '-K', '-', '-X', 'POST', API, '--data-binary', json.dumps(body, ensure_ascii=False)],
                           input=cfg, capture_output=True, text=True, timeout=300)
        if r.returncode != 0:
            raise RuntimeError(f'curl failed: {r.stderr.strip()}')
        resp = json.loads(r.stdout)
        last = resp.get('base_resp')
        if last and last.get('status_code') == 0 and resp.get('data', {}).get('audio'):
            out.write_bytes(bytes.fromhex(resp['data']['audio']))
            return {**resp.get('extra_info', {}), 'model': m}
    raise RuntimeError(f'MiniMax TTS failed: {last}')


if __name__ == '__main__':
    if len(sys.argv) != 6:
        sys.exit(__doc__)
    info = synth(Path(sys.argv[1]), sys.argv[2], sys.argv[5], float(sys.argv[3]), int(sys.argv[4]))
    print(sys.argv[1], info.get('model'), info.get('audio_length'), 'ms', info.get('usage_characters'), 'chars')
