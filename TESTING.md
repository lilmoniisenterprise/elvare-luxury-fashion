# ÉLVARÉ — QA Testing Report

**Result: 107 of 107 automated checks passed.**

| | |
|---|---|
| Run at | 2026-11-06 04:00:43 (build environment clock) |
| Browser | Google Chrome (headless) via Playwright |
| Served from | `http://localhost:8766/elvare-luxury-fashion/` (local static server mirroring the GitHub Pages project path) |
| Viewports | Mobile 375×812 (touch), Tablet 768×1024 (touch), Desktop 1440×900 |
| Duration | 196.3 s |
| Raw results | `tools/qa_results.json` · Suite: `tools/qa_test.py` |

## What was tested

All results below come from the automated suite actually executed against the built site. Nothing is estimated.

| Area | Check | Result |
|---|---|---|
| Pages | 46 HTML files found | ✅ Pass |
| Pages | All pages return 200 with no failed requests (mobile) | ✅ Pass |
| JavaScript | No console/page errors on any page (mobile) | ✅ Pass |
| Responsive | No horizontal overflow on any page (mobile 375px) | ✅ Pass |
| Pages | All pages return 200 with no failed requests (tablet) | ✅ Pass |
| JavaScript | No console/page errors on any page (tablet) | ✅ Pass |
| Responsive | No horizontal overflow on any page (tablet 768px) | ✅ Pass |
| Pages | All pages return 200 with no failed requests (desktop) | ✅ Pass |
| JavaScript | No console/page errors on any page (desktop) | ✅ Pass |
| Responsive | No horizontal overflow on any page (desktop 1440px) | ✅ Pass |
| Images | All rendered images load after scrolling (desktop) | ✅ Pass |
| Links | All 46 unique internal link targets resolve | ✅ Pass |
| Links | External CTAs point only to virellionapex.com | ✅ Pass |
| Browse | Women page lists 16 products | ✅ Pass |
| Category nav | Dresses tab shows only dresses (3) | ✅ Pass |
| Category nav | URL reflects category (?cat=dresses) | ✅ Pass |
| Sorting | Price low→high is ascending | ✅ Pass |
| Sorting | Price high→low is descending | ✅ Pass |
| Sorting | Newest sorts by date added | ✅ Pass |
| Sorting | Popularity sorts by popularity score | ✅ Pass |
| Filtering | Price $200–$300 filter | ✅ Pass |
| Filtering | Size 38 filter (footwear only) | ✅ Pass |
| Filtering | Colour 'Champagne' filter | ✅ Pass |
| Filtering | Impossible combination shows empty state | ✅ Pass |
| Filtering | Clear filters restores all 16 | ✅ Pass |
| Category nav | Men ?cat=outerwear deep link restores filter (2 coats) | ✅ Pass |
| Collections | shop.html?collection=evening shows the Evening Edit | ✅ Pass |
| Search | Search 'coat' returns coats | ✅ Pass |
| Search | Search 'silk' returns silk pieces | ✅ Pass |
| Search | Search with no match shows empty state | ✅ Pass |
| Search | Header search overlay shows live suggestions | ✅ Pass |
| Search | Submitting header search opens results page | ✅ Pass |
| Product | Add to bag without size shows validation error | ✅ Pass |
| Colour selection | Selecting Obsidian swaps product image and label | ✅ Pass |
| Gallery | Thumbnail switches main image to detail view | ✅ Pass |
| Gallery | Next arrow cycles the gallery | ✅ Pass |
| Size selection | Selecting size M updates state | ✅ Pass |
| Cart | Add 2 × dress → bag count 2 | ✅ Pass |
| Cart drawer | Cart drawer opens after add | ✅ Pass |
| Cart | Line stores chosen colour and size | ✅ Pass |
| Accessibility | Escape closes the cart drawer | ✅ Pass |
| Size guide | Size guide modal opens, tabs switch, Escape closes | ✅ Pass |
| Recently viewed | Recently viewed shows previously visited product | ✅ Pass |
| Recommendations | Related products rail is populated | ✅ Pass |
| Quick view | Quick view validates size then adds to bag | ✅ Pass |
| Persistence | Bag persists after reload (localStorage) | ✅ Pass |
| Persistence | 3 distinct lines stored in localStorage | ✅ Pass |
| Totals | Subtotal $1,780 correct | ✅ Pass |
| Totals | Free standard shipping applied over $500 | ✅ Pass |
| Totals | Tax 8.25% = $146.85 | ✅ Pass |
| Totals | Grand total = subtotal + shipping + tax | ✅ Pass |
| Cart | Decrease quantity updates count (4→3) | ✅ Pass |
| Cart | Typing quantity 3 updates line (count 5) | ✅ Pass |
| Cart | Remove line works (count 4) | ✅ Pass |
| Totals | Totals recalculate after edits | ✅ Pass |
| Totals | Under $500: standard $25, express $35, tax on $65 | ✅ Pass |
| Checkout | Empty information step shows field errors | ✅ Pass |
| Form validation | Invalid email and ZIP are rejected | ✅ Pass |
| Checkout | Valid information advances to Delivery | ✅ Pass |
| Checkout | Delivery option updates summary (Express $35) | ✅ Pass |
| Checkout | Payment step offers 3 simulated methods, no card inputs | ✅ Pass |
| Checkout | Order cannot be placed without accepting demo terms | ✅ Pass |
| Checkout | Confirmation shows demo order number ELV-YYMMDD-XXXX | ✅ Pass |
| Checkout | Receipt total matches bag total with express | ✅ Pass |
| Checkout | Receipt is labelled as a demonstration | ✅ Pass |
| Checkout | Bag is emptied after order | ✅ Pass |
| Checkout | Printable receipt button present (window.print) | ✅ Pass |
| Checkout | Print stylesheet hides header/footer | ✅ Pass |
| Checkout | Last demo receipt can be reopened from empty checkout | ✅ Pass |
| Wishlist | Heart toggles add to wishlist (count 2) | ✅ Pass |
| Wishlist | Wishlist page lists saved items | ✅ Pass |
| Wishlist | Removing from wishlist page updates list | ✅ Pass |
| Wishlist | Wishlist persists after reload | ✅ Pass |
| Newsletter | Newsletter rejects invalid and confirms valid email (demo) | ✅ Pass |
| Form validation | Contact form flags required fields | ✅ Pass |
| Form validation | Contact form validates order number format | ✅ Pass |
| Form validation | Valid contact form shows honest demo confirmation | ✅ Pass |
| FAQ | FAQ accordions expand | ✅ Pass |
| FAQ | FAQ item opens on click | ✅ Pass |
| Privacy | 'Clear demo data' empties wishlist | ✅ Pass |
| Mobile nav | Desktop nav hidden, menu button visible at 375px | ✅ Pass |
| Mobile nav | Menu drawer opens | ✅ Pass |
| Mobile nav | Submenu link navigates to Women › Knitwear | ✅ Pass |
| Mobile filters | Filter drawer opens and closes on mobile | ✅ Pass |
| Responsive | Product grid is 2 columns on mobile | ✅ Pass |
| Touch targets | Interactive controls ≥ 36px on mobile (most ≥ 44px) | ✅ Pass |
| Mobile cart | Add to bag on mobile opens drawer | ✅ Pass |
| Back to top | Back-to-top appears after scrolling | ✅ Pass |
| Back to top | Back-to-top returns to top | ✅ Pass |
| Responsive | Tablet 768px grid shows 2 columns with filter drawer | ✅ Pass |
| SEO/A11y | Every page: one h1, description, canonical, OG + Twitter tags, alt on all images, labelled inputs, named buttons, valid JSON-LD | ✅ Pass |
| SEO | Page titles are unique | ✅ Pass |
| SEO | Product page has Product + BreadcrumbList JSON-LD | ✅ Pass |
| Keyboard | First Tab focuses the skip link | ✅ Pass |
| Keyboard | Skip link moves focus to main content | ✅ Pass |
| Keyboard | Arrow keys move through size radio group | ✅ Pass |
| Keyboard | Arrow keys browse the image gallery | ✅ Pass |
| Keyboard | Focus is trapped inside open cart drawer | ✅ Pass |
| Deployment | sitemap.xml served | ✅ Pass |
| Deployment | robots.txt served | ✅ Pass |
| Deployment | site.webmanifest served | ✅ Pass |
| Deployment | favicon.svg served | ✅ Pass |
| Deployment | .nojekyll served | ✅ Pass |
| Deployment | assets/img/og/elvare-og.jpg served | ✅ Pass |
| SEO | Sitemap lists home, category and all 32 product URLs | ✅ Pass |
| 404 | Custom 404 renders styled with working assets at nested path | ✅ Pass |
| 404 | 404 'Return home' link resolves to site home | ✅ Pass |

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
