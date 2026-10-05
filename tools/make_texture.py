"""由 DEM 生成地形贴图（分层设色 × 晕渲）与 three.js 用的高度图。
用法：python3 tools/make_texture.py <name>
输出：assets/terrain/<name>_tex.jpg、<name>_h.png（16 位灰度高度）、<name>.json 追加 hmin/hmax
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, label, median_filter

GRID = 800
T = Path(__file__).resolve().parent.parent / 'assets' / 'terrain'

# (海拔 m, RGB) —— 偏旧地图的低饱和自然色
# 辽西/辽河平原海拔多在 0–100 m，低处色阶要细，否则平原和丘陵分不开
STOPS = [(0, (70, 92, 62)), (40, (80, 100, 64)), (120, (98, 112, 70)), (250, (122, 126, 80)), (500, (146, 138, 92)),
         (900, (168, 150, 110)), (1500, (190, 176, 150)), (2500, (222, 216, 204)), (4000, (245, 245, 245))]


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


def main(name: str) -> None:
    meta = json.loads((T / f'{name}.json').read_text())
    dem = np.load(T / f'{name}.npy')
    # Terrarium 局部有负值噪点，先中值去噪再截断
    # 海洋：大片连通的 ≤0 m 区域（小块负值是 Terrarium 噪点，按陆地修补）
    lab, _ = label(dem <= 0)
    sizes = np.bincount(lab.ravel())
    sizes[0] = 0
    ocean = sizes[lab] > 20000
    bad = (dem < 0) & ~ocean
    dem = np.where(bad, median_filter(dem, 9), dem)
    dem = np.clip(dem, 1, None)
    cell = (meta['lon1'] - meta['lon0']) * 111320 * np.cos(np.radians((meta['lat0'] + meta['lat1']) / 2)) / meta['w']
    shade = hillshade(gaussian_filter(dem, 0.8), cell)
    col = tint(dem) * (0.35 + 0.8 * shade[..., None])
    col[ocean] = (34, 58, 78)
    # 轻微暗角，聚焦画面中心
    h, w = dem.shape
    yy, xx = np.mgrid[0:h, 0:w]
    vig = 1 - 0.25 * (((xx / w - 0.5) ** 2 + (yy / h - 0.5) ** 2) * 2.2)
    col = np.clip(col, 0, 255).astype(np.uint8)   # 不加暗角：两级地形拼接处需无缝
    Image.fromarray(col).save(T / f'{name}_tex.jpg', quality=92)
    hmin, hmax = float(dem.min()), float(dem.max())
    h16 = ((dem - hmin) / (hmax - hmin) * 65535).astype(np.uint16)
    Image.fromarray(h16).save(T / f'{name}_h.png')
    # 网格高度（three.js 顶点用）：降采样到 GRID 列，uint16 小端
    gw = GRID
    gh = round(gw * h / w)
    small = np.asarray(Image.fromarray(dem.astype(np.float32)).resize((gw, gh), Image.BILINEAR))
    ((small - hmin) / (hmax - hmin) * 65535).astype('<u2').tofile(T / f'{name}_h.bin')
    meta.update(hmin=hmin, hmax=hmax, cell_m=float(cell), gw=gw, gh=gh)
    (T / f'{name}.json').write_text(json.dumps(meta, indent=1))
    print(name, meta)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
