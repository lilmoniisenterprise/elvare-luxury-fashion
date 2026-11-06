"""Runs on GitHub Actions: searches Unsplash (free licence, non-Plus only) per slot and builds
numbered contact sheets so candidates can be checked by eye. Also downloads picked photos."""
import json, sys, io, time, urllib.request, urllib.parse, pathlib
from PIL import Image, ImageDraw
H = {"User-Agent": "Mozilla/5.0 (photo-candidate helper)", "Accept": "application/json"}
out = pathlib.Path("photo-work/out"); out.mkdir(parents=True, exist_ok=True)
def get(url, binary=False):
    for i in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=H), timeout=60) as r:
                b = r.read(); return b if binary else json.loads(b)
        except Exception as e:
            err = e; time.sleep(3)
    raise err
def search():
    db = {}
    p = pathlib.Path("photo-work/candidates.json")
    if p.exists(): db = json.loads(p.read_text())
    for line in pathlib.Path("photo-work/queries.txt").read_text().splitlines():
        if not line.strip() or line.startswith("#"): continue
        slot, q = line.split("|", 1)
        if slot in db and db[slot]["q"] == q: continue
        orient = "landscape" if slot.startswith("wide-") else "portrait"
        res = []
        for page in (1, 2):
            u = "https://unsplash.com/napi/search/photos?" + urllib.parse.urlencode({"query": q, "per_page": 30, "page": page, "orientation": orient, "plus": "none"})
            try: j = get(u)
            except Exception as e: print("FAIL", slot, e); break
            for r in j.get("results", []):
                if r.get("premium") or r.get("plus"): continue
                res.append({"id": r["id"], "w": r["width"], "h": r["height"], "by": r["user"]["name"], "user": r["user"]["username"],
                            "alt": r.get("alt_description") or "", "raw": r["urls"]["raw"].split("?")[0]})
            if len(res) >= 40: break
        res = res[:40]
        db[slot] = {"q": q, "c": res}
        thumbs = []
        for r in res:
            try: thumbs.append(Image.open(io.BytesIO(get(r["raw"] + "?w=260&h=325&fit=crop&fm=jpg&q=60", True))).convert("RGB").resize((200, 250)))
            except Exception: thumbs.append(Image.new("RGB", (200, 250), "red"))
        cols = 8; rows = max(1, (len(thumbs) + cols - 1) // cols)
        sheet = Image.new("RGB", (cols * 204, rows * 274), "white"); d = ImageDraw.Draw(sheet)
        for i, t in enumerate(thumbs):
            x, y = (i % cols) * 204, (i // cols) * 274
            sheet.paste(t, (x + 2, y + 2)); d.rectangle((x + 2, y + 252, x + 202, y + 272), fill="black")
            d.text((x + 8, y + 256), f"{i}", fill="yellow")
        sheet.save(out / f"{slot}.jpg", quality=72)
        print("ok", slot, len(res))
    p.write_text(json.dumps(db, indent=0))
def fetch():
    # picks.txt lines: name|unsplash_id
    d = pathlib.Path("photo-work/full"); d.mkdir(exist_ok=True)
    for line in pathlib.Path("photo-work/picks.txt").read_text().splitlines():
        if not line.strip() or line.startswith("#"): continue
        name, pid = line.split("|")[:2]
        f = d / f"{pid}.jpg"
        if f.exists(): continue
        try:
            j = get(f"https://unsplash.com/napi/photos/{pid}")
            if j.get("premium") or j.get("plus"): print("PLUS", pid); continue
            raw = j["urls"]["raw"].split("?")[0]
            f.write_bytes(get(raw + "?w=2400&fm=jpg&q=86", True))
            meta = {"id": pid, "by": j["user"]["name"], "user": j["user"]["username"], "w": j["width"], "h": j["height"], "alt": j.get("alt_description") or ""}
            (d / f"{pid}.json").write_text(json.dumps(meta))
            print("got", name, pid)
        except Exception as e: print("FAIL", pid, e)
if __name__ == "__main__":
    {"search": search, "fetch": fetch}[sys.argv[1]]()
