"""把多张 still 拼成 2×2 预览图（审片用）。用法：python3 tools/montage.py out.jpg a.jpg b.jpg c.jpg d.jpg"""
import sys
from PIL import Image, ImageDraw
out, files = sys.argv[1], sys.argv[2:]
W, H = 960, 540
canvas = Image.new('RGB', (W * 2, H * ((len(files) + 1) // 2)), 'black')
for i, f in enumerate(files):
    im = Image.open(f).resize((W, H))
    ImageDraw.Draw(im).text((8, 8), f.split('_')[-1], fill='yellow')
    canvas.paste(im, ((i % 2) * W, (i // 2) * H))
canvas.save(out, quality=85)
