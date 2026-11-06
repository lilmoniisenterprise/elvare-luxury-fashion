/* ÉLVARÉ — demonstration checkout.
   Information → Delivery → Payment (simulated, no card data) → Confirmation with printable receipt.
   Nothing is transmitted; order data lives only in this browser. */
(function () {
  'use strict';
  var E = window.Elvare; if (!E) return;
  var $ = E.$, $$ = E.$$, esc = E.esc, money = E.money;
  var root = $('[data-checkout-root]'); if (!root) return;
  var stepsEl = $('[data-steps]');

  var STATES = ['AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'DC', 'FL', 'GA', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY'];
  var PAY = {
    card: { title: 'Simulated card payment', sub: 'Demonstrates a card step without collecting any card details' },
    wallet: { title: 'Simulated digital wallet', sub: 'Demonstrates an express wallet payment' },
    invoice: { title: 'Demo invoice', sub: 'Demonstrates a pay-later invoice option' }
  };
  var data = E.store.get('checkout', { info: {}, ship: 'standard', gift: '', pay: 'card' });
  var step = 1;

  function save() { E.store.set('checkout', data); }

  function field(name, label, type, opts) {
    opts = opts || {};
    var v = data.info[name] || '';
    var input = type === 'select'
      ? '<select class="input" id="f-' + name + '" name="' + name + '"' + (opts.required ? ' required' : '') + ' autocomplete="' + (opts.ac || 'off') + '"><option value="">Select</option>' + opts.options.map(function (o) { return '<option' + (o === v ? ' selected' : '') + '>' + o + '</option>'; }).join('') + '</select>'
      : '<input class="input" id="f-' + name + '" name="' + name + '" type="' + type + '" value="' + esc(v) + '"' + (opts.required ? ' required' : '') + (opts.ac ? ' autocomplete="' + opts.ac + '"' : '') + (opts.mode ? ' inputmode="' + opts.mode + '"' : '') + (opts.ph ? ' placeholder="' + esc(opts.ph) + '"' : '') + '>';
    return '<div class="field' + (opts.span ? ' span-2' : '') + '"><label for="f-' + name + '">' + label + (opts.required ? '' : ' <span style="text-transform:none;letter-spacing:0;color:var(--muted)">(optional)</span>') + '</label>' + input + '<span class="field-error" id="e-' + name + '"></span></div>';
  }

  function summary() {
    var t = E.cart.totals(data.ship);
    return '<aside class="summary-box" aria-labelledby="os-title"><h2 id="os-title">Order summary</h2>' +
      E.cart.items().map(function (l) {
        var p = E.byId[l.id]; var c = p.colors.filter(function (x) { return x.name === l.color; })[0] || p.colors[0];
        return '<div class="mini-line"><img src="' + E.imgFor(p, c.key) + '" alt="" width="480" height="600" loading="lazy"><div><div class="ml-name">' + esc(p.name) + '</div><div class="ml-meta">' + esc(l.color) + ' · ' + esc(l.size) + ' · Qty ' + l.qty + '</div></div><span>' + money(p.price * l.qty) + '</span></div>';
      }).join('') + '<div style="margin-top:1.25rem">' + E.totalsHTML(t, { progress: false, shipLabel: E.SHIPPING[data.ship].label }) + '</div>' +
      '<p class="demo-note"><a class="text-link" href="cart.html">Edit bag</a> · Simulated order — no payment is taken.</p></aside>';
  }

  function setSteps(n) {
    $$('li', stepsEl).forEach(function (li, i) {
      li.classList.toggle('is-active', i + 1 === n); li.classList.toggle('is-done', i + 1 < n);
      if (i + 1 === n) li.setAttribute('aria-current', 'step'); else li.removeAttribute('aria-current');
    });
  }

  function render() {
    setSteps(step);
    if (!E.cart.items().length) {
      var last = E.store.get('lastOrder', null);
      root.innerHTML = '<div class="empty-state"><h2>Your bag is empty</h2><p>Add a piece to your bag to begin the demonstration checkout.</p><div class="hero__ctas" style="justify-content:center"><a class="btn" href="shop.html">Shop the collection</a>' +
        (last ? '<button class="btn btn--ghost" type="button" data-view-last>View last demo receipt</button>' : '') + '</div></div>';
      var b = $('[data-view-last]'); if (b) b.addEventListener('click', function () { confirmation(last); });
      return;
    }
    var html = '';
    if (step === 1) {
      html = '<form data-step-form novalidate><fieldset><legend>Contact</legend><div class="form-grid">' +
        field('email', 'Email', 'email', { required: true, ac: 'email', span: true }) +
        field('phone', 'Phone', 'tel', { ac: 'tel', mode: 'tel', span: true }) +
        '</div></fieldset><fieldset><legend>Shipping address</legend><div class="form-grid">' +
        field('first', 'First name', 'text', { required: true, ac: 'given-name' }) +
        field('last', 'Last name', 'text', { required: true, ac: 'family-name' }) +
        field('address1', 'Address', 'text', { required: true, ac: 'address-line1', span: true }) +
        field('address2', 'Apartment, suite', 'text', { ac: 'address-line2', span: true }) +
        field('city', 'City', 'text', { required: true, ac: 'address-level2' }) +
        field('state', 'State', 'select', { required: true, options: STATES, ac: 'address-level1' }) +
        field('zip', 'ZIP code', 'text', { required: true, ac: 'postal-code', mode: 'numeric', ph: '12345' }) +
        '<div class="field"><label for="f-country">Country</label><input class="input" id="f-country" value="United States" disabled><span class="field-error"></span></div>' +
        '</div><p class="form-note">Demonstration: shipping is shown for US addresses only. Use any fictional address.</p></fieldset>' +
        '<div class="hero__ctas" style="margin-top:0"><button class="btn" type="submit">Continue to delivery</button><a class="btn btn--ghost" href="cart.html">Return to bag</a></div></form>';
    } else if (step === 2) {
      var sub = E.cart.totals('standard').subtotal;
      html = '<form data-step-form novalidate><fieldset><legend>Delivery method</legend>' +
        Object.keys(E.SHIPPING).map(function (k) {
          var s = E.SHIPPING[k]; var price = (k === 'standard' && sub >= E.FREE_SHIP) ? 'Complimentary' : money(s.price);
          return '<label class="radio-card"><input type="radio" name="ship" value="' + k + '"' + (data.ship === k ? ' checked' : '') + '><span class="rc-main"><span class="rc-title">' + s.label + '</span><br><span class="rc-sub">' + s.eta + '</span></span><span class="rc-price">' + price + '</span></label>';
        }).join('') + '</fieldset>' +
        '<fieldset><legend>Presentation</legend><div class="field"><label for="f-gift">Gift message</label><textarea class="input" id="f-gift" name="gift" maxlength="200" placeholder="Optional — up to 200 characters">' + esc(data.gift || '') + '</textarea></div></fieldset>' +
        '<div class="review-block"><div><h3>Ship to</h3>' + addr() + '</div><button class="text-link" type="button" data-goto="1">Edit</button></div>' +
        '<div class="hero__ctas"><button class="btn" type="submit">Continue to payment</button><button class="btn btn--ghost" type="button" data-goto="1">Back</button></div></form>';
    } else if (step === 3) {
      html = '<form data-step-form novalidate><fieldset><legend>Payment</legend>' +
        '<div class="demo-banner"><span>' + '🔒' + '</span><span><strong>No payment details are requested.</strong> Choose a simulated method to see how a real checkout step would feel. No card is charged and no payment processor is connected.</span></div>' +
        Object.keys(PAY).map(function (k) {
          return '<label class="radio-card"><input type="radio" name="pay" value="' + k + '"' + (data.pay === k ? ' checked' : '') + '><span class="rc-main"><span class="rc-title">' + PAY[k].title + '</span><br><span class="rc-sub">' + PAY[k].sub + '</span></span></label>';
        }).join('') +
        '<div class="demo-pay" data-pay-detail></div></fieldset>' +
        '<div class="review-block"><div><h3>Contact</h3>' + esc(data.info.email) + '</div><button class="text-link" type="button" data-goto="1">Edit</button></div>' +
        '<div class="review-block"><div><h3>Ship to</h3>' + addr() + '</div><button class="text-link" type="button" data-goto="1">Edit</button></div>' +
        '<div class="review-block"><div><h3>Delivery</h3>' + E.SHIPPING[data.ship].label + ' · ' + E.SHIPPING[data.ship].eta + '</div><button class="text-link" type="button" data-goto="2">Edit</button></div>' +
        '<label class="check" style="margin:1.5rem 0 .5rem"><input type="checkbox" name="agree" required> I understand this is a simulated order: nothing will be shipped and no payment will be taken. I accept the <a class="text-link" href="terms.html">demonstration terms</a>.</label>' +
        '<p class="field-error" data-agree-error role="alert"></p>' +
        '<div class="hero__ctas"><button class="btn" type="submit" data-place>Place demonstration order · ' + money(E.cart.totals(data.ship).total, true) + '</button><button class="btn btn--ghost" type="button" data-goto="2">Back</button></div></form>';
    }
    root.innerHTML = '<div class="checkout"><div>' + html + '</div>' + summary() + '</div>';
    bind();
  }

  function addr() {
    var i = data.info;
    return esc(i.first + ' ' + i.last) + '<br>' + esc(i.address1) + (i.address2 ? ', ' + esc(i.address2) : '') + '<br>' + esc(i.city) + ', ' + esc(i.state) + ' ' + esc(i.zip) + '<br>United States';
  }

  function validateInfo(form) {
    var errs = {}, f = function (n) { return (form[n].value || '').trim(); };
    ['email', 'first', 'last', 'address1', 'city', 'state', 'zip'].forEach(function (n) { if (!f(n)) errs[n] = 'This field is required.'; });
    if (f('email') && !E.EMAIL_RE.test(f('email'))) errs.email = 'Please enter a valid email address.';
    if (f('zip') && !/^\d{5}(-\d{4})?$/.test(f('zip'))) errs.zip = 'Please enter a 5-digit ZIP code.';
    if (f('phone') && !/^[+()\d\s.-]{7,20}$/.test(f('phone'))) errs.phone = 'Please enter a valid phone number.';
    ['email', 'phone', 'first', 'last', 'address1', 'address2', 'city', 'state', 'zip'].forEach(function (n) {
      var inp = form[n], e = $('#e-' + n);
      inp.closest('.field').classList.toggle('has-error', !!errs[n]);
      if (e) e.textContent = errs[n] || '';
      if (errs[n]) { inp.setAttribute('aria-invalid', 'true'); inp.setAttribute('aria-describedby', 'e-' + n); } else inp.removeAttribute('aria-invalid');
    });
    var first = Object.keys(errs)[0];
    if (first) { form[first].focus(); return false; }
    return true;
  }

  function payDetail() {
    var box = $('[data-pay-detail]'); if (!box) return;
    box.innerHTML = {
      card: '<strong>Demo card</strong> — card number, expiry and security code fields are intentionally omitted. In a live build these would be rendered by a PCI-compliant payment provider (for example in a hosted field), never stored by the website.',
      wallet: '<strong>Demo wallet</strong> — in a live build this button would open the provider\'s secure sheet. Here it simply records the method on your demo receipt.',
      invoice: '<strong>Demo invoice</strong> — in a live build, an invoice would be emailed after approval. Here, no email is sent.'
    }[data.pay];
  }

  function bind() {
    var form = $('[data-step-form]', root);
    $$('[data-goto]', root).forEach(function (b) { b.addEventListener('click', function () { step = parseInt(b.getAttribute('data-goto'), 10); render(); focusTop(); }); });
    if (step === 1) {
      form.addEventListener('submit', function (ev) {
        ev.preventDefault();
        ['email', 'phone', 'first', 'last', 'address1', 'address2', 'city', 'state', 'zip'].forEach(function (n) { data.info[n] = (form[n].value || '').trim(); });
        save();
        if (validateInfo(form)) { step = 2; render(); focusTop(); }
      });
    } else if (step === 2) {
      form.addEventListener('change', function () { data.ship = form.querySelector('input[name="ship"]:checked').value; save(); var s = $('.summary-box', root); s.outerHTML = summary(); });
      form.addEventListener('submit', function (ev) { ev.preventDefault(); data.gift = form.gift.value.trim(); save(); step = 3; render(); focusTop(); });
    } else if (step === 3) {
      payDetail();
      form.addEventListener('change', function (ev) { if (ev.target.name === 'pay') { data.pay = ev.target.value; save(); payDetail(); } });
      form.addEventListener('submit', function (ev) {
        ev.preventDefault();
        var err = $('[data-agree-error]');
        if (!form.agree.checked) { err.textContent = 'Please confirm you understand this is a simulated order.'; form.agree.focus(); return; }
        err.textContent = '';
        var btn = $('[data-place]'); btn.disabled = true; btn.textContent = 'Processing demonstration…';
        setTimeout(placeOrder, 900);
      });
    }
  }

  function orderNumber() {
    var d = new Date(), pad = function (n) { return (n < 10 ? '0' : '') + n; };
    var rand = '';
    var chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
    var buf = (window.crypto && crypto.getRandomValues) ? crypto.getRandomValues(new Uint8Array(4)) : [1, 2, 3, 4].map(function () { return Math.floor(Math.random() * 256); });
    for (var i = 0; i < 4; i++) rand += chars[buf[i] % chars.length];
    return 'ELV-' + String(d.getFullYear()).slice(2) + pad(d.getMonth() + 1) + pad(d.getDate()) + '-' + rand;
  }

  function placeOrder() {
    var t = E.cart.totals(data.ship);
    var order = {
      number: orderNumber(), date: new Date().toISOString(), info: data.info, ship: data.ship, gift: data.gift, pay: data.pay,
      lines: E.cart.items().map(function (l) { var p = E.byId[l.id]; return { id: l.id, name: p.name, color: l.color, size: l.size, qty: l.qty, price: p.price }; }),
      totals: t, demo: true
    };
    E.store.set('lastOrder', order);
    E.cart.clear();
    data.gift = ''; save();
    confirmation(order);
  }

  function confirmation(o) {
    setSteps(4);
    var d = new Date(o.date);
    var i = o.info;
    root.innerHTML = '<div class="confirmation"><div class="center"><span class="eyebrow">Demonstration order confirmed</span><h2 class="display">Thank you, ' + esc(i.first) + '.</h2>' +
      '<p class="lede" style="margin-inline:auto">Your simulated order <strong>' + esc(o.number) + '</strong> has been recorded in this browser. No payment was taken and nothing will be shipped.</p>' +
      '<div class="hero__ctas no-print" style="justify-content:center"><button class="btn" type="button" data-print>Print receipt</button><a class="btn btn--ghost" href="shop.html">Continue shopping</a></div></div>' +
      '<div class="receipt" id="receipt"><div class="receipt-head"><img src="' + E.root + 'assets/brand/elvare-wordmark-black.svg" alt="ÉLVARÉ" width="500" height="100"><div class="receipt-meta">Demonstration receipt<br>Order ' + esc(o.number) + '<br>' + d.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' }) + ' · ' + d.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' }) + '</div></div>' +
      '<div class="receipt-grid"><div><h3 class="label">Customer</h3>' + esc(i.first + ' ' + i.last) + '<br>' + esc(i.email) + (i.phone ? '<br>' + esc(i.phone) : '') + '</div>' +
      '<div><h3 class="label">Ship to</h3>' + esc(i.address1) + (i.address2 ? ', ' + esc(i.address2) : '') + '<br>' + esc(i.city) + ', ' + esc(i.state) + ' ' + esc(i.zip) + '<br>United States</div>' +
      '<div><h3 class="label">Delivery &amp; payment</h3>' + E.SHIPPING[o.ship].label + ' — ' + E.SHIPPING[o.ship].eta + '<br>' + PAY[o.pay].title + ' (no charge)</div></div>' +
      o.lines.map(function (l) { return '<div class="mini-line" style="grid-template-columns:1fr auto"><div><div class="ml-name">' + esc(l.name) + '</div><div class="ml-meta">' + esc(l.color) + ' · Size ' + esc(l.size) + ' · ' + l.qty + ' × ' + money(l.price) + ' · ' + esc(l.id) + '</div></div><span>' + money(l.price * l.qty, true) + '</span></div>'; }).join('') +
      (o.gift ? '<p class="form-note" style="margin-top:1rem">Gift message: “' + esc(o.gift) + '”</p>' : '') +
      '<div style="max-width:360px;margin:1.5rem 0 0 auto">' + E.totalsHTML(o.totals, { progress: false, shipLabel: E.SHIPPING[o.ship].label }) + '</div>' +
      '<span class="receipt-stamp">Demonstration only · Not a real transaction</span>' +
      '<p class="demo-note">ÉLVARÉ is a fictional brand. This receipt was generated in your browser by a Virellion Apex portfolio demonstration and has no commercial value.</p></div></div>';
    $('[data-print]', root).addEventListener('click', function () { window.print(); });
    focusTop();
  }

  function focusTop() {
    var h = $('h1'); window.scrollTo({ top: 0, behavior: 'smooth' });
    var t = root.querySelector('legend, h2'); if (t) { t.setAttribute('tabindex', '-1'); t.focus({ preventScroll: true }); }
  }

  document.addEventListener('elvare:update', function () { if (step < 4 && !root.querySelector('.confirmation')) { var s = $('.summary-box', root); if (s) s.outerHTML = summary(); if (!E.cart.items().length) render(); } });
  render();
})();
