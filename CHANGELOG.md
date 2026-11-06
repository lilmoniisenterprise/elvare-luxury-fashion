# Changelog

All notable changes to the ÉLVARÉ demonstration website.

## [1.1.0] — 2026-11-06

### Changed — real photography
- Replaced all rendered illustrations with **real fashion photography** from Unsplash (Unsplash License), self-hosted as responsive WebP under the existing file names. 85 photographs: 72 product colourways and 13 campaign, collection and editorial images.
- Every photo was **checked by eye** for visible brand logos and for a match with its product name and colour. Rejected candidates included card-network logos, a designer-style lapel pin, embossed maker's stamps on a bag, mules and a card holder, a check-pattern designer bag, sunglasses text, garment labels, and shop and café signage.
- Products: 4:5 crops at 480 and 960 px. Alternate and detail gallery views are closer crops of the default colourway's photograph. Campaign: 16:9 heroes with portrait companions, 2:1 seasonal banner and 4:5 tiles.
- Catalogue aligned to the photography: colourways now match the photos (for example Aurelle in Forest, Cobalt and Violet; Alba in Sand, Olive and Bordeaux). Colourways were dropped where no honest match was found. Six products were renamed: Riviera Tailored Jacket, Margaux Pleated Midi Skirt, Delmar Linen Band-Collar Shirt, Teodor Wool Cardigan, Varenne Wool Overcoat and Harbor Quilted Jacket. Their descriptions and details were edited to match.
- Rewrote campaign alt text from what each photograph shows. Product alternate views are now labelled "alternate view".
- New Open Graph image built from campaign photography. Fixed `build_icons.py`, whose `file://` background silently failed to load.
- Saved bag lines whose colourway no longer exists are dropped on load.

### Added
- **Photo Credits page** (`credits.html`) listing every photographer with a link to the original photo; linked from the footer on every page. Data in `tools/photo_credits.json`.
- `tools/build_photos.py`: reproducible crop and encode pipeline.

### Removed
- `tools/build_images.py` (illustration renderer), so it can't overwrite the photography.

### QA
- `tools/qa_test.py` updated for the renamed Varenne product (URL and colour) and the catalogue's two coats ("coats rank first" instead of "top three are coats"). 107/107 checks pass.

## [1.0.0] — 2026-11-06

### Added
- Original ÉLVARÉ brand identity: outlined-vector wordmark (black/ivory, with and without tagline), arched-window monogram, SVG + PNG favicons, Apple touch icon, PWA icons (incl. maskable), 1200×630 social-sharing image.
- Luxury editorial design system: Obsidian, Charcoal, Ivory, Champagne Gold, Stone, White; self-hosted Latin Modern Roman 17 display and Inter text faces.
- 32-product fictional catalog (16 women's, 16 men's) with IDs, categories, collections, tags, sizes, colourways, availability and premium pricing.
- Rendered product imagery for every colourway plus alternate and detail views; campaign, collection and editorial scenes; responsive WebP at multiple widths.
- Pages: Home, Women, Men, Shop All/Search, Collections, 32 product pages, Our Story, Contact with FAQ, Shipping & Returns with size guide, Privacy, Terms, Bag, Wishlist, Checkout, branded 404.
- Shopping: category navigation, live search, price/size/colour/stock filters, four sort orders, URL-synced state, quick view, product gallery with zoom/keyboard/swipe, size guide modal, recently viewed, related products.
- Bag drawer and page with quantity editing, removal, free-shipping progress, shipping, demo tax and totals calculated in cents; `localStorage` persistence and cross-tab sync.
- Simulated four-step checkout with validation, delivery options, payment-method selection without card fields, demo order numbers and printable receipt.
- Wishlist, newsletter demo, contact form validation, "clear demo data" tool, mobile navigation and filter drawers, breadcrumbs, back-to-top, toasts.
- SEO: unique titles/descriptions, canonical URLs, Open Graph and Twitter tags, JSON-LD (Organization, WebSite + SearchAction, Product, BreadcrumbList, CollectionPage, FAQPage), sitemap, robots.txt, web manifest, `.nojekyll`.
- Virellion Apex portfolio band with "Request a Similar Website", "Schedule a Consultation" and "Explore Virellion Apex" links; demonstration disclosures throughout.
- Build tooling (`tools/`) and automated Playwright QA suite with written TESTING report.
