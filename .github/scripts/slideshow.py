"""Build a crossfading square WebP slideshow.

usage: slideshow.py OUT.webp photo|page FILE...
  photo: center-crop to square (portrait shots biased upward to keep faces)
  page:  rendered PDF page; crop top square inside the margins (title + abstract)
"""
import sys
from PIL import Image, ImageOps

S = 640
out, mode, *srcs = sys.argv[1:]

def square(p):
    im = ImageOps.exif_transpose(Image.open(p)).convert("RGBA")
    bg = Image.new("RGBA", im.size, "white")  # PDF renders are transparent
    im = Image.alpha_composite(bg, im).convert("RGB")
    w, h = im.size
    if mode == "page":
        m = int(w * 0.07)
        side = w - 2 * m
        box = (m, int(h * 0.04), m + side, int(h * 0.04) + side)
    else:
        side = min(w, h)
        x = (w - side) // 2
        y = int((h - side) * (0.25 if h > w else 0.5))
        box = (x, y, x + side, y + side)
    return im.crop(box).resize((S, S), Image.LANCZOS)

imgs = [square(p) for p in srcs]
frames, durs = [], []
for i, a in enumerate(imgs):
    b = imgs[(i + 1) % len(imgs)]
    frames.append(a); durs.append(3000)  # time each slide stays (ms)
    steps = 3 if mode == "page" else 8  # text-heavy fades are costly
    for k in range(1, steps):
        frames.append(Image.blend(a, b, k / steps)); durs.append(480 // (steps - 1))  # every fade ~480ms total
frames[0].save(out, save_all=True, append_images=frames[1:], duration=durs,
               loop=0, quality=70 if mode == "page" else 80, method=6)
print(f"built {out} from {len(imgs)} images")
