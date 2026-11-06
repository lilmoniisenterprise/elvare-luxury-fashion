"""ÉLVARÉ image renderer.

Renders an art-directed, consistent set of product still-lifes and campaign scenes
(no external sources, no third-party logos) and exports responsive WebP sizes.
Run from project root:  python3 tools/build_images.py [--only products|campaign]
"""
import sys, math, random
from pathlib import Path
import numpy as np
import cv2
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).parent))
from catalog import products, C, slugify  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
PDIR = ROOT / "assets" / "img" / "products"
CDIR = ROOT / "assets" / "img" / "campaign"
SS = 2  # supersampling factor for masks


def hex2rgb(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], dtype=np.float32) / 255.0


def blur(a, r):
    k = int(r) * 2 + 1
    return cv2.GaussianBlur(a, (k, k), r / 2.0)


def qb(p0, c, p1, n=14):
    """Quadratic bezier points."""
    return [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * c[0] + t ** 2 * p1[0],
             (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * c[1] + t ** 2 * p1[1]) for t in np.linspace(0, 1, n)]


class Canvas:
    def __init__(self, w, h):
        self.w, self.h = w, h

    def mask(self, polys=(), ellipses=(), lines=(), width=6, rects=()):
        im = Image.new("L", (self.w * SS, self.h * SS), 0)
        d = ImageDraw.Draw(im)
        for p in polys:
            d.polygon([(x * SS, y * SS) for x, y in p], fill=255)
        for e in ellipses:
            d.ellipse([v * SS for v in e], fill=255)
        for r in rects:
            d.rounded_rectangle([v * SS for v in r[:4]], radius=r[4] * SS if len(r) > 4 else 0, fill=255)
        for ln in lines:
            d.line([(x * SS, y * SS) for x, y in ln], fill=255, width=int(width * SS), joint="curve")
        im = im.resize((self.w, self.h), Image.LANCZOS)
        return np.asarray(im, dtype=np.float32) / 255.0


# ---------------------------------------------------------------- backdrops
def studio_backdrop(w, h, tone=("#efe9de", "#d9d0c1"), light=(0.32, 0.18), floor=0.84, seed=0):
    top, bot = hex2rgb(tone[0]), hex2rgb(tone[1])
    y = np.linspace(0, 1, h)[:, None, None]
    img = top * (1 - y) + bot * y
    img = np.broadcast_to(img, (h, w, 3)).copy()
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    d = np.sqrt(((xx / w - light[0]) * 1.2) ** 2 + (yy / h - light[1]) ** 2)
    img *= (1.06 - 0.22 * np.clip(d, 0, 1.2))[..., None]
    if floor:  # soft sweep where wall meets floor
        f = np.clip((yy / h - floor) / 0.12, 0, 1)
        img *= (1 - 0.06 * np.sin(f * math.pi))[..., None]
    return img


def grain(img, amt=0.018, seed=1):
    rng = np.random.default_rng(seed)
    n = rng.normal(0, amt, img.shape[:2]).astype(np.float32)
    return np.clip(img + n[..., None], 0, 1)


def vignette(img, s=0.25):
    h, w = img.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    d = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2)
    return img * (1 - s * np.clip(d - 0.55, 0, 1))[..., None]


def drop_shadow(img, m, off=(18, 26), r=34, strength=0.32):
    sh = np.roll(np.roll(m, off[1], 0), off[0], 1)
    sh = blur(sh, r)
    return img * (1 - strength * sh)[..., None]


def paint(img, m, color, light_dir=-1, vol=0.22, texture=None, sheen=False, seed=3, edge_r=38):
    """Composite a garment part with volume shading, directional light and texture."""
    h, w = m.shape
    col = hex2rgb(color) if isinstance(color, str) else color
    lum = float(col @ np.array([0.3, 0.59, 0.11]))
    # volume: darker toward silhouette edges
    inner = blur(m, edge_r)
    shade = 1 - vol + vol * np.clip(inner * 1.6, 0, 1)
    xx = np.linspace(0, 1, w)[None, :]
    yy = np.linspace(0, 1, h)[:, None]
    dirl = 1.06 - 0.16 * (xx if light_dir < 0 else 1 - xx) - 0.05 * yy
    f = shade * dirl
    tex = np.zeros_like(m)
    rng = np.random.default_rng(seed)
    if texture == "knit":
        tex += 0.05 * np.sin(np.arange(w)[None, :] / 2.2) * np.ones((h, 1))
    elif texture == "rib":
        tex += 0.07 * np.sign(np.sin(np.arange(w)[None, :] / 3.0)) * np.ones((h, 1))
    elif texture == "twill":
        yy2, xx2 = np.mgrid[0:h, 0:w]
        tex += 0.025 * np.sin((xx2 + yy2) / 2.0)
    elif texture == "suede":
        tex += blur(rng.normal(0, 0.06, (h, w)).astype(np.float32), 2)
    elif texture == "quilt":
        yy2, xx2 = np.mgrid[0:h, 0:w]
        tex += 0.09 * (np.abs(np.sin((xx2 + yy2) / 26.0)) ** 0.25 + np.abs(np.sin((xx2 - yy2) / 26.0)) ** 0.25 - 1.6)
    tex += rng.normal(0, 0.012, (h, w)).astype(np.float32)
    if sheen:  # satin specular band
        band = np.exp(-((xx - 0.38 - 0.08 * yy) / 0.07) ** 2)
        f = f + (0.32 if lum < 0.3 else 0.16) * band * inner
    # dark colours need a little lift so they read; light colours need a little more modelling
    if lum < 0.15:
        f = 0.75 + 0.6 * (f - 0.75) + 0.08
    out = col[None, None, :] * (f + tex)[..., None]
    if lum < 0.15:
        out += 0.025
    out = np.clip(out, 0, 1)
    return img * (1 - m[..., None]) + out * m[..., None]


def strokes(img, cv, lines, width, darkness=0.16, r=6, light=False):
    m = blur(cv.mask(lines=lines, width=width), r)
    if light:
        return np.clip(img + darkness * m[..., None], 0, 1)
    return img * (1 - darkness * m)[..., None]


def finish(img, seed=1, amt=0.014):
    return grain(vignette(img, 0.18), amt, seed)


def save(img, path_base, widths, ratio=None, quality=80):
    im = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8))
    for wdt in widths:
        hgt = round(im.height * wdt / im.width)
        im.resize((wdt, hgt), Image.LANCZOS).save(f"{path_base}-{wdt}.webp", "WEBP", quality=quality, method=6)


# ---------------------------------------------------------------- garment geometry
# Product canvas is 1000 x 1250. Garments hang from a hanger at (500, 200).
def hanger(img, cv, y=200, wide=300):
    hook = qb((500, y - 10), (500, y - 95), (535, y - 92)) + qb((535, y - 92), (560, y - 80), (548, y - 58))
    bar = [(500 - wide, y + 34), (500, y - 6), (500 + wide, y + 34)]
    m = cv.mask(lines=[hook, bar], width=7)
    img = drop_shadow(img, m, (8, 12), 8, 0.25)
    return paint(img, m, "#9c8a6a", vol=0.1, edge_r=3)


def top_shape(kind, length=820, sleeve="long", neck="collar"):
    """Generic hanging top: body + sleeves polygons. Returns dict of parts."""
    sh = 205  # shoulder y
    sw = 190  # half shoulder width
    hem = sh + length * 0.62 if kind in ("shirt", "tee", "knit") else sh + length
    hw = 175 if kind != "coat" else 205
    body = [(500 - 70, sh - 18), (500 - sw, sh + 20)] + qb((500 - sw, sh + 20), (500 - sw - 6, sh + 180), (500 - hw, hem)) + \
           [(500 + hw, hem)] + qb((500 + sw + 6, sh + 180), (500 + sw + 6, sh + 180), (500 + sw, sh + 20))[::-1][:-1] + \
           [(500 + sw, sh + 20), (500 + 70, sh - 18)]
    body = [(500 - 70, sh - 18), (500 - sw, sh + 22), (500 - sw - 4, sh + 200), (500 - hw, hem), (500 + hw, hem),
            (500 + sw + 4, sh + 200), (500 + sw, sh + 22), (500 + 70, sh - 18)]
    sleeves = []
    if sleeve == "long":
        L = length * (0.62 if kind not in ("coat",) else 0.66) + 40
        for s in (-1, 1):
            sleeves.append([(500 + s * sw, sh + 22), (500 + s * (sw + 70), sh + 70), (500 + s * (sw + 98), sh + L),
                            (500 + s * (sw + 30), sh + L + 6), (500 + s * (sw + 6), sh + 200)])
    elif sleeve == "short":
        for s in (-1, 1):
            sleeves.append([(500 + s * sw, sh + 22), (500 + s * (sw + 78), sh + 90), (500 + s * (sw + 46), sh + 205),
                            (500 + s * (sw + 2), sh + 190)])
    return body, sleeves, sh, hem


def render_product(p, color_hex, variant="main", seed=0):
    W, H = 1000, 1250
    cv = Canvas(W, H)
    tones = {"main": ("#f1ebe1", "#dcd3c4"), "alt": ("#e2dbcf", "#c9bfae")}
    img = studio_backdrop(W, H, tones["alt" if variant == "alt" else "main"],
                          light=(0.28, 0.12) if variant != "alt" else (0.72, 0.15))
    shape = p["shape"]
    col = color_hex
    darker = hex2rgb(col) * 0.78
    tex = None
    if shape in ("sweater", "cardigan", "rollneck", "mcardigan"):
        tex = "knit" if shape != "cardigan" else "rib"
    if shape in ("mchino", "mtrouser", "blazer", "mblazer", "longcoat", "overcoat"):
        tex = "twill"
    if shape == "overshirt":
        tex = "suede"
    if shape == "fieldcoat":
        tex = "quilt"
    sheen = shape in ("slipdress", "slipskirt", "blouse")

    def garment(parts, details=(), light_strokes=(), buttons=(), dark_parts=(), hang=True, wide=300, line_w=5):
        nonlocal img
        if hang:
            img = hanger(img, cv, wide=wide)
        full = cv.mask(polys=[pp for pp in parts] + [pp for pp in dark_parts])
        img = drop_shadow(img, full)
        for pp in parts:
            img = paint(img, cv.mask(polys=[pp]), col, texture=tex, sheen=sheen, seed=seed)
        for pp in dark_parts:
            img = paint(img, cv.mask(polys=[pp]), darker, texture=tex, seed=seed + 1, vol=0.3, edge_r=14)
        if details:
            img = strokes(img, cv, details, line_w, 0.20, 5)
        if light_strokes:
            img = strokes(img, cv, light_strokes, 10, 0.06, 10, light=True)
        for (x, y, r) in buttons:
            bm = cv.mask(ellipses=[(x - r, y - r, x + r, y + r)])
            img = paint(img, bm, hex2rgb(col) * 0.6 + 0.25, vol=0.3, edge_r=2)
        if hang:  # hanger bar visible over garment shoulders
            img = hanger(img, cv, wide=wide)

    if shape in ("shirt", "mshirt", "blouse"):
        body, sl, sh, hem = top_shape("shirt", 900)
        coll = [[(430, sh - 18), (500, sh + 55), (470, sh + 60), (418, sh + 8)], [(570, sh - 18), (500, sh + 55), (530, sh + 60), (582, sh + 8)]]
        det = [[(500, sh + 55), (500, hem)], [(320, sh + 380), (360, sh + 520)], [(680, sh + 330), (650, sh + 500)]]
        btn = [(512, sh + 90 + i * 85, 6) for i in range(int((hem - sh - 110) // 85))]
        if shape == "blouse":
            coll = [[(440, sh - 10), (500, sh + 30), (560, sh - 10), (575, sh + 10), (500, sh + 60), (425, sh + 10)]]
            det = [[(500, sh + 60), (470, sh + 190)], [(500, sh + 60), (540, sh + 180)], [(320, sh + 380), (360, sh + 520)]]
            btn = []
        garment([body] + sl, det, [[(380, sh + 100), (360, hem - 40)]], btn, dark_parts=coll)
    elif shape in ("tee", "mocktee", "campshirt"):
        body, sl, sh, hem = top_shape("tee", 860, sleeve="short")
        dark = []
        det = [[(330, sh + 400), (350, hem - 30)], [(660, sh + 260), (640, sh + 420)]]
        if shape == "tee":
            dark = [[(445, sh - 14)] + qb((445, sh - 14), (500, sh + 40), (555, sh - 14)) + [(545, sh - 20)] + qb((545, sh - 20), (500, sh + 25), (455, sh - 20))]
        elif shape == "mocktee":
            dark = [[(440, sh - 40), (560, sh - 40), (565, sh + 4), (435, sh + 4)]]
        else:
            dark = [[(430, sh - 18), (500, sh + 120), (455, sh + 110), (410, sh + 10)], [(570, sh - 18), (500, sh + 120), (545, sh + 110), (590, sh + 10)]]
            det.append([(500, sh + 120), (500, hem)])
        garment([body] + sl, det, [[(390, sh + 80), (370, hem - 40)]], dark_parts=dark,
                buttons=[(512, sh + 170 + i * 90, 6) for i in range(4)] if shape == "campshirt" else ())
    elif shape in ("sweater", "rollneck", "cardigan", "mcardigan"):
        body, sl, sh, hem = top_shape("knit", 880)
        dark = []
        bands = [[(500 - 175, hem - 38), (500 + 175, hem - 38), (500 + 175, hem), (500 - 175, hem)]]
        for s in (-1, 1):
            L = 880 * 0.62 + 40
            bands.append([(500 + s * (190 + 92), sh + L - 46), (500 + s * (190 + 36), sh + L - 40), (500 + s * (190 + 30), sh + L + 6), (500 + s * (190 + 98), sh + L)])
        if shape == "sweater":
            dark = [[(440, sh - 16)] + qb((440, sh - 16), (500, sh + 50), (560, sh - 16)) + [(548, sh - 24)] + qb((548, sh - 24), (500, sh + 32), (452, sh - 24))]
        elif shape == "rollneck":
            dark = [[(432, sh - 70), (568, sh - 70), (574, sh + 6), (426, sh + 6)]]
        else:
            dark = [[(445, sh - 16), (500, sh + 240), (555, sh - 16), (565, sh - 10), (512, sh + 260), (512, hem), (488, hem), (488, sh + 260), (435, sh - 10)]]
            if shape == "mcardigan":
                dark = [[(430, sh - 20), (520, sh + 300), (490, sh + 300), (405, sh)], [(570, sh - 20), (520, sh + 300), (510, hem), (490, hem), (488, sh + 300), (595, sh)]]
        btn = [(500, sh + 300 + i * 70, 7) for i in range(4)] if shape in ("cardigan", "mcardigan") else ()
        garment([body] + sl, [[(330, sh + 380), (345, hem - 60)], [(670, sh + 260), (655, sh + 430)]], [[(390, sh + 90), (380, hem - 60)]], btn, dark_parts=dark + bands)
    elif shape in ("blazer", "mblazer", "overshirt", "fieldcoat"):
        length = {"blazer": 760, "mblazer": 900, "overshirt": 900, "fieldcoat": 1000}[shape]
        body, sl, sh, hem = top_shape("coat" if shape == "fieldcoat" else "shirt", length)
        if shape in ("blazer", "mblazer"):
            hem = sh + length * 0.66
            body[3] = (500 - 178, hem); body[4] = (500 + 178, hem)
            lap = [[(440, sh - 20), (500, sh + 250), (470, sh + 250), (390, sh + 90), (420, sh + 70), (405, sh + 20)],
                   [(560, sh - 20), (500, sh + 250), (530, sh + 250), (610, sh + 90), (580, sh + 70), (595, sh + 20)]]
            det = [[(500, sh + 250), (500, hem)], [(360, sh + 360), (420, sh + 360)], [(580, sh + 360), (640, sh + 360)], [(560, sh + 150), (610, sh + 145)]]
            btn = [(512, sh + 290, 8), (512, sh + 370, 8)] if shape == "mblazer" else [(512, sh + 285, 9)]
        else:
            lap = [[(430, sh - 18), (500, sh + 60), (470, sh + 70), (412, sh + 10)], [(570, sh - 18), (500, sh + 60), (530, sh + 70), (588, sh + 10)]]
            if shape == "fieldcoat":
                lap = [[(425, sh - 30), (500, sh + 40), (575, sh - 30), (600, sh + 20), (500, sh + 90), (400, sh + 20)]]
            det = [[(500, sh + 60), (500, hem)], [(380, sh + 120), (460, sh + 120)], [(540, sh + 120), (620, sh + 120)]]
            if shape == "fieldcoat":
                det += [[(360, sh + 430), (460, sh + 430)], [(540, sh + 430), (640, sh + 430)]]
            btn = [(512, sh + 110 + i * 100, 7) for i in range(int((hem - sh - 140) // 100))]
        garment([body] + sl, det, [[(390, sh + 120), (380, hem - 40)]], btn, dark_parts=lap)
    elif shape in ("longcoat", "overcoat"):
        body, sl, sh, hem = top_shape("coat", 950)
        hem = 1170
        body[3] = (500 - 215, hem); body[4] = (500 + 215, hem)
        if shape == "longcoat":
            lap = [[(440, sh - 22), (500, sh + 380), (472, sh + 380), (372, sh + 120), (392, sh + 10)],
                   [(560, sh - 22), (500, sh + 380), (528, sh + 380), (628, sh + 120), (608, sh + 10)]]
            belt = [[(305, sh + 420), (695, sh + 420), (697, sh + 452), (303, sh + 452)], [(560, sh + 440), (585, sh + 440), (600, sh + 600), (575, sh + 604)]]
            det = [[(500, sh + 380), (520, hem)], [(360, sh + 560), (380, hem - 30)], [(640, sh + 520), (620, hem - 40)]]
            garment([body] + sl, det, [[(400, sh + 130), (410, hem - 40)]], (), dark_parts=lap + belt)
        else:
            lap = [[(440, sh - 22), (500, sh + 300), (470, sh + 300), (385, sh + 110), (412, sh + 90), (395, sh + 20)],
                   [(560, sh - 22), (500, sh + 300), (530, sh + 300), (615, sh + 110), (588, sh + 90), (605, sh + 20)]]
            det = [[(500, sh + 300), (500, hem)], [(340, sh + 480), (410, sh + 470)], [(590, sh + 470), (660, sh + 480)], [(580, sh + 170), (630, sh + 165)]]
            btn = [(515, sh + 340 + i * 110, 9) for i in range(3)]
            garment([body] + sl, det, [[(400, sh + 130), (410, hem - 40)]], btn, dark_parts=lap)
    elif shape == "slipdress":
        sh = 230
        body = [(440, sh + 40), (560, sh + 40)] + qb((560, sh + 40), (600, sh + 360), (690, 1180)) + qb((690, 1180), (500, 1200), (310, 1180)) + qb((310, 1180), (400, sh + 360), (440, sh + 40))
        straps = [[(330, sh), (440, sh + 48)], [(670, sh), (560, sh + 48)]]
        img = hanger(img, cv, sh, wide=200)
        m = cv.mask(polys=[body])
        img = drop_shadow(img, m)
        img = paint(img, m, col, sheen=True, seed=seed)
        img = paint(img, cv.mask(lines=straps, width=5), darker, vol=0.0, edge_r=2)
        img = strokes(img, cv, [qb((450, sh + 50), (500, sh + 110), (550, sh + 50)), qb((455, sh + 70), (500, sh + 150), (545, sh + 70)),
                                [(470, sh + 400), (420, 1150)], [(540, sh + 380), (590, 1150)], [(505, sh + 500), (505, 1170)]], 6, 0.18, 9)
        img = strokes(img, cv, [[(450, sh + 300), (380, 1140)], [(560, sh + 450), (620, 1120)]], 12, 0.10, 14, light=True)
    elif shape == "columndress":
        body, sl, sh, hem = top_shape("coat", 960)
        hem = 1190
        body = [(440, sh - 40), (560, sh - 40), (565, sh - 14), (500 + 165, sh + 20), (500 + 160, sh + 260), (500 + 140, sh + 420), (500 + 175, hem), (500 - 175, hem), (500 - 140, sh + 420), (500 - 160, sh + 260), (500 - 165, sh + 20), (435, sh - 14)]
        sl = [[(500 + s * 165, sh + 20), (500 + s * 225, sh + 70), (500 + s * 250, sh + 600), (500 + s * 200, sh + 606), (500 + s * 160, sh + 260)] for s in (-1, 1)]
        garment([body] + sl, [[(480, sh + 460), (460, hem - 10)], [(540, sh + 480), (560, hem - 10)]], [[(420, sh + 100), (400, hem - 40)]], (), wide=240)
    elif shape == "wrapdress":
        body, sl, sh, hem = top_shape("coat", 900)
        hem = 1120
        body = [(440, sh - 18), (500 - 175, sh + 22), (500 - 160, sh + 300), (500 - 130, sh + 380), (500 - 240, hem), (500 + 240, hem), (500 + 130, sh + 380), (500 + 160, sh + 300), (500 + 175, sh + 22), (560, sh - 18)]
        sl = [[(500 + s * 175, sh + 22), (500 + s * 240, sh + 70), (500 + s * 262, sh + 400), (500 + s * 205, sh + 405), (500 + s * 170, sh + 220)] for s in (-1, 1)]
        dark = [[(440, sh - 18), (560, sh + 360), (540, sh + 380), (430, sh + 10)], [(560, sh + 380), (610, sh + 380), (640, sh + 560), (618, sh + 566), (590, sh + 420)]]
        garment([body] + sl, [[(560, sh + 380), (420, hem - 10)], [(600, sh + 420), (650, hem - 10)], [(360, sh + 380), (620, sh + 384)]],
                [[(420, sh + 140), (380, hem - 60)]], (), dark_parts=dark, wide=260)
    elif shape in ("slipskirt", "pleatskirt"):
        top = 330
        body = [(380, top), (620, top)] + qb((620, top), (650, top + 300), (720, 1100)) + qb((720, 1100), (500, 1120), (280, 1100)) + qb((280, 1100), (350, top + 300), (380, top))
        band = [[(375, top - 30), (625, top - 30), (625, top + 6), (375, top + 6)]]
        clips = [[(400, top - 70), (400, top - 20)], [(600, top - 70), (600, top - 20)], [(380, top - 70), (620, top - 70)]]
        img = paint(img, cv.mask(lines=[[(500, top - 70), (500, top - 140)] + qb((500, top - 140), (500, top - 180), (530, top - 175))], width=6), "#9c8a6a", vol=0.1, edge_r=3)
        m = cv.mask(polys=[body] + band)
        img = drop_shadow(img, m)
        img = paint(img, cv.mask(polys=[body]), col, sheen=shape == "slipskirt", texture=None if shape == "slipskirt" else "twill", seed=seed)
        img = paint(img, cv.mask(polys=band), darker, vol=0.2, edge_r=6)
        img = paint(img, cv.mask(lines=clips, width=7), "#9c8a6a", vol=0.1, edge_r=3)
        if shape == "pleatskirt":
            pl = [[(390 + i * 24, top + 10), (300 + i * 42, 1095)] for i in range(10)]
            img = strokes(img, cv, pl, 4, 0.22, 3)
            img = strokes(img, cv, [[(395 + i * 24, top + 10), (310 + i * 42, 1095)] for i in range(10)], 4, 0.08, 4, light=True)
        else:
            img = strokes(img, cv, [[(450, top + 200), (390, 1090)], [(560, top + 260), (620, 1090)]], 6, 0.16, 9)
            img = strokes(img, cv, [[(470, top + 150), (430, 1080)]], 14, 0.14, 16, light=True)
    elif shape in ("widetrouser", "slimtrouser", "mtrouser", "mchino"):
        top = 280
        wide = shape == "widetrouser"
        hw = 160
        crotch = top + (300 if wide else 280)
        bot = 1170
        if wide:
            legs = [[(500 - hw, top), (500, top), (500, crotch), (515, crotch + 20), (470, bot), (300, bot)],
                    [(500, top), (500 + hw, top), (700, bot), (530, bot), (485, crotch + 20), (500, crotch)]]
        elif shape == "slimtrouser":
            legs = [[(500 - hw + 10, top), (500, top), (500, crotch), (485, bot - 60), (390, bot - 60), (350, crotch)],
                    [(500, top), (500 + hw - 10, top), (650, crotch), (610, bot - 60), (515, bot - 60), (500, crotch)]]
        else:
            legs = [[(500 - hw, top), (500, top), (500, crotch), (482, bot), (370, bot), (345, crotch)],
                    [(500, top), (500 + hw, top), (655, crotch), (630, bot), (518, bot), (500, crotch)]]
        band = [[(500 - hw - 2, top - 34), (500 + hw + 2, top - 34), (500 + hw, top + 4), (500 - hw, top + 4)]]
        img = paint(img, cv.mask(lines=[[(500, top - 80), (500, top - 150)] + qb((500, top - 150), (500, top - 190), (530, top - 185)), [(380, top - 80), (620, top - 80)], [(400, top - 80), (400, top - 30)], [(600, top - 80), (600, top - 30)]], width=6), "#9c8a6a", vol=0.1, edge_r=3)
        m = cv.mask(polys=legs + band)
        img = drop_shadow(img, m)
        for lg in legs:
            img = paint(img, cv.mask(polys=[lg]), col, texture=tex, seed=seed)
        img = paint(img, cv.mask(polys=band), darker, vol=0.2, edge_r=6)
        lx = [(420, top + 10), (400 if not wide else 390, bot - 70)]
        rx = [(580, top + 10), (600 if not wide else 610, bot - 70)]
        img = strokes(img, cv, [lx, rx, [(500, top + 10), (500, crotch)]], 4, 0.2, 3)
        if shape in ("widetrouser", "mtrouser"):
            img = strokes(img, cv, [[(450, top + 6), (455, top + 90)], [(550, top + 6), (545, top + 90)]], 4, 0.18, 3)
        img = strokes(img, cv, [[(424, top + 40), (406, bot - 90)], [(584, top + 40), (604, bot - 90)]], 10, 0.07, 6, light=True)
        img = paint(img, cv.mask(lines=[[(400, top - 80), (400, top - 22)], [(600, top - 80), (600, top - 22)]], width=7), "#9c8a6a", vol=0.1, edge_r=3)
    elif shape in ("bag", "cardholder", "belt", "derby", "mule", "scarf", "mscarf"):
        # plinth still life
        py = 900
        plinth = [(170, py), (830, py), (860, 1250), (140, 1250)]
        pm = cv.mask(polys=[plinth])
        img = paint(img, pm, "#e7e0d4", vol=0.05, edge_r=4, light_dir=-1)
        img = strokes(img, cv, [[(170, py), (830, py)]], 3, -0.25, 2)  # lit top edge (negative darkness = lighten)
        if shape == "bag":
            body = [(330, 560)] + qb((330, 560), (310, 870), (340, 900)) + [(660, 900)] + qb((660, 900), (690, 870), (670, 560))
            flap = [(330, 560), (670, 560)] + qb((670, 560), (640, 690), (500, 700)) + qb((500, 700), (360, 690), (330, 560))
            handle = qb((390, 560), (500, 330), (610, 560), 24)
            m = cv.mask(polys=[body, flap])
            img = drop_shadow(img, m, (30, 10), 26, 0.4)
            img = paint(img, cv.mask(lines=[handle], width=26), darker, vol=0.4, edge_r=6)
            img = paint(img, cv.mask(polys=[body]), col, vol=0.3, seed=seed)
            img = paint(img, cv.mask(polys=[flap]), hex2rgb(col) * 0.9, vol=0.3, edge_r=20, seed=seed)
            img = paint(img, cv.mask(lines=[qb((485, 700), (500, 670), (515, 700))], width=8), "#c6a66b", vol=0.1, edge_r=2)
            img = strokes(img, cv, [qb((338, 572), (500, 600), (662, 572))], 3, 0.25, 2)
        elif shape == "cardholder":
            body = [(330, 700), (670, 700), (690, 900), (310, 900)]
            m = cv.mask(rects=[(330, 640, 670, 900, 22)])
            img = drop_shadow(img, m, (26, 10), 20, 0.4)
            img = paint(img, m, col, vol=0.25, edge_r=18, seed=seed)
            img = strokes(img, cv, [qb((350, 720 + i * 45), (500, 700 + i * 45), (650, 720 + i * 45)) for i in range(3)], 4, 0.28, 2)
            img = strokes(img, cv, [[(480, 840), (500, 820), (520, 840)]], 3, 0.3, 1)
        elif shape == "belt":
            rings = []
            for i, r in enumerate((190, 150, 110)):
                rings.append([(500 + r * math.cos(t), 760 + r * 0.42 * math.sin(t)) for t in np.linspace(0, 2 * math.pi, 80)])
            m = cv.mask(lines=rings, width=40)
            img = drop_shadow(img, m, (20, 16), 20, 0.4)
            img = paint(img, m, col, vol=0.4, edge_r=8, seed=seed)
            img = strokes(img, cv, rings, 2, 0.25, 1)
            bk = cv.mask(lines=[[(640, 780), (720, 780), (720, 840), (640, 840), (640, 780)]], width=9)
            img = paint(img, bk, "#b9b3a8", vol=0.2, edge_r=2)
        elif shape in ("derby", "mule"):
            if shape == "derby":
                sole = [(250, 880), (760, 880), (765, 900), (245, 900)]
                upper = [(260, 880)] + qb((260, 880), (255, 700), (330, 690)) + [(480, 680)] + qb((480, 680), (560, 690), (640, 760)) + qb((640, 760), (760, 800), (760, 880))
                det = [qb((430, 690), (470, 760), (560, 740)), [(470, 700), (540, 735)], [(480, 690), (520, 712)]]
            else:
                sole = [(250, 880), (760, 880), (765, 892), (300, 892)]
                upper = [(470, 880)] + qb((470, 880), (520, 720), (620, 760)) + qb((620, 760), (720, 820), (780, 880))
                heel = [(255, 700), (300, 700), (300, 720), (285, 900), (270, 900)]
                bed = [(255, 700)] + qb((255, 700), (400, 690), (520, 880))
                img = paint(img, cv.mask(polys=[heel]), darker, vol=0.3, edge_r=4)
                img = paint(img, cv.mask(lines=[bed], width=12), darker, vol=0.3, edge_r=3)
                det = [qb((480, 870), (540, 760), (640, 770))]
            m = cv.mask(polys=[upper, sole])
            img = drop_shadow(img, m, (30, 8), 22, 0.45)
            img = paint(img, cv.mask(polys=[upper]), col, vol=0.35, edge_r=24, seed=seed)
            img = paint(img, cv.mask(polys=[sole]), "#2a2522", vol=0.1, edge_r=2)
            img = strokes(img, cv, det, 4, 0.3, 2)
            img = strokes(img, cv, [qb((300, 760), (420, 700), (560, 720))], 14, 0.12, 12, light=True)
        elif shape == "scarf":
            sq = [(500, 520), (760, 720), (500, 920), (240, 720)]
            m = cv.mask(polys=[sq])
            img = drop_shadow(img, m, (24, 12), 24, 0.35)
            img = paint(img, m, col, vol=0.12, sheen=True, seed=seed)
            inner = [(500, 560), (708, 720), (500, 880), (292, 720), (500, 560)]
            img = paint(img, cv.mask(lines=[inner], width=10), "#f3ecdf" if hex2rgb(col).mean() < 0.5 else "#1f2a3d", vol=0, edge_r=1)
            arch = qb((450, 780), (450, 640), (500, 640)) + qb((500, 640), (550, 640), (550, 780))
            img = paint(img, cv.mask(lines=[arch], width=8), "#c6a66b", vol=0, edge_r=1)
        else:  # mscarf hanging over a rail
            rail = cv.mask(lines=[[(160, 380), (840, 380)]], width=12)
            img = paint(img, rail, "#9c8a6a", vol=0.2, edge_r=3)
            strips = [[(400, 380), (480, 380), (470, 1060), (390, 1060)], [(520, 380), (600, 380), (620, 1000), (540, 1000)]]
            m = cv.mask(polys=strips)
            img = drop_shadow(img, m)
            for s_ in strips:
                img = paint(img, cv.mask(polys=[s_]), col, texture="twill", seed=seed)
            fr = [[(392 + i * 8, 1060), (390 + i * 8, 1110)] for i in range(10)] + [[(542 + i * 8, 1000), (545 + i * 8, 1050)] for i in range(10)]
            img = paint(img, cv.mask(lines=fr, width=3), darker, vol=0, edge_r=1)
            img = paint(img, rail * (cv.mask(polys=[[(380, 360), (620, 360), (620, 395), (380, 395)]])), "#9c8a6a", vol=0.2, edge_r=3)
    else:
        raise ValueError(shape)
    return finish(img, seed=seed + 7)


# ---------------------------------------------------------------- campaign scenes
def figure(img, cv, x, base, scale, outfit, gender="w", lit=1.0, shadow_dir=1):
    """Stylised fashion figure: elongated editorial proportions, shadow-play rendering."""
    s = scale
    head_h = 70 * s
    top = base - 8.3 * head_h
    hx = x
    skin = hex2rgb("#6b5244") * (0.55 + 0.45 * lit)
    hair = hex2rgb("#15110f")
    # legs
    leg_top = top + 4.2 * head_h
    lw = 22 * s
    legs = [[(hx - 30 * s, leg_top), (hx - 6 * s, leg_top), (hx - 12 * s, base - 12 * s), (hx - 12 * s - lw, base - 12 * s)],
            [(hx + 6 * s, leg_top), (hx + 30 * s, leg_top), (hx + 34 * s, base - 12 * s), (hx + 12 * s, base - 12 * s)]]
    legcol = outfit.get("legs", "#1a1a1a")
    shoes = [(hx - 46 * s, base - 16 * s, hx - 4 * s, base + 2 * s), (hx + 6 * s, base - 16 * s, hx + 52 * s, base + 2 * s)]
    neck = [(hx - 9 * s, top + head_h * 0.9), (hx + 9 * s, top + head_h * 0.9), (hx + 11 * s, top + head_h * 1.35), (hx - 11 * s, top + head_h * 1.35)]
    head = (hx - 24 * s, top, hx + 24 * s, top + head_h)
    sh_y = top + head_h * 1.35
    sw = (62 if gender == "m" else 52) * s
    coat_len = outfit.get("len", 6.2) * head_h
    hem_w = outfit.get("hem", 1.15) * sw
    body = [(hx - sw, sh_y + 8 * s), (hx - 18 * s, sh_y - 4 * s), (hx + 18 * s, sh_y - 4 * s), (hx + sw, sh_y + 8 * s),
            (hx + sw + 6 * s, sh_y + 3.2 * head_h), (hx + hem_w, sh_y + coat_len), (hx - hem_w, sh_y + coat_len), (hx - sw - 6 * s, sh_y + 3.2 * head_h)]
    arms = [[(hx + s_ * sw, sh_y + 8 * s), (hx + s_ * (sw + 20 * s), sh_y + 30 * s), (hx + s_ * (sw + 26 * s), sh_y + 3.4 * head_h),
             (hx + s_ * (sw + 4 * s), sh_y + 3.4 * head_h), (hx + s_ * (sw - 6 * s), sh_y + 60 * s)] for s_ in (-1, 1)]
    full = cv.mask(polys=legs + [body] + arms + [neck], ellipses=[head] + [tuple(v) for v in shoes])
    # cast shadow on floor and wall
    sh_m = cv.mask(polys=[[(hx - 40 * s, base), (hx + 40 * s, base), (hx + shadow_dir * 520 * s, base - 30 * s), (hx + shadow_dir * 470 * s, base - 50 * s)]])
    img = img * (1 - 0.35 * blur(sh_m, 18))[..., None]
    wall_sh = np.roll(full, int(shadow_dir * 160 * s), 1)
    wall_sh = np.roll(wall_sh, int(-40 * s), 0)
    img = img * (1 - 0.18 * blur(wall_sh, 26 * s))[..., None]
    for lg in legs:
        img = paint(img, cv.mask(polys=[lg]), hex2rgb(legcol) * (0.7 + 0.3 * lit), vol=0.3, edge_r=4)
    for sm in shoes:
        img = paint(img, cv.mask(ellipses=[sm]), "#0f0f0f", vol=0.2, edge_r=2)
    img = paint(img, cv.mask(polys=[neck]), skin, vol=0.3, edge_r=3)
    img = paint(img, cv.mask(ellipses=[head]), skin, vol=0.4, edge_r=10 * s, light_dir=-shadow_dir)
    if gender == "w":
        hairm = cv.mask(ellipses=[(hx - 26 * s, top - 4 * s, hx + 26 * s, top + head_h * 0.55), (hx + 8 * s, top + 2 * s, hx + 40 * s, top + 34 * s)])
    else:
        hairm = cv.mask(ellipses=[(hx - 25 * s, top - 6 * s, hx + 25 * s, top + head_h * 0.42)])
    img = paint(img, hairm, hair, vol=0.2, edge_r=4)
    ccol = hex2rgb(outfit["coat"]) * (0.62 + 0.38 * lit)
    for a in arms:
        img = paint(img, cv.mask(polys=[a]), ccol * 0.92, vol=0.35, edge_r=8 * s, light_dir=-shadow_dir, texture="twill")
    img = paint(img, cv.mask(polys=[body]), ccol, vol=0.32, edge_r=22 * s, light_dir=-shadow_dir, texture="twill", sheen=outfit.get("sheen", False))
    if outfit.get("lapel", True):
        img = strokes(img, cv, [[(hx - 18 * s, sh_y - 2 * s), (hx, sh_y + 1.6 * head_h), (hx + 18 * s, sh_y - 2 * s)], [(hx, sh_y + 1.6 * head_h), (hx + 4 * s, sh_y + coat_len)]], 3 * s, 0.35, 2)
    if outfit.get("belt"):
        img = strokes(img, cv, [[(hx - sw - 4 * s, sh_y + 2.6 * head_h), (hx + sw + 4 * s, sh_y + 2.6 * head_h)]], 7 * s, 0.35, 2)
    # rim light on lit side
    edge = np.clip(full - np.roll(full, int(-shadow_dir * 5 * s), 1), 0, 1)
    img = np.clip(img + 0.22 * lit * blur(edge, 3)[..., None], 0, 1)
    return img


def interior(w, h, wall="#e9e1d4", floor_c="#cfc4b2", horizon=0.78, arches=(), light_beams=(), seed=0, dark=False):
    img = np.zeros((h, w, 3), np.float32)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    wc, fc = hex2rgb(wall), hex2rgb(floor_c)
    hz = int(h * horizon)
    img[:hz] = wc * (0.92 + 0.08 * (1 - yy[:hz] / hz))[..., None]
    img[hz:] = fc * (0.82 + 0.18 * ((yy[hz:] - hz) / (h - hz)))[..., None]
    img[hz - 2:hz + 1] *= 0.86
    # plaster texture
    rng = np.random.default_rng(seed)
    pl = blur(rng.normal(0, 1, (h // 4, w // 4)).astype(np.float32), 6)
    pl = cv2.resize(pl, (w, h))
    img *= (1 + 0.03 * pl)[..., None]
    cv = Canvas(w, h)
    for (ax, aw, ah, depth) in arches:  # architectural arched niches/doorways
        x0, x1 = ax - aw / 2, ax + aw / 2
        top = hz - ah
        poly = [(x0, hz)] + [(ax + aw / 2 * math.cos(t), top + aw / 2 - aw / 2 * math.sin(t)) for t in np.linspace(math.pi, 0, 40)] + [(x1, hz)]
        m = cv.mask(polys=[poly])
        img = img * (1 - depth * m)[..., None] + hex2rgb("#2b2622")[None, None, :] * (depth * m)[..., None] * 0.3
    for (pts, strength) in light_beams:  # sunlight patches projected on wall/floor
        m = blur(cv.mask(polys=[pts]), 14)
        img = np.clip(img * (1 + strength * m)[..., None] + np.array([0.05, 0.035, 0.0]) * strength * m[..., None], 0, 1)
    if dark:
        img *= 0.45
    return img, cv, hz


def campaign_scenes():
    CDIR.mkdir(parents=True, exist_ok=True)
    scenes = {}

    def hero_w(w, h, seed=11):
        img, cv, hz = interior(w, h, "#e6ddcf", "#cdbfab", 0.8,
                               arches=[(w * 0.86, w * 0.16, h * 0.62, 0.5)],
                               light_beams=[([(w * 0.5, h * 0.08), (w * 0.66, h * 0.06), (w * 0.74, h * 0.8), (w * 0.56, h * 0.8)], 0.22),
                                            ([(w * 0.56, h * 0.8), (w * 0.74, h * 0.8), (w * 0.9, h), (w * 0.6, h)], 0.18)], seed=seed)
        img = figure(img, cv, w * (0.6 if w > h else 0.42), h * 0.93, h / 820, {"coat": "#b38b5d", "len": 5.4, "hem": 1.35, "belt": True}, "w", 1.0, 1)
        img = figure(img, cv, w * (0.72 if w > h else 0.64), h * 0.95, h / 790, {"coat": "#1a1a1a", "len": 6.0, "hem": 1.0, "lapel": False, "sheen": True}, "w", 0.8, 1)
        return finish(img, seed, 0.016)

    def hero_m(w, h, seed=12):
        img, cv, hz = interior(w, h, "#d9d3ca", "#bdb4a6", 0.79,
                               arches=[(w * 0.26, w * 0.17, h * 0.6, 0.6), (w * 0.5, w * 0.17, h * 0.6, 0.6)],
                               light_beams=[([(w * 0.56, h * 0.1), (w * 0.72, h * 0.1), (w * 0.82, h * 0.79), (w * 0.62, h * 0.79)], 0.24)], seed=seed)
        img = figure(img, cv, w * (0.68 if w > h else 0.38), h * 0.94, h / 800, {"coat": "#3a3a3a", "len": 4.6, "hem": 1.12, "legs": "#2a2a2a"}, "m", 1.0, -1)
        img = figure(img, cv, w * (0.8 if w > h else 0.62), h * 0.95, h / 830, {"coat": "#b38b5d", "len": 4.4, "hem": 1.1, "legs": "#1f2a3d"}, "m", 0.9, -1)
        return finish(img, seed, 0.016)

    def seasonal(w, h, seed=13):
        img, cv, hz = interior(w, h, "#3b3530", "#2a2521", 0.8,
                               light_beams=[([(w * 0.42, 0), (w * 0.58, 0), (w * 0.66, h * 0.8), (w * 0.38, h * 0.8)], 0.7),
                                            ([(w * 0.38, h * 0.8), (w * 0.66, h * 0.8), (w * 0.8, h), (w * 0.3, h)], 0.5)], seed=seed)
        img = figure(img, cv, w * 0.5, h * 0.93, h / 830, {"coat": "#d9c39a", "len": 5.6, "hem": 1.4, "belt": True}, "w", 1.0, 1)
        return finish(img, seed, 0.02)

    def collection(name, coat, bg, fl, gender, beam=0.3, dark=False, seed=20, **kw):
        w, h = 1200, 1500
        img, cv, hz = interior(w, h, bg, fl, 0.82,
                               arches=[(w * 0.5, w * 0.56, h * 0.66, 0.18 if not dark else 0.35)],
                               light_beams=[([(w * 0.12, h * 0.1), (w * 0.34, h * 0.1), (w * 0.52, h * 0.82), (w * 0.24, h * 0.82)], beam)], seed=seed)
        outfit = {"coat": coat, "len": 5.6 if gender == "w" else 4.6, "hem": 1.3 if gender == "w" else 1.1}
        outfit.update(kw)
        img = figure(img, cv, w * 0.5, h * 0.94, h / 820, outfit, gender, 1.0, 1)
        return finish(img, seed, 0.016)

    def editorial_detail(w, h, col, seed=30, sheen=False):
        img = studio_backdrop(w, h, ("#e9e2d6", "#d3c8b6"), (0.3, 0.2), floor=0)
        cv = Canvas(w, h)
        drape = [(w * 0.1, 0), (w * 0.9, 0)] + qb((w * 0.9, 0), (w * 0.7, h * 0.5), (w * 1.0, h)) + [(0, h)] + qb((0, h), (w * 0.35, h * 0.5), (w * 0.1, 0))
        img = paint(img, cv.mask(polys=[drape]), col, vol=0.3, sheen=sheen, seed=seed, edge_r=60)
        folds = [qb((w * (0.2 + 0.12 * i), 0), (w * (0.35 + 0.1 * i), h * 0.5), (w * (0.15 + 0.16 * i), h)) for i in range(5)]
        img = strokes(img, cv, folds, 22, 0.2, 30)
        img = strokes(img, cv, [qb((w * (0.26 + 0.12 * i), 0), (w * (0.41 + 0.1 * i), h * 0.5), (w * (0.21 + 0.16 * i), h)) for i in range(5)], 18, 0.1, 30, light=True)
        return finish(img, seed, 0.016)

    jobs = [
        ("hero-women", lambda: hero_w(2400, 1350), [800, 1600, 2400]),
        ("hero-women-portrait", lambda: hero_w(1100, 1400, 14), [600, 1100]),
        ("hero-men", lambda: hero_m(2400, 1350), [800, 1600, 2400]),
        ("hero-men-portrait", lambda: hero_m(1100, 1400, 15), [600, 1100]),
        ("seasonal-aw26", lambda: seasonal(2400, 1200), [800, 1600, 2400]),
        ("collection-signature", lambda: collection("signature", "#1a1a1a", "#e6ddcf", "#cdbfab", "w", lapel=False, sheen=True), [600, 1200]),
        ("collection-essentials", lambda: collection("essentials", "#cfc6b6", "#ece6dc", "#d8cfbf", "m", 0.25, legs="#efe8db", seed=21), [600, 1200]),
        ("collection-evening", lambda: collection("evening", "#5e1f2a", "#2b2522", "#1d1917", "w", 0.6, True, 22, lapel=False, sheen=True), [600, 1200]),
        ("collection-tailored", lambda: collection("tailored", "#3a3a3a", "#d9d3ca", "#bdb4a6", "m", 0.3, legs="#3a3a3a", seed=23), [600, 1200]),
        ("collection-resort", lambda: collection("resort", "#efe8db", "#efe3cf", "#dcc9aa", "w", 0.45, seed=24, belt=True), [600, 1200]),
        ("collection-seasonal", lambda: collection("seasonal", "#b38b5d", "#d4c9b8", "#b6a891", "m", 0.35, legs="#1a1a1a", seed=25), [600, 1200]),
        ("editorial-silk", lambda: editorial_detail(1200, 1500, "#d9c39a", 31, True), [600, 1200]),
        ("editorial-wool", lambda: editorial_detail(1200, 1500, "#b38b5d", 32), [600, 1200]),
        ("editorial-noir", lambda: editorial_detail(1200, 1500, "#1a1a1a", 33, True), [600, 1200]),
        ("atelier", lambda: collection("atelier", "#efe8db", "#d9d0c2", "#c4b7a3", "w", 0.4, seed=26, lapel=False), [600, 1200]),
    ]
    for name, fn, widths in jobs:
        img = fn()
        save(img, str(CDIR / name), widths, quality=78)
        print("campaign", name)


def product_images():
    PDIR.mkdir(parents=True, exist_ok=True)
    ps = products()
    for i, p in enumerate(ps):
        slug = p["slug"]
        for ci, c in enumerate(p["colors"]):
            img = render_product(p, c["hex"], "main", seed=i * 10 + ci)
            base = PDIR / f"{slug}-{c['key']}"
            save(img, str(base), [480, 960])
            if ci == 0:
                # detail: zoomed crop of the main render
                h, w = img.shape[:2]
                y0 = int(h * (0.18 if p["shape"] not in ("bag", "derby", "mule", "belt", "cardholder", "scarf", "mscarf") else 0.42))
                crop = img[y0:y0 + int(h * 0.5), int(w * 0.2):int(w * 0.2) + int(w * 0.6)]
                crop = cv2.resize(crop, (w, h), interpolation=cv2.INTER_CUBIC)
                save(grain(crop, 0.01, i), str(PDIR / f"{slug}-detail"), [480, 960])
                alt = render_product(p, c["hex"], "alt", seed=i * 10 + 5)
                save(alt[:, ::-1], str(PDIR / f"{slug}-alt"), [480, 960])
        print("product", p["id"], slug, len(p["colors"]), "colours")


if __name__ == "__main__":
    only = sys.argv[2] if len(sys.argv) > 2 and sys.argv[1] == "--only" else None
    if only in (None, "campaign"):
        campaign_scenes()
    if only in (None, "products"):
        product_images()
