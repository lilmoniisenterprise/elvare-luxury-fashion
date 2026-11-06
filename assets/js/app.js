/* ÉLVARÉ — core application script.
   Store (bag, wishlist, recently viewed), header behaviour, drawers, modals, search,
   quick view, newsletter, toast and back-to-top. No dependencies. */
(function () {
  'use strict';

  var DATA = window.ELVARE || { products: [], categories: {}, collections: {} };
  var ROOT = document.body.getAttribute('data-root') || '';
  var TAX_RATE = 0.0825;           // flat demonstration tax rate
  var FREE_SHIP = 500;             // free standard shipping threshold (USD)
  var SHIPPING = {
    standard: { label: 'Standard', eta: '5–7 business days', price: 25 },
    express: { label: 'Express', eta: '2–3 business days', price: 35 },
    nextday: { label: 'Next day', eta: 'Next business day (order before 1pm ET)', price: 60 }
  };

  /* ---------------- helpers ---------------- */
  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };
  var esc = function (s) { return String(s).replace(/[&<>"']/g, function (m) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[m]; }); };
  var money = function (n, cents) {
    return '$' + Number(n).toLocaleString('en-US', { minimumFractionDigits: cents ? 2 : 0, maximumFractionDigits: cents ? 2 : 0 });
  };
  var byId = {};
  DATA.products.forEach(function (p) { byId[p.id] = p; });
  var productUrl = function (p) { return ROOT + 'product/' + p.slug + '.html'; };
  var imgFor = function (p, colorKey, w) {
    var key = colorKey || p.colors[0].key;
    return ROOT + 'assets/img/products/' + p.slug + '-' + key + '-' + (w || 480) + '.webp';
  };

  /* ---------------- storage (safe) ---------------- */
  var mem = {};
  var store = {
    get: function (k, d) {
      try { var v = window.localStorage.getItem('elvare:' + k); return v ? JSON.parse(v) : d; }
      catch (e) { return mem[k] !== undefined ? mem[k] : d; }
    },
    set: function (k, v) {
      try { window.localStorage.setItem('elvare:' + k, JSON.stringify(v)); }
      catch (e) { mem[k] = v; }
    },
    remove: function (k) { try { window.localStorage.removeItem('elvare:' + k); } catch (e) { delete mem[k]; } }
  };

  /* ---------------- cart ---------------- */
  var Cart = {
    items: function () {
      // drop lines whose product no longer exists (defensive against stale storage)
      // lines whose product or colourway no longer exists (e.g. after a catalogue update) are dropped
      return store.get('cart', []).filter(function (l) { return byId[l.id] && l.qty > 0 && byId[l.id].colors.some(function (c) { return c.name === l.color; }); });
    },
    save: function (items) { store.set('cart', items); emit(); },
    add: function (id, color, size, qty) {
      var p = byId[id]; if (!p) return false;
      qty = Math.max(1, Math.min(10, parseInt(qty, 10) || 1));
      var items = Cart.items();
      var key = id + '|' + color + '|' + size;
      var line = items.filter(function (l) { return l.key === key; })[0];
      if (line) line.qty = Math.min(10, line.qty + qty);
      else items.push({ key: key, id: id, color: color, size: size, qty: qty, added: Date.now() });
      Cart.save(items);
      return true;
    },
    update: function (key, qty) {
      var items = Cart.items();
      items.forEach(function (l) { if (l.key === key) l.qty = Math.max(1, Math.min(10, qty)); });
      Cart.save(items);
    },
    remove: function (key) { Cart.save(Cart.items().filter(function (l) { return l.key !== key; })); },
    clear: function () { Cart.save([]); },
    count: function () { return Cart.items().reduce(function (s, l) { return s + l.qty; }, 0); },
    totals: function (method) {
      // Work in cents to avoid floating point drift.
      var sub = Cart.items().reduce(function (s, l) { return s + byId[l.id].price * 100 * l.qty; }, 0);
      method = method || 'standard';
      var ship = 0;
      if (sub > 0) ship = (method === 'standard' && sub >= FREE_SHIP * 100) ? 0 : SHIPPING[method].price * 100;
      var tax = Math.round(sub * TAX_RATE);
      return { subtotal: sub / 100, shipping: ship / 100, tax: tax / 100, total: (sub + ship + tax) / 100, method: method };
    }
  };

  /* ---------------- wishlist & recently viewed ---------------- */
  var Wish = {
    ids: function () { return store.get('wishlist', []).filter(function (id) { return byId[id]; }); },
    has: function (id) { return Wish.ids().indexOf(id) > -1; },
    toggle: function (id) {
      var ids = Wish.ids(); var i = ids.indexOf(id);
      if (i > -1) ids.splice(i, 1); else ids.unshift(id);
      store.set('wishlist', ids); emit();
      return i === -1;
    }
  };
  var Recent = {
    ids: function () { return store.get('recent', []).filter(function (id) { return byId[id]; }); },
    push: function (id) { var ids = Recent.ids().filter(function (x) { return x !== id; }); ids.unshift(id); store.set('recent', ids.slice(0, 8)); }
  };

  /* ---------------- events ---------------- */
  function emit() { document.dispatchEvent(new CustomEvent('elvare:update')); }

  /* ---------------- UI: toast ---------------- */
  function toast(msg, link) {
    var region = $('.toast-region'); if (!region) return;
    var t = document.createElement('div'); t.className = 'toast';
    t.innerHTML = '<span>' + esc(msg) + '</span>' + (link ? '<a href="' + link.href + '">' + esc(link.text) + '</a>' : '');
    region.appendChild(t);
    setTimeout(function () { t.style.opacity = '0'; t.style.transition = 'opacity .4s'; }, 3200);
    setTimeout(function () { t.remove(); }, 3700);
  }

  /* ---------------- UI: overlays (drawers + modals) with focus management ---------------- */
  var lastFocus = null;
  var openEl = null;
  var FOCUSABLE = 'a[href], button:not([disabled]), input:not([disabled]):not([type="hidden"]), select, textarea, [tabindex]:not([tabindex="-1"])';
  function openOverlay(el, trigger) {
    if (!el) return;
    if (openEl && openEl !== el) closeOverlay(openEl, true);
    lastFocus = trigger || document.activeElement;
    el.classList.add('is-open'); el.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';
    $$('[aria-controls="' + el.id + '"]').forEach(function (b) { b.setAttribute('aria-expanded', 'true'); });
    openEl = el;
    setTimeout(function () { var f = $(FOCUSABLE, el.querySelector('.drawer__panel, .modal__dialog') || el); if (f) f.focus(); }, 60);
  }
  function closeOverlay(el, silent) {
    el = el || openEl; if (!el) return;
    el.classList.remove('is-open'); el.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
    $$('[aria-controls="' + el.id + '"]').forEach(function (b) { b.setAttribute('aria-expanded', 'false'); });
    if (openEl === el) openEl = null;
    if (!silent && lastFocus && lastFocus.focus) lastFocus.focus();
  }
  document.addEventListener('keydown', function (ev) {
    if (!openEl) return;
    if (ev.key === 'Escape') { closeOverlay(); return; }
    if (ev.key === 'Tab') { // focus trap
      var f = $$(FOCUSABLE, openEl).filter(function (n) { return n.offsetParent !== null; });
      if (!f.length) return;
      if (ev.shiftKey && document.activeElement === f[0]) { ev.preventDefault(); f[f.length - 1].focus(); }
      else if (!ev.shiftKey && document.activeElement === f[f.length - 1]) { ev.preventDefault(); f[0].focus(); }
    }
  });

  /* ---------------- product card (JS mirror of the static template) ---------------- */
  var ICON_HEART = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 20.5s-7.5-4.6-9.2-9.4C1.6 7.6 3.9 4.5 7.2 4.5c2 0 3.6 1.1 4.8 2.8 1.2-1.7 2.8-2.8 4.8-2.8 3.3 0 5.6 3.1 4.4 6.6-1.7 4.8-9.2 9.4-9.2 9.4z"/></svg>';
  function cardHTML(p) {
    var flag = p.availability === 'low_stock' ? '<span class="card__flag">Low stock</span>' :
      p.availability === 'preorder' ? '<span class="card__flag">Pre-order</span>' :
      p.isNew ? '<span class="card__flag card__flag--dark">New</span>' : '';
    var sizes = '(min-width: 1200px) 23vw, (min-width: 900px) 30vw, 48vw';
    var base = ROOT + 'assets/img/products/' + p.slug;
    var main = base + '-' + p.colors[0].key;
    var cat = DATA.categories[p.category] || '';
    var alt = p.name + ' in ' + p.colors[0].name + ' — ÉLVARÉ ' + cat.toLowerCase();
    var wished = Wish.has(p.id);
    return '<article class="card" data-id="' + p.id + '"><div class="card__media">' + flag +
      '<img src="' + main + '-480.webp" srcset="' + main + '-480.webp 480w, ' + main + '-960.webp 960w" sizes="' + sizes + '" width="960" height="1200" alt="' + esc(alt) + '" loading="lazy" decoding="async">' +
      '<img class="img-alt" src="' + base + '-alt-480.webp" srcset="' + base + '-alt-480.webp 480w, ' + base + '-alt-960.webp 960w" sizes="' + sizes + '" width="960" height="1200" alt="' + esc(alt + ', alternate view') + '" loading="lazy" decoding="async">' +
      '<button class="icon-btn card__wish" type="button" data-wish="' + p.id + '" aria-pressed="' + wished + '" aria-label="' + (wished ? 'Remove ' : 'Add ') + esc(p.name) + (wished ? ' from' : ' to') + ' wishlist">' + ICON_HEART + '</button>' +
      '<button class="card__quick" type="button" data-quick="' + p.id + '">Quick view</button></div>' +
      '<div class="card__body"><span class="card__cat">' + esc(cat) + '</span><h3 class="card__name"><a href="' + productUrl(p) + '">' + esc(p.name) + '</a></h3>' +
      '<span class="card__price">' + money(p.price) + '</span><div class="swatches" aria-label="' + p.colors.length + ' colours available">' +
      p.colors.map(function (c) { return '<span class="swatch-dot" style="background:' + c.hex + '" title="' + esc(c.name) + '"></span>'; }).join('') + '</div></div></article>';
  }

  /* ---------------- header counts + wish button state ---------------- */
  function syncUI() {
    var c = Cart.count(), w = Wish.ids().length;
    $$('[data-cart-count]').forEach(function (b) { b.textContent = c; b.setAttribute('data-count', c); });
    $$('[data-wish-count]').forEach(function (b) { b.textContent = w; b.setAttribute('data-count', w); });
    $$('[data-wish-count-text]').forEach(function (b) { b.textContent = w; });
    $$('[data-wish]').forEach(function (b) {
      var on = Wish.has(b.getAttribute('data-wish'));
      b.setAttribute('aria-pressed', on);
      var p = byId[b.getAttribute('data-wish')];
      if (p) b.setAttribute('aria-label', (on ? 'Remove ' + p.name + ' from' : 'Add ' + p.name + ' to') + ' wishlist');
    });
    renderCartDrawer();
  }

  /* ---------------- cart line + totals markup (shared by drawer / page / checkout) ---------------- */
  function lineHTML(l, opts) {
    var p = byId[l.id]; var col = p.colors.filter(function (c) { return c.name === l.color; })[0] || p.colors[0];
    return '<div class="cart-line" data-line="' + esc(l.key) + '"><a href="' + productUrl(p) + '"><img src="' + imgFor(p, col.key, 480) + '" alt="' + esc(p.name + ' in ' + col.name) + '" width="480" height="600" loading="lazy"></a>' +
      '<div><a class="cart-line__name" href="' + productUrl(p) + '">' + esc(p.name) + '</a><div class="cart-line__meta">' + esc(col.name) + ' · Size ' + esc(l.size) + (p.availability === 'preorder' ? ' · Pre-order' : '') + '</div>' +
      '<div class="cart-line__row"><div class="qty qty--sm" role="group" aria-label="Quantity for ' + esc(p.name) + '"><button type="button" data-line-qty="-1" aria-label="Decrease quantity">−</button>' +
      '<input type="number" min="1" max="10" value="' + l.qty + '" aria-label="Quantity" data-line-input><button type="button" data-line-qty="1" aria-label="Increase quantity">+</button></div>' +
      '<span>' + money(p.price * l.qty) + '</span></div><button class="remove-btn" type="button" data-line-remove>Remove</button></div></div>';
  }
  function totalsHTML(t, opts) {
    opts = opts || {};
    var remain = Math.max(0, FREE_SHIP - t.subtotal);
    var progress = opts.progress === false ? '' : '<div class="ship-progress">' + (remain > 0 ? 'You are ' + money(remain, true) + ' away from complimentary standard shipping' : 'Your order qualifies for complimentary standard shipping') +
      '<div class="bar"><i style="width:' + Math.min(100, t.subtotal / FREE_SHIP * 100) + '%"></i></div></div>';
    return progress + '<div class="totals">' +
      '<div class="row"><span>Subtotal</span><span>' + money(t.subtotal, true) + '</span></div>' +
      '<div class="row"><span>Shipping' + (opts.shipLabel ? ' (' + esc(opts.shipLabel) + ')' : ' (standard, est.)') + '</span><span>' + (t.shipping === 0 ? 'Complimentary' : money(t.shipping, true)) + '</span></div>' +
      '<div class="row"><span>Estimated tax (8.25% demo rate)</span><span>' + money(t.tax, true) + '</span></div>' +
      '<div class="row row--total"><span>Total</span><span>' + money(t.total, true) + ' USD</span></div></div>';
  }

  function renderCartDrawer() {
    var body = $('[data-cart-lines]'), foot = $('[data-cart-foot]');
    if (!body) return;
    var items = Cart.items();
    if (!items.length) {
      body.innerHTML = '<div class="empty-state" style="border:0;background:none;padding:3rem 0"><h3>Your bag is empty</h3><p>Discover new arrivals and the pieces of the season.</p><div class="hero__ctas" style="justify-content:center"><a class="btn" href="' + ROOT + 'women.html">Shop Women</a><a class="btn btn--ghost" href="' + ROOT + 'men.html">Shop Men</a></div></div>';
      foot.innerHTML = ''; foot.hidden = true; return;
    }
    foot.hidden = false;
    body.innerHTML = items.map(function (l) { return lineHTML(l); }).join('');
    foot.innerHTML = totalsHTML(Cart.totals()) +
      '<div style="display:grid;gap:.5rem;margin-top:1rem"><a class="btn btn--block" href="' + ROOT + 'checkout.html">Checkout</a><a class="btn btn--ghost btn--block" href="' + ROOT + 'cart.html">View bag</a></div>' +
      '<p class="demo-note">Demonstration store: checkout is simulated and no payment is taken.</p>';
  }

  // Delegated quantity/remove handling for any cart line on the page
  document.addEventListener('click', function (ev) {
    var line = ev.target.closest('[data-line]'); if (!line) return;
    var key = line.getAttribute('data-line');
    var item = Cart.items().filter(function (l) { return l.key === key; })[0]; if (!item) return;
    var step = ev.target.closest('[data-line-qty]');
    if (step) { Cart.update(key, item.qty + parseInt(step.getAttribute('data-line-qty'), 10)); refocus(key, '[data-line-qty="' + step.getAttribute('data-line-qty') + '"]'); }
    if (ev.target.closest('[data-line-remove]')) { Cart.remove(key); toast(byId[item.id].name + ' removed from your bag'); }
  });
  document.addEventListener('change', function (ev) {
    if (!ev.target.matches('[data-line-input]')) return;
    var key = ev.target.closest('[data-line]').getAttribute('data-line');
    var v = parseInt(ev.target.value, 10); if (isNaN(v) || v < 1) v = 1; if (v > 10) v = 10;
    Cart.update(key, v);
  });
  function refocus(key, sel) { // keep keyboard focus stable after re-render
    var el = document.querySelector('[data-line="' + (window.CSS && CSS.escape ? CSS.escape(key) : key) + '"] ' + sel);
    if (el) el.focus();
  }

  /* ---------------- global click handlers ---------------- */
  document.addEventListener('click', function (ev) {
    var t;
    if ((t = ev.target.closest('[data-open]'))) { ev.preventDefault(); openOverlay(document.getElementById(t.getAttribute('data-open')), t); return; }
    if ((t = ev.target.closest('[data-open-modal]'))) { ev.preventDefault(); openOverlay(document.getElementById(t.getAttribute('data-open-modal')), t); return; }
    if (ev.target.closest('[data-close]')) { closeOverlay(ev.target.closest('.drawer, .modal')); return; }
    if ((t = ev.target.closest('[data-wish]'))) {
      ev.preventDefault();
      var id = t.getAttribute('data-wish'); var added = Wish.toggle(id);
      toast(added ? byId[id].name + ' saved to your wishlist' : byId[id].name + ' removed from your wishlist', added ? { href: ROOT + 'wishlist.html', text: 'View' } : null);
      return;
    }
    if ((t = ev.target.closest('[data-quick]'))) { ev.preventDefault(); quickView(t.getAttribute('data-quick'), t); return; }
    if ((t = ev.target.closest('[data-rail]'))) {
      var rail = document.getElementById(t.getAttribute('data-rail'));
      if (rail) rail.scrollBy({ left: parseInt(t.getAttribute('data-dir'), 10) * rail.clientWidth * 0.8, behavior: 'smooth' });
      return;
    }
    if ((t = ev.target.closest('[data-sg-tab]'))) {
      var wrap = t.parentNode.parentNode;
      $$('[data-sg-tab]', wrap).forEach(function (b) { var on = b === t; b.classList.toggle('is-active', on); b.setAttribute('aria-selected', on); });
      $$('[data-sg-panel]', wrap).forEach(function (pn) { pn.hidden = pn.getAttribute('data-sg-panel') !== t.getAttribute('data-sg-tab'); });
      return;
    }
    if (ev.target.closest('[data-to-top]')) { window.scrollTo({ top: 0, behavior: 'smooth' }); var m = $('#main'); if (m) m.focus({ preventScroll: true }); }
  });

  /* ---------------- quick view ---------------- */
  function quickView(id, trigger) {
    var p = byId[id]; if (!p) return;
    var modal = $('#quickview'); var body = $('[data-qv-body]', modal);
    var one = p.sizes.length === 1;
    body.innerHTML = '<div class="quickview"><img data-qv-img src="' + imgFor(p, null, 960) + '" alt="' + esc(p.name + ' in ' + p.colors[0].name) + '" width="960" height="1200">' +
      '<div><span class="eyebrow">' + esc(DATA.categories[p.category] || '') + '</span><h2 id="qv-title">' + esc(p.name) + '</h2><p class="pdp__price">' + money(p.price) + '</p>' +
      '<p class="pdp__desc">' + esc(p.description) + '</p>' +
      '<div class="option-row"><div class="option-head"><span class="label" id="qv-color">Colour <span data-qv-colorname>' + esc(p.colors[0].name) + '</span></span></div><div class="color-swatches" role="radiogroup" aria-labelledby="qv-color">' +
      p.colors.map(function (c, i) { return '<button class="color-swatch" type="button" role="radio" aria-checked="' + (i === 0) + '" data-qv-color="' + esc(c.name) + '" data-key="' + c.key + '" style="background-color:' + c.hex + '" aria-label="' + esc(c.name) + '"></button>'; }).join('') + '</div></div>' +
      '<div class="option-row" data-qv-sizerow><div class="option-head"><span class="label" id="qv-size">Size</span><button class="text-link" type="button" data-open-modal="size-guide" style="font-size:.8rem">Size guide</button></div><div class="size-grid" role="radiogroup" aria-labelledby="qv-size">' +
      p.sizes.map(function (s) { return '<button class="size-btn" type="button" role="radio" aria-checked="' + one + '" data-qv-size="' + esc(s) + '">' + esc(s) + '</button>'; }).join('') + '</div><p class="field-error" data-qv-err role="alert"></p></div>' +
      '<div style="display:grid;gap:.6rem"><button class="btn btn--block" type="button" data-qv-add>Add to Bag</button><a class="btn btn--ghost btn--block" href="' + productUrl(p) + '">View full details</a></div></div></div>';
    var state = { color: p.colors[0].name, size: one ? p.sizes[0] : null };
    body.onclick = function (ev) {
      var c = ev.target.closest('[data-qv-color]'), s = ev.target.closest('[data-qv-size]');
      if (c) {
        state.color = c.getAttribute('data-qv-color');
        $$('[data-qv-color]', body).forEach(function (b) { b.setAttribute('aria-checked', b === c); });
        $('[data-qv-img]', body).src = imgFor(p, c.getAttribute('data-key'), 960);
        $('[data-qv-img]', body).alt = p.name + ' in ' + state.color;
        $('[data-qv-colorname]', body).textContent = state.color;
      }
      if (s) { state.size = s.getAttribute('data-qv-size'); $$('[data-qv-size]', body).forEach(function (b) { b.setAttribute('aria-checked', b === s); }); $('[data-qv-err]', body).textContent = ''; }
      if (ev.target.closest('[data-qv-add]')) {
        if (!state.size) { $('[data-qv-err]', body).textContent = 'Please select a size.'; return; }
        Cart.add(p.id, state.color, state.size, 1);
        closeOverlay(modal, true);
        openOverlay($('#cart-drawer'));
        toast(p.name + ' added to your bag');
      }
    };
    openOverlay(modal, trigger);
  }

  /* ---------------- search overlay with live suggestions ---------------- */
  function searchProducts(q) {
    q = (q || '').trim().toLowerCase(); if (!q) return [];
    var terms = q.split(/\s+/);
    return DATA.products.map(function (p) {
      var hay = (p.name + ' ' + p.category + ' ' + (DATA.categories[p.category] || '') + ' ' + p.gender + ' ' + p.tags.join(' ') + ' ' +
        p.colors.map(function (c) { return c.name; }).join(' ') + ' ' + p.collections.map(function (c) { return DATA.collections[c]; }).join(' ') + ' ' + p.description).toLowerCase();
      var score = 0;
      for (var i = 0; i < terms.length; i++) {
        var t = terms[i].replace(/s$/, ''); // naive singularisation: "coats" → "coat"
        if (hay.indexOf(t) === -1) return null;
        score += (p.name.toLowerCase().indexOf(t) > -1 ? 3 : 0) + (p.tags.join(' ').indexOf(t) > -1 ? 2 : 0) + 1;
      }
      return { p: p, score: score };
    }).filter(Boolean).sort(function (a, b) { return b.score - a.score || b.p.popularity - a.p.popularity; }).map(function (r) { return r.p; });
  }
  var overlay = $('#search-overlay');
  $$('[data-open-search]').forEach(function (b) {
    b.addEventListener('click', function () {
      overlay.classList.add('is-open'); overlay.setAttribute('aria-hidden', 'false'); document.body.style.overflow = 'hidden';
      lastFocus = b; openEl = overlay; setTimeout(function () { $('#search-input').focus(); }, 50);
    });
  });
  $$('[data-close-search]').forEach(function (b) { b.addEventListener('click', function () { closeOverlay(overlay); }); });
  var sInput = $('#search-input');
  if (sInput) sInput.addEventListener('input', function () {
    var res = searchProducts(sInput.value).slice(0, 6), box = $('#search-suggest');
    if (!sInput.value.trim()) { box.innerHTML = ''; return; }
    box.innerHTML = res.length ? res.map(function (p) {
      return '<a href="' + productUrl(p) + '"><img src="' + imgFor(p) + '" alt="" width="48" height="60" loading="lazy"><span><span class="s-name">' + esc(p.name) + '</span><br><span class="s-meta">' + esc(DATA.categories[p.category]) + ' · ' + money(p.price) + '</span></span></a>';
    }).join('') + '<a href="' + ROOT + 'shop.html?q=' + encodeURIComponent(sInput.value.trim()) + '" class="link-arrow" style="border-bottom:1px solid;justify-self:start;margin-top:.75rem">See all results</a>'
      : '<p class="form-note">No pieces found for “' + esc(sInput.value) + '”. Try “coat”, “silk” or “knit”.</p>';
  });

  /* ---------------- newsletter (demonstration) ---------------- */
  var EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
  $$('[data-newsletter]').forEach(function (f) {
    var msg = f.parentNode.querySelector('[data-nl-msg]');
    f.addEventListener('submit', function (ev) {
      ev.preventDefault();
      var v = f.email.value.trim();
      msg.className = 'form-msg';
      if (!EMAIL_RE.test(v)) { msg.textContent = 'Please enter a valid email address.'; msg.classList.add('is-error'); f.email.setAttribute('aria-invalid', 'true'); f.email.focus(); return; }
      f.email.removeAttribute('aria-invalid');
      var list = store.get('newsletter', []); if (list.indexOf(v) === -1) list.push(v); store.set('newsletter', list);
      msg.textContent = 'Thank you — ' + v + ' is subscribed in this demonstration (saved in your browser only; no email will be sent).';
      msg.classList.add('is-success'); f.reset();
    });
  });

  /* ---------------- header shadow, back to top, reveal ---------------- */
  var header = $('.site-header'), toTop = $('[data-to-top]');
  var onScroll = function () {
    var y = window.scrollY;
    if (header) header.classList.toggle('is-scrolled', y > 8);
    if (toTop) toTop.classList.toggle('is-visible', y > 700);
  };
  window.addEventListener('scroll', onScroll, { passive: true }); onScroll();
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (es) { es.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add('is-in'); io.unobserve(en.target); } }); }, { rootMargin: '0px 0px -8% 0px' });
    $$('.reveal').forEach(function (el) { io.observe(el); });
  } else { $$('.reveal').forEach(function (el) { el.classList.add('is-in'); }); }

  // Close the mobile nav when a same-page anchor is followed
  $$('#nav-drawer a').forEach(function (a) { a.addEventListener('click', function () { closeOverlay($('#nav-drawer'), true); }); });

  document.addEventListener('elvare:update', syncUI);
  window.addEventListener('storage', function (ev) { if (ev.key && ev.key.indexOf('elvare:') === 0) syncUI(); }); // sync across tabs
  syncUI();

  /* ---------------- public API for page scripts ---------------- */
  window.Elvare = {
    data: DATA, byId: byId, root: ROOT, cart: Cart, wish: Wish, recent: Recent, store: store,
    money: money, esc: esc, cardHTML: cardHTML, toast: toast, productUrl: productUrl, imgFor: imgFor,
    openOverlay: openOverlay, closeOverlay: closeOverlay, search: searchProducts, lineHTML: lineHTML, totalsHTML: totalsHTML,
    SHIPPING: SHIPPING, FREE_SHIP: FREE_SHIP, TAX_RATE: TAX_RATE, EMAIL_RE: EMAIL_RE, $: $, $$: $$
  };
})();
