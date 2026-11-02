import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'tools'))
from person import people  # noqa: E402

PEOPLE = people()


def load(who: str, name: str):
    return json.loads((ROOT / 'data' / who / name).read_text())


def node(code: str):
    """在 src/ 下用 node 执行 ESM 片段，返回其 stdout 的 JSON。"""
    out = subprocess.run(['node', '--input-type=module', '-e', code], cwd=ROOT / 'src', capture_output=True, text=True, check=True)
    return json.loads(out.stdout)


def ages(who: str) -> dict:
    """每个半年步的 [年龄, 纪年]，以及出生覆盖（由 person.json 经 makePerson 计算）。"""
    ids = [s['id'] for s in load(who, 'steps.json')['steps']]
    return node(f"""import {{ makePerson }} from './person.js';
import fs from 'node:fs';
const p = makePerson(JSON.parse(fs.readFileSync('../data/{who}/person.json'))), out = {{}};
for (const id of {json.dumps(ids)}) {{ const [, y, h] = id.match(/^(-?\\d+)H([12])$/); out[id] = [p.age(+y, +h), p.era(+y, +h)]; }}
out.birth = p.birth || null;
console.log(JSON.stringify(out));""")


@pytest.fixture(params=PEOPLE)
def who(request):
    if not (ROOT / 'data' / request.param / 'steps.json').exists():
        pytest.fail(f'data/{request.param}/steps.json missing')
    return request.param
