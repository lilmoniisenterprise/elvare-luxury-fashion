/* ÉLVARÉ — contact form validation (demonstration, nothing is transmitted) and privacy tools. */
(function () {
  'use strict';
  var E = window.Elvare; if (!E) return;
  var form = E.$('[data-contact-form]');
  if (form) {
    var msg = E.$('[data-contact-msg]');
    var setErr = function (input, text) {
      var f = input.closest('.field'); if (!f) return;
      f.classList.toggle('has-error', !!text);
      f.querySelector('.field-error').textContent = text || '';
      if (text) input.setAttribute('aria-invalid', 'true'); else input.removeAttribute('aria-invalid');
    };
    var check = function (input) {
      var v = input.value.trim();
      if (input.required && !v) return 'This field is required.';
      if (input.type === 'email' && v && !E.EMAIL_RE.test(v)) return 'Please enter a valid email address.';
      if (input.name === 'message' && v.length < 20) return 'Please write at least 20 characters so we can help.';
      if (input.name === 'order' && v && !/^ELV-[A-Z0-9-]{4,}$/i.test(v)) return 'Order numbers look like ELV-261106-ABCD.';
      return '';
    };
    E.$$('.input', form).forEach(function (i) {
      i.addEventListener('blur', function () { if (i.value) setErr(i, check(i)); });
      i.addEventListener('input', function () { if (i.closest('.field').classList.contains('has-error')) setErr(i, check(i)); });
    });
    form.addEventListener('submit', function (ev) {
      ev.preventDefault();
      var first = null;
      E.$$('.input', form).forEach(function (i) { var er = check(i); setErr(i, er); if (er && !first) first = i; });
      var cErr = E.$('[data-consent-error]');
      cErr.textContent = form.consent.checked ? '' : 'Please confirm you understand this is a demonstration form.';
      if (!form.consent.checked && !first) first = form.consent;
      msg.className = 'form-msg';
      if (first) { first.focus(); msg.textContent = 'Please review the highlighted fields.'; msg.classList.add('is-error'); return; }
      var ref = 'MSG-' + Date.now().toString(36).toUpperCase().slice(-6);
      msg.textContent = 'Thank you, ' + form.first.value.trim() + '. Your message passed validation (reference ' + ref + '). As this is a demonstration website, it has not been sent to anyone.';
      msg.classList.add('is-success');
      form.reset();
    });
  }
  var clear = E.$('[data-clear-demo]');
  if (clear) clear.addEventListener('click', function () {
    ['cart', 'wishlist', 'recent', 'newsletter', 'lastOrder', 'checkout'].forEach(E.store.remove);
    document.dispatchEvent(new CustomEvent('elvare:update'));
    E.$('[data-clear-msg]').textContent = 'All demonstration data has been cleared from this browser.';
  });
})();
