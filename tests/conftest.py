import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
PEOPLE = ['mao', 'zhuge', 'sushi', 'libai', 'zhuyz', 'jiang']


def load(who: str, name: str):
    return json.loads((ROOT / 'data' / who / name).read_text())


@pytest.fixture(params=PEOPLE)
def who(request):
    if not (ROOT / 'data' / request.param / 'steps.json').exists():
        pytest.fail(f'data/{request.param}/steps.json missing')
    return request.param
