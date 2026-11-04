# /// script
# dependencies = []
# ///
"""Build README design SVGs into assets/: hero, link buttons, section headers.

Each comes in -light/-dark. Fonts are fetched from Google Fonts and embedded so
GitHub renders them identically everywhere. The hero wraps assets/title-*.svg,
so run title.py first if the title lines or colors change.
"""
import base64
import re
import urllib.request
from pathlib import Path

OUT = Path(__file__).resolve().parents[2] / "assets"

# Keep in sync with title.py COLORS and the snake workflow.
P = {
    "light": dict(accent="#F49A78", deep="#CF5F3E", soft="#FFEAE1", ink="#4A3530", muted="#957D74", bg="#FFFFFF"),
    "dark":  dict(accent="#FFBBA0", deep="#FF9E80", soft="#3B231C", ink="#F5E5DF", muted="#A8918A", bg="#0D1117"),
}
HERO_LINES = ["🫧 LLM inference · CUDA kernels · Quantum ML", "💻 Python · C++ · CUDA   📷 Photography"]
BUTTONS = ["LinkedIn", "Email"]
HEADERS_A = {"writing": ("writing", "Thoughts unbounded"), "photos": ("photography", "Catching light")}
HEADERS_C = {"pond": "Swimming in commits"}

ICONS = {
    "Website": '<circle cx="12" cy="12" r="10"/><path d="M2 12h20M12 2a15 15 0 0 1 0 20M12 2a15 15 0 0 0 0 20"/>',
    "Scholar": '<path d="M2 9l10-5 10 5-10 5z"/><path d="M6 11v5c3 2 9 2 12 0v-5"/>',
    "LinkedIn": '<rect x="3" y="3" width="18" height="18" rx="3"/><path d="M8 10v7M8 7v.01M12 17v-4a2 2 0 0 1 4 0v4M12 10v7"/>',
    "Email": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 6 9-6"/>',
}


def font(family, css_name):
    """Latin woff2 subset of a Google Font as an @font-face rule."""
    ua = {"User-Agent": "Mozilla/5.0 (Macintosh) AppleWebKit/537.36 Chrome/120 Safari/537.36"}
    css = urllib.request.urlopen(urllib.request.Request(
        f"https://fonts.googleapis.com/css2?family={family}", headers=ua)).read().decode()
    url = re.findall(r"url\((https://[^)]+\.woff2)\)", css)[-1]  # latin block is last
    data = base64.b64encode(urllib.request.urlopen(url).read()).decode()
    return f"@font-face{{font-family:'{css_name}';src:url(data:font/woff2;base64,{data}) format('woff2')}}"


MONO = font("Cutive+Mono", "CM")
HAND = font("Caveat:wght@500", "CV")


def svg(w, h, style, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'width="{w}" height="{h}" viewBox="0 0 {w} {h}"><style>{style}</style>{body}</svg>')


def button(label, c):
    """Outline pill with a stroke icon."""
    w = int(len(label) * 8.4 + 64)
    return svg(w, 44, MONO + f".t{{font-family:CM,monospace;font-size:14px;fill:{c['deep']}}}",
               f'<rect x="2" y="2" width="{w - 4}" height="40" rx="20" fill="none" stroke="{c["accent"]}" stroke-width="1.5"/>'
               f'<g transform="translate(20,14) scale(.667)" fill="none" stroke="{c["deep"]}" stroke-width="2.2" '
               f'stroke-linecap="round" stroke-linejoin="round">{ICONS[label]}</g>'
               f'<text class="t" x="44" y="27">{label}</text>')


def header_a(label, title, c, w=395):
    """Tiny spaced caps label over a handwritten title."""
    return svg(w, 72, MONO + HAND +
               f".l{{font-family:CM,monospace;font-size:12px;letter-spacing:3px;fill:{c['deep']}}}"
               f".t{{font-family:CV,cursive;font-size:34px;fill:{c['ink']}}}",
               f'<g text-anchor="middle"><text class="l" x="{w / 2}" y="18">{label.upper()}</text>'
               f'<text class="t" x="{w / 2}" y="58">{title}</text></g>')


def header_c(title, c, w=900):
    """Handwritten title over a drifting pond-ripple underline."""
    wave = "M0 6 " + " ".join(f"q 10 {-5 if i % 2 == 0 else 5} 20 0" for i in range(30))
    return svg(w, 76, HAND + f".t{{font-family:CV,cursive;font-size:36px;fill:{c['ink']}}}"
               ".r{animation:r 4s linear infinite}@keyframes r{to{transform:translateX(-40px)}}",
               f'<defs><clipPath id="cw"><rect x="{w / 2 - 150}" y="0" width="300" height="20"/></clipPath>'
               f'<linearGradient id="fw"><stop offset="0" stop-color="{c["accent"]}" stop-opacity="0"/>'
               f'<stop offset=".5" stop-color="{c["accent"]}"/><stop offset="1" stop-color="{c["accent"]}" stop-opacity="0"/></linearGradient></defs>'
               f'<text class="t" x="{w / 2}" y="40" text-anchor="middle">{title}</text>'
               f'<g transform="translate(0,52)" clip-path="url(#cw)"><path class="r" d="{wave}" transform="translate({w / 2 - 150},0)" '
               f'fill="none" stroke="url(#fw)" stroke-width="2" stroke-linecap="round"/></g>')


def hero(mode, c):
    """Typing title on a rounded card with drifting blurred blobs."""
    title = re.sub(r"<!--.*?-->", "", (OUT / f"title-{mode}.svg").read_text(), flags=re.S)
    inner = re.search(r"<svg[^>]*>(.*)</svg>", title, re.S).group(1)
    w, h = 900, 230
    lines = "".join(f'<text class="m" x="{w / 2}" y="{148 + 28 * i}">{t}</text>' for i, t in enumerate(HERO_LINES))
    return svg(w, h,
               ".b1{animation:f1 14s ease-in-out infinite}.b2{animation:f2 18s ease-in-out infinite}"
               ".b3{animation:f1 22s ease-in-out infinite reverse}"
               "@keyframes f1{0%,100%{transform:translate(0,0)}50%{transform:translate(40px,18px)}}"
               "@keyframes f2{0%,100%{transform:translate(0,0)}50%{transform:translate(-36px,-14px)}}"
               + MONO + f".m{{font-family:CM,monospace;font-size:16px;fill:{c['ink']}}}",
               f'<defs><radialGradient id="bg" cx="50%" cy="0%" r="90%"><stop offset="0" stop-color="{c["soft"]}"/>'
               f'<stop offset="1" stop-color="{c["bg"]}"/></radialGradient>'
               f'<filter id="bl" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="45"/></filter>'
               f'<clipPath id="cd"><rect width="{w}" height="{h}" rx="24"/></clipPath></defs>'
               f'<g clip-path="url(#cd)"><rect width="{w}" height="{h}" fill="url(#bg)"/>'
               f'<g filter="url(#bl)" opacity="{.5 if mode == "light" else .35}">'
               f'<circle class="b1" cx="230" cy="90" r="110" fill="{c["accent"]}"/>'
               f'<circle class="b2" cx="680" cy="70" r="120" fill="{c["deep"]}" opacity=".6"/>'
               f'<circle class="b3" cx="470" cy="210" r="100" fill="{c["accent"]}"/></g>'
               f'<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="23.5" fill="none" stroke="{c["accent"]}" stroke-opacity=".35"/></g>'
               f'<svg x="{w / 2 - 337}" y="40" width="675" height="75" viewBox="0 0 450 50">{inner}</svg>'
               f'<g text-anchor="middle">{lines}</g>')


def write(name, s):
    (OUT / name).write_text(s)
    print("wrote", OUT / name)


for mode, c in P.items():
    write(f"hero-{mode}.svg", hero(mode, c))
    for label in BUTTONS:
        write(f"btn-{label.lower()}-{mode}.svg", button(label, c))
    for key, (label, title) in HEADERS_A.items():
        write(f"head-{key}-{mode}.svg", header_a(label, title, c))
    for key, title in HEADERS_C.items():
        write(f"head-{key}-{mode}.svg", header_c(title, c))
