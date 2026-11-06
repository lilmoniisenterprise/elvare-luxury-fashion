"""ÉLVARÉ photography pipeline (v1.1).

Crops and encodes the self-hosted product and campaign photography as responsive WebP using the
site's existing file names. Sources are free-licence Unsplash photos (see tools/photo_credits.json),
downloaded once at 2400 px and checked by eye; the originals are not committed to the repository.

Usage:  python3 tools/build_photos.py SOURCE_DIR
SOURCE_DIR must contain <unsplash-id>.jpg for every id in photo_credits.json.
Crop tuples are (centre-x, centre-y, zoom) as fractions of the source image.
"""
import json, sys
from pathlib import Path
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
PDIR, CDIR = ROOT / "assets/img/products", ROOT / "assets/img/campaign"
DEF_MAIN, DEF_ALT, DEF_DETAIL = (0.5, 0.5, 1.0), (0.5, 0.45, 1.45), (0.5, 0.5, 3.0)


def crop(im, aspect, cx, cy, z):
    W, H = im.size
    w, h = (W, W / aspect) if W / H < aspect else (H * aspect, H)
    w, h = w / z, h / z
    x = min(max(cx * W - w / 2, 0), W - w)
    y = min(max(cy * H - h / 2, 0), H - h)
    return im.crop((round(x), round(y), round(x + w), round(y + h)))


def save(im, base, sizes, q=80):
    for (w, h) in sizes:
        r = im.resize((w, h), Image.LANCZOS)
        if w < im.width * 0.6:
            r = r.filter(ImageFilter.UnsharpMask(radius=0.6, percent=40, threshold=2))
        r.save(f"{base}-{w}.webp", "WEBP", quality=q, method=6)


def main(src):
    data = json.loads((ROOT / "tools/photo_credits.json").read_text())
    src = Path(src)
    opened = {}
    def get(pid):
        if pid not in opened:
            opened[pid] = Image.open(src / f"{pid}.jpg").convert("RGB")
        return opened[pid]
    PSIZES = [(480, 600), (960, 1200)]
    for item in data["photos"]:
        im = get(item["id"])
        for use in item["uses"]:
            kind, name = use["kind"], use["name"]
            c = tuple(use.get("crop", DEF_MAIN))
            if kind == "product":
                save(crop(im, 0.8, *c), PDIR / name, PSIZES)
                if use.get("alt"):
                    save(crop(im, 0.8, *tuple(use.get("alt_crop", DEF_ALT))), PDIR / use["alt"], PSIZES)
                if use.get("detail"):
                    save(crop(im, 0.8, *tuple(use.get("detail_crop", DEF_DETAIL))), PDIR / use["detail"], PSIZES)
            elif kind == "campaign-wide":   # 16:9 hero + 1100x1400 portrait companion
                save(crop(im, 16 / 9, *c), CDIR / name, [(800, 450), (1600, 900), (2400, 1350)], 78)
                save(crop(im, 1100 / 1400, *tuple(use.get("portrait_crop", c))), CDIR / f"{name}-portrait", [(600, 764), (1100, 1400)], 78)
            elif kind == "campaign-banner":  # 2:1
                save(crop(im, 2.0, *c), CDIR / name, [(800, 400), (1600, 800), (2400, 1200)], 78)
            elif kind == "campaign-tile":    # 4:5
                save(crop(im, 0.8, *c), CDIR / name, [(600, 750), (1200, 1500)], 78)
            print("ok", name)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ROOT / "photo-src")
