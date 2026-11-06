"""ÉLVARÉ static site builder.

Generates every HTML page, product data, sitemap, robots and manifest from shared templates.
No runtime build step is needed for hosting: the generated files are committed as-is.
Run from project root:  python3 tools/build_site.py
"""
import json, html, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from catalog import products, CATEGORIES, COLLECTIONS  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent

# ---- Deployment configuration (change and rebuild if the hosting URL changes) ----
BASE_URL = "https://lilmoniisenterprise.github.io/elvare-luxury-fashion/"
BASE_PATH = "/elvare-luxury-fashion/"   # used only by 404.html, which GitHub Pages serves at any depth
VA = "https://virellionapex.com"
VERSION = "1.0.0"
BUILD_DATE = "2026-11-06"

PRODUCTS = products()
BY_ID = {p["id"]: p for p in PRODUCTS}
CAT_LABEL = {k: v for g in CATEGORIES.values() for k, v in g}
CAT_LABEL.update({"jackets-coats": "Jackets & Coats", "tops": "Tops & Shirts"})
SITEMAP = []

e = html.escape


def money(v):
    return f"${v:,.0f}"


ICON = {
    "search": '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="10.5" cy="10.5" r="6.5"/><path d="M15.5 15.5 21 21"/></svg>',
    "heart": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 20.5s-7.5-4.6-9.2-9.4C1.6 7.6 3.9 4.5 7.2 4.5c2 0 3.6 1.1 4.8 2.8 1.2-1.7 2.8-2.8 4.8-2.8 3.3 0 5.6 3.1 4.4 6.6-1.7 4.8-9.2 9.4-9.2 9.4z"/></svg>',
    "bag": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 8h14l-1 13H6L5 8z"/><path d="M9 8V6a3 3 0 0 1 6 0v2"/></svg>',
    "menu": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 7h18M3 12h18M3 17h12"/></svg>',
    "close": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 5l14 14M19 5 5 19"/></svg>',
    "left": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M15 4 7 12l8 8"/></svg>',
    "right": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m9 4 8 8-8 8"/></svg>',
    "up": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 15l8-8 8 8"/></svg>',
    "filter": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 6h18M6 12h12M10 18h4"/></svg>',
    "truck": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M2 6h12v10H2zM14 10h4l3 3v3h-7z"/><circle cx="6" cy="18" r="1.6"/><circle cx="17" cy="18" r="1.6"/></svg>',
    "return": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 9h11a5 5 0 0 1 0 10H8"/><path d="M8 5 4 9l4 4"/></svg>',
    "gift": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 10h16v10H4zM3 7h18v3H3zM12 7v13"/><path d="M12 7c-2-3-5-3-5-1s3 1 5 1c2 0 5 1 5-1s-3-2-5 1z"/></svg>',
    "lock": '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="5" y="11" width="14" height="10"/><path d="M8 11V8a4 4 0 0 1 8 0v3"/></svg>',
}


def srcset(base, widths=(480, 960)):
    return ", ".join(f"{base}-{w}.webp {w}w" for w in widths)


def img(rel, base, alt, sizes, widths=(480, 960), w=960, h=1200, lazy=True, cls="", fetch=None):
    attrs = f'loading="lazy" decoding="async"' if lazy else 'decoding="async"'
    if fetch:
        attrs += f' fetchpriority="{fetch}"'
    c = f' class="{cls}"' if cls else ""
    return (f'<img{c} src="{rel}{base}-{widths[0]}.webp" srcset="{", ".join(f"{rel}{base}-{x}.webp {x}w" for x in widths)}" '
            f'sizes="{sizes}" width="{w}" height="{h}" alt="{e(alt)}" {attrs}>')


def product_url(p, rel):
    return f"{rel}product/{p['slug']}.html"


def alt_text(p, color=None, view=""):
    c = color or p["colors"][0]["name"]
    return f"{p['name']} in {c}{view} — ÉLVARÉ {CAT_LABEL.get(p['category'], p['category']).lower()}"


def card(p, rel, sizes="(min-width: 1200px) 23vw, (min-width: 900px) 30vw, 48vw"):
    flag = ""
    if p["availability"] == "low_stock":
        flag = '<span class="card__flag">Low stock</span>'
    elif p["availability"] == "preorder":
        flag = '<span class="card__flag">Pre-order</span>'
    elif p["isNew"]:
        flag = '<span class="card__flag card__flag--dark">New</span>'
    dots = "".join(f'<span class="swatch-dot" style="background:{c["hex"]}" title="{e(c["name"])}"></span>' for c in p["colors"])
    return f'''<article class="card" data-id="{p['id']}">
  <div class="card__media">{flag}
    {img(rel, p['image'], alt_text(p), sizes)}
    {img(rel, 'assets/img/products/' + p['slug'] + '-alt', alt_text(p, view=', alternate view'), sizes, cls='img-alt')}
    <button class="icon-btn card__wish" type="button" data-wish="{p['id']}" aria-pressed="false" aria-label="Add {e(p['name'])} to wishlist">{ICON['heart']}</button>
    <button class="card__quick" type="button" data-quick="{p['id']}">Quick view</button>
  </div>
  <div class="card__body">
    <span class="card__cat">{e(CAT_LABEL.get(p['category'], ''))}</span>
    <h3 class="card__name"><a href="{product_url(p, rel)}">{e(p['name'])}</a></h3>
    <span class="card__price">{money(p['price'])}</span>
    <div class="swatches" aria-label="{len(p['colors'])} colours available">{dots}</div>
  </div>
</article>'''


# ------------------------------------------------------------------ layout
def head(title, desc, path, rel, og="assets/img/og/elvare-og.jpg", jsonld=(), noindex=False, base=None):
    url = BASE_URL + ("" if path == "index.html" else path)
    ld = "".join(f'<script type="application/ld+json">{json.dumps(j, ensure_ascii=False)}</script>' for j in jsonld)
    full_title = title if "ÉLVARÉ" in title else f"{title} | ÉLVARÉ"
    robots = '<meta name="robots" content="noindex, follow">' if noindex else '<meta name="robots" content="index, follow, max-image-preview:large">'
    basetag = f'<base href="{base}">' if base else ""
    return f'''<!DOCTYPE html>
<html lang="en" class="no-js">
<head>
<meta charset="utf-8">
{basetag}<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(full_title)}</title>
<meta name="description" content="{e(desc)}">
{robots}
<link rel="canonical" href="{url}">
<meta name="theme-color" content="#111111">
<meta property="og:type" content="website">
<meta property="og:site_name" content="ÉLVARÉ">
<meta property="og:title" content="{e(full_title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{BASE_URL}{og}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="ÉLVARÉ — The Art of Modern Luxury">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{e(full_title)}">
<meta name="twitter:description" content="{e(desc)}">
<meta name="twitter:image" content="{BASE_URL}{og}">
<link rel="icon" href="{rel}favicon.svg" type="image/svg+xml">
<link rel="icon" href="{rel}assets/brand/favicon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="{rel}assets/brand/apple-touch-icon.png">
<link rel="manifest" href="{rel}site.webmanifest">
<link rel="preload" href="{rel}assets/fonts/lm-roman-17.woff" as="font" type="font/woff" crossorigin>
<link rel="preload" href="{rel}assets/fonts/inter-400.woff" as="font" type="font/woff" crossorigin>
<link rel="stylesheet" href="{rel}assets/css/styles.css?v={VERSION}">
<script>document.documentElement.classList.remove('no-js');</script>
{ld}
</head>'''


NAV = [("women.html", "Women"), ("men.html", "Men"), ("collections.html", "Collections"), ("about.html", "Our Story")]


def header(rel, active):
    links = "".join(f'<li><a href="{rel}{h}"{" aria-current=\"page\"" if h == active else ""}>{t}</a></li>' for h, t in NAV)
    wcats = "".join(f'<li><a href="{rel}women.html?cat={k}">{v}</a></li>' for k, v in CATEGORIES["women"])
    mcats = "".join(f'<li><a href="{rel}men.html?cat={k}">{v}</a></li>' for k, v in CATEGORIES["men"])
    return f'''<a class="skip-link" href="#main">Skip to content</a>
<div class="announce">Complimentary standard shipping over $500 · <a href="{rel}shipping.html">Demonstration store</a><span class="announce-long"> — no real orders are placed</span></div>
<header class="site-header" id="top">
  <div class="container header-inner">
    <div class="header-left">
      <button class="icon-btn hide-desktop" type="button" data-open="nav-drawer" aria-controls="nav-drawer" aria-expanded="false" aria-label="Open menu">{ICON['menu']}</button>
      <nav class="main-nav" aria-label="Primary"><ul>{links}</ul></nav>
    </div>
    <a class="logo" href="{rel}index.html" aria-label="ÉLVARÉ home"><img src="{rel}assets/brand/elvare-wordmark-black.svg" alt="ÉLVARÉ" width="500" height="100"></a>
    <div class="header-right">
      <button class="icon-btn" type="button" data-open-search aria-label="Search">{ICON['search']}</button>
      <a class="icon-btn hide-mobile" href="{rel}wishlist.html" aria-label="Wishlist">{ICON['heart']}<span class="badge" data-wish-count data-count="0">0</span></a>
      <button class="icon-btn" type="button" data-open="cart-drawer" aria-controls="cart-drawer" aria-expanded="false" aria-label="Shopping bag">{ICON['bag']}<span class="badge" data-cart-count data-count="0">0</span></button>
    </div>
  </div>
</header>
<div class="drawer drawer--left" id="nav-drawer" aria-hidden="true">
  <div class="drawer__scrim" data-close></div>
  <div class="drawer__panel" role="dialog" aria-modal="true" aria-label="Menu">
    <div class="drawer__head"><img src="{rel}assets/brand/elvare-wordmark-black.svg" alt="ÉLVARÉ" width="130" height="26" style="height:18px;width:auto"><button class="icon-btn" type="button" data-close aria-label="Close menu">{ICON['close']}</button></div>
    <nav class="drawer__body mobile-nav" aria-label="Mobile">
      <details><summary>Women</summary><ul class="sub">{wcats}<li><a href="{rel}women.html">Shop all women</a></li></ul></details>
      <details><summary>Men</summary><ul class="sub">{mcats}<li><a href="{rel}men.html">Shop all men</a></li></ul></details>
      <a href="{rel}collections.html">Collections</a>
      <a href="{rel}about.html">Our Story</a>
      <a href="{rel}shop.html">Shop All</a>
      <div class="utility">
        <a href="{rel}wishlist.html">Wishlist (<span data-wish-count-text>0</span>)</a>
        <a href="{rel}cart.html">Shopping bag</a>
        <a href="{rel}contact.html">Client services</a>
        <a href="{rel}shipping.html">Shipping &amp; returns</a>
      </div>
    </nav>
  </div>
</div>'''


def footer(rel):
    year = BUILD_DATE[:4]
    return f'''<section class="va-band" aria-labelledby="va-title">
  <div class="container va-band__inner">
    <div>
      <span class="eyebrow">Portfolio Project 02 · Virellion Apex</span>
      <h2 id="va-title">Want a luxury storefront like this?</h2>
      <p>ÉLVARÉ is a fictional fashion house designed and developed by Virellion Apex to demonstrate luxury brand development, e-commerce UX and responsive web engineering.</p>
    </div>
    <div class="va-band__ctas">
      <a class="btn btn--gold" href="{VA}" rel="noopener">Request a Similar Website</a>
      <a class="btn btn--outline-light" href="{VA}" rel="noopener">Schedule a Consultation</a>
    </div>
  </div>
</section>
<footer class="site-footer">
  <div class="container">
    <div class="footer-top">
      <div class="footer-brand">
        <img src="{rel}assets/brand/elvare-wordmark-ivory.svg" alt="ÉLVARÉ" width="500" height="100" loading="lazy">
        <p>The Art of Modern Luxury. Contemporary fashion for women and men — timeless silhouettes, refined tailoring and understated detail.</p>
        <img class="footer-monogram" src="{rel}assets/brand/elvare-monogram-ivory.svg" alt="" width="200" height="260" loading="lazy">
      </div>
      <div class="footer-col"><h2>Shop</h2><ul>
        <li><a href="{rel}women.html">Women</a></li><li><a href="{rel}men.html">Men</a></li>
        <li><a href="{rel}women.html?cat=new">New Arrivals</a></li><li><a href="{rel}collections.html">Collections</a></li>
        <li><a href="{rel}shop.html?cat=accessories">Accessories</a></li><li><a href="{rel}wishlist.html">Wishlist</a></li></ul></div>
      <div class="footer-col"><h2>Client Services</h2><ul>
        <li><a href="{rel}contact.html">Contact</a></li><li><a href="{rel}shipping.html">Shipping &amp; Returns</a></li>
        <li><a href="{rel}contact.html#faq">FAQ</a></li><li><a href="{rel}shipping.html#size-guide">Size Guide</a></li>
        <li><a href="{rel}cart.html">Shopping Bag</a></li></ul></div>
      <div class="footer-col"><h2>The House</h2><ul>
        <li><a href="{rel}about.html">Our Story</a></li><li><a href="{rel}privacy.html">Privacy Policy</a></li>
        <li><a href="{rel}terms.html">Terms &amp; Conditions</a></li><li><a href="{rel}sitemap.xml">Sitemap</a></li>
        <li><a href="{VA}" rel="noopener">Explore Virellion Apex</a></li></ul></div>
    </div>
    <div class="footer-bottom">
      <p>© {year} ÉLVARÉ — a fictional brand. Demonstration website: products, prices, policies and transactions are simulated. No payments are taken.</p>
      <p>Designed &amp; developed by <a href="{VA}" rel="noopener">Virellion Apex</a></p>
    </div>
  </div>
</footer>'''


def shell_extras(rel):
    """Search overlay, cart drawer, modals, toast, back to top — present on every page."""
    return f'''<div class="search-overlay" id="search-overlay" role="dialog" aria-modal="true" aria-label="Search" aria-hidden="true">
  <button class="icon-btn search-close" type="button" data-close-search aria-label="Close search">{ICON['close']}</button>
  <form action="{rel}shop.html" method="get" role="search">
    <label for="search-input">Search the house</label>
    <div class="search-field"><input id="search-input" name="q" type="search" autocomplete="off" placeholder="Coats, silk, tailoring…"><button class="icon-btn" type="submit" aria-label="Submit search">{ICON['search']}</button></div>
    <div class="search-popular" aria-label="Popular searches">
      <a class="chip" href="{rel}shop.html?q=coat">Coats</a><a class="chip" href="{rel}shop.html?q=silk">Silk</a><a class="chip" href="{rel}shop.html?q=knit">Knitwear</a><a class="chip" href="{rel}shop.html?q=leather">Leather</a><a class="chip" href="{rel}shop.html?q=tailoring">Tailoring</a>
    </div>
  </form>
  <div class="search-suggest" id="search-suggest" aria-live="polite"></div>
</div>
<div class="drawer drawer--right" id="cart-drawer" aria-hidden="true">
  <div class="drawer__scrim" data-close></div>
  <div class="drawer__panel" role="dialog" aria-modal="true" aria-labelledby="cart-title">
    <div class="drawer__head"><h2 class="drawer__title" id="cart-title">Shopping Bag</h2><button class="icon-btn" type="button" data-close aria-label="Close bag">{ICON['close']}</button></div>
    <div class="drawer__body" data-cart-lines></div>
    <div class="drawer__foot" data-cart-foot></div>
  </div>
</div>
<div class="modal" id="quickview" aria-hidden="true">
  <div class="modal__scrim" data-close></div>
  <div class="modal__dialog" role="dialog" aria-modal="true" aria-labelledby="qv-title">
    <button class="icon-btn modal__close" type="button" data-close aria-label="Close quick view">{ICON['close']}</button>
    <div data-qv-body></div>
  </div>
</div>
<div class="modal" id="size-guide" aria-hidden="true">
  <div class="modal__scrim" data-close></div>
  <div class="modal__dialog modal__dialog--sm" role="dialog" aria-modal="true" aria-labelledby="sg-title">
    <button class="icon-btn modal__close" type="button" data-close aria-label="Close size guide">{ICON['close']}</button>
    {size_guide_html('sg-title')}
  </div>
</div>
<div class="toast-region" aria-live="polite" aria-atomic="true"></div>
<button class="to-top" type="button" data-to-top aria-label="Back to top">{ICON['up']}</button>'''


def size_guide_html(title_id, heading="h2"):
    return f'''<{heading} id="{title_id}">Size Guide</{heading}>
<p class="form-note" style="margin-top:0">Body measurements in centimetres. If you are between sizes, we suggest the larger size for tailoring and the smaller for knitwear.</p>
<div class="tabs" role="tablist" aria-label="Size guide">
  <button class="chip is-active" type="button" role="tab" aria-selected="true" data-sg-tab="sg-women">Women</button>
  <button class="chip" type="button" role="tab" aria-selected="false" data-sg-tab="sg-men">Men</button>
  <button class="chip" type="button" role="tab" aria-selected="false" data-sg-tab="sg-shoes">Footwear</button>
</div>
<div class="table-wrap" data-sg-panel="sg-women" role="tabpanel"><table class="size-table"><thead><tr><th>Size</th><th>Bust</th><th>Waist</th><th>Hip</th><th>Trouser</th></tr></thead><tbody>
<tr><td>XS</td><td>80–83</td><td>62–65</td><td>87–90</td><td>24</td></tr><tr><td>S</td><td>84–87</td><td>66–69</td><td>91–94</td><td>26</td></tr><tr><td>M</td><td>88–92</td><td>70–74</td><td>95–99</td><td>28</td></tr><tr><td>L</td><td>93–97</td><td>75–79</td><td>100–104</td><td>30</td></tr><tr><td>XL</td><td>98–103</td><td>80–85</td><td>105–110</td><td>32</td></tr></tbody></table></div>
<div class="table-wrap" data-sg-panel="sg-men" role="tabpanel" hidden><table class="size-table"><thead><tr><th>Size</th><th>Chest</th><th>Waist</th><th>Neck</th><th>Trouser</th></tr></thead><tbody>
<tr><td>S</td><td>88–94</td><td>74–79</td><td>37–38</td><td>28–30</td></tr><tr><td>M</td><td>95–101</td><td>80–85</td><td>39–40</td><td>32</td></tr><tr><td>L</td><td>102–108</td><td>86–92</td><td>41–42</td><td>34</td></tr><tr><td>XL</td><td>109–115</td><td>93–99</td><td>43–44</td><td>36</td></tr><tr><td>XXL</td><td>116–122</td><td>100–106</td><td>45–46</td><td>38</td></tr></tbody></table></div>
<div class="table-wrap" data-sg-panel="sg-shoes" role="tabpanel" hidden><table class="size-table"><thead><tr><th>EU</th><th>UK</th><th>US Women</th><th>US Men</th><th>Foot length</th></tr></thead><tbody>
<tr><td>36</td><td>3</td><td>6</td><td>—</td><td>23.0</td></tr><tr><td>37</td><td>4</td><td>7</td><td>—</td><td>23.7</td></tr><tr><td>38</td><td>5</td><td>8</td><td>—</td><td>24.3</td></tr><tr><td>39</td><td>6</td><td>9</td><td>—</td><td>25.0</td></tr><tr><td>40</td><td>6.5</td><td>9.5</td><td>7</td><td>25.6</td></tr><tr><td>41</td><td>7.5</td><td>10.5</td><td>8</td><td>26.3</td></tr><tr><td>42</td><td>8</td><td>—</td><td>9</td><td>27.0</td></tr><tr><td>43</td><td>9</td><td>—</td><td>10</td><td>27.6</td></tr><tr><td>44</td><td>9.5</td><td>—</td><td>10.5</td><td>28.3</td></tr><tr><td>45</td><td>10.5</td><td>—</td><td>11.5</td><td>29.0</td></tr></tbody></table></div>'''


def page(path, title, desc, body, active="", jsonld=(), scripts=(), rel="", noindex=False, body_attrs="", base=None, sitemap=True, priority="0.7"):
    js = "".join(f'<script src="{rel}assets/js/{s}?v={VERSION}" defer></script>' for s in ("products.js", "app.js") + tuple(scripts))
    doc = f'''{head(title, desc, path, rel, jsonld=jsonld, noindex=noindex, base=base)}
<body data-root="{rel}" {body_attrs}>
{header(rel, active)}
<main id="main" tabindex="-1">
{body}
</main>
{footer(rel)}
{shell_extras(rel)}
{js}
</body>
</html>
'''
    out = ROOT / path
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(doc)
    if sitemap and not noindex:
        SITEMAP.append((path, priority))


def breadcrumb(rel, items):
    lis = "".join((f'<li><a href="{rel}{h}">{e(t)}</a></li>' if h else f'<li aria-current="page">{e(t)}</li>') for t, h in items)
    return f'<nav class="breadcrumb" aria-label="Breadcrumb"><ol>{lis}</ol></nav>'


def crumb_ld(items):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": t, **({"item": BASE_URL + h} if h is not None else {})} for i, (t, h) in enumerate(items)]}


def picture(rel, wide, tall, alt, eager=False):
    lazy = 'decoding="async" fetchpriority="high"' if eager else 'loading="lazy" decoding="async"'
    return f'''<picture>
  <source media="(max-width: 700px)" srcset="{rel}assets/img/campaign/{tall}-600.webp 600w, {rel}assets/img/campaign/{tall}-1100.webp 1100w" sizes="100vw">
  <img src="{rel}assets/img/campaign/{wide}-1600.webp" srcset="{rel}assets/img/campaign/{wide}-800.webp 800w, {rel}assets/img/campaign/{wide}-1600.webp 1600w, {rel}assets/img/campaign/{wide}-2400.webp 2400w" sizes="100vw" width="2400" height="1350" alt="{e(alt)}" {lazy}>
</picture>'''


def camp(rel, name, alt, sizes="(min-width: 900px) 33vw, 100vw", widths=(600, 1200), w=1200, h=1500, cls=""):
    return img(rel, f"assets/img/campaign/{name}", alt, sizes, widths, w, h, cls=cls)


# ------------------------------------------------------------------ pages
ORG_LD = {"@context": "https://schema.org", "@type": "Organization", "name": "ÉLVARÉ", "url": BASE_URL,
          "logo": BASE_URL + "assets/brand/elvare-monogram-obsidian.svg", "slogan": "The Art of Modern Luxury",
          "description": "ÉLVARÉ is a fictional luxury fashion house created as a demonstration website by Virellion Apex."}
SITE_LD = {"@context": "https://schema.org", "@type": "WebSite", "name": "ÉLVARÉ", "url": BASE_URL,
           "potentialAction": {"@type": "SearchAction", "target": BASE_URL + "shop.html?q={search_term_string}", "query-input": "required name=search_term_string"}}


def rail(rel, items, label, rid):
    cards = "".join(card(p, rel, "(min-width: 900px) 24vw, (min-width: 600px) 40vw, 68vw") for p in items)
    return f'''<div class="rail-wrap"><div class="rail" id="{rid}" tabindex="0" role="region" aria-label="{e(label)}">{cards}</div></div>'''


def rail_controls(rid):
    return f'<div class="rail-controls"><button class="rail-btn" type="button" data-rail="{rid}" data-dir="-1" aria-label="Scroll left">{ICON["left"]}</button><button class="rail-btn" type="button" data-rail="{rid}" data-dir="1" aria-label="Scroll right">{ICON["right"]}</button></div>'


def build_home():
    rel = ""
    new = sorted([p for p in PRODUCTS if p["isNew"]], key=lambda p: p["added"], reverse=True)
    best = sorted([p for p in PRODUCTS if p["bestseller"]], key=lambda p: -p["popularity"])[:8]
    coll_cards = "".join(f'''<article class="collection-card reveal"><a class="tile" href="collections.html#{k}">{camp(rel, "collection-" + k, f"{t} campaign illustration — ÉLVARÉ")}
      <div class="tile__label"><h3>{e(t)}</h3><p>{e(d)}</p><span class="link-arrow">Discover</span></div></a></article>''' for k, t, d in COLLECTIONS)
    body = f'''
<section class="hero" aria-labelledby="hero-title">
  {picture(rel, "hero-women", "hero-women-portrait", "Two figures in a camel belted coat and a black column dress stand in warm window light against a plaster wall — ÉLVARÉ Autumn–Winter 2026 campaign", eager=True)}
  <div class="container hero__content">
    <span class="eyebrow">Autumn–Winter 2026 · The Quiet Hour</span>
    <h1 id="hero-title">The Art of <em>Modern</em> Luxury</h1>
    <p>Timeless silhouettes, refined tailoring and understated detail — a contemporary wardrobe composed with intent.</p>
    <div class="hero__ctas"><a class="btn btn--light" href="women.html">Shop Women</a><a class="btn btn--outline-light" href="men.html">Shop Men</a></div>
  </div>
</section>

<section class="section section--tight">
  <div class="container intro reveal">
    <img class="monogram-mark" src="assets/brand/elvare-monogram-black.svg" alt="" width="200" height="260">
    <span class="eyebrow">The House of ÉLVARÉ</span>
    <h2>Quiet confidence, considered in every line.</h2>
    <p>ÉLVARÉ designs for those who dress with intention. Each piece begins with proportion — the fall of a coat, the line of a trouser, the weight of silk against light — and ends only when nothing more can be taken away.</p>
    <a class="link-arrow" href="about.html">Discover our story</a>
  </div>
</section>

<section class="section section--white" aria-labelledby="new-title">
  <div class="container">
    <div class="section-head"><div><span class="eyebrow">Just Arrived</span><h2 id="new-title">New Arrivals</h2></div>{rail_controls("rail-new")}</div>
    {rail(rel, new, "New arrivals", "rail-new")}
    <p style="margin-top:2rem"><a class="link-arrow" href="shop.html?cat=new">View all new arrivals</a></p>
  </div>
</section>

<section class="section section--tight" aria-label="Shop by department">
  <div class="container split">
    <a class="tile reveal" href="women.html">{camp(rel, "hero-women-portrait", "Women's campaign — figures in tailored outerwear in a sunlit room", "(min-width: 600px) 50vw, 100vw", (600, 1100), 1100, 1400)}
      <div class="tile__label"><span class="eyebrow">Women</span><h3>Fluid lines, precise tailoring</h3><span class="link-arrow">Shop Women</span></div></a>
    <a class="tile reveal" href="men.html">{camp(rel, "hero-men-portrait", "Men's campaign — two figures in charcoal and camel coats beside arched doorways", "(min-width: 600px) 50vw, 100vw", (600, 1100), 1100, 1400)}
      <div class="tile__label"><span class="eyebrow">Men</span><h3>Relaxed structure, enduring form</h3><span class="link-arrow">Shop Men</span></div></a>
  </div>
</section>

<section class="section" aria-labelledby="coll-title">
  <div class="container">
    <div class="section-head"><div><span class="eyebrow">Curated</span><h2 id="coll-title">Featured Collections</h2></div><a class="link-arrow" href="collections.html">All collections</a></div>
    <div class="collections-grid">{coll_cards}</div>
  </div>
</section>

<section class="campaign" aria-labelledby="season-title">
  {img(rel, "assets/img/campaign/seasonal-aw26", "A lone figure in a champagne belted coat stands in a shaft of light in a darkened room", "100vw", (800, 1600, 2400), 2400, 1200)}
  <div class="container"><div class="campaign__content reveal">
    <span class="eyebrow">Seasonal Campaign</span>
    <h2 id="season-title">The Quiet Hour</h2>
    <p>For Autumn–Winter 2026, ÉLVARÉ turns to the last light of the day: double-faced wool, cashmere-blend knits and silhouettes that hold their shape as the evening draws in.</p>
    <a class="btn btn--light" href="collections.html#seasonal">Explore the season</a>
  </div></div>
</section>

<section class="section section--white" aria-labelledby="best-title">
  <div class="container">
    <div class="section-head"><div><span class="eyebrow">Most Coveted</span><h2 id="best-title">Best Sellers</h2></div><a class="link-arrow" href="shop.html?sort=popular">Shop best sellers</a></div>
    <div class="grid grid--4">{"".join(card(p, rel) for p in best)}</div>
  </div>
</section>

<section class="section" aria-labelledby="ed-title">
  <div class="container editorial">
    <div class="editorial__images reveal">
      {camp(rel, "editorial-silk", "Close study of champagne silk satin falling in soft folds", "(min-width: 900px) 27vw, 50vw")}
      {camp(rel, "editorial-wool", "Close study of camel wool draped in deep folds", "(min-width: 900px) 27vw, 50vw")}
    </div>
    <div class="reveal">
      <span class="eyebrow">The Edit</span>
      <h2 id="ed-title" class="display">Materials first.</h2>
      <p class="quote">“We begin with how a fabric moves, and let the garment follow.”</p>
      <p class="lede">From fluid silk satin to dense double-faced wool, every ÉLVARÉ piece is designed around the character of its material — its weight, its drape and the way it meets the light.</p>
      <a class="link-arrow" href="collections.html#signature">Shop the Signature Collection</a>
    </div>
  </div>
</section>

<section class="section section--dark newsletter" aria-labelledby="nl-title">
  <div class="container narrow">
    <span class="eyebrow">The ÉLVARÉ Letter</span>
    <h2 id="nl-title">Receive the season first</h2>
    <p class="lede" style="margin-inline:auto">Collection previews, editorial stories and private invitations, delivered with restraint.</p>
    {newsletter_form("home")}
  </div>
</section>'''
    page("index.html", "ÉLVARÉ — The Art of Modern Luxury | Luxury Fashion House",
         "ÉLVARÉ is a contemporary luxury fashion house for women and men: refined tailoring, silk evening wear, cashmere-blend knitwear and leather accessories. A Virellion Apex demonstration store.",
         body, "", [ORG_LD, SITE_LD], scripts=(), priority="1.0")


def newsletter_form(fid):
    return f'''<form class="newsletter-form" data-newsletter novalidate>
      <label class="visually-hidden" for="nl-{fid}">Email address</label>
      <input class="input" id="nl-{fid}" name="email" type="email" autocomplete="email" placeholder="Your email address" required>
      <button class="btn btn--gold" type="submit">Subscribe</button>
    </form>
    <p class="form-msg" role="status" data-nl-msg></p>
    <p class="form-note">Demonstration form: your address is stored only in this browser and is never sent anywhere.</p>'''


def filters_html(scope):
    sizes = []
    for p in PRODUCTS:
        if scope in ("all", p["gender"]):
            for s in p["sizes"]:
                if s not in sizes:
                    sizes.append(s)
    order = ["XS", "S", "M", "L", "XL", "XXL"]
    alpha = [s for s in order if s in sizes]
    nums = sorted([s for s in sizes if s.isdigit()], key=int)
    sizes = alpha + nums + (["One Size"] if "One Size" in sizes else [])
    colors = []
    for p in PRODUCTS:
        if scope in ("all", p["gender"]):
            for c in p["colors"]:
                if c["name"] not in [x["name"] for x in colors]:
                    colors.append(c)
    s_html = "".join(f'<label class="opt"><input type="checkbox" name="size" value="{e(s)}"><span>{e(s)}</span></label>' for s in sizes)
    c_html = "".join(f'<label class="opt opt--color"><input type="checkbox" name="color" value="{c["name"]}"><span><i style="background:{c["hex"]}"></i>{c["name"]}</span></label>' for c in colors)
    return f'''<aside class="filters-panel" id="filters" aria-label="Product filters">
  <div class="drawer__scrim" data-close-filters></div>
  <div class="drawer__panel">
    <div class="drawer__head"><h2 class="drawer__title">Filter</h2><button class="icon-btn" type="button" data-close-filters aria-label="Close filters">{ICON['close']}</button></div>
    <form class="drawer__body filters" data-filters>
      <fieldset><legend>Price</legend>
        <div class="price-range"><div><label class="visually-hidden" for="pmin">Minimum price</label><input class="input" id="pmin" name="min" type="number" inputmode="numeric" min="0" step="10" placeholder="Min $"></div>
        <div><label class="visually-hidden" for="pmax">Maximum price</label><input class="input" id="pmax" name="max" type="number" inputmode="numeric" min="0" step="10" placeholder="Max $"></div></div>
        <div class="size-options" style="margin-top:.75rem">
          <button class="chip" type="button" data-price="0-150">Under $150</button><button class="chip" type="button" data-price="150-300">$150–$300</button>
          <button class="chip" type="button" data-price="300-600">$300–$600</button><button class="chip" type="button" data-price="600-">$600+</button></div>
      </fieldset>
      <fieldset><legend>Size</legend><div class="size-options">{s_html}</div></fieldset>
      <fieldset><legend>Colour</legend><div class="color-options">{c_html}</div></fieldset>
      <fieldset><legend>Availability</legend><label class="check"><input type="checkbox" name="instock" value="1"> In stock only</label></fieldset>
      <button class="btn btn--ghost btn--block" type="button" data-clear-filters>Clear all filters</button>
    </form>
    <div class="drawer__foot"><button class="btn btn--block" type="button" data-close-filters>Show <span data-result-count>0</span> results</button></div>
  </div>
</aside>'''


def build_listing(path, scope, title, h1, desc, hero=None, eyebrow=""):
    rel = ""
    items = [p for p in PRODUCTS if scope == "all" or p["gender"] == scope]
    cats = CATEGORIES.get(scope) or [("new", "New Arrivals")] + sorted({(p["category"], CAT_LABEL[p["category"]]) for p in PRODUCTS if p["category"] != "new"}, key=lambda x: x[1])
    tabs = f'<button class="chip is-active" type="button" data-cat="">All</button>' + "".join(f'<button class="chip" type="button" data-cat="{k}">{v}</button>' for k, v in cats)
    top = ""
    if hero:
        top = f'''<section class="hero hero--page" aria-labelledby="page-title">{picture(rel, hero[0], hero[1], hero[2], eager=True)}
<div class="container hero__content">{breadcrumb(rel, [("Home", "index.html"), (h1, None)]).replace('class="breadcrumb"', 'class="breadcrumb" style="color:rgba(245,241,233,.8)"')}<span class="eyebrow">{eyebrow}</span><h1 id="page-title" data-listing-title>{e(h1)}</h1><p>{e(desc)}</p></div></section>'''
    else:
        top = f'''<section class="page-head"><div class="container">{breadcrumb(rel, [("Home", "index.html"), (h1, None)])}<span class="eyebrow">{eyebrow}</span><h1 id="page-title" data-listing-title>{e(h1)}</h1><p class="lede" data-listing-sub>{e(desc)}</p></div></section>'''
    body = f'''{top}
<section class="section section--tight" aria-label="Products">
  <div class="container">
    <div class="cat-tabs" role="toolbar" aria-label="Categories">{tabs}</div>
    <div class="shop-layout">
      {filters_html(scope)}
      <div>
        <div class="toolbar">
          <span class="count" aria-live="polite"><span data-result-count>{len(items)}</span> pieces</span>
          <div class="toolbar-actions">
            <button class="filter-toggle hide-desktop" type="button" data-open-filters aria-controls="filters">{ICON['filter']} Filter</button>
            <label class="visually-hidden" for="sort">Sort products</label>
            <select class="input sort-select" id="sort" data-sort>
              <option value="featured">Featured</option><option value="newest">Newest</option><option value="popular">Most popular</option>
              <option value="price-asc">Price: low to high</option><option value="price-desc">Price: high to low</option></select>
          </div>
        </div>
        <div class="active-filters" data-active-filters></div>
        <div class="grid" data-grid>{"".join(card(p, rel) for p in items)}</div>
        <div class="empty-state" data-empty hidden><h2>No pieces match your selection</h2><p>Try removing a filter or searching for something else.</p><button class="btn" type="button" data-clear-filters>Clear filters</button></div>
      </div>
    </div>
  </div>
</section>'''
    ld = [crumb_ld([("Home", ""), (h1, path)]),
          {"@context": "https://schema.org", "@type": "CollectionPage", "name": h1, "url": BASE_URL + path, "description": desc}]
    page(path, title, desc, body, path if path in ("women.html", "men.html") else "", ld, ("catalog.js",), body_attrs=f'data-scope="{scope}"', priority="0.9")


def build_collections():
    rel = ""
    sections = []
    for i, (k, t, d) in enumerate(COLLECTIONS):
        items = [p for p in PRODUCTS if k in p["collections"]]
        sections.append(f'''<section class="section{' section--white' if i % 2 == 0 else ''}" id="{k}" aria-labelledby="c-{k}">
  <div class="container">
    <div class="editorial" style="margin-bottom:3rem">
      <a class="tile reveal" href="shop.html?collection={k}">{camp(rel, "collection-" + k, f"{t} — campaign illustration", "(min-width: 900px) 50vw, 100vw")}<div class="tile__label"><span class="link-arrow">Shop the collection</span></div></a>
      <div class="reveal"><span class="eyebrow">Collection {i + 1:02d} · {len(items)} pieces</span><h2 id="c-{k}" class="display">{e(t)}</h2><p class="lede">{e(d)}</p>
        <a class="btn" href="shop.html?collection={k}">Shop {e(t)}</a></div>
    </div>
    <div class="section-head"><h3 style="font-size:1.5rem;margin:0">Pieces from {e(t)}</h3>{rail_controls("rail-" + k)}</div>
    {rail(rel, items, t, "rail-" + k)}
  </div>
</section>''')
    nav = "".join(f'<a class="chip" href="#{k}">{e(t)}</a>' for k, t, _ in COLLECTIONS)
    body = f'''<section class="hero hero--page" aria-labelledby="page-title">{picture(rel, "seasonal-aw26", "hero-women-portrait", "Figure in a champagne coat in a shaft of evening light — ÉLVARÉ collections", eager=True)}
<div class="container hero__content">{breadcrumb(rel, [("Home", "index.html"), ("Collections", None)]).replace('class="breadcrumb"', 'class="breadcrumb" style="color:rgba(245,241,233,.8)"')}<span class="eyebrow">Curated by the House</span><h1 id="page-title">Collections</h1><p>Six curated edits, each composed around a mood, a moment and a way of dressing.</p></div></section>
<nav class="section--tight" aria-label="Collections"><div class="container cat-tabs" style="margin:0;padding-top:1.5rem">{nav}</div></nav>
{"".join(sections)}'''
    page("collections.html", "Collections — Signature, Evening, Tailored & Resort",
         "Explore ÉLVARÉ's curated collections: The Signature Collection, Modern Essentials, Evening Edit, The Tailored Collection, Resort and Seasonal Arrivals.",
         body, "collections.html", [crumb_ld([("Home", ""), ("Collections", "collections.html")])], priority="0.8")


def build_product(p):
    rel = "../"
    path = f"product/{p['slug']}.html"
    gender_page = "women.html" if p["gender"] == "women" else "men.html"
    gname = "Women" if p["gender"] == "women" else "Men"
    cat = CAT_LABEL[p["category"]]
    c0 = p["colors"][0]
    views = [(p["image"], alt_text(p)), (f"assets/img/products/{p['slug']}-alt", alt_text(p, view=", alternate studio view")),
             (f"assets/img/products/{p['slug']}-detail", alt_text(p, view=", fabric and construction detail"))]
    thumbs = "".join(f'<button type="button" data-thumb="{i}" aria-label="View image {i + 1}"{" aria-current=\"true\"" if i == 0 else ""}>{img(rel, v[0], "", "90px", (480,), 480, 600)}</button>' for i, v in enumerate(views))
    swatches = "".join(f'<button class="color-swatch" type="button" role="radio" aria-checked="{"true" if i == 0 else "false"}" data-color="{c["name"]}" data-key="{c["key"]}" style="background-color:{c["hex"]}" aria-label="{c["name"]}"></button>' for i, c in enumerate(p["colors"]))
    one = p["sizes"] == ["One Size"]
    sizes = "".join(f'<button class="size-btn" type="button" role="radio" aria-checked="{"true" if one else "false"}" data-size="{e(s)}">{e(s)}</button>' for s in p["sizes"])
    stock = {"in_stock": ("In stock — ready to ship", ""), "low_stock": ("Low stock — only a few remaining", "is-low"),
             "preorder": ("Pre-order — ships in 3–4 weeks", "is-pre")}[p["availability"]]
    details = "".join(f"<li>{e(d)}</li>" for d in p["details"])
    related = [x for x in PRODUCTS if x["id"] != p["id"] and (x["category"] == p["category"] or set(x["collections"]) & set(p["collections"])) and x["gender"] == p["gender"]]
    related = sorted(related, key=lambda x: (x["category"] != p["category"], -x["popularity"]))[:8]
    avail_ld = {"in_stock": "InStock", "low_stock": "LimitedAvailability", "preorder": "PreOrder"}[p["availability"]]
    ld = [{"@context": "https://schema.org", "@type": "Product", "name": p["name"], "sku": p["id"], "description": p["description"],
           "image": [BASE_URL + p["image"] + "-960.webp"], "brand": {"@type": "Brand", "name": "ÉLVARÉ"}, "category": f"{gname} > {cat}",
           "color": ", ".join(c["name"] for c in p["colors"]),
           "offers": {"@type": "Offer", "url": BASE_URL + path, "priceCurrency": "USD", "price": f"{p['price']:.2f}",
                      "availability": f"https://schema.org/{avail_ld}", "itemCondition": "https://schema.org/NewCondition"}},
          crumb_ld([("Home", ""), (gname, gender_page), (cat, f"{gender_page}?cat={p['category']}"), (p["name"], path)])]
    body = f'''<div class="container">
  <div style="padding-top:1.5rem">{breadcrumb(rel, [("Home", "index.html"), (gname, gender_page), (cat, f"{gender_page}?cat={p['category']}"), (p["name"], None)])}</div>
  <article class="pdp" data-product="{p['id']}">
    <div class="gallery">
      <div class="gallery__main" data-gallery-main>
        {img(rel, views[0][0], views[0][1], "(min-width: 900px) 50vw, 100vw", lazy=False, fetch="high")}
        <button class="gallery__nav gallery__nav--prev" type="button" data-gallery-step="-1" aria-label="Previous image">{ICON['left']}</button>
        <button class="gallery__nav gallery__nav--next" type="button" data-gallery-step="1" aria-label="Next image">{ICON['right']}</button>
      </div>
      <div class="gallery__thumbs">{thumbs}</div>
    </div>
    <div class="pdp__info">
      <span class="eyebrow">{e(gname)} · {e(cat)}</span>
      <h1>{e(p['name'])}</h1>
      <p class="pdp__price">{money(p['price'])} <span class="visually-hidden">US dollars</span></p>
      <p class="pdp__stock {stock[1]}">{stock[0]}</p>
      <p class="pdp__desc">{e(p['description'])}</p>
      <div class="option-row"><div class="option-head"><span class="label" id="color-label">Colour <span data-color-name>{e(c0['name'])}</span></span></div>
        <div class="color-swatches" role="radiogroup" aria-labelledby="color-label">{swatches}</div></div>
      <div class="option-row" data-size-row><div class="option-head"><span class="label" id="size-label">Size <span data-size-name>{"One Size" if one else "Select a size"}</span></span>
        {"" if one else '<button class="text-link" type="button" data-open-modal="size-guide" style="font-size:.8rem">Size guide</button>'}</div>
        <div class="size-grid" role="radiogroup" aria-labelledby="size-label">{sizes}</div>
        <p class="field-error" data-size-error role="alert"></p></div>
      <div class="buy-row">
        <div class="qty" role="group" aria-label="Quantity"><button type="button" data-qty="-1" aria-label="Decrease quantity">−</button><input type="number" value="1" min="1" max="10" aria-label="Quantity" data-qty-input><button type="button" data-qty="1" aria-label="Increase quantity">+</button></div>
        <button class="btn" type="button" data-add-to-cart>{"Pre-order — Add to Bag" if p['availability'] == 'preorder' else "Add to Bag"}</button>
        <button class="icon-btn" type="button" data-wish="{p['id']}" aria-pressed="false" aria-label="Add to wishlist">{ICON['heart']}</button>
      </div>
      <p class="form-note" style="margin:0">Demonstration store — adding to bag is fully functional; checkout is simulated and no payment is taken.</p>
      <ul class="assurances">
        <li>{ICON['truck']} Complimentary standard shipping on orders over $500</li>
        <li>{ICON['return']} Returns within 30 days of delivery</li>
        <li>{ICON['gift']} Signature ÉLVARÉ presentation box</li>
      </ul>
      <div class="accordion">
        <details open><summary>Details &amp; composition</summary><div class="acc-body"><ul>{details}</ul><p style="margin-top:.75rem">Product code: {p['id']}</p></div></details>
        <details><summary>Fit &amp; sizing</summary><div class="acc-body"><p>{"One size." if one else "Available in " + ", ".join(p["sizes"]) + ". Consult the size guide for body measurements."}</p></div></details>
        <details><summary>Shipping &amp; returns</summary><div class="acc-body"><p>Standard delivery in 5–7 business days, express in 2–3 business days. Returns accepted within 30 days in original condition. <a class="text-link" href="../shipping.html">Full policy</a>.</p></div></details>
      </div>
    </div>
  </article>
</div>
<section class="section" aria-labelledby="rel-title">
  <div class="container">
    <div class="section-head"><div><span class="eyebrow">Complete the look</span><h2 id="rel-title">You may also like</h2></div>{rail_controls("rail-related")}</div>
    {rail(rel, related, "Related products", "rail-related")}
  </div>
</section>
<section class="section section--white" aria-labelledby="rv-title" data-recent-section hidden>
  <div class="container">
    <div class="section-head"><div><span class="eyebrow">Your browsing</span><h2 id="rv-title">Recently viewed</h2></div></div>
    <div class="grid grid--4" data-recent></div>
  </div>
</section>'''
    desc = f"{p['name']} — {p['description'][:120].rsplit(' ', 1)[0]}… {money(p['price'])}. ÉLVARÉ {gname.lower()}'s {cat.lower()}."
    page(path, f"{p['name']} — {gname}'s {cat}", desc, body, "", ld, ("product.js",), rel=rel, priority="0.8")


def build_simple_pages():
    rel = ""
    # ---------------- Our Story
    body = f'''<section class="hero hero--page" aria-labelledby="page-title">{picture(rel, "hero-men", "hero-men-portrait", "Two figures in tailored coats beside arched doorways in soft light", eager=True)}
<div class="container hero__content">{breadcrumb(rel, [("Home", "index.html"), ("Our Story", None)]).replace('class="breadcrumb"', 'class="breadcrumb" style="color:rgba(245,241,233,.8)"')}<span class="eyebrow">The House</span><h1 id="page-title">Our Story</h1><p>A fashion house founded on proportion, restraint and the belief that true luxury is felt before it is seen.</p></div></section>
<section class="section"><div class="container editorial">
  <div class="reveal"><span class="eyebrow">Philosophy</span><h2 class="display">Less, considered more deeply.</h2>
    <p class="lede">ÉLVARÉ began with a simple conviction: a wardrobe should be built, not accumulated. Every collection is an exercise in editing — refining the silhouettes that matter until each one feels inevitable.</p>
    <p>The name joins two ideas the house returns to in every season: <em>élan</em>, the ease of movement, and <em>rare</em>, the quiet distinction of things made with intent. Our clothes are designed to move with the body, to be worn for years and to grow more personal with time.</p></div>
  <div class="reveal">{camp(rel, "atelier", "A figure in an ivory coat stands in an arched niche lit by afternoon sun", "(min-width: 900px) 45vw, 100vw")}</div>
</div></section>
<section class="section section--white"><div class="container">
  <div class="center" style="margin-bottom:3rem"><span class="eyebrow">How we design</span><h2 class="display">Three principles</h2></div>
  <div class="values">
    <div class="value reveal"><span class="num">I.</span><h3>Proportion before ornament</h3><p>We start with the line — where a shoulder sits, how a hem falls, the space between garment and body. Decoration is added only when it earns its place.</p></div>
    <div class="value reveal"><span class="num">II.</span><h3>Materials that move</h3><p>Silk satin, double-faced wool, fine merino and supple leather are chosen for how they drape, age and catch the light — never for novelty alone.</p></div>
    <div class="value reveal"><span class="num">III.</span><h3>Made to be kept</h3><p>Our collections build on one another season after season, so each new piece works with what you already own.</p></div>
  </div>
</div></section>
<section class="section"><div class="container editorial">
  <div class="editorial__images reveal">{camp(rel, "editorial-noir", "Close study of black satin with a soft sheen", "(min-width: 900px) 27vw, 50vw")}{camp(rel, "collection-tailored", "Figure in a charcoal coat and matching trousers in an arched room", "(min-width: 900px) 27vw, 50vw")}</div>
  <div class="reveal"><span class="eyebrow">Craft &amp; inspiration</span><h2 class="display">Inspired by the atelier.</h2>
    <p>The house draws on the traditions of the tailoring atelier: precise pattern-cutting, careful finishing and garments considered from the inside out. Our design language is shaped by architecture — arched windows, plaster walls, and the way light travels across a room through the day.</p>
    <p>That is why the ÉLVARÉ monogram sits within an arch: a reminder that every piece should frame the person wearing it, rather than the other way around.</p>
    <p class="quote">“Modern luxury is quiet. It is in the cut, the cloth and the confidence of the person wearing it.”</p></div>
</div></section>
<section class="section section--dark"><div class="container narrow center">
  <span class="eyebrow">A note on this website</span><h2>A demonstration fashion house</h2>
  <p class="lede" style="margin-inline:auto">ÉLVARÉ is a fictional brand created by Virellion Apex as Portfolio Project 02. Its story, products and policies are illustrative. We make no claims about real manufacturing locations, certifications or sustainability credentials.</p>
  <div class="hero__ctas" style="justify-content:center"><a class="btn btn--light" href="collections.html">Explore the collections</a><a class="btn btn--outline-light" href="{VA}" rel="noopener">Explore Virellion Apex</a></div>
</div></section>'''
    page("about.html", "Our Story — The House of ÉLVARÉ", "Discover the philosophy, design direction and atelier-inspired craft behind ÉLVARÉ, a contemporary luxury fashion house for women and men.",
         body, "about.html", [crumb_ld([("Home", ""), ("Our Story", "about.html")])])

    # ---------------- Contact
    faqs = [
        ("Is this a real store?", "No. ÉLVARÉ is a fictional demonstration website created by Virellion Apex. You can browse, add to bag and complete a simulated checkout, but no orders are fulfilled and no payment is ever taken."),
        ("How long does delivery take?", "In this demonstration, standard delivery is shown as 5–7 business days, express as 2–3 business days and next-day delivery for orders placed before 1pm."),
        ("What is the returns policy?", "The demonstration policy allows returns within 30 days of delivery for unworn items with original tags. See Shipping & Returns for full details."),
        ("How do I choose my size?", "Open the size guide on any product page for body measurements in centimetres. Between sizes, we suggest sizing up for tailoring and down for knitwear."),
        ("Can I change or cancel an order?", "In a live store, orders could be amended within one hour of purchase. In this demonstration, orders exist only in your browser and can be cleared at any time."),
        ("How is my information used?", "Form entries, your bag and wishlist are stored only in your own browser using localStorage. Nothing is transmitted to a server. See our Privacy Policy."),
    ]
    faq_html = "".join(f'<details><summary>{e(q)}</summary><div class="acc-body"><p>{e(a)}</p></div></details>' for q, a in faqs)
    faq_ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]}
    body = f'''<section class="page-head"><div class="container">{breadcrumb(rel, [("Home", "index.html"), ("Contact", None)])}<span class="eyebrow">Client Services</span><h1>Contact Us</h1><p class="lede">Our client advisors are here to help with orders, sizing, shipping and returns.</p></div></section>
<section class="section section--tight"><div class="container contact-grid">
  <div class="info-list">
    <div><h3>Client services</h3><p>Monday – Saturday, 9am – 7pm (ET)<br>Sunday, 11am – 5pm (ET)</p></div>
    <div><h3>Email</h3><p>client.services@elvare-demo.example<br><span class="form-note">Placeholder address for demonstration</span></p></div>
    <div><h3>Telephone</h3><p>+1 (555) 010-0199<br><span class="form-note">Fictional number for demonstration</span></p></div>
    <div><h3>Order support</h3><p>Have your demonstration order number (format ELV-XXXXXX-XXXX) ready. You can find it on your confirmation receipt.</p></div>
    <div><h3>Shipping &amp; returns inquiries</h3><p>Read our <a class="text-link" href="shipping.html">Shipping &amp; Returns</a> policy, or select the relevant topic in the form.</p></div>
  </div>
  <div class="summary-box">
    <h2>Send a message</h2>
    <div class="demo-banner"><span>ⓘ</span><span><strong>Demonstration form.</strong> Your message is validated but not sent — there is no server behind this website.</span></div>
    <form data-contact-form novalidate>
      <div class="form-grid">
        <div class="field"><label for="c-first">First name</label><input class="input" id="c-first" name="first" autocomplete="given-name" required><span class="field-error"></span></div>
        <div class="field"><label for="c-last">Last name</label><input class="input" id="c-last" name="last" autocomplete="family-name" required><span class="field-error"></span></div>
        <div class="field span-2"><label for="c-email">Email</label><input class="input" id="c-email" name="email" type="email" autocomplete="email" required><span class="field-error"></span></div>
        <div class="field"><label for="c-topic">Topic</label><select class="input" id="c-topic" name="topic" required><option value="">Select a topic</option><option>Order support</option><option>Shipping inquiry</option><option>Returns &amp; exchanges</option><option>Sizing &amp; fit</option><option>Product question</option><option>Other</option></select><span class="field-error"></span></div>
        <div class="field"><label for="c-order">Order number (optional)</label><input class="input" id="c-order" name="order" placeholder="ELV-…" pattern="^$|^ELV-[A-Z0-9-]{{4,}}$"><span class="field-error"></span></div>
        <div class="field span-2"><label for="c-msg">Message</label><textarea class="input" id="c-msg" name="message" required minlength="20"></textarea><span class="field-error"></span></div>
      </div>
      <label class="check" style="margin-bottom:1.25rem"><input type="checkbox" name="consent" required> I understand this is a demonstration form and my message will not be delivered.</label>
      <p class="field-error" data-consent-error></p>
      <button class="btn btn--block" type="submit">Send message</button>
      <p class="form-msg" role="status" data-contact-msg></p>
    </form>
  </div>
</div></section>
<section class="section section--white" id="faq" aria-labelledby="faq-title"><div class="container narrow">
  <span class="eyebrow">Help</span><h2 id="faq-title" class="display">Frequently asked questions</h2>
  <div class="accordion faq">{faq_html}</div>
</div></section>'''
    page("contact.html", "Contact & Client Services", "Contact ÉLVARÉ client services for order support, shipping and returns inquiries, sizing advice and frequently asked questions.",
         body, "", [crumb_ld([("Home", ""), ("Contact", "contact.html")]), faq_ld], ("forms.js",))

    # ---------------- Shipping
    body = f'''<section class="page-head"><div class="container">{breadcrumb(rel, [("Home", "index.html"), ("Shipping & Returns", None)])}<span class="eyebrow">Client Services</span><h1>Shipping &amp; Returns</h1><p class="lede">Clear, simple policies — presented for demonstration purposes.</p></div></section>
<section class="section section--tight"><div class="container prose">
  <div class="notice"><strong>Demonstration policy.</strong> ÉLVARÉ is a fictional store. These policies illustrate how a luxury retailer might present shipping and returns; no goods are shipped and no payments are taken.</div>
  <h2>Delivery options</h2>
  <table><thead><tr><th>Service</th><th>Timeframe</th><th>Cost</th></tr></thead><tbody>
    <tr><td>Standard</td><td>5–7 business days</td><td>$25, complimentary on orders over $500</td></tr>
    <tr><td>Express</td><td>2–3 business days</td><td>$35</td></tr>
    <tr><td>Next day</td><td>Next business day when ordered before 1pm ET</td><td>$60</td></tr></tbody></table>
  <p>Shipping costs and estimated sales tax (shown at a flat demonstration rate of 8.25%) are calculated in your bag and at checkout before you confirm a simulated order.</p>
  <h2>Presentation</h2><p>Every order is described as arriving in the signature ÉLVARÉ presentation box with tissue and a handwritten card on request.</p>
  <h2>Returns</h2>
  <ul><li>Returns accepted within 30 days of delivery.</li><li>Items must be unworn, unwashed and returned with original tags and packaging.</li><li>Footwear must be tried on carpeted surfaces only.</li><li>Pre-order pieces follow the same 30-day window from their delivery date.</li><li>Refunds are issued to the original payment method within 10 business days of the return being received.</li></ul>
  <h2>Exchanges</h2><p>Size exchanges are offered on full-price items subject to availability. Contact client services with your order number to arrange an exchange.</p>
  <h2 id="size-guide">Size guide</h2>
  {size_guide_html("sg-page-title", "h3")}
  <h2>Questions</h2><p>Visit our <a class="text-link" href="contact.html">Contact page</a> for client services and frequently asked questions.</p>
</div></section>'''
    page("shipping.html", "Shipping & Returns", "ÉLVARÉ demonstration shipping options, delivery times, returns and exchanges policy, and size guide.", body, "",
         [crumb_ld([("Home", ""), ("Shipping & Returns", "shipping.html")])])

    # ---------------- Privacy
    body = f'''<section class="page-head"><div class="container">{breadcrumb(rel, [("Home", "index.html"), ("Privacy Policy", None)])}<span class="eyebrow">Legal</span><h1>Privacy Policy</h1><p class="lede">Last updated {BUILD_DATE}. A demonstration privacy policy describing exactly how this website behaves.</p></div></section>
<section class="section section--tight"><div class="container prose">
  <div class="notice"><strong>Summary:</strong> this demonstration website has no server, no accounts, no analytics and no payment processing. Everything you enter stays in your own browser.</div>
  <h2>1. Who we are</h2><p>ÉLVARÉ is a fictional fashion brand. This website was designed and developed by Virellion Apex as a portfolio demonstration and is hosted as a static website.</p>
  <h2>2. Information stored in your browser</h2>
  <p>To make the shopping experience functional, the site stores the following in your browser's <code>localStorage</code>:</p>
  <ul><li>Your shopping bag (product, colour, size and quantity).</li><li>Your wishlist.</li><li>Recently viewed products.</li><li>Newsletter sign-up email address (demonstration only).</li><li>Details of your most recent simulated order, so the confirmation and receipt can be displayed.</li></ul>
  <p>This information never leaves your device. You can remove it at any time by clearing your browser's site data, or by using the "Clear demo data" button below.</p>
  <p><button class="btn btn--ghost" type="button" data-clear-demo>Clear demo data</button> <span class="form-msg" data-clear-msg role="status"></span></p>
  <h2>3. Forms</h2><p>The contact, newsletter and checkout forms validate your entries in the browser but do not transmit them. Checkout never asks for real card numbers; payment selection is simulated.</p>
  <h2>4. Cookies, analytics and tracking</h2><p>This website sets no cookies and uses no analytics, advertising or third-party tracking scripts.</p>
  <h2>5. Hosting</h2><p>The site is served by a static hosting provider (such as GitHub Pages), which may record standard technical request logs (for example IP address and user agent) for security and operations under its own privacy policy.</p>
  <h2>6. Links</h2><p>Links to virellionapex.com lead to a separate website with its own privacy practices.</p>
  <h2>7. Contact</h2><p>For questions about this demonstration, please visit <a class="text-link" href="{VA}" rel="noopener">Virellion Apex</a>.</p>
</div></section>'''
    page("privacy.html", "Privacy Policy", "Privacy policy for the ÉLVARÉ demonstration store: no server, no tracking — cart, wishlist and forms are stored only in your browser.", body, "",
         [crumb_ld([("Home", ""), ("Privacy Policy", "privacy.html")])], ("forms.js",), priority="0.3")

    # ---------------- Terms
    body = f'''<section class="page-head"><div class="container">{breadcrumb(rel, [("Home", "index.html"), ("Terms & Conditions", None)])}<span class="eyebrow">Legal</span><h1>Terms &amp; Conditions</h1><p class="lede">Last updated {BUILD_DATE}. Terms for the ÉLVARÉ demonstration store.</p></div></section>
<section class="section section--tight"><div class="container prose">
  <div class="notice"><strong>Important:</strong> ÉLVARÉ is a fictional brand and this is a demonstration website. No products are for sale and no contract of sale is formed by using it.</div>
  <h2>1. Purpose of this website</h2><p>This website was created by Virellion Apex to demonstrate luxury e-commerce design and development. All brand names, product names, descriptions, images, prices and policies are fictional or illustrative.</p>
  <h2>2. Simulated orders</h2><ul><li>Orders placed through checkout are simulations. No goods will be delivered.</li><li>No payment is requested, collected or processed. Never enter real card details anywhere on this website — none are requested.</li><li>Order numbers and receipts are generated in your browser for demonstration only and have no commercial value.</li></ul>
  <h2>3. Pricing and availability</h2><p>Prices are shown in US dollars and are illustrative. Availability labels (in stock, low stock, pre-order) are part of the demonstration and do not reflect real inventory.</p>
  <h2>4. Intellectual property</h2><p>The ÉLVARÉ name, logo, monogram, imagery and website design were created for this demonstration. They may not be reproduced for commercial purposes without permission from Virellion Apex. No third-party brand names or logos are used.</p>
  <h2>5. Acceptable use</h2><p>Please do not attempt to disrupt the website or use it to misrepresent the existence of a real store.</p>
  <h2>6. Liability</h2><p>The website is provided "as is" for demonstration. To the extent permitted by law, no liability is accepted for reliance on its fictional content.</p>
  <h2>7. Contact</h2><p>Questions about this demonstration can be directed to <a class="text-link" href="{VA}" rel="noopener">Virellion Apex</a>.</p>
</div></section>'''
    page("terms.html", "Terms & Conditions", "Terms and conditions for the ÉLVARÉ demonstration store, including simulated orders, pricing and intellectual property.", body, "",
         [crumb_ld([("Home", ""), ("Terms & Conditions", "terms.html")])], priority="0.3")

    # ---------------- Cart
    body = f'''<section class="page-head"><div class="container">{breadcrumb(rel, [("Home", "index.html"), ("Shopping Bag", None)])}<h1>Shopping Bag</h1></div></section>
<section class="section section--tight" style="padding-top:0"><div class="container cart-page">
  <div><div data-cart-page-lines></div></div>
  <aside class="summary-box" aria-labelledby="sum-title"><h2 id="sum-title">Order summary</h2><div data-cart-page-summary></div></aside>
</div></section>
<section class="section section--white" aria-labelledby="rec-title"><div class="container">
  <div class="section-head"><div><span class="eyebrow">Recommended</span><h2 id="rec-title">Complete your wardrobe</h2></div></div>
  <div class="grid grid--4">{"".join(card(p, rel) for p in sorted(PRODUCTS, key=lambda x: -x["popularity"])[:4])}</div>
</div></section>'''
    page("cart.html", "Shopping Bag", "Review your ÉLVARÉ shopping bag, update quantities and proceed to the demonstration checkout.", body, "", (), ("cart.js",), noindex=True)

    # ---------------- Wishlist
    body = f'''<section class="page-head"><div class="container">{breadcrumb(rel, [("Home", "index.html"), ("Wishlist", None)])}<span class="eyebrow">Saved pieces</span><h1>Wishlist</h1><p class="lede">Your saved pieces are kept in this browser.</p></div></section>
<section class="section section--tight" style="padding-top:0"><div class="container"><div class="grid grid--4" data-wishlist-grid></div>
<div class="empty-state" data-wishlist-empty hidden><h2>Your wishlist is empty</h2><p>Tap the heart on any piece to save it here.</p><div class="hero__ctas" style="justify-content:center"><a class="btn" href="women.html">Shop Women</a><a class="btn btn--ghost" href="men.html">Shop Men</a></div></div></div></section>'''
    page("wishlist.html", "Wishlist", "Your saved ÉLVARÉ pieces.", body, "", (), ("wishlist.js",), noindex=True)

    # ---------------- Checkout
    body = f'''<section class="page-head" style="padding-bottom:1rem"><div class="container">{breadcrumb(rel, [("Home", "index.html"), ("Bag", "cart.html"), ("Checkout", None)])}<h1>Secure Checkout <span class="form-note" style="font-family:var(--sans);font-size:.8rem;letter-spacing:.1em;text-transform:uppercase;vertical-align:middle">· Demonstration</span></h1></div></section>
<section class="section section--tight" style="padding-top:0"><div class="container">
  <ol class="steps" data-steps><li class="is-active">Information</li><li>Delivery</li><li>Payment</li><li>Confirmation</li></ol>
  <div class="demo-banner no-print"><span>ⓘ</span><span><strong>Simulated checkout.</strong> This is a portfolio demonstration. No order is placed, nothing is shipped and no payment details are requested or processed.</span></div>
  <div data-checkout-root></div>
</div></section>'''
    page("checkout.html", "Checkout (Demonstration)", "ÉLVARÉ demonstration checkout: customer information, delivery options, simulated payment and printable receipt.", body, "", (), ("checkout.js",), noindex=True)

    # ---------------- 404 (served by GitHub Pages at any depth → uses base href)
    body = f'''<section class="notfound"><div class="container narrow">
  <p class="big" aria-hidden="true">404</p>
  <span class="eyebrow">Page not found</span>
  <h1 class="display">This piece has left the collection.</h1>
  <p class="lede" style="margin-inline:auto">The page you are looking for may have moved or no longer exists. Let us guide you back.</p>
  <div class="hero__ctas" style="justify-content:center"><a class="btn" href="index.html">Return home</a><a class="btn btn--ghost" href="women.html">Shop Women</a><a class="btn btn--ghost" href="men.html">Shop Men</a></div>
  <form action="shop.html" method="get" role="search" style="max-width:460px;margin:2.5rem auto 0"><label class="visually-hidden" for="nf-q">Search</label><div class="search-field"><input id="nf-q" name="q" type="search" placeholder="Search the house" style="font-size:1.4rem"><button class="icon-btn" type="submit" aria-label="Search">{ICON['search']}</button></div></form>
</div></section>'''
    page("404.html", "Page Not Found", "The page you requested could not be found.", body, "", (), noindex=True, base=BASE_PATH)


def write_data():
    keep = ["id", "slug", "name", "gender", "category", "price", "colors", "sizes", "collections", "tags", "availability",
            "popularity", "added", "isNew", "bestseller", "description", "image"]
    data = [{k: p[k] for k in keep} for p in PRODUCTS]
    js = ("/* ÉLVARÉ product catalog — generated by tools/build_site.py from tools/catalog.py. Fictional demonstration data. */\n"
          f"window.ELVARE = {{ products: {json.dumps(data, ensure_ascii=False, separators=(',', ':'))},\n"
          f"categories: {json.dumps(CAT_LABEL, ensure_ascii=False)},\n"
          f"collections: {json.dumps({k: t for k, t, _ in COLLECTIONS}, ensure_ascii=False)} }};\n")
    (ROOT / "assets/js/products.js").write_text(js)


def write_seo():
    urls = "".join(f"  <url><loc>{BASE_URL}{'' if pth == 'index.html' else pth}</loc><lastmod>{BUILD_DATE}</lastmod><priority>{pr}</priority></url>\n" for pth, pr in SITEMAP)
    (ROOT / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>\n')
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nDisallow: /tools/\n\nSitemap: {BASE_URL}sitemap.xml\n")
    manifest = {"name": "ÉLVARÉ — The Art of Modern Luxury", "short_name": "ÉLVARÉ", "start_url": "./index.html", "scope": "./",
                "display": "standalone", "background_color": "#F5F1E9", "theme_color": "#111111",
                "description": "ÉLVARÉ luxury fashion house — a Virellion Apex demonstration store.",
                "icons": [{"src": "assets/brand/icon-192.png", "sizes": "192x192", "type": "image/png"},
                          {"src": "assets/brand/icon-512.png", "sizes": "512x512", "type": "image/png"},
                          {"src": "assets/brand/icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}]}
    (ROOT / "site.webmanifest").write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
    (ROOT / ".nojekyll").write_text("")


if __name__ == "__main__":
    write_data()
    build_home()
    build_listing("women.html", "women", "Women's Luxury Fashion — Dresses, Coats, Tailoring & Knitwear", "Women",
                  "Silk dresses, double-faced wool coats, precise tailoring, cashmere-blend knitwear and leather accessories.",
                  ("hero-women", "hero-women-portrait", "Figures in a camel coat and black dress in warm window light"), "The Women's Collection")
    build_listing("men.html", "men", "Men's Luxury Fashion — Overcoats, Tailoring, Shirts & Knitwear", "Men",
                  "Camel overcoats, unstructured tailoring, Oxford shirts, merino knitwear and leather accessories.",
                  ("hero-men", "hero-men-portrait", "Two figures in charcoal and camel coats beside arched doorways"), "The Men's Collection")
    build_listing("shop.html", "all", "Shop All — Luxury Fashion for Women & Men", "Shop All",
                  "The complete ÉLVARÉ collection for women and men.", None, "Women & Men")
    build_collections()
    for p in PRODUCTS:
        build_product(p)
    build_simple_pages()
    write_seo()
    print("pages:", len(SITEMAP), "indexed +", "cart, wishlist, checkout, 404")
