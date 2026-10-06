"""下载 Sentinel-2 无云卫星影像（EOX s2cloudless 2022 版，WMTS/3857；2016 版条带接缝与残云明显），重采样到地形层的等经纬度网格。
用法：python3 tools/fetch_imagery.py <name> <zoom>
输入：assets/terrain/<name>.json（范围与贴图宽高，由 fetch_dem.py 生成）
输出：assets/terrain/<name>_sat.jpg（与 <name>_tex.jpg 同尺寸），瓦片缓存在 assets/terrain/s2tiles/
署名：EOxCloudless https://cloudless.eox.at by EOX IT Services GmbH (Contains modified Copernicus Sentinel data 2022)
许可：非商业使用 CC BY-NC-SA 4.0；商业使用需向 EOX 购买授权
"""
import io
import json
import math
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
from PIL import Image
from scipy.ndimage import map_coordinates

YEAR = 2022
URL = f'https://tiles.maps.eox.at/wmts/1.0.0/s2cloudless-{YEAR}_3857/default/g/{{z}}/{{y}}/{{x}}.jpg'
T = Path(__file__).resolve().parent.parent / 'assets' / 'terrain'
CACHE = T / f's2tiles_{YEAR}'


def tile_xy(lon: float, lat: float, z: int) -> tuple:
    n = 2 ** z
    return (lon + 180) / 360 * n, (1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * n


def fetch(z: int, x: int, y: int) -> np.ndarray:
    p = CACHE / f'{z}_{x}_{y}.jpg'
    for _ in range(3):
        if not p.exists():
            tmp = p.with_suffix('.part')
            subprocess.run(['curl', '-sfL', '--retry', '6', '--retry-all-errors', '-o', str(tmp), URL.format(z=z, x=x, y=y)], check=True)
            tmp.rename(p)
        try:
            return np.asarray(Image.open(io.BytesIO(p.read_bytes())).convert('RGB'))
        except OSError:          # 半截文件：删掉重下
            p.unlink()
    raise RuntimeError(f'tile {z}/{x}/{y} unreadable')


def main(name: str, z: int) -> None:
    meta = json.loads((T / f'{name}.json').read_text())
    lon0, lon1, lat0, lat1, w, h = (meta[k] for k in ('lon0', 'lon1', 'lat0', 'lat1', 'w', 'h'))
    CACHE.mkdir(exist_ok=True)
    fx0, fy0 = tile_xy(lon0, min(lat1, 85), z)
    fx1, fy1 = tile_xy(lon1, max(lat0, -85), z)
    xs, ys = range(int(fx0), int(fx1) + 1), range(int(fy0), int(fy1) + 1)
    jobs = [(z, x, y) for y in ys for x in xs]
    print(name, f'z{z}', len(jobs), 'tiles')
    with ThreadPoolExecutor(6) as ex:
        tiles = list(ex.map(lambda a: fetch(*a), jobs))
    mosaic = np.zeros((len(ys) * 256, len(xs) * 256, 3), np.uint8)
    for (_, x, y), t in zip(jobs, tiles):
        mosaic[(y - ys[0]) * 256:(y - ys[0] + 1) * 256, (x - xs[0]) * 256:(x - xs[0] + 1) * 256] = t
    n = 2 ** z
    out = np.zeros((h, w, 3), np.uint8)
    lons = np.linspace(lon0, lon1, w)
    for r0 in range(0, h, 512):          # 分块重采样，控制内存
        lats = np.linspace(lat1, lat0, h)[r0:r0 + 512]
        LON, LAT = np.meshgrid(lons, lats)
        px = ((LON + 180) / 360 * n - xs[0]) * 256
        py = ((1 - np.arcsinh(np.tan(np.radians(LAT))) / np.pi) / 2 * n - ys[0]) * 256
        for c in range(3):
            out[r0:r0 + len(lats), :, c] = map_coordinates(mosaic[..., c], [py, px], order=1, mode='nearest')
    Image.fromarray(out).save(T / f'{name}_sat.jpg', quality=92)
    print(name, 'sat', out.shape)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], int(sys.argv[2]))
