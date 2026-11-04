# /// script
# dependencies = []
# ///
"""Build README design SVGs into assets/: hero, link buttons, section headers.

Each comes in -light/-dark. Fonts are fetched from Google Fonts and embedded so
GitHub renders them identically everywhere. The hero wraps assets/title-*.svg,
so run title.py first if the title lines or colors change.
"""
import base64
import hashlib
import random
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "assets"

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


STAR = "M0,-{s} Q0,0 {s},0 Q0,0 0,{s} Q0,0 -{s},0 Q0,0 0,-{s}Z"  # 4-point sparkle
TWINKLE = ("@keyframes tw{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.25;transform:scale(.6)}}"
           ".tw{animation:tw 2.4s ease-in-out infinite;transform-box:fill-box;transform-origin:center}")


def cloud(c, opacity=.85):
    return (f'<g fill="{c["accent"]}" opacity="{opacity}"><circle cx="-6" cy="2" r="5"/><circle cx="1" cy="-2" r="7"/>'
            f'<circle cx="8" cy="2" r="5"/><rect x="-6" y="2" width="14" height="5"/></g>')


def divider_sky(c, w=560, h=44):
    """Clouds drifting over scattered twinkling stars, with shooting stars streaking past now and then."""
    # (y, scale, seconds per crossing, start offset as fraction of crossing)
    flock = [(13, 1.0, 26, 0), (31, .75, 34, .17), (20, .6, 30, .33),
             (29, .9, 38, .5), (11, .7, 28, .67), (24, 1.1, 40, .83)]
    clouds = "".join(
        f'<g transform="translate(0,{y})"><g class="fly" style="animation-duration:{t}s;'
        f'animation-delay:-{t * off:.1f}s"><g transform="scale({k})">{cloud(c, .9)}</g></g></g>' for y, k, t, off in flock)
    # Scattered stars: faint most of the time, each flaring briefly at its own pace.
    rng = random.Random(4)
    twinkles = "".join(
        f'<g transform="translate({x:.0f},{rng.uniform(5, h - 5):.0f})"><g class="gl" style="animation-duration:'
        f'{rng.uniform(8, 16):.1f}s;animation-delay:-{rng.uniform(0, 16):.1f}s">'
        f'<path d="{STAR.format(s=round(1.5 + 5 * rng.random() ** 2, 1))}" fill="{c["deep"]}"/></g></g>'
        for x in [w * (i + rng.uniform(.2, .8)) / 16 for i in range(16)])
    # (y start, y end, delay s) within a 9s cycle; each streak is visible for ~1.6s
    streaks = [(4, 20, 0), (10, 30, 4.6)]
    stars = "".join(
        f'<g class="sh" style="animation-name:sh{i};animation-delay:{d}s">'
        f'<rect x="-60" y="-.8" width="60" height="1.6" rx=".8" fill="url(#sg)"/>'
        f'<path d="{STAR.format(s=3.2)}" fill="{c["deep"]}"/></g>' for i, (y0, y1, d) in enumerate(streaks))
    css = (f"@keyframes fly{{from{{transform:translateX(-30px)}}to{{transform:translateX({w + 30}px)}}}}"
           ".fly{animation:fly linear infinite}"
           ".sh{animation:sh0 9s ease-in infinite;opacity:0}"
           "@keyframes gl{0%,45%,100%{opacity:.2;transform:scale(.7)}72%{opacity:1;transform:scale(1.1)}}"
           ".gl{animation:gl ease-in-out infinite;transform-box:fill-box;transform-origin:center}"
           + "".join(f"@keyframes sh{i}{{0%{{transform:translate(-20px,{y0}px) rotate(2deg);opacity:0}}3%{{opacity:1}}"
                     f"18%{{transform:translate({w * .85:.0f}px,{y1}px) rotate(2deg);opacity:0}}100%{{opacity:0}}}}"
                     for i, (y0, y1, _) in enumerate(streaks)))
    defs = (f'<defs><linearGradient id="eg"><stop offset="0" stop-color="#fff" stop-opacity="0"/>'
            f'<stop offset=".12" stop-color="#fff"/><stop offset=".88" stop-color="#fff"/>'
            f'<stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
            f'<mask id="em"><rect width="{w}" height="{h}" fill="url(#eg)"/></mask>'
            f'<linearGradient id="sg"><stop offset="0" stop-color="{c["deep"]}" stop-opacity="0"/>'
            f'<stop offset="1" stop-color="{c["deep"]}"/></linearGradient></defs>')
    return svg(w, h, css, defs + f'<g mask="url(#em)">{twinkles}{clouds}{stars}</g>')


def divider_kaomoji(c, w=560, h=40):
    """Drifting clouds and glowing moons around a blinking kaomoji."""
    cloud_ = cloud(c)
    moon = f'<circle r="7" fill="{c["deep"]}" mask="url(#cr)"/>'
    dot = f'<circle r="1.6" fill="{c["accent"]}"/>'
    left = [(60, dot), (88, cloud_), (118, dot), (136, dot), (162, moon), (186, dot)]
    body = ['<defs><mask id="cr"><circle r="7" fill="#fff"/><circle cx="3.5" cy="-2.5" r="6" fill="#000"/></mask></defs>']
    for x, g in left:
        for xx, flip in ((x, 1), (w - x, -1)):
            cls = "dr" if g is cloud_ else "gl" if g is moon else "tw"
            body.append(f'<g transform="translate({xx},{h / 2}) scale({flip},1)"><g class="{cls}" '
                        f'style="animation-delay:{(x % 7) * .3:.1f}s">{g}</g></g>')
    face = (f'<text class="k" x="{w / 2}" y="{h / 2 + 7}">(˶ᵔ ᵕ ᵔ˶)</text>'
            f'<text class="k shut" x="{w / 2}" y="{h / 2 + 7}">(˶˘ ᵕ ˘˶)</text>')
    style = (TWINKLE + f".k{{font-size:22px;fill:{c['ink']};text-anchor:middle}}"
             ".k{animation:open 4s steps(1) infinite}.shut{animation-name:shut}"
             "@keyframes open{0%,90%{opacity:1}91%,96%{opacity:0}97%{opacity:1}}"
             "@keyframes shut{0%,90%{opacity:0}91%,96%{opacity:1}97%{opacity:0}}"
             ".dr{animation:dr 6s ease-in-out infinite}@keyframes dr{0%,100%{transform:translateX(-4px)}50%{transform:translateX(4px)}}"
             ".gl{animation:gl 3s ease-in-out infinite}@keyframes gl{0%,100%{opacity:1}50%{opacity:.45}}")
    return svg(w, h, style, "".join(body) + face)


def stamp_readme():
    """Append ?v=<content hash> to README asset links so browsers and GitHub's cache refetch changed files."""
    readme = ROOT / "README.md"

    def bump(m):
        digest = hashlib.sha1((ROOT / m[1]).read_bytes()).hexdigest()[:8]
        return f"{m[1]}?v={digest}"

    readme.write_text(re.sub(r"(assets/[\w.-]+\.(?:svg|webp))(?:\?v=\w+)?", bump, readme.read_text()))


def write(name, s):
    (OUT / name).write_text(s)
    print("wrote", OUT / name)



if __name__ == "__main__":
    for mode, c in P.items():
        write(f"hero-{mode}.svg", hero(mode, c))
        for label in BUTTONS:
            write(f"btn-{label.lower()}-{mode}.svg", button(label, c))
        for key, (label, title) in HEADERS_A.items():
            write(f"head-{key}-{mode}.svg", header_a(label, title, c))
        for key, title in HEADERS_C.items():
            write(f"head-{key}-{mode}.svg", header_c(title, c))
        write(f"div-sky-{mode}.svg", divider_sky(c))
        write(f"div-kaomoji-{mode}.svg", divider_kaomoji(c))
    stamp_readme()
