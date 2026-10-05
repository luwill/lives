"""Natural Earth 10m 河流/湖泊 → data/common/rivers.geojson、lakes.geojson（裁剪到中国范围，带中文名）。
用法：python3 data/_build/build_geo.py
依赖：仅标准库 + numpy（自带极简 shp/dbf 读取，避免引入 pyshp）。
"""
import json
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
NE = ROOT / 'data' / '_build' / 'cache' / 'ne'
OUT = ROOT / 'data' / 'common'
BBOX = (70, 15, 138, 55)


def read_dbf(path: Path) -> list[dict]:
    b = path.read_bytes()
    n, hlen, rlen = struct.unpack('<IHH', b[4:12])
    fields, off = [], 32
    while b[off] != 0x0D:
        name = b[off:off + 11].split(b'\0')[0].decode('latin1')
        fields.append((name, b[off + 16]))
        off += 32
    recs = []
    for i in range(n):
        r = b[hlen + i * rlen + 1: hlen + (i + 1) * rlen]
        rec, p = {}, 0
        for name, ln in fields:
            rec[name] = r[p:p + ln].decode('utf-8', 'replace').strip('\x00 ')
            p += ln
        recs.append(rec)
    return recs


def read_shp(path: Path) -> list[list[list[tuple]]]:
    """返回每条记录的 parts（点列表）；支持 PolyLine(3) / Polygon(5)。"""
    b = path.read_bytes()
    off, out = 100, []
    while off < len(b):
        _, clen = struct.unpack('>II', b[off:off + 8])
        rec = b[off + 8: off + 8 + clen * 2]
        off += 8 + clen * 2
        st = struct.unpack('<i', rec[:4])[0]
        if st not in (3, 5):
            out.append([])
            continue
        nparts, npts = struct.unpack('<ii', rec[36:44])
        parts = list(struct.unpack(f'<{nparts}i', rec[44:44 + 4 * nparts])) + [npts]
        pts = struct.unpack(f'<{2 * npts}d', rec[44 + 4 * nparts: 44 + 4 * nparts + 16 * npts])
        xy = list(zip(pts[0::2], pts[1::2]))
        out.append([xy[parts[k]:parts[k + 1]] for k in range(nparts)])
    return out


def in_bbox(part: list[tuple]) -> bool:
    return any(BBOX[0] <= x <= BBOX[2] and BBOX[1] <= y <= BBOX[3] for x, y in part)


def build(stem: str, out_name: str, min_rank: int) -> None:
    recs = read_dbf(NE / f'{stem}.dbf')
    geoms = read_shp(NE / f'{stem}.shp')
    feats = []
    for rec, parts in zip(recs, geoms):
        parts = [[(round(x, 4), round(y, 4)) for x, y in p] for p in parts if in_bbox(p)]
        if not parts:
            continue
        rank = int(float(rec.get('scalerank') or 99))
        if rank > min_rank:
            continue
        feats.append({'type': 'Feature', 'properties': {
            'name': rec.get('name', ''), 'name_zh': rec.get('name_zh', ''), 'rank': rank},
            'geometry': {'type': 'MultiLineString', 'coordinates': parts}})
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / out_name).write_text(json.dumps({'type': 'FeatureCollection', 'features': feats}, ensure_ascii=False))
    print(out_name, len(feats), 'features', sum(len(p) for f in feats for p in f['geometry']['coordinates']), 'pts')


if __name__ == '__main__':
    build('ne_10m_rivers_lake_centerlines', 'rivers.geojson', 8)
    build('ne_10m_lakes', 'lakes.geojson', 6)
