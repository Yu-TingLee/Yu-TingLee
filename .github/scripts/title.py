# /// script
# dependencies = []
# ///
"""Build the typing title SVGs (assets/title-{dark,light}.svg).

Fetches from readme-typing-svg, then retimes the animation: the service ties
deletion to 20% of the typing duration, which deletes too fast.
"""
import re
import urllib.parse
import urllib.request
from pathlib import Path

LINES = [
    "I need more tokenzzzz... (✖╭╮✖)",
    "Making LLMs go brrr on GPUs!!!",
    "It's all just linear algebra ✨",
]
COLORS = {"dark": "FFC6B3", "light": "F4A28C"}
TYPE_MS, HOLD_MS, DELETE_MS = 2400, 1000, 1800

OUT = Path(__file__).resolve().parents[2] / "assets"


def fetch(color):
    q = urllib.parse.urlencode({
        "font": "Cutive Mono", "color": color, "center": "true", "vCenter": "true",
        "width": "450", "duration": "3000", "pause": "1000", "lines": ";".join(LINES),
    })
    req = urllib.request.Request(f"https://readme-typing-svg.demolab.com?{q}",
                                 headers={"User-Agent": "title.py"})
    return urllib.request.urlopen(req).read().decode()


def retime(svg):
    total = TYPE_MS + HOLD_MS + DELETE_MS
    keys = f"0;{TYPE_MS / total:.4f};{(TYPE_MS + HOLD_MS) / total:.4f};1"
    svg, n = re.subn(r"dur='\d+ms'", f"dur='{total}ms'", svg)
    svg, m = re.subn(r"keyTimes='0;[\d.]+;[\d.]+;1'", f"keyTimes='{keys}'", svg)
    assert n == m == len(LINES), (n, m)
    return svg


for mode, color in COLORS.items():
    path = OUT / f"title-{mode}.svg"
    path.write_text(retime(fetch(color)))
    print("wrote", path)
