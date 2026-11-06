"""ÉLVARÉ brand asset builder.

Generates the outlined wordmark, monogram, favicon SVG and self-hosted web fonts.
Text is converted to vector paths so the logo renders identically everywhere.
Run from project root:  python3 tools/build_brand.py
"""
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools import subset

ROOT = Path(__file__).resolve().parent.parent
BRAND = ROOT / "assets" / "brand"
FONTS = ROOT / "assets" / "fonts"
LM = "/usr/share/texmf/fonts/opentype/public/lm/"
DISPLAY = LM + "lmroman17-regular.otf"

OBSIDIAN, IVORY, GOLD = "#111111", "#F5F1E9", "#C6A66B"


def text_path(font_path, text, size, tracking):
    """Return (svg path d, width, cap height) for text at given em size and tracking (em fraction)."""
    f = TTFont(font_path)
    gs = f.getGlyphSet()
    cmap = f.getBestCmap()
    upm = f["head"].unitsPerEm
    scale = size / upm
    pen = SVGPathPen(gs)
    x = 0.0
    names = [cmap[ord(c)] for c in text]
    for i, n in enumerate(names):
        # flip y: font units are y-up, SVG is y-down; baseline at y=0
        tp = TransformPen(pen, (scale, 0, 0, -scale, x, 0))
        gs[n].draw(tp)
        x += gs[n].width * scale
        if i < len(names) - 1:
            x += tracking * size
    cap = f["OS/2"].sCapHeight * scale if hasattr(f["OS/2"], "sCapHeight") else 0.7 * size
    return pen.getCommands(), x, cap


def wordmark(fill, name, tagline=False):
    size = 100
    d, w, cap = text_path(DISPLAY, "ÉLVARÉ", size, 0.32)
    top_accent = 34  # space for accents above cap height
    pad = 4
    h = cap + top_accent + pad * 2
    extra = ""
    if tagline:
        td, tw, tcap = text_path(DISPLAY, "THE ART OF MODERN LUXURY", 15, 0.42)
        ty = cap + 48
        tx = (w - tw) / 2
        extra = (f'<line x1="{w/2-40:.1f}" y1="{cap+22:.1f}" x2="{w/2+40:.1f}" y2="{cap+22:.1f}" '
                 f'stroke="{GOLD}" stroke-width="1.2"/>'
                 f'<path transform="translate({tx:.1f} {ty:.1f})" d="{td}" fill="{fill}"/>')
        h = ty + 6 + pad + cap + top_accent + pad
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 {-cap-top_accent-pad:.1f} {w:.1f} {h:.1f}" '
           f'role="img" aria-label="ÉLVARÉ"><title>ÉLVARÉ</title><path d="{d}" fill="{fill}"/>{extra}</svg>')
    (BRAND / name).write_text(svg)
    return d, w, cap


def monogram(fg, bg, name, frame=True):
    """Arched-window monogram: É set inside a slender maison arch with a gold keystone."""
    d, w, cap = text_path(DISPLAY, "É", 150, 0)
    W, H = 200, 260
    tx, ty = (W - w) / 2, 196
    arch = (f'<path d="M30 248 V100 A70 70 0 0 1 170 100 V248" fill="none" stroke="{GOLD}" stroke-width="3"/>'
            f'<path d="M93 22 L100 13 L107 22 Z" fill="{GOLD}"/>' if frame else "")
    bgrect = f'<rect width="{W}" height="{H}" fill="{bg}"/>' if bg else ""
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" aria-label="ÉLVARÉ monogram">'
           f'<title>ÉLVARÉ monogram</title>{bgrect}{arch}<path transform="translate({tx:.1f} {ty})" d="{d}" fill="{fg}"/></svg>')
    (BRAND / name).write_text(svg)


def favicon():
    d, w, cap = text_path(DISPLAY, "É", 52, 0)
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="6" fill="{OBSIDIAN}"/>'
           f'<path d="M14 58 V27 A18 18 0 0 1 50 27 V58" fill="none" stroke="{GOLD}" stroke-width="3"/>'
           f'<path transform="translate({(64-w)/2:.1f} 55)" d="{d}" fill="{IVORY}"/></svg>')
    (ROOT / "favicon.svg").write_text(svg)


def fonts():
    uni = "U+0020-007E,U+00A0-00FF,U+2013-2014,U+2018-201E,U+2022,U+2026,U+20AC,U+2122,U+2190-2193,U+00D7"
    jobs = [
        (DISPLAY, "lm-roman-17.woff"),
        (LM + "lmroman12-italic.otf", "lm-roman-12-italic.woff"),
        ("/usr/share/fonts/opentype/inter/Inter-Light.otf", "inter-300.woff"),
        ("/usr/share/fonts/opentype/inter/Inter-Regular.otf", "inter-400.woff"),
        ("/usr/share/fonts/opentype/inter/Inter-Medium.otf", "inter-500.woff"),
    ]
    for src, out in jobs:
        opts = subset.Options()
        opts.flavor = "woff"
        opts.layout_features = ["kern", "liga", "tnum", "lnum"]
        opts.name_IDs = ["*"]
        opts.notdef_outline = True
        f = subset.load_font(src, opts)
        s = subset.Subsetter(opts)
        s.populate(unicodes=subset.parse_unicodes(uni))
        s.subset(f)
        subset.save_font(f, str(FONTS / out), opts)
        print("font", out, (FONTS / out).stat().st_size // 1024, "KB")


if __name__ == "__main__":
    BRAND.mkdir(parents=True, exist_ok=True)
    FONTS.mkdir(parents=True, exist_ok=True)
    wordmark(OBSIDIAN, "elvare-wordmark-black.svg")
    wordmark(IVORY, "elvare-wordmark-ivory.svg")
    wordmark(OBSIDIAN, "elvare-wordmark-tagline-black.svg", tagline=True)
    wordmark(IVORY, "elvare-wordmark-tagline-ivory.svg", tagline=True)
    monogram(OBSIDIAN, None, "elvare-monogram-black.svg")
    monogram(IVORY, OBSIDIAN, "elvare-monogram-obsidian.svg")
    monogram(IVORY, None, "elvare-monogram-ivory.svg")
    favicon()
    fonts()
    print("brand assets written")
