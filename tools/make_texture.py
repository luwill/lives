"""由 DEM 生成地形贴图（分层设色 × 晕渲 + 烘焙河湖）与 three.js 用的高度网格。
用法：python3 tools/make_texture.py <name> [grid_w]
输出：assets/terrain/<name>_tex.jpg、<name>_h.bin（uint16 网格）、<name>.json 追加 hmin/hmax/gw/gh
河流与湖泊直接画进贴图：垂直夸张随镜头变化时，贴图上的河流始终贴合地面。
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import gaussian_filter, label, median_filter

ROOT = Path(__file__).resolve().parent.parent
T = ROOT / 'assets' / 'terrain'
GEO = ROOT / 'data' / 'common'

# (海拔 m, RGB)：低饱和的旧地图配色，平原段色阶更细，高原段过渡到冷灰
STOPS = [(0, (78, 104, 70)), (50, (88, 112, 72)), (200, (110, 124, 78)), (500, (140, 138, 92)), (1000, (164, 148, 106)),
         (1800, (176, 158, 124)), (3000, (170, 160, 142)), (4200, (190, 184, 172)), (5200, (226, 224, 220)), (6500, (250, 250, 252))]
OCEAN_SHALLOW, OCEAN_DEEP = np.array((52, 84, 104)), np.array((22, 40, 60))
RIVER = (96, 156, 196)
LAKE = (70, 122, 160)


def tint(dem: np.ndarray) -> np.ndarray:
    hs = np.array([s[0] for s in STOPS], float)
    cols = np.array([s[1] for s in STOPS], float)
    return np.stack([np.interp(dem, hs, cols[:, k]) for k in range(3)], -1)


def hillshade(dem: np.ndarray, cell_m: float, az: float = 315, alt: float = 40) -> np.ndarray:
    gy, gx = np.gradient(dem, cell_m)
    slope = np.arctan(np.hypot(gx, gy) * 1.6)
    aspect = np.arctan2(-gx, gy)
    a, z = np.radians(az), np.radians(90 - alt)
    return np.clip(np.cos(z) * np.cos(slope) + np.sin(z) * np.sin(slope) * np.cos(a - aspect), 0, 1)


def ocean_mask(dem: np.ndarray) -> np.ndarray:
    """海洋 = 与图边相连的 ≤0 m 区域（吐鲁番盆地等内陆洼地不算）。"""
    lab, _ = label(dem <= 0)
    edge = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    edge = edge[edge > 0]
    return np.isin(lab, edge)


def draw_water(img: Image.Image, meta: dict, cell_km: float) -> None:
    w, h = img.size
    sx, sy = w / (meta['lon1'] - meta['lon0']), h / (meta['lat1'] - meta['lat0'])
    px = lambda c: [((x - meta['lon0']) * sx, (meta['lat1'] - y) * sy) for x, y in c]
    dr = ImageDraw.Draw(img)
    for f in json.loads((GEO / 'lakes.geojson').read_text())['features']:
        for ring in f['geometry']['coordinates']:
            if len(ring) > 2:
                dr.polygon(px(ring), fill=LAKE)
    for f in json.loads((GEO / 'rivers.geojson').read_text())['features']:
        rank = f['properties']['rank']
        km = 3.2 if rank <= 3 else 1.8 if rank <= 6 else 1.1
        width = int(np.clip(round(km / cell_km), 2 if rank <= 3 else 1, 7))
        for line in f['geometry']['coordinates']:
            if len(line) > 1:
                dr.line(px(line), fill=RIVER, width=width, joint='curve')


def main(name: str, grid_w: int) -> None:
    meta = json.loads((T / f'{name}.json').read_text())
    dem = np.load(T / f'{name}.npy')
    ocean = ocean_mask(dem)
    depth = np.clip(-dem, 0, 4000)
    bad = (dem < 0) & ~ocean           # Terrarium 局部负值噪点按陆地修补
    dem = np.where(bad, median_filter(dem, 9), dem)
    land = np.clip(dem, 1, None)
    cell = (meta['lon1'] - meta['lon0']) * 111320 * np.cos(np.radians((meta['lat0'] + meta['lat1']) / 2)) / meta['w']
    shade = hillshade(gaussian_filter(land, 0.8), cell)
    col = tint(land) * (0.38 + 0.78 * shade[..., None])
    k = (np.sqrt(depth / 4000))[..., None]
    col = np.where(ocean[..., None], OCEAN_SHALLOW * (1 - k) + OCEAN_DEEP * k, col)
    img = Image.fromarray(np.clip(col, 0, 255).astype(np.uint8))
    draw_water(img, meta, cell / 1000)
    img.save(T / f'{name}_tex.jpg', quality=90)
    # 网格：海面压平到 0，避免海底地形抬起
    hgt = np.where(ocean, 0, land)
    hmin, hmax = 0.0, float(hgt.max())
    gh = round(grid_w * hgt.shape[0] / hgt.shape[1])
    small = np.asarray(Image.fromarray(hgt.astype(np.float32)).resize((grid_w, gh), Image.BILINEAR))
    ((small - hmin) / (hmax - hmin) * 65535).astype('<u2').tofile(T / f'{name}_h.bin')
    meta.update(hmin=hmin, hmax=hmax, cell_m=float(cell), gw=grid_w, gh=gh)
    (T / f'{name}.json').write_text(json.dumps(meta, indent=1))
    print(name, meta)


if __name__ == '__main__':
    if len(sys.argv) not in (2, 3):
        sys.exit(__doc__)
    main(sys.argv[1], int(sys.argv[2]) if len(sys.argv) == 3 else 1024)
