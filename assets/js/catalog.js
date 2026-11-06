/* ÉLVARÉ — listing pages (Women, Men, Shop All / search results).
   Category tabs, search, price/size/colour/stock filters, sorting, URL state, mobile filter drawer. */
(function () {
  'use strict';
  var E = window.Elvare; if (!E) return;
  var $ = E.$, $$ = E.$$;
  var scope = document.body.getAttribute('data-scope') || 'all';
  var grid = $('[data-grid]'), form = $('[data-filters]'), sortSel = $('[data-sort]');
  var empty = $('[data-empty]'), chipsBox = $('[data-active-filters]');
  if (!grid || !form) return;

  var params = new URLSearchParams(location.search);
  var state = {
    cat: params.get('cat') || '',
    q: params.get('q') || '',
    collection: params.get('collection') || '',
    sort: params.get('sort') || 'featured',
    min: params.get('min') || '', max: params.get('max') || '',
    sizes: params.getAll('size'), colors: params.getAll('color'),
    instock: params.get('instock') === '1'
  };

  // restore form controls from URL state
  sortSel.value = ['featured', 'newest', 'popular', 'price-asc', 'price-desc'].indexOf(state.sort) > -1 ? state.sort : 'featured';
  form.min.value = state.min; form.max.value = state.max; form.instock.checked = state.instock;
  $$('input[name="size"]', form).forEach(function (i) { i.checked = state.sizes.indexOf(i.value) > -1; });
  $$('input[name="color"]', form).forEach(function (i) { i.checked = state.colors.indexOf(i.value) > -1; });

  var title = $('[data-listing-title]'), sub = $('[data-listing-sub]');
  var baseTitle = title ? title.textContent : '';

  function readForm() {
    state.min = form.min.value; state.max = form.max.value; state.instock = form.instock.checked;
    state.sizes = $$('input[name="size"]:checked', form).map(function (i) { return i.value; });
    state.colors = $$('input[name="color"]:checked', form).map(function (i) { return i.value; });
    state.sort = sortSel.value;
  }

  function filtered() {
    var list = state.q ? E.search(state.q) : E.data.products.slice();
    var min = parseFloat(state.min), max = parseFloat(state.max);
    if (!isNaN(min) && !isNaN(max) && min > max) { var t = min; min = max; max = t; } // tolerate reversed range
    return list.filter(function (p) {
      if (scope !== 'all' && p.gender !== scope) return false;
      if (state.cat === 'new' && !p.isNew) return false;
      if (state.cat && state.cat !== 'new' && p.category !== state.cat && !(state.cat === 'jackets' && p.category === 'jackets-coats')) return false;
      if (state.collection && p.collections.indexOf(state.collection) === -1) return false;
      if (!isNaN(min) && p.price < min) return false;
      if (!isNaN(max) && p.price > max) return false;
      if (state.sizes.length && !p.sizes.some(function (s) { return state.sizes.indexOf(s) > -1; })) return false;
      if (state.colors.length && !p.colors.some(function (c) { return state.colors.indexOf(c.name) > -1; })) return false;
      if (state.instock && p.availability === 'preorder') return false;
      return true;
    });
  }

  function sorted(list) {
    var s = state.sort;
    var fn = {
      'price-asc': function (a, b) { return a.price - b.price; },
      'price-desc': function (a, b) { return b.price - a.price; },
      'newest': function (a, b) { return b.added < a.added ? -1 : b.added > a.added ? 1 : 0; },
      'popular': function (a, b) { return b.popularity - a.popularity; }
    }[s];
    if (fn) return list.slice().sort(fn);
    return state.q ? list : list.slice().sort(function (a, b) { return (b.bestseller - a.bestseller) || (b.isNew - a.isNew) || (b.popularity - a.popularity); });
  }

  function syncURL() {
    var u = new URLSearchParams();
    if (state.q) u.set('q', state.q);
    if (state.cat) u.set('cat', state.cat);
    if (state.collection) u.set('collection', state.collection);
    if (state.sort !== 'featured') u.set('sort', state.sort);
    if (state.min) u.set('min', state.min);
    if (state.max) u.set('max', state.max);
    state.sizes.forEach(function (s) { u.append('size', s); });
    state.colors.forEach(function (c) { u.append('color', c); });
    if (state.instock) u.set('instock', '1');
    var qs = u.toString();
    history.replaceState(null, '', location.pathname + (qs ? '?' + qs : ''));
  }

  function chip(label, key, val) {
    return '<button class="chip" type="button" data-remove="' + key + '" data-val="' + E.esc(val || '') + '">' + E.esc(label) + ' <span aria-hidden="true">×</span><span class="visually-hidden">Remove filter</span></button>';
  }

  var lastGrid = null, lastChips = null;
  function render() {
    var list = sorted(filtered());
    var gridHTML = list.map(E.cardHTML).join('');
    if (gridHTML !== lastGrid) { grid.innerHTML = gridHTML; lastGrid = gridHTML; }
    empty.hidden = list.length > 0; grid.hidden = list.length === 0;
    $$('[data-result-count]').forEach(function (n) { n.textContent = list.length; });
    $$('.cat-tabs [data-cat]').forEach(function (b) { var on = b.getAttribute('data-cat') === state.cat; b.classList.toggle('is-active', on); b.setAttribute('aria-pressed', on); });
    // headings reflect search / collection / category context
    if (title) {
      var catLabel = state.cat === 'new' ? 'New Arrivals' : (E.data.categories[state.cat] || '');
      if (state.q) { title.textContent = 'Results for “' + state.q + '”'; }
      else if (state.collection && E.data.collections[state.collection]) { title.textContent = E.data.collections[state.collection]; }
      else if (catLabel) { title.textContent = baseTitle === 'Shop All' ? catLabel : baseTitle + ' · ' + catLabel; }
      else { title.textContent = baseTitle; }
      if (sub && state.q) sub.textContent = list.length + (list.length === 1 ? ' piece matches' : ' pieces match') + ' your search.';
      document.title = title.textContent + ' | ÉLVARÉ';
    }
    var chips = [];
    if (state.q) chips.push(chip('Search: ' + state.q, 'q'));
    if (state.collection) chips.push(chip(E.data.collections[state.collection] || state.collection, 'collection'));
    if (state.min || state.max) chips.push(chip('$' + (state.min || 0) + ' – ' + (state.max ? '$' + state.max : 'any'), 'price'));
    state.sizes.forEach(function (s) { chips.push(chip('Size ' + s, 'size', s)); });
    state.colors.forEach(function (c) { chips.push(chip(c, 'color', c)); });
    if (state.instock) chips.push(chip('In stock', 'instock'));
    // only touch the DOM when chips change, so a blur-triggered re-render never swallows a click
    var chipsHTML = chips.join('') + (chips.length > 1 ? '<button class="chip" type="button" data-clear-filters>Clear all</button>' : '');
    if (chipsHTML !== lastChips) { chipsBox.innerHTML = chipsHTML; lastChips = chipsHTML; }
    syncURL();
  }

  function clearAll() {
    form.reset(); state.q = ''; state.collection = ''; readForm(); render();
  }

  // events
  form.addEventListener('change', function () { readForm(); render(); });
  form.addEventListener('input', function (ev) { if (ev.target.type === 'number') { clearTimeout(form._t); form._t = setTimeout(function () { readForm(); render(); }, 350); } });
  form.addEventListener('submit', function (ev) { ev.preventDefault(); });
  sortSel.addEventListener('change', function () { readForm(); render(); });
  document.addEventListener('click', function (ev) {
    var t;
    if ((t = ev.target.closest('.cat-tabs [data-cat]'))) { state.cat = t.getAttribute('data-cat'); render(); return; }
    if ((t = ev.target.closest('[data-price]'))) {
      var r = t.getAttribute('data-price').split('-'); form.min.value = r[0]; form.max.value = r[1] || ''; readForm(); render(); return;
    }
    if (ev.target.closest('[data-clear-filters]')) { clearAll(); return; }
    if ((t = ev.target.closest('[data-remove]'))) {
      var k = t.getAttribute('data-remove'), v = t.getAttribute('data-val');
      if (k === 'q') state.q = '';
      if (k === 'collection') state.collection = '';
      if (k === 'price') { form.min.value = ''; form.max.value = ''; }
      if (k === 'size' || k === 'color') { var inp = form.querySelector('input[name="' + k + '"][value="' + v.replace(/"/g, '\\"') + '"]'); if (inp) inp.checked = false; }
      if (k === 'instock') form.instock.checked = false;
      readForm(); render(); return;
    }
    if (ev.target.closest('[data-open-filters]')) { var fp = $('#filters'); fp.classList.add('is-open'); document.body.style.overflow = 'hidden'; var f = fp.querySelector('input, button'); if (f) f.focus(); return; }
    if (ev.target.closest('[data-close-filters]')) { $('#filters').classList.remove('is-open'); document.body.style.overflow = ''; var tg = $('[data-open-filters]'); if (tg && ev.target.closest('.drawer__foot, .drawer__head')) tg.focus(); }
  });
  document.addEventListener('keydown', function (ev) { if (ev.key === 'Escape' && $('#filters').classList.contains('is-open')) { $('#filters').classList.remove('is-open'); document.body.style.overflow = ''; } });
  document.addEventListener('elvare:update', function () { /* wish states are synced by app.js */ });

  render();
})();
