"""check_env 在当前项目上应报告就绪（lives/ 是完整环境）。"""
import subprocess
import sys

from conftest import ROOT


def test_check_env_ready():
    r = subprocess.run([sys.executable, 'tools/check_env.py'], cwd=ROOT, capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    assert '环境就绪' in r.stdout
