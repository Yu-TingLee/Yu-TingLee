"""Build a crossfading WebP slideshow.

usage: slideshow.py OUT.webp photo|page FILE...
  photo: 800x800 center-crop (portrait shots biased upward to keep faces)
  page:  full page centered in an 800x800 white square (rendered PDF page or screenshot)
"""
import io
import sys
from PIL import Image, ImageCms, ImageOps

HOLD_MS = 4000  # time each slide stays
FADE_MS = 480   # crossfade length
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
        W, H = 800, 800  # square, same as photos
        im = ImageOps.contain(im, (W, H), Image.LANCZOS)
        canvas = Image.new("RGB", (W, H), "white")
        canvas.paste(im, ((W - im.width) // 2, (H - im.height) // 2))
        return canvas
    side = min(w, h)
    x = (w - side) // 2
    y = int((h - side) * (0.25 if h > w else 0.5))
    return im.crop((x, y, x + side, y + side)).resize((800, 800), Image.LANCZOS)


imgs = [frame(p) for p in srcs]
steps = 3 if mode == "page" else 8  # text-heavy fades are costly
frames, durs = [], []
for i, a in enumerate(imgs):
    b = imgs[(i + 1) % len(imgs)]
    frames.append(a); durs.append(HOLD_MS)
    for k in range(1, steps):
        frames.append(Image.blend(a, b, k / steps)); durs.append(FADE_MS // (steps - 1))
frames[0].save(out, save_all=True, append_images=frames[1:], duration=durs, loop=0,
               quality=75 if mode == "page" else 85, method=6)
print(f"built {out} from {len(imgs)} images")
