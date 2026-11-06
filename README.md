# ÉLVARÉ — The Art of Modern Luxury

**Portfolio Project 02 · Virellion Apex** — a fully functional luxury fashion e-commerce demonstration website.

ÉLVARÉ is a **fictional** fashion house for women and men. The site demonstrates luxury brand development, editorial UI/UX, a complete front-end shopping experience (browse → filter → product → bag → checkout → receipt) and deployment-ready static engineering. All transactions are simulated; no payment is ever requested or taken.

- Live URL (after deployment): `https://lilmoniisenterprise.github.io/elvare-luxury-fashion/`
- Designed & developed by [Virellion Apex](https://virellionapex.com)

---

## Features

| Area | What works |
|---|---|
| Brand | Original outlined-vector wordmark, arched-window monogram, favicon set, app icons, Open Graph image |
| Pages | Home, Women, Men, Shop All/Search, Collections, 32 product pages, Our Story, Contact + FAQ, Shipping & Returns, Privacy, Terms, Bag, Wishlist, Checkout, custom 404 |
| Catalog | 32 fictional products (16 women / 16 men), unique IDs, categories, descriptions, prices, sizes, colourways, tags, availability |
| Browsing | Category tabs, live search with suggestions, price/size/colour/stock filters, sort by featured/newest/popularity/price, shareable URLs, quick view |
| Product | Gallery with thumbnails, arrows, keyboard, swipe and click-to-zoom; per-colour imagery; size & colour selection; quantity; size guide modal; related products; recently viewed |
| Bag | Drawer + full page, add/remove/update, free-shipping progress, shipping, 8.25% demo tax, totals in cents, `localStorage` persistence, cross-tab sync |
| Checkout | Information → Delivery → Simulated payment (no card fields) → Confirmation, demo order number, printable receipt |
| Extras | Wishlist, newsletter demo, mobile nav drawer, mobile filter drawer, breadcrumbs, back-to-top, toasts, privacy "clear demo data" |
| Quality | Semantic HTML, skip link, focus trapping, ARIA radios/dialogs, reduced-motion support, lazy-loaded responsive WebP, JSON-LD, sitemap, robots, manifest |

## Project structure

```
elvare-luxury-fashion/
├── index.html, women.html, men.html, shop.html, collections.html
├── about.html, contact.html, shipping.html, privacy.html, terms.html
├── cart.html, wishlist.html, checkout.html, 404.html
├── product/                 32 generated product detail pages
├── assets/
│   ├── css/styles.css       design system + layout (mobile-first)
│   ├── js/                  products.js (data), app.js (core), catalog.js, product.js,
│   │                        cart.js, checkout.js, wishlist.js, forms.js
│   ├── fonts/               self-hosted WOFF (Latin Modern Roman 17 / Inter)
│   ├── brand/               logo, monogram, favicons, app icons
│   └── img/                 products/ (per-colour WebP, 480 & 960w), campaign/, og/
├── tools/                   build + QA scripts (not needed at runtime)
├── favicon.svg, site.webmanifest, sitemap.xml, robots.txt, .nojekyll
├── README.md, CHANGELOG.md, TESTING.md
```

No framework and no runtime dependencies: plain HTML5, CSS3 and vanilla JavaScript. Every path is relative, so the site works on GitHub Pages project URLs, Cloudflare Pages or a custom subdomain.

## Deploying to GitHub Pages

1. Create an **empty public** repository named `elvare-luxury-fashion` (no README).
2. Upload the contents of this folder (not the folder itself) to the repository root, or from a terminal:
   ```bash
   cd elvare-luxury-fashion
   git init && git add . && git commit -m "ÉLVARÉ v1.0.0"
   git branch -M main
   git remote add origin https://github.com/lilmoniisenterprise/elvare-luxury-fashion.git
   git push -u origin main
   ```
3. On GitHub: **Settings → Pages → Build and deployment → Source: Deploy from a branch → Branch: `main` / `(root)` → Save.**
4. Wait 1–2 minutes, then open `https://lilmoniisenterprise.github.io/elvare-luxury-fashion/`.

### Deploying to Cloudflare Pages (optional, e.g. `fashion.virellionapex.com`)
Connect the repository in Cloudflare Pages with **no build command** and output directory `/`. After attaching a custom domain, update the URL settings below and rebuild so canonical URLs, sitemap and the 404 page match.

### If the hosting URL changes
Edit `BASE_URL` and `BASE_PATH` at the top of `tools/build_site.py`, then run `python3 tools/build_site.py`. (`BASE_PATH` is used only by `404.html`, which hosts serve at any URL depth. For a root domain set it to `/`.)

## Rebuilding (developers)

Python 3.10+ with Pillow, NumPy, OpenCV, fontTools and Playwright:

```bash
python3 tools/build_brand.py    # logo SVGs + self-hosted fonts
python3 tools/build_photos.py SRC  # crop + encode photography from downloaded originals (≈1 min)
python3 tools/build_icons.py    # favicons, app icons, OG image
python3 tools/build_site.py     # all HTML, products.js, sitemap, robots, manifest
python3 tools/qa_test.py http://localhost:8766/elvare-luxury-fashion/   # QA suite
```

The product catalog lives in `tools/catalog.py` (single source of truth for pages, data and images).

## Photography

All product and campaign images are **real fashion photographs from [Unsplash](https://unsplash.com)**, used under the [Unsplash License](https://unsplash.com/license) and **self-hosted** in this repository (no hotlinking). Every photographer is credited on the site's **Photo Credits** page (`credits.html`, linked in the footer) and in `tools/photo_credits.json`.

How the set was produced (v1.1.0):

- **Checked by eye.** Every candidate was viewed at full resolution before use. Photos were rejected for any visible brand mark: card-network logos, a designer-style lapel pin, embossed maker's stamps on bags, shoes and card holders, a check-pattern designer bag, sunglasses text, garment labels and shop signage.
- **Product matches its name.** Each colourway image shows that garment type in that colour. Where no honest match existed, the colourway was removed or renamed (for example Céleste is now Champagne, Obsidian and Garnet), and six products were renamed to match their photography: Riviera Tailored Jacket, Margaux Pleated Midi Skirt, Delmar Linen Band-Collar Shirt, Teodor Wool Cardigan, Varenne Wool Overcoat and Harbor Quilted Jacket. Descriptions and details were edited to match.
- **Crops.** Products are 4:5 (480 × 600 and 960 × 1200 WebP). The gallery's *alternate* and *detail* views are closer crops of the default colourway's photo. Campaign heroes are 16:9 with a 1100 × 1400 portrait companion for phones, the seasonal banner is 2:1, and collection and editorial tiles are 4:5.
- **File names are unchanged** (`<product-slug>-<colour>`, `-alt`, `-detail`, and the existing campaign names), so the site code didn't change.
- **Rebuild:** download each id in `tools/photo_credits.json` from Unsplash as `<id>.jpg` (about 2400 px) into a folder, then run `python3 tools/build_photos.py <folder>`. Crop centres and zoom levels live in the same JSON. The originals are not committed.

The garments pictured are by other makers and are shown only to demonstrate the store. ÉLVARÉ and its products remain fictional. For a real client, replace the photos with the brand's own photography using the same file names.

## Demonstration disclosures

- ÉLVARÉ, its products, story and policies are fictional. No real manufacturing, certification or sustainability claims are made.
- No backend: forms validate in the browser and are **not** sent; the bag, wishlist and demo orders live only in `localStorage`.
- Checkout never shows or collects card fields and connects to no payment processor.
- Contact details shown are placeholders (`.example` email, 555-01xx number).

## Production upgrade path

For a live store: a hosted commerce/payment provider (e.g. Shopify Storefront API or Stripe Checkout) for PCI-compliant payments, a serverless function or form service for contact/newsletter, a headless CMS or commerce backend for inventory, and the brand's own product photography. Virellion Apex can scope this: [Request a Similar Website](https://virellionapex.com).

## Credits & licences

- Display face: Latin Modern Roman (GUST Font License). Text face: Inter (SIL Open Font License). Both self-hosted.
- Photography: Unsplash contributors under the Unsplash License — full list on `credits.html` and in `tools/photo_credits.json`.
- Design, development and brand identity: Virellion Apex, 2026.
