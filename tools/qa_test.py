"""ÉLVARÉ automated QA suite (Playwright + headless Chrome).

Serves the site under its GitHub Pages project path and exercises pages, links, images,
filters, search, sorting, product options, bag, persistence, totals, checkout, wishlist,
forms, mobile navigation, overflow and the custom 404. Writes results to tools/qa_results.json.

Usage:  python3 tools/qa_test.py http://localhost:8766/elvare-luxury-fashion/
"""
import json, re, sys, time
from pathlib import Path
from urllib.parse import urljoin, urlparse
from playwright.sync_api import sync_playwright

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8766/elvare-luxury-fashion/"
ROOT = Path(__file__).resolve().parent.parent
RESULTS = []
VIEWPORTS = {"mobile": (375, 812), "tablet": (768, 1024), "desktop": (1440, 900)}


def record(area, name, ok, detail=""):
    RESULTS.append({"area": area, "test": name, "pass": bool(ok), "detail": str(detail)[:300]})
    print(("PASS " if ok else "FAIL ") + f"[{area}] {name}" + (f" — {detail}" if detail and not ok else ""))


def all_pages():
    pages = sorted(p.name for p in ROOT.glob("*.html"))
    pages += sorted("product/" + p.name for p in (ROOT / "product").glob("*.html"))
    return pages


def new_page(browser, vp="desktop"):
    w, h = VIEWPORTS[vp]
    ctx = browser.new_context(viewport={"width": w, "height": h}, is_mobile=vp == "mobile", has_touch=vp != "desktop")
    pg = ctx.new_page()
    pg._errors = []
    pg._bad = []
    pg.on("pageerror", lambda e: pg._errors.append(str(e)))
    pg.on("console", lambda m: pg._errors.append(m.text) if m.type == "error" else None)
    pg.on("response", lambda r: pg._bad.append(f"{r.status} {r.url}") if r.status >= 400 else None)
    pg.on("requestfailed", lambda r: pg._bad.append(f"FAILED {r.url}") if not r.url.startswith(("https://virellionapex.com",)) else None)
    return ctx, pg


def scroll_all(pg):
    h = pg.evaluate("document.documentElement.scrollHeight")
    vh = pg.viewport_size["height"]
    for _ in range(0, h, vh // 2):
        pg.mouse.wheel(0, vh // 2)
        pg.wait_for_timeout(50)
    pg.wait_for_timeout(700)


def cart_count(pg):
    return int(pg.locator("[data-cart-count]").first.inner_text())


def test_pages_and_links(browser):
    pages = all_pages()
    record("Pages", f"{len(pages)} HTML files found", len(pages) >= 44, pages)
    for vp in VIEWPORTS:
        ctx, pg = new_page(browser, vp)
        overflow, errors, bad, broken_imgs = [], [], [], []
        for path in pages:
            pg._errors.clear(); pg._bad.clear()
            r = pg.goto(BASE + path, wait_until="networkidle")
            if r.status != 200:
                bad.append(f"{path}: HTTP {r.status}")
            if vp == "desktop":
                scroll_all(pg)
                imgs = pg.evaluate("""Array.from(document.images).filter(i => { const r = i.getBoundingClientRect(); const rail = i.closest('.rail');
                     return r.width > 0 && (!rail || (r.left < innerWidth && r.right > 0)); }).filter(i => !(i.complete && i.naturalWidth > 0)).map(i => i.currentSrc || i.src)""")
                broken_imgs += [f"{path}: {s}" for s in imgs]
            ov = pg.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
            if ov > 1:
                culprits = pg.evaluate("""Array.from(document.querySelectorAll('body *')).filter(e => e.getBoundingClientRect().right > document.documentElement.clientWidth + 1 && !e.closest('.rail, .drawer, .search-overlay, .table-wrap, .cat-tabs')).slice(0,3).map(e => e.tagName + '.' + e.className)""")
                overflow.append(f"{path}: +{ov}px {culprits}")
            errors += [f"{path}: {e}" for e in pg._errors]
            bad += [f"{path}: {b}" for b in pg._bad]
        record("Pages", f"All pages return 200 with no failed requests ({vp})", not bad, bad[:5])
        record("JavaScript", f"No console/page errors on any page ({vp})", not errors, errors[:5])
        record("Responsive", f"No horizontal overflow on any page ({vp} {VIEWPORTS[vp][0]}px)", not overflow, overflow[:5])
        if vp == "desktop":
            record("Images", "All rendered images load after scrolling (desktop)", not broken_imgs, broken_imgs[:5])
        ctx.close()

    # every internal link on every page resolves to an existing file
    ctx, pg = new_page(browser)
    missing, checked = set(), set()
    for path in pages:
        pg.goto(BASE + path, wait_until="domcontentloaded")
        hrefs = pg.evaluate("Array.from(document.querySelectorAll('a[href]')).map(a => a.href)")
        for h in hrefs:
            u = urlparse(h)
            if not h.startswith(BASE):
                continue
            f = u.path[len(urlparse(BASE).path):] or "index.html"
            if f in checked:
                continue
            checked.add(f)
            if not (ROOT / f).exists():
                missing.add(f"{path} → {f}")
    record("Links", f"All {len(checked)} unique internal link targets resolve", not missing, sorted(missing)[:5])
    ext = set()
    for path in ["index.html", "about.html"]:
        pg.goto(BASE + path)
        ext |= set(pg.evaluate("Array.from(document.querySelectorAll('a[href^=\"http\"]')).map(a => a.href)"))
    record("Links", "External CTAs point only to virellionapex.com or the Calendly consultation link", all(e.startswith(("https://virellionapex.com","https://calendly.com/virellionapex/")) for e in ext), ext)
    ctx.close()


def test_listing(browser):
    ctx, pg = new_page(browser)
    pg.goto(BASE + "women.html", wait_until="networkidle")
    n = lambda: pg.locator("[data-grid] .card").count()
    record("Browse", "Women page lists 16 products", n() == 16, n())
    pg.click(".cat-tabs [data-cat='dresses']")
    names = pg.locator("[data-grid] .card__cat").all_inner_texts()
    record("Category nav", "Dresses tab shows only dresses (3)", n() == 3 and all(x.lower() == "dresses" for x in names), names)
    record("Category nav", "URL reflects category (?cat=dresses)", "cat=dresses" in pg.url, pg.url)
    pg.click(".cat-tabs [data-cat='']")
    pg.select_option("[data-sort]", "price-asc")
    prices = [int(re.sub(r"\D", "", x)) for x in pg.locator("[data-grid] .card__price").all_inner_texts()]
    record("Sorting", "Price low→high is ascending", prices == sorted(prices) and len(prices) == 16, prices)
    pg.select_option("[data-sort]", "price-desc")
    prices = [int(re.sub(r"\D", "", x)) for x in pg.locator("[data-grid] .card__price").all_inner_texts()]
    record("Sorting", "Price high→low is descending", prices == sorted(prices, reverse=True), prices)
    data = pg.evaluate("window.ELVARE.products.filter(p => p.gender === 'women')")
    pg.select_option("[data-sort]", "newest")
    ids = pg.evaluate("Array.from(document.querySelectorAll('[data-grid] .card')).map(c => c.dataset.id)")
    exp = [p["id"] for p in sorted(data, key=lambda p: p["added"], reverse=True)]
    record("Sorting", "Newest sorts by date added", ids == exp, ids[:4])
    pg.select_option("[data-sort]", "popular")
    ids = pg.evaluate("Array.from(document.querySelectorAll('[data-grid] .card')).map(c => c.dataset.id)")
    exp = [p["id"] for p in sorted(data, key=lambda p: -p["popularity"])]
    record("Sorting", "Popularity sorts by popularity score", ids == exp, ids[:4])
    # price filter
    pg.fill("#pmin", "200"); pg.fill("#pmax", "300"); pg.wait_for_timeout(600)
    prices = [int(re.sub(r"\D", "", x)) for x in pg.locator("[data-grid] .card__price").all_inner_texts()]
    exp = [p for p in data if 200 <= p["price"] <= 300]
    record("Filtering", "Price $200–$300 filter", prices and all(200 <= x <= 300 for x in prices) and len(prices) == len(exp), prices)
    pg.click("[data-active-filters] [data-remove='price']")
    # size filter
    pg.click("label.opt:has(input[name='size'][value='38'])")
    ids = pg.evaluate("Array.from(document.querySelectorAll('[data-grid] .card')).map(c => c.dataset.id)")
    exp = [p["id"] for p in data if "38" in p["sizes"]]
    record("Filtering", "Size 38 filter (footwear only)", sorted(ids) == sorted(exp) and len(ids) == 1, ids)
    pg.click("label.opt:has(input[name='size'][value='38'])")
    # colour filter
    pg.click("label.opt--color:has(input[value='Champagne'])")
    ids = pg.evaluate("Array.from(document.querySelectorAll('[data-grid] .card')).map(c => c.dataset.id)")
    exp = [p["id"] for p in data if any(c["name"] == "Champagne" for c in p["colors"])]
    record("Filtering", "Colour 'Champagne' filter", sorted(ids) == sorted(exp) and len(ids) > 0, ids)
    # combination → empty state → clear
    pg.fill("#pmax", "100"); pg.wait_for_timeout(600)
    record("Filtering", "Impossible combination shows empty state", pg.locator("[data-empty]").is_visible(), "")
    pg.locator("[data-empty] [data-clear-filters]").click()
    record("Filtering", "Clear filters restores all 16", n() == 16, n())
    # URL state restore
    pg.goto(BASE + "men.html?cat=outerwear&sort=price-desc", wait_until="networkidle")
    names = pg.locator("[data-grid] .card__name").all_inner_texts()
    record("Category nav", "Men ?cat=outerwear deep link restores filter (2 coats)", len(names) == 2 and "Varenne" in names[0], names)
    # collection filter
    pg.goto(BASE + "shop.html?collection=evening", wait_until="networkidle")
    cnt = n(); exp = len([1 for p in pg.evaluate("window.ELVARE.products") if "evening" in p["collections"]])
    record("Collections", "shop.html?collection=evening shows the Evening Edit", cnt == exp and "Evening" in pg.inner_text("h1"), cnt)
    # search
    pg.goto(BASE + "shop.html?q=coat", wait_until="networkidle")
    names = pg.locator("[data-grid] .card__name").all_inner_texts()
    record("Search", "Search 'coat' returns the coats first", len(names) >= 2 and all("coat" in x.lower() for x in names[:2]), names)
    pg.goto(BASE + "shop.html?q=silk", wait_until="networkidle")
    record("Search", "Search 'silk' returns silk pieces", n() >= 4, pg.locator("[data-grid] .card__name").all_inner_texts())
    pg.goto(BASE + "shop.html?q=zzzz", wait_until="networkidle")
    record("Search", "Search with no match shows empty state", pg.locator("[data-empty]").is_visible(), "")
    # header search overlay suggestions
    pg.goto(BASE + "index.html", wait_until="networkidle")
    pg.click("[data-open-search]")
    pg.fill("#search-input", "cashmere")
    sug = pg.locator("#search-suggest a").count()
    record("Search", "Header search overlay shows live suggestions", sug >= 2, sug)
    pg.press("#search-input", "Enter"); pg.wait_for_load_state("networkidle")
    record("Search", "Submitting header search opens results page", "shop.html?q=cashmere" in pg.url and n() >= 2, pg.url)
    ctx.close()


def test_product_cart_checkout(browser):
    ctx, pg = new_page(browser)
    pg.goto(BASE + "product/celeste-silk-slip-dress.html", wait_until="networkidle")
    pg.click("[data-add-to-cart]")
    record("Product", "Add to bag without size shows validation error", "select a size" in pg.inner_text("[data-size-error]").lower() and cart_count(pg) == 0, "")
    src0 = pg.get_attribute("[data-gallery-main] img", "src")
    pg.click("[data-color='Obsidian']")
    src1 = pg.get_attribute("[data-gallery-main] img", "src")
    record("Colour selection", "Selecting Obsidian swaps product image and label", "obsidian" in src1 and src0 != src1 and pg.inner_text("[data-color-name]") == "Obsidian", src1)
    pg.click("[data-thumb='2']")
    record("Gallery", "Thumbnail switches main image to detail view", "detail" in pg.get_attribute("[data-gallery-main] img", "src"), "")
    pg.click("[data-gallery-step='1']")
    record("Gallery", "Next arrow cycles the gallery", "obsidian" in pg.get_attribute("[data-gallery-main] img", "src"), "")
    pg.click("[data-size='M']")
    record("Size selection", "Selecting size M updates state", pg.get_attribute("[data-size='M']", "aria-checked") == "true" and pg.inner_text("[data-size-name]") == "M", "")
    pg.click("[data-qty='1']")
    pg.click("[data-add-to-cart]")
    pg.wait_for_timeout(300)
    record("Cart", "Add 2 × dress → bag count 2", cart_count(pg) == 2, cart_count(pg))
    record("Cart drawer", "Cart drawer opens after add", pg.locator("#cart-drawer.is-open").count() == 1, "")
    line = pg.locator("#cart-drawer .cart-line__meta").first.inner_text()
    record("Cart", "Line stores chosen colour and size", "Obsidian" in line and "M" in line, line)
    pg.keyboard.press("Escape")
    record("Accessibility", "Escape closes the cart drawer", pg.locator("#cart-drawer.is-open").count() == 0, "")
    # size guide modal
    pg.click("[data-open-modal='size-guide']")
    ok = pg.locator("#size-guide.is-open").count() == 1
    pg.click("[data-sg-tab='sg-men']")
    ok2 = pg.locator("[data-sg-panel='sg-men']").is_visible()
    pg.keyboard.press("Escape")
    record("Size guide", "Size guide modal opens, tabs switch, Escape closes", ok and ok2 and pg.locator("#size-guide.is-open").count() == 0, "")
    # recently viewed
    pg.goto(BASE + "product/varenne-wool-overcoat.html", wait_until="networkidle")
    rv = pg.locator("[data-recent] .card__name").all_inner_texts()
    record("Recently viewed", "Recently viewed shows previously visited product", "Céleste Silk Slip Dress" in rv, rv)
    record("Recommendations", "Related products rail is populated", pg.locator("#rail-related .card").count() >= 4, pg.locator("#rail-related .card").count())
    pg.click("[data-size='L']"); pg.click("[data-color='Stone']"); pg.click("[data-add-to-cart]")
    pg.wait_for_timeout(200); pg.keyboard.press("Escape")
    # quick view from listing
    pg.goto(BASE + "men.html", wait_until="networkidle")
    pg.locator(".card[data-id='EM-213']").hover()
    pg.click(".card[data-id='EM-213'] [data-quick]")
    pg.click("[data-qv-add]")
    err = pg.inner_text("[data-qv-err]")
    pg.click("[data-qv-size='90']"); pg.click("[data-qv-add]"); pg.wait_for_timeout(200)
    record("Quick view", "Quick view validates size then adds to bag", "size" in err.lower() and cart_count(pg) == 4, cart_count(pg))
    pg.keyboard.press("Escape")
    # persistence across reload
    pg.reload(wait_until="networkidle")
    record("Persistence", "Bag persists after reload (localStorage)", cart_count(pg) == 4, cart_count(pg))
    stored = pg.evaluate("JSON.parse(localStorage.getItem('elvare:cart')).length")
    record("Persistence", "3 distinct lines stored in localStorage", stored == 3, stored)
    # cart page totals
    pg.goto(BASE + "cart.html", wait_until="networkidle")
    sub_exp = 385 * 2 + 890 + 120
    tax_exp = round(sub_exp * 0.0825, 2)
    txt = pg.inner_text("[data-cart-page-summary]")
    record("Totals", f"Subtotal ${sub_exp:,} correct", f"${sub_exp:,.2f}" in txt, txt.replace("\n", " | "))
    record("Totals", "Free standard shipping applied over $500", "Complimentary" in txt, "")
    record("Totals", f"Tax 8.25% = ${tax_exp:,.2f}", f"${tax_exp:,.2f}" in txt, "")
    record("Totals", "Grand total = subtotal + shipping + tax", f"${sub_exp + tax_exp:,.2f}" in txt, "")
    # update quantity & remove
    first = pg.locator("[data-cart-page-lines] .cart-line").first
    first.locator("[data-line-qty='-1']").click(); pg.wait_for_timeout(150)
    record("Cart", "Decrease quantity updates count (4→3)", cart_count(pg) == 3, cart_count(pg))
    inp = pg.locator("[data-cart-page-lines] [data-line-input]").nth(1)
    inp.fill("3"); inp.dispatch_event("change"); pg.wait_for_timeout(150)
    record("Cart", "Typing quantity 3 updates line (count 5)", cart_count(pg) == 5, cart_count(pg))
    pg.locator("[data-cart-page-lines] .cart-line").last.locator("[data-line-remove]").click(); pg.wait_for_timeout(150)
    record("Cart", "Remove line works (count 4)", cart_count(pg) == 4 and pg.locator("[data-cart-page-lines] .cart-line").count() == 2, cart_count(pg))
    t = pg.evaluate("Elvare.cart.totals('standard')")
    exp_sub = 385 + 890 * 3
    record("Totals", "Totals recalculate after edits", abs(t["subtotal"] - exp_sub) < .001 and abs(t["total"] - (exp_sub + round(exp_sub * .0825, 2))) < .001, t)
    # below free shipping threshold
    t2 = pg.evaluate("(() => { const s = localStorage.getItem('elvare:cart'); localStorage.setItem('elvare:cart', JSON.stringify([{key:'EM-203|White|M',id:'EM-203',color:'White',size:'M',qty:1}])); const r = Elvare.cart.totals('standard'); const e = Elvare.cart.totals('express'); localStorage.setItem('elvare:cart', s); return [r, e]; })()")
    record("Totals", "Under $500: standard $25, express $35, tax on $65", t2[0]["shipping"] == 25 and t2[1]["shipping"] == 35 and abs(t2[0]["tax"] - 5.36) < .001 and abs(t2[0]["total"] - 95.36) < .001, t2)
    # checkout
    pg.goto(BASE + "checkout.html", wait_until="networkidle")
    pg.click("[data-step-form] button[type=submit]")
    errs = pg.locator("[data-step-form] .field.has-error").count()
    record("Checkout", "Empty information step shows field errors", errs >= 6, errs)
    pg.fill("#f-email", "not-an-email"); pg.fill("#f-zip", "12")
    pg.click("[data-step-form] button[type=submit]")
    record("Form validation", "Invalid email and ZIP are rejected", "valid email" in pg.inner_text("#e-email") and "ZIP" in pg.inner_text("#e-zip"), "")
    for k, v in {"email": "client@example.com", "first": "Amelia", "last": "Laurent", "address1": "12 Arch Street", "city": "Chicago", "zip": "60601", "phone": "+1 555 010 0100"}.items():
        pg.fill(f"#f-{k}", v)
    pg.select_option("#f-state", "IL")
    pg.click("[data-step-form] button[type=submit]")
    record("Checkout", "Valid information advances to Delivery", pg.locator("input[name=ship]").count() == 3, "")
    pg.check("input[name=ship][value=express]")
    sm = pg.inner_text(".summary-box")
    record("Checkout", "Delivery option updates summary (Express $35)", "Express" in sm and "$35.00" in sm, "")
    pg.fill("#f-gift", "With love.")
    pg.click("[data-step-form] button[type=submit]")
    record("Checkout", "Payment step offers 3 simulated methods, no card inputs", pg.locator("input[name=pay]").count() == 3 and pg.locator("input[autocomplete*='cc-'], input[name*='card']").count() == 0, "")
    pg.check("input[name=pay][value=wallet]")
    pg.click("[data-place]")
    record("Checkout", "Order cannot be placed without accepting demo terms", "simulated" in pg.inner_text("[data-agree-error]"), "")
    pg.check("input[name=agree]")
    total_exp = pg.evaluate("Elvare.cart.totals('express').total")
    pg.click("[data-place]")
    pg.wait_for_selector(".receipt", timeout=5000)
    rtxt = pg.inner_text(".receipt")
    num = re.search(r"ELV-\d{6}-[A-Z0-9]{4}", rtxt)
    record("Checkout", "Confirmation shows demo order number ELV-YYMMDD-XXXX", bool(num), num.group(0) if num else rtxt[:120])
    record("Checkout", "Receipt total matches bag total with express", f"${total_exp:,.2f}" in rtxt, total_exp)
    record("Checkout", "Receipt is labelled as a demonstration", "demonstration only" in rtxt.lower() and "not a real transaction" in rtxt.lower(), "")
    record("Checkout", "Bag is emptied after order", cart_count(pg) == 0, cart_count(pg))
    record("Checkout", "Printable receipt button present (window.print)", pg.locator("[data-print]").count() == 1, "")
    pg.emulate_media(media="print")
    record("Checkout", "Print stylesheet hides header/footer", not pg.locator(".site-header").is_visible() and pg.locator(".receipt").is_visible(), "")
    pg.emulate_media(media="screen")
    pg.goto(BASE + "checkout.html", wait_until="networkidle")
    pg.click("[data-view-last]")
    record("Checkout", "Last demo receipt can be reopened from empty checkout", pg.locator(".receipt").count() == 1, "")
    ctx.close()


def test_wishlist_forms(browser):
    ctx, pg = new_page(browser)
    pg.goto(BASE + "women.html", wait_until="networkidle")
    pg.click(".card[data-id='EW-106'] [data-wish]")
    pg.click(".card[data-id='EW-114'] [data-wish]")
    wc = pg.locator("[data-wish-count]").first.inner_text()
    record("Wishlist", "Heart toggles add to wishlist (count 2)", wc == "2", wc)
    pg.goto(BASE + "wishlist.html", wait_until="networkidle")
    record("Wishlist", "Wishlist page lists saved items", pg.locator("[data-wishlist-grid] .card").count() == 2, "")
    pg.click("[data-wishlist-grid] .card[data-id='EW-106'] [data-wish]")
    record("Wishlist", "Removing from wishlist page updates list", pg.locator("[data-wishlist-grid] .card").count() == 1, "")
    pg.reload(wait_until="networkidle")
    record("Wishlist", "Wishlist persists after reload", pg.locator("[data-wishlist-grid] .card").count() == 1, "")
    # newsletter
    pg.goto(BASE + "index.html", wait_until="networkidle")
    f = pg.locator("[data-newsletter]").first
    f.locator("input").fill("bad@")
    f.locator("button").click()
    m1 = pg.locator("[data-nl-msg]").first.inner_text()
    f.locator("input").fill("reader@example.com"); f.locator("button").click()
    m2 = pg.locator("[data-nl-msg]").first.inner_text()
    record("Newsletter", "Newsletter rejects invalid and confirms valid email (demo)", "valid email" in m1 and "demonstration" in m2, m2)
    # contact
    pg.goto(BASE + "contact.html", wait_until="networkidle")
    pg.click("[data-contact-form] button[type=submit]")
    e = pg.locator("[data-contact-form] .field.has-error").count()
    record("Form validation", "Contact form flags required fields", e >= 5, e)
    pg.fill("#c-first", "Noor"); pg.fill("#c-last", "Ames"); pg.fill("#c-email", "noor@example.com")
    pg.select_option("#c-topic", "Returns & exchanges"); pg.fill("#c-order", "bad"); pg.fill("#c-msg", "I would like to arrange a return for my order please.")
    pg.click("[data-contact-form] button[type=submit]")
    record("Form validation", "Contact form validates order number format", "ELV-" in pg.inner_text("[data-contact-form] .field.has-error .field-error"), "")
    pg.fill("#c-order", "ELV-261106-ABCD"); pg.check("[name=consent]")
    pg.click("[data-contact-form] button[type=submit]")
    msg = pg.inner_text("[data-contact-msg]")
    record("Form validation", "Valid contact form shows honest demo confirmation", "not been sent" in msg, msg)
    record("FAQ", "FAQ accordions expand", pg.locator("#faq details").count() >= 6, "")
    pg.locator("#faq summary").first.click()
    record("FAQ", "FAQ item opens on click", pg.locator("#faq details[open]").count() == 1, "")
    # privacy clear
    pg.goto(BASE + "privacy.html", wait_until="networkidle")
    pg.click("[data-clear-demo]")
    record("Privacy", "'Clear demo data' empties wishlist", pg.locator("[data-wish-count]").first.inner_text() == "0", "")
    ctx.close()


def test_mobile(browser):
    ctx, pg = new_page(browser, "mobile")
    pg.goto(BASE + "index.html", wait_until="networkidle")
    record("Mobile nav", "Desktop nav hidden, menu button visible at 375px", not pg.locator(".main-nav").is_visible() and pg.locator("[data-open='nav-drawer']").is_visible(), "")
    pg.click("[data-open='nav-drawer']"); pg.wait_for_timeout(500)
    record("Mobile nav", "Menu drawer opens", pg.locator("#nav-drawer.is-open").count() == 1 and pg.get_attribute("[data-open='nav-drawer']", "aria-expanded") == "true", "")
    pg.locator("#nav-drawer summary").first.click()
    pg.locator("#nav-drawer a[href*='women.html?cat=knitwear']").click(); pg.wait_for_load_state("networkidle")
    record("Mobile nav", "Submenu link navigates to Women › Knitwear", "cat=knitwear" in pg.url and pg.locator("[data-grid] .card").count() == 2, pg.url)
    pg.click("[data-open-filters]"); pg.wait_for_timeout(400)
    vis = pg.locator("#filters.is-open").count() == 1
    pg.locator("#filters .drawer__foot [data-close-filters]").click(); pg.wait_for_timeout(400)
    record("Mobile filters", "Filter drawer opens and closes on mobile", vis and pg.locator("#filters.is-open").count() == 0, "")
    cols = pg.evaluate("getComputedStyle(document.querySelector('[data-grid]')).gridTemplateColumns.split(' ').length")
    record("Responsive", "Product grid is 2 columns on mobile", cols == 2, cols)
    sizes = pg.evaluate("Array.from(document.querySelectorAll('.icon-btn, .btn, .size-btn, .chip')).filter(e => e.offsetParent).map(e => { const r = e.getBoundingClientRect(); return Math.min(r.width, r.height); })")
    small = [s for s in sizes if s < 36]
    record("Touch targets", "Interactive controls ≥ 36px on mobile (most ≥ 44px)", not small, small[:5])
    pg.goto(BASE + "product/alba-wide-leg-trouser.html", wait_until="networkidle")
    pg.click("[data-size='28']"); pg.click("[data-add-to-cart]"); pg.wait_for_timeout(500)
    record("Mobile cart", "Add to bag on mobile opens drawer", pg.locator("#cart-drawer.is-open").count() == 1 and cart_count(pg) == 1, "")
    pg.keyboard.press("Escape")
    box = pg.locator("[data-gallery-main]").bounding_box()
    pg.mouse.move(box["x"] + 5, box["y"] + 5)
    pg.locator("[data-gallery-main]").dispatch_event("touchstart", {"touches": [{"clientX": 300, "clientY": 200}]}) if False else None
    pg.mouse.wheel(0, 3000); pg.wait_for_timeout(500)
    record("Back to top", "Back-to-top appears after scrolling", pg.locator(".to-top.is-visible").count() == 1, "")
    pg.click("[data-to-top]"); pg.wait_for_timeout(900)
    record("Back to top", "Back-to-top returns to top", pg.evaluate("scrollY") < 50, pg.evaluate("scrollY"))
    ctx.close()
    ctx, pg = new_page(browser, "tablet")
    pg.goto(BASE + "women.html", wait_until="networkidle")
    cols = pg.evaluate("getComputedStyle(document.querySelector('[data-grid]')).gridTemplateColumns.split(' ').length")
    record("Responsive", "Tablet 768px grid shows 2 columns with filter drawer", cols == 2 and pg.locator("[data-open-filters]").is_visible(), cols)
    ctx.close()


def test_a11y_seo(browser):
    ctx, pg = new_page(browser)
    issues = []
    for path in all_pages():
        pg.goto(BASE + path, wait_until="domcontentloaded")
        r = pg.evaluate("""() => ({
            h1: document.querySelectorAll('h1').length,
            title: document.title, desc: (document.querySelector('meta[name=description]')||{}).content || '',
            canon: (document.querySelector('link[rel=canonical]')||{}).href || '',
            og: !!document.querySelector('meta[property="og:image"]'), tw: !!document.querySelector('meta[name="twitter:card"]'),
            noalt: Array.from(document.images).filter(i => !i.hasAttribute('alt')).length,
            lang: document.documentElement.lang,
            unlabeled: Array.from(document.querySelectorAll('input:not([type=hidden]), select, textarea')).filter(i => !i.disabled && !i.labels?.length && !i.getAttribute('aria-label')).map(i => i.name || i.id),
            emptyBtn: Array.from(document.querySelectorAll('button')).filter(b => !b.textContent.trim() && !b.getAttribute('aria-label')).length,
            ld: Array.from(document.querySelectorAll('script[type="application/ld+json"]')).map(s => { try { JSON.parse(s.textContent); return true } catch(e) { return false } })
        })""")
        if r["h1"] != 1: issues.append(f"{path}: {r['h1']} h1")
        if not r["desc"] or not r["canon"] or not r["og"] or not r["tw"]: issues.append(f"{path}: missing meta")
        if r["noalt"]: issues.append(f"{path}: {r['noalt']} img without alt")
        if r["unlabeled"]: issues.append(f"{path}: unlabeled {r['unlabeled']}")
        if r["emptyBtn"]: issues.append(f"{path}: {r['emptyBtn']} unnamed buttons")
        if not all(r["ld"]): issues.append(f"{path}: invalid JSON-LD")
        if r["lang"] != "en": issues.append(f"{path}: lang")
    record("SEO/A11y", "Every page: one h1, description, canonical, OG + Twitter tags, alt on all images, labelled inputs, named buttons, valid JSON-LD", not issues, issues[:6])
    titles = []
    for path in all_pages():
        pg.goto(BASE + path, wait_until="domcontentloaded"); titles.append(pg.title())
    record("SEO", "Page titles are unique", len(set(titles)) == len(titles), [t for t in titles if titles.count(t) > 1][:4])
    pg.goto(BASE + "product/etoile-top-handle-bag.html")
    ld = pg.evaluate("Array.from(document.querySelectorAll('script[type=\"application/ld+json\"]')).map(s => JSON.parse(s.textContent)['@type'])")
    record("SEO", "Product page has Product + BreadcrumbList JSON-LD", "Product" in ld and "BreadcrumbList" in ld, ld)
    pg.goto(BASE + "index.html")
    pg.keyboard.press("Tab")
    record("Keyboard", "First Tab focuses the skip link", pg.evaluate("document.activeElement.className") == "skip-link", pg.evaluate("document.activeElement.className"))
    pg.keyboard.press("Enter")
    record("Keyboard", "Skip link moves focus to main content", pg.evaluate("document.activeElement.id") == "main", "")
    pg.goto(BASE + "product/noor-cashmere-blend-crewneck.html", wait_until="networkidle")
    pg.focus("[data-size='XS']"); pg.keyboard.press("ArrowRight")
    record("Keyboard", "Arrow keys move through size radio group", pg.get_attribute("[data-size='S']", "aria-checked") == "true", "")
    pg.focus("[data-gallery-main]"); pg.keyboard.press("ArrowRight")
    record("Keyboard", "Arrow keys browse the image gallery", "alt" in pg.get_attribute("[data-gallery-main] img", "src"), "")
    pg.click("[data-open='cart-drawer']"); pg.wait_for_timeout(300)
    inside = []
    for _ in range(8):
        pg.keyboard.press("Tab"); inside.append(pg.evaluate("!!document.activeElement.closest('#cart-drawer')"))
    record("Keyboard", "Focus is trapped inside open cart drawer", all(inside), inside)
    for f in ["sitemap.xml", "robots.txt", "site.webmanifest", "favicon.svg", ".nojekyll", "assets/img/og/elvare-og.jpg"]:
        r = pg.request.get(BASE + f)
        record("Deployment", f"{f} served", r.status == 200, r.status)
    sm = pg.request.get(BASE + "sitemap.xml").text()
    record("SEO", "Sitemap lists home, category and all 32 product URLs", sm.count("/product/") == 32 and "women.html" in sm, sm.count("<url>"))
    # 404 served at an arbitrary depth (simulating GitHub Pages behaviour)
    body = (ROOT / "404.html").read_text()
    pg.route("**/elvare-luxury-fashion/some/deep/missing-page", lambda route: route.fulfill(status=404, body=body, content_type="text/html"))
    pg._bad.clear()
    pg.goto(BASE + "some/deep/missing-page", wait_until="networkidle")
    bad = [b for b in pg._bad if "missing-page" not in b]
    css_ok = pg.evaluate("getComputedStyle(document.body).backgroundColor") == "rgb(245, 241, 233)"
    record("404", "Custom 404 renders styled with working assets at nested path", css_ok and not bad and "left the collection" in pg.inner_text("h1"), bad[:3])
    pg.click(".notfound a[href='index.html']"); pg.wait_for_load_state("domcontentloaded")
    record("404", "404 'Return home' link resolves to site home", pg.url.rstrip("/").endswith("elvare-luxury-fashion/index.html"), pg.url)
    ctx.close()


if __name__ == "__main__":
    t0 = time.time()
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path="/usr/bin/google-chrome")
        for fn in (test_pages_and_links, test_listing, test_product_cart_checkout, test_wishlist_forms, test_mobile, test_a11y_seo):
            try:
                fn(b)
            except Exception as ex:  # a crashed group is a failure, never silently skipped
                record(fn.__name__, "test group crashed", False, repr(ex))
        b.close()
    passed = sum(r["pass"] for r in RESULTS)
    out = {"base": BASE, "run_at": time.strftime("%Y-%m-%d %H:%M:%S"), "browser": "Google Chrome (headless) via Playwright",
           "passed": passed, "total": len(RESULTS), "seconds": round(time.time() - t0, 1), "results": RESULTS}
    (Path(__file__).parent / "qa_results.json").write_text(json.dumps(out, indent=2, ensure_ascii=False))
    print(f"\n{passed}/{len(RESULTS)} passed in {out['seconds']}s")
