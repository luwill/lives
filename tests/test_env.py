"""check_env 在当前项目上应报告就绪（lives/ 是完整环境）。"""
import os
import subprocess
import sys

import pytest

from conftest import ROOT


def run_check(**env):
    return subprocess.run([sys.executable, 'tools/check_env.py'], cwd=ROOT, capture_output=True, text=True,
                          env={**os.environ, **env})


@pytest.mark.env
def test_check_env_ready():
    r = run_check()
    assert r.returncode == 0, r.stdout + r.stderr
    assert '环境就绪' in r.stdout


@pytest.mark.env
def test_check_env_reports_bad_chrome():
    r = run_check(LIFETRAIL_CHROME='/nope')
    assert r.returncode == 1, r.stdout + r.stderr
    assert 'LIFETRAIL_CHROME not found' in r.stdout
