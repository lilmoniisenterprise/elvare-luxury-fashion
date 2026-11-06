"""Generates TESTING.md from tools/qa_results.json (the actual QA run output)."""
import json
from pathlib import Path
R = Path(__file__).resolve().parent
d = json.loads((R / "qa_results.json").read_text())
areas = {}
for r in d["results"]:
    areas.setdefault(r["area"], []).append(r)
rows = "\n".join(f"| {r['area']} | {r['test']} | {'✅ Pass' if r['pass'] else '❌ Fail'} |" for r in d["results"])
md = f"""# ÉLVARÉ — QA Testing Report

**Result: {d['passed']} of {d['total']} automated checks passed.**

| | |
|---|---|
| Run at | {d['run_at']} (build environment clock) |
| Browser | {d['browser']} |
| Served from | `{d['base']}` (local static server mirroring the GitHub Pages project path) |
| Viewports | Mobile 375×812 (touch), Tablet 768×1024 (touch), Desktop 1440×900 |
| Duration | {d['seconds']} s |
| Raw results | `tools/qa_results.json` · Suite: `tools/qa_test.py` |

## What was tested

All results below come from the automated suite actually executed against the built site. Nothing is estimated.

| Area | Check | Result |
|---|---|---|
{rows}

## Coverage notes

- **Pages:** every HTML file (18 site pages + 32 product pages) was loaded at all three viewports and checked for HTTP errors, failed requests, console/JavaScript errors and horizontal overflow.
- **Images:** on desktop each page was scrolled like a user and every rendered image was confirmed decoded (`naturalWidth > 0`). Cards further along horizontal rails load lazily when swiped into view, by design.
- **Links:** every internal `<a href>` on every page was resolved against the files on disk. External links were confirmed to point only to `virellionapex.com`.
- **Calculations:** subtotal, free-shipping threshold, express/next-day pricing, 8.25% demonstration tax and grand totals were checked against independently computed values, including after quantity edits and removals.
- **404:** GitHub Pages serves `404.html` at any URL depth; this was simulated by serving it at `/elvare-luxury-fashion/some/deep/missing-page` and confirming styles, fonts and links still resolve via its `<base href>`.

## Bugs found and fixed during QA

1. **Filter chips could ignore a click after typing a price.** Leaving the price field triggered a re-render that replaced the chip being clicked. Fixed by only re-rendering chips/grid when their content changes (`assets/js/catalog.js`). Re-tested: pass.
2. **Headline legibility on small screens** over campaign figures — strengthened the mobile hero gradient and shortened the announcement bar on phones (visual review of mobile screenshots).

## Not tested / limitations

- **Lighthouse was not run.** The Lighthouse CLI is not installed in the build environment and package installation was unavailable, so **no Lighthouse scores are claimed.** Recommended after deployment: Chrome DevTools → Lighthouse, or https://pagespeed.web.dev/ against the live URL.
- Only Chromium (Google Chrome) was automated. Safari and Firefox were not available; the code uses widely supported standards (`:has()` is used only for a cosmetic radio-card highlight with no functional dependency).
- Real devices were not used; mobile/tablet were emulated with touch enabled.
- Screen-reader output was not tested with an actual screen reader; structural checks (labels, names, headings, landmarks, focus management) were automated.
- The live GitHub Pages deployment must be verified after Pages is enabled (see README).
"""
(R.parent / "TESTING.md").write_text(md)
print("TESTING.md written")
