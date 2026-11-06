"""Rasterises favicons, app icons and the Open Graph image with headless Chrome.
Run from project root after build_brand.py and build_images.py:  python3 tools/build_icons.py
"""
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT = Path(__file__).resolve().parent.parent
B = ROOT / "assets/brand"
fav = (ROOT / "favicon.svg").read_text()
mono = (B / "elvare-monogram-ivory.svg").read_text()
word = (B / "elvare-wordmark-tagline-ivory.svg").read_text()
import base64
# embedded as a data URI: file:// backgrounds are blocked inside set_content() pages
hero = "data:image/webp;base64," + base64.b64encode((ROOT / "assets/img/campaign/collection-signature-1200.webp").read_bytes()).decode()

def shot(pg, html, w, h, out, jpeg=False):
    pg.set_viewport_size({"width": w, "height": h})
    pg.set_content(f"<html><body style='margin:0;width:{w}px;height:{h}px;overflow:hidden'>{html}</body></html>")
    pg.wait_for_timeout(150)
    pg.screenshot(path=str(out), type="jpeg" if jpeg else "png", quality=86 if jpeg else None, omit_background=False)

with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--allow-file-access-from-files"])
    pg = b.new_page()
    for size, name in [(32, "favicon-32.png"), (180, "apple-touch-icon.png"), (192, "icon-192.png"), (512, "icon-512.png")]:
        shot(pg, f"<div style='width:{size}px;height:{size}px'>{fav.replace('<svg ', f'<svg width=\"{size}\" height=\"{size}\" ')}</div>", size, size, B / name)
    shot(pg, f"<div style='width:512px;height:512px;background:#111;display:grid;place-items:center'><div style='width:250px'>{mono.replace('<svg ', '<svg width=\"250\" ')}</div></div>", 512, 512, B / "icon-maskable-512.png")
    og = (f"<div style='position:relative;width:1200px;height:630px;background:#111'>"
          f"<div style='position:absolute;right:0;top:0;width:560px;height:630px;background:url({hero}) center 35%/cover'></div>"
          f"<div style='position:absolute;right:0;top:0;width:560px;height:630px;background:linear-gradient(90deg,#111 0%,rgba(17,17,17,0) 30%)'></div>"
          f"<div style='position:absolute;left:80px;top:50%;transform:translateY(-50%);width:520px'>{word.replace('<svg ', '<svg width=\"520\" ')}</div>"
          f"<div style='position:absolute;left:80px;bottom:46px;font:500 13px/1 Arial;letter-spacing:.24em;color:#C6A66B'>LUXURY FASHION HOUSE · A VIRELLION APEX DEMONSTRATION</div></div>")
    shot(pg, og, 1200, 630, ROOT / "assets/img/og/elvare-og.jpg", jpeg=True)
    b.close()
print("icons + og written")
