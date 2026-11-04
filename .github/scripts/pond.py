# /// script
# dependencies = ["pillow"]
# ///
"""Frame the koi gif with a pond ring of text symbols.

usage: pond.py IN.gif OUT.gif FONT.ttf
Koi pixels are copied untouched; the ring is drawn without anti-aliasing
so it matches the pixel-art koi and survives GIF's 1-bit transparency.
"""
import sys
from itertools import cycle

from PIL import Image, ImageDraw, ImageFont, ImageSequence

MARGIN = 34  # ring band width around the koi, px
WIDTH = 795  # pond width = README slideshow row (2 x 395px imgs + gap)
SIZE = 18  # font size, px
COLOR = (226, 140, 112, 255)  # coral, matches design.py palette; readable on light + dark
TOP = "⋆ ˚ ° ∿ ~ ∿ ° ˚ ✧ ˚ °".split()  # mirrored around a center ☁
SIDE = "˚ ° ∿ ⋆ ° ˚ ~ ✧".split()
BOTTOM_FILL = "∿ ~".split()
FISH = ("><(((°>", "<°)))><")


def text_row(draw, font, y, width, x0, items):
    """Lay items across [x0, x0+width] with equal gaps between them, centered on y."""
    widths = [draw.textlength(s, font=font) for s in items]
    gap = (width - sum(widths)) / len(items)
    x = x0 + gap / 2
    for s, w in zip(items, widths):
        draw.text((x + w / 2, y), s, font=font, fill=COLOR, anchor="mm")
        x += w + gap


def ring(w, h, font):
    W, H = max(WIDTH, w + 2 * MARGIN), h + 2 * MARGIN
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.fontmode = "1"
    step = 26
    # top: pattern mirrored around a center cloud
    half = [s for s, _ in zip(cycle(TOP), range((W // step - 1) // 2))]
    text_row(d, font, MARGIN / 2, W, 0, half + ["☁"] + half[::-1])
    # bottom: water with two fish
    n = (W - 2 * 90) // step
    half = [s for s, _ in zip(cycle(BOTTOM_FILL), range(n // 3))]
    text_row(d, font, H - MARGIN / 2, W, 0, half + [FISH[0]] + half + [FISH[1]] + half)
    # sides
    n = h // step
    for x in (MARGIN / 2, W - MARGIN / 2):
        col = [s for s, _ in zip(cycle(SIDE), range(n))]
        for i, s in enumerate(col):
            cy = MARGIN + h * (i + 0.5) / n
            d.text((x, cy), s, font=font, fill=COLOR, anchor="mm")
    return im


def main(src, dst, font_path):
    koi = Image.open(src)
    font = ImageFont.truetype(font_path, SIZE)
    base = ring(*koi.size, font)
    x = (base.width - koi.width) // 2
    frames, durations = [], []
    for f in ImageSequence.Iterator(koi):
        canvas = base.copy()
        canvas.alpha_composite(f.convert("RGBA"), (x, MARGIN))
        frames.append(canvas)
        durations.append(f.info.get("duration", koi.info.get("duration", 70)))
    frames[0].save(
        dst,
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        loop=koi.info.get("loop", 0),
        disposal=2,
        optimize=False,
    )


if __name__ == "__main__":
    main(*sys.argv[1:4])
