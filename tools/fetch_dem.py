"""下载 Terrarium DEM 瓦片，拼接并重采样为等经纬度网格（float32 米）。
用法：python3 tools/fetch_dem.py <name> <lon0> <lon1> <lat0> <lat1> <zoom> <out_w>
输出：assets/terrain/<name>.npy 以及 <name>.json（范围、尺寸）
"""
import io
import json
import math
import sys
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
from PIL import Image
from scipy.ndimage import map_coordinates

URL = 'https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png'
CACHE = Path(__file__).resolve().parent.parent / 'assets' / 'terrain' / 'tiles'
OUT = CACHE.parent


def tile_xy(lon, lat, z):
    n = 2 ** z
    x = (lon + 180) / 360 * n
    y = (1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * n
    return x, y


def valid(p):
    try:
        Image.open(p).convert('RGB')
        return True
    except Exception:
        return False


def fetch(z, x, y):
    p = CACHE / f'{z}_{x}_{y}.png'
    if not p.exists() or not valid(p):
        # 系统 Python 缺根证书，改用 curl 下载
        # 带宽被其他下载占用时会出现半截文件（curl 18），写临时文件、成功后再改名
        tmp = p.with_suffix('.part')
        subprocess.run(['curl', '-sfL', '--retry', '6', '--retry-all-errors', '-o', str(tmp), URL.format(z=z, x=x, y=y)], check=True)
        tmp.rename(p)
    rgb = np.asarray(Image.open(io.BytesIO(p.read_bytes())).convert('RGB')).astype(np.float32)
    return rgb[..., 0] * 256 + rgb[..., 1] + rgb[..., 2] / 256 - 32768


def main(name, lon0, lon1, lat0, lat1, z, out_w):
    CACHE.mkdir(parents=True, exist_ok=True)
    fx0, fy0 = tile_xy(lon0, lat1, z)
    fx1, fy1 = tile_xy(lon1, lat0, z)
    xs, ys = range(int(fx0), int(fx1) + 1), range(int(fy0), int(fy1) + 1)
    jobs = [(z, x, y) for y in ys for x in xs]
    with ThreadPoolExecutor(8) as ex:
        tiles = list(ex.map(lambda a: fetch(*a), jobs))
    mosaic = np.zeros((len(ys) * 256, len(xs) * 256), np.float32)
    for (zz, x, y), t in zip(jobs, tiles):
        mosaic[(y - ys[0]) * 256:(y - ys[0] + 1) * 256, (x - xs[0]) * 256:(x - xs[0] + 1) * 256] = t
    # 等经纬度网格；高宽比按纬度中心 cos 修正，使格网近似等距
    mid = math.radians((lat0 + lat1) / 2)
    out_h = round(out_w * (lat1 - lat0) / ((lon1 - lon0) * math.cos(mid)))
    lons = np.linspace(lon0, lon1, out_w)
    lats = np.linspace(lat1, lat0, out_h)
    LON, LAT = np.meshgrid(lons, lats)
    n = 2 ** z
    px = ((LON + 180) / 360 * n - xs[0]) * 256
    py = ((1 - np.arcsinh(np.tan(np.radians(LAT))) / np.pi) / 2 * n - ys[0]) * 256
    dem = map_coordinates(mosaic, [py, px], order=1, mode='nearest').astype(np.float32)
    np.save(OUT / f'{name}.npy', dem)
    meta = dict(lon0=lon0, lon1=lon1, lat0=lat0, lat1=lat1, w=out_w, h=out_h,
                min=float(dem.min()), max=float(dem.max()))
    (OUT / f'{name}.json').write_text(json.dumps(meta, indent=1))
    print(name, meta)


if __name__ == '__main__':
    if len(sys.argv) != 8:
        sys.exit(__doc__)
    a = sys.argv
    main(a[1], *map(float, a[2:6]), int(a[6]), int(a[7]))
