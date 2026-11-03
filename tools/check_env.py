"""环境检查：一次列出所有缺失项（不自动安装）。用法：python3 tools/check_env.py [--skip-terrain]；全部就绪时退出码 0。"""
import importlib.util
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PY = ['numpy', 'scipy', 'PIL', 'edge_tts', 'pytest']
OPTIONAL_PY = {'lunar_python': '农历换算（研究阶段可用查表代替）'}


def has_npm_pkg(pkg: str) -> bool:
    """沿目录向上找 node_modules/<pkg>（与 node 的解析一致，符号链接与父目录均可）。"""
    return any((d / 'node_modules' / pkg / 'package.json').exists() for d in [ROOT, *ROOT.parents])


def missing(skip_terrain: bool = False) -> list[str]:
    out = [f'命令 {c}' for c in ('ffmpeg', 'ffprobe', 'node', 'curl') if not shutil.which(c)]
    out += [f'Python 包 {m}' for m in PY if importlib.util.find_spec(m) is None]
    npm_missing = [pkg for pkg in ('three', 'playwright-core') if not has_npm_pkg(pkg)]
    out += [f'npm 包 {pkg}（在项目根目录运行 npm install）' for pkg in npm_missing]
    r = None if 'playwright-core' in npm_missing else subprocess.run(['node', '-e', "import('./render.mjs').then(m=>console.log(m.findChrome())).catch(e=>{console.error(e.message);process.exit(1)})"],
                       cwd=ROOT, capture_output=True, text=True) if shutil.which('node') else None
    if 'playwright-core' in npm_missing:
        pass   # 缺 playwright-core 时 Chromium 探测必然失败，不重复报告
    elif r is None or r.returncode != 0:
        out.append(f"Chromium（{r.stderr.strip() if r else 'node 缺失'}）")
    if not skip_terrain and not (ROOT / 'assets' / 'terrain' / 'world.json').exists():
        out.append('地形缓存（运行 zsh ~/.claude/skills/lifetrail/scripts/setup_terrain.sh <项目目录>）')
    return out


def main() -> int:
    miss = missing('--skip-terrain' in sys.argv[1:])
    for m in miss:
        print('缺失：', m)
    for m, why in OPTIONAL_PY.items():
        if importlib.util.find_spec(m) is None:
            print(f'可选：{m} 未安装（{why}）')
    print('环境就绪' if not miss else f'共 {len(miss)} 项缺失')
    return 1 if miss else 0


if __name__ == '__main__':
    sys.exit(main())
