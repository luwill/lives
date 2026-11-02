"""人物配置读取：data/<who>/person.json（测试、TTS、总装、成片检查共用）。"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REQUIRED = ('name', 'life', 'tagline', 'color', 'glow', 'age', 'eras', 'voice', 'span', 'targets')


def people() -> list[str]:
    """data/ 下所有带 person.json 的人物键，按字母排序。"""
    return sorted(p.parent.name for p in (ROOT / 'data').glob('*/person.json'))


def load_person(who: str) -> dict:
    p = ROOT / 'data' / who / 'person.json'
    if not p.exists():
        raise FileNotFoundError(f'{p} missing')
    cfg = json.loads(p.read_text())
    missing = [k for k in REQUIRED if k not in cfg]
    if missing:
        raise ValueError(f'{p}: missing fields {missing}')
    return cfg


def voice_of(who: str) -> tuple[str, str, str]:
    v = load_person(who)['voice']
    return v['name'], v['rate'], v['pitch']
