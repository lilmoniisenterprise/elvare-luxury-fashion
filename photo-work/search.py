"""Runs on GitHub Actions (temporary). sheets: numbered contact sheets per group from c.txt so
candidates can be checked by eye. fetch: downloads picks (picks.txt: id lines) at 2400px.
All photos are Unsplash free-licence (non-Plus) images from images.unsplash.com."""
import sys, io, time, urllib.request, pathlib
from PIL import Image, ImageDraw
H = {"User-Agent": "Mozilla/5.0"}
def get(url):
    for i in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=H), timeout=60) as r: return r.read()
        except Exception as e: err = e; time.sleep(2)
    raise err
def groups():
    g, slot = {}, None
    for l in pathlib.Path("photo-work/c.txt").read_text().splitlines():
        l = l.strip()
        if l.startswith("@"): slot = l[1:]; g.setdefault(slot, [])
        elif l: g[slot].append(l.split("|"))
    return g
def sheets():
    out = pathlib.Path("photo-work/sheets"); out.mkdir(exist_ok=True)
    for slot, items in groups().items():
        f = out / f"{slot}.jpg"
        if f.exists(): continue
        th = []
        for pid, raw, by in items:
            try: im = Image.open(io.BytesIO(get(f"https://images.unsplash.com/photo-{raw}?w=320&fm=jpg&q=60"))).convert("RGB"); im.thumbnail((240, 300))
            except Exception as e: print("FAIL", slot, pid, e); im = Image.new("RGB", (240, 300), "red")
            th.append(im)
        cols = 6; rows = (len(th) + cols - 1) // cols
        S = Image.new("RGB", (cols * 246, rows * 326), "white"); d = ImageDraw.Draw(S)
        for i, t in enumerate(th):
            x, y = (i % cols) * 246, (i // cols) * 326
            S.paste(t, (x + 3 + (240 - t.width) // 2, y + 3 + (300 - t.height) // 2))
            d.rectangle((x + 3, y + 304, x + 60, y + 323), fill="black"); d.text((x + 8, y + 307), str(i), fill="yellow")
        S.save(f, quality=75); print("sheet", slot, len(th))
def fetch():
    d = pathlib.Path("photo-work/full"); d.mkdir(exist_ok=True)
    raws = {pid: raw for items in groups().values() for pid, raw, by in items}
    for l in pathlib.Path("photo-work/picks.txt").read_text().split():
        pid = l.strip()
        if not pid or (d / f"{pid}.jpg").exists(): continue
        try: (d / f"{pid}.jpg").write_bytes(get(f"https://images.unsplash.com/photo-{raws[pid]}?w=2400&fm=jpg&q=86")); print("got", pid)
        except Exception as e: print("FAIL", pid, e)
if __name__ == "__main__":
    for a in sys.argv[1:]: {"sheets": sheets, "fetch": fetch}[a]()
