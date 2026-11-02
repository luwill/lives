"""由 DEM 生成地形贴图（分层设色 × 晕渲 + 烘焙河湖）与 three.js 用的高度网格。
用法：python3 tools/make_texture.py <name> [grid_w] [--sat]
--sat：以 <name>_sat.jpg（fetch_imagery.py 生成的 Sentinel-2 无云影像）为底色，叠多方向晕渲，代替分层设色
输出：assets/terrain/<name>_tex.jpg、<name>_h.bin（uint16 网格）、<name>.json 追加 hmin/hmax/gw/gh
河流与湖泊直接画进贴图：垂直夸张随镜头变化时，贴图上的河流始终贴合地面。
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import binary_dilation, gaussian_filter, label, median_filter

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


def hillshade_md(dem: np.ndarray, cell_m: float) -> np.ndarray:
    """多方向晕渲：西北主光加三个辅光，山体背光面不至于全黑，细节更立体。"""
    w = {315: 0.45, 270: 0.2, 360: 0.2, 225: 0.15}
    return sum(k * hillshade(dem, cell_m, az, 42) for az, k in w.items())


def declutter_clouds(sat: np.ndarray, land: np.ndarray) -> np.ndarray:
    """去云渣：2016 版无云影像在秦岭、川西等多云区残留白色碎云。
    判据：亮（灰度 >150）、近乎无色（通道差 <28）、海拔 <3800 m（高山积雪不动）；
    掩膜外扩 2 像素后，用周围非云像素的高斯加权平均（归一化卷积）填补。"""
    lum = sat.mean(-1)
    spread = sat.max(-1) - sat.min(-1)
    cloud = (lum > 150) & (spread < 28) & (land < 3800)
    cloud = binary_dilation(cloud, iterations=2)
    keep = (~cloud).astype(np.float32)
    out = sat.copy()
    todo = cloud.copy()
    for sigma in (8, 32, 96):          # 大片云区附近没有晴空像素：逐级放大半径，避免除以 0 填成黑块
        w = gaussian_filter(keep, sigma)
        ok = todo & (w > 0.05)
        for c in range(3):
            fill = gaussian_filter(sat[..., c] * keep, sigma) / np.maximum(w, 1e-6)
            out[..., c] = np.where(ok, fill, out[..., c])
        todo &= ~ok
    print('clouds filled', f'{cloud.mean():.2%}')
    return out


def satellite(name: str, land: np.ndarray, ocean: np.ndarray, cell: float) -> np.ndarray:
    """卫星底色 × 晕渲：平地亮度基本不变，山体按坡向明暗；海面与旧配色各半，保持统一色调。"""
    sat = np.asarray(Image.open(T / f'{name}_sat.jpg').convert('RGB')).astype(np.float32)
    assert sat.shape[:2] == land.shape, (sat.shape, land.shape)
    sat = declutter_clouds(sat, land)
    shade = hillshade_md(gaussian_filter(land, 0.7), cell)
    flat = np.sin(np.radians(42))
    lum = sat.mean(-1, keepdims=True)
    sat = lum + (sat - lum) * 1.12                       # 略提饱和度
    col = sat * np.clip(1 + 1.15 * (shade - flat), 0.35, 1.6)[..., None]
    return np.where(ocean[..., None], col * 0.5 + OCEAN_SHALLOW * 0.5, col)


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


def main(name: str, grid_w: int, use_sat: bool = False) -> None:
    meta = json.loads((T / f'{name}.json').read_text())
    dem = np.load(T / f'{name}.npy')
    ocean = ocean_mask(dem)
    depth = np.clip(-dem, 0, 4000)
    bad = (dem < 0) & ~ocean           # Terrarium 局部负值噪点按陆地修补
    dem = np.where(bad, median_filter(dem, 9), dem)
    # Terrarium 偶有单像素高程尖峰（华东平原出现 5000 m 以上）：高出 5×5 中值 800 m 以上的点按中值修补
    med = median_filter(dem, 5)
    dem = np.where(dem - med > 800, med, dem)
    land = np.clip(dem, 1, None)
    cell = (meta['lon1'] - meta['lon0']) * 111320 * np.cos(np.radians((meta['lat0'] + meta['lat1']) / 2)) / meta['w']
    if use_sat:
        col = satellite(name, land, ocean, cell)
    else:
        shade = hillshade(gaussian_filter(land, 0.8), cell)
        col = tint(land) * (0.38 + 0.78 * shade[..., None])
        k = (np.sqrt(depth / 4000))[..., None]
        col = np.where(ocean[..., None], OCEAN_SHALLOW * (1 - k) + OCEAN_DEEP * k, col)
    img = Image.fromarray(np.clip(col, 0, 255).astype(np.uint8))
    if use_sat:                       # 卫星上已有水体：河湖半透明叠加，保证可读又不抢真实地貌
        water = img.copy()
        draw_water(water, meta, cell / 1000)
        img = Image.blend(img, water, 0.6)
    else:
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
    args = [a for a in sys.argv[1:] if a != '--sat']
    if len(args) not in (1, 2):
        sys.exit(__doc__)
    main(args[0], int(args[1]) if len(args) == 2 else 1024, '--sat' in sys.argv)
