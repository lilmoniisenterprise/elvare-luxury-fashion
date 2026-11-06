/* ÉLVARÉ — product detail page: gallery, colour & size selection, quantity, add to bag,
   wishlist, recently viewed. */
(function () {
  'use strict';
  var E = window.Elvare; if (!E) return;
  var $ = E.$, $$ = E.$$;
  var root = $('[data-product]'); if (!root) return;
  var p = E.byId[root.getAttribute('data-product')]; if (!p) return;

  var state = { color: p.colors[0], size: p.sizes.length === 1 ? p.sizes[0] : null, view: 0 };
  var mainBox = $('[data-gallery-main]'), mainImg = $('img', mainBox);
  var base = E.root + 'assets/img/products/' + p.slug;

  function views() {
    return [
      { src: base + '-' + state.color.key, alt: p.name + ' in ' + state.color.name },
      { src: base + '-alt', alt: p.name + ' in ' + p.colors[0].name + ', alternate studio view' },
      { src: base + '-detail', alt: p.name + ', fabric and construction detail' }
    ];
  }
  function show(i) {
    var v = views(); state.view = (i + v.length) % v.length;
    var cur = v[state.view];
    mainImg.src = cur.src + '-960.webp';
    mainImg.srcset = cur.src + '-480.webp 480w, ' + cur.src + '-960.webp 960w';
    mainImg.alt = cur.alt;
    mainBox.classList.remove('is-zoom');
    $$('[data-thumb]').forEach(function (b, idx) { b.setAttribute('aria-current', idx === state.view ? 'true' : 'false'); });
  }
  function updateThumb0() {
    var t = $('[data-thumb="0"] img');
    if (t) { t.src = base + '-' + state.color.key + '-480.webp'; t.srcset = base + '-' + state.color.key + '-480.webp 480w'; }
  }

  // gallery controls
  $$('[data-thumb]').forEach(function (b) { b.addEventListener('click', function () { show(parseInt(b.getAttribute('data-thumb'), 10)); }); });
  $$('[data-gallery-step]').forEach(function (b) { b.addEventListener('click', function (ev) { ev.stopPropagation(); show(state.view + parseInt(b.getAttribute('data-gallery-step'), 10)); }); });
  mainBox.addEventListener('click', function (ev) {
    if (ev.target.closest('button')) return;
    var r = mainBox.getBoundingClientRect();
    mainImg.style.transformOrigin = ((ev.clientX - r.left) / r.width * 100) + '% ' + ((ev.clientY - r.top) / r.height * 100) + '%';
    mainBox.classList.toggle('is-zoom');
  });
  mainBox.setAttribute('tabindex', '0');
  mainBox.setAttribute('aria-label', 'Product images. Use left and right arrow keys to browse; click to zoom.');
  mainBox.addEventListener('keydown', function (ev) {
    if (ev.key === 'ArrowRight') { ev.preventDefault(); show(state.view + 1); }
    if (ev.key === 'ArrowLeft') { ev.preventDefault(); show(state.view - 1); }
  });
  // touch swipe
  var sx = null;
  mainBox.addEventListener('touchstart', function (ev) { sx = ev.touches[0].clientX; }, { passive: true });
  mainBox.addEventListener('touchend', function (ev) { if (sx === null) return; var dx = ev.changedTouches[0].clientX - sx; if (Math.abs(dx) > 40) show(state.view + (dx < 0 ? 1 : -1)); sx = null; });

  // colour selection (roving radio)
  var swatches = $$('[data-color]');
  function pickColor(btn) {
    state.color = p.colors.filter(function (c) { return c.name === btn.getAttribute('data-color'); })[0];
    swatches.forEach(function (b) { var on = b === btn; b.setAttribute('aria-checked', on); b.tabIndex = on ? 0 : -1; });
    $('[data-color-name]').textContent = state.color.name;
    updateThumb0(); show(0);
  }
  swatches.forEach(function (b, i) {
    b.tabIndex = i === 0 ? 0 : -1;
    b.addEventListener('click', function () { pickColor(b); });
    b.addEventListener('keydown', function (ev) { radioKeys(ev, swatches, pickColor); });
  });

  // size selection
  var sizeBtns = $$('[data-size]'), sizeRow = $('[data-size-row]'), sizeErr = $('[data-size-error]');
  function pickSize(btn) {
    state.size = btn.getAttribute('data-size');
    sizeBtns.forEach(function (b) { var on = b === btn; b.setAttribute('aria-checked', on); b.tabIndex = on ? 0 : -1; });
    $('[data-size-name]').textContent = state.size;
    sizeRow.classList.remove('has-error'); sizeErr.textContent = '';
  }
  sizeBtns.forEach(function (b, i) {
    b.tabIndex = (state.size ? b.getAttribute('data-size') === state.size : i === 0) ? 0 : -1;
    b.addEventListener('click', function () { pickSize(b); });
    b.addEventListener('keydown', function (ev) { radioKeys(ev, sizeBtns, pickSize); });
  });
  function radioKeys(ev, list, pick) {
    var i = list.indexOf(ev.currentTarget), n = null;
    if (ev.key === 'ArrowRight' || ev.key === 'ArrowDown') n = list[(i + 1) % list.length];
    if (ev.key === 'ArrowLeft' || ev.key === 'ArrowUp') n = list[(i - 1 + list.length) % list.length];
    if (n) { ev.preventDefault(); pick(n); n.focus(); }
  }

  // quantity
  var qty = $('[data-qty-input]');
  function clampQty() { var v = parseInt(qty.value, 10); if (isNaN(v) || v < 1) v = 1; if (v > 10) v = 10; qty.value = v; return v; }
  $$('[data-qty]').forEach(function (b) { b.addEventListener('click', function () { qty.value = (parseInt(qty.value, 10) || 1) + parseInt(b.getAttribute('data-qty'), 10); clampQty(); }); });
  qty.addEventListener('change', clampQty);

  // add to bag
  $('[data-add-to-cart]').addEventListener('click', function () {
    if (!state.size) {
      sizeRow.classList.add('has-error'); sizeErr.textContent = 'Please select a size to continue.';
      if (sizeBtns[0]) sizeBtns[0].focus();
      return;
    }
    var n = clampQty();
    E.cart.add(p.id, state.color.name, state.size, n);
    E.toast(n + ' × ' + p.name + ' added to your bag', { href: E.root + 'cart.html', text: 'View bag' });
    E.openOverlay(document.getElementById('cart-drawer'), this);
  });

  // recently viewed (render before recording the current product)
  var recent = E.recent.ids().filter(function (id) { return id !== p.id; }).slice(0, 4);
  if (recent.length) {
    $('[data-recent]').innerHTML = recent.map(function (id) { return E.cardHTML(E.byId[id]); }).join('');
    $('[data-recent-section]').hidden = false;
  }
  E.recent.push(p.id);
})();
