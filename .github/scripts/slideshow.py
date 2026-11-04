#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["pillow"]
# ///
"""Build a crossfading WebP slideshow.

usage: slideshow.py OUT.webp photo|page FILE...
  photo: 800x800 center-crop (portrait shots biased upward to keep faces)
  page:  page as a shadowed sheet on a warm card (rendered PDF page or screenshot)
Both get rounded, transparent corners so they sit well on light + dark GitHub.
"""
import io
import sys
from PIL import Image, ImageCms, ImageDraw, ImageFilter, ImageOps

HOLD_MS = 4000  # time each slide stays
FADE_MS = 480   # crossfade length
SIDE = 800
RADIUS = 44     # ~22px at the README's 395px display width
INSET = 16      # transparent margin -> visible gap between the two side-by-side cards
CARD = "#F8E4DA"  # warm coral-tinted card, matches design.py palette
out, mode, *srcs = sys.argv[1:]
SRGB = ImageCms.createProfile("sRGB")


def load(p):
    im = ImageOps.exif_transpose(Image.open(p))
    icc = im.info.get("icc_profile")
    rgba = im.convert("RGBA")
    bg = Image.new("RGBA", im.size, "white")  # PDF renders are transparent
    im = Image.alpha_composite(bg, rgba).convert("RGB")
    if icc:  # e.g. Display P3 -> sRGB, else colors look off in browsers
        src = ImageCms.ImageCmsProfile(io.BytesIO(icc))
        im = ImageCms.profileToProfile(im, src, SRGB, outputMode="RGB")
    return im


def frame(p):
    im = load(p)
    w, h = im.size
    if mode == "page":
        im = ImageOps.contain(im, (SIDE - 150, SIDE - 110), Image.LANCZOS)
        x, y = (SIDE - im.width) // 2, (SIDE - im.height) // 2 - 6
        canvas = Image.new("RGB", (SIDE, SIDE), CARD)
        shadow = Image.new("L", (SIDE, SIDE), 0)
        ImageDraw.Draw(shadow).rectangle((x, y + 14, x + im.width, y + im.height + 14), fill=70)
        canvas.paste((150, 90, 70), mask=shadow.filter(ImageFilter.GaussianBlur(18)))
        canvas.paste(im, (x, y))
        return canvas
    side = min(w, h)
    x = (w - side) // 2
    y = int((h - side) * (0.25 if h > w else 0.5))
    return im.crop((x, y, x + side, y + side)).resize((SIDE, SIDE), Image.LANCZOS)


def rounded(im, mask):
    im = im.convert("RGBA")
    im.putalpha(mask)
    return im


print(f"{out}: loading {len(srcs)} images...", flush=True)
imgs = [frame(p) for p in srcs]
steps = 3 if mode == "page" else 8  # text-heavy fades are costly
frames, durs = [], []
for i, a in enumerate(imgs):
    b = imgs[(i + 1) % len(imgs)]
    frames.append(a); durs.append(HOLD_MS)
    for k in range(1, steps):
        frames.append(Image.blend(a, b, k / steps)); durs.append(FADE_MS // (steps - 1))
big = Image.new("L", (SIDE * 4, SIDE * 4), 0)  # 4x supersampled for smooth corners
ImageDraw.Draw(big).rounded_rectangle((INSET * 4, INSET * 4, (SIDE - INSET) * 4 - 1, (SIDE - INSET) * 4 - 1), RADIUS * 4, fill=255)
mask = big.resize((SIDE, SIDE), Image.LANCZOS)
frames = [rounded(f, mask) for f in frames]
print(f"{out}: encoding {len(frames)} frames...", flush=True)
frames[0].save(out, save_all=True, append_images=frames[1:], duration=durs, loop=0,
               quality=75 if mode == "page" else 85, method=4)  # 6 = smaller but ~3x slower
print(f"built {out} from {len(imgs)} images")
