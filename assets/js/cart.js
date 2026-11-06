/* ÉLVARÉ — full shopping bag page. */
(function () {
  'use strict';
  var E = window.Elvare; if (!E) return;
  var linesBox = E.$('[data-cart-page-lines]'), sumBox = E.$('[data-cart-page-summary]');
  if (!linesBox) return;
  function render() {
    var items = E.cart.items();
    if (!items.length) {
      linesBox.innerHTML = '<div class="empty-state"><h2>Your bag is empty</h2><p>Discover the pieces of the season and add your favourites here.</p><div class="hero__ctas" style="justify-content:center"><a class="btn" href="women.html">Shop Women</a><a class="btn btn--ghost" href="men.html">Shop Men</a></div></div>';
      sumBox.innerHTML = '<p class="form-note">Add a piece to see your order summary.</p>';
      return;
    }
    linesBox.innerHTML = '<p class="form-note" style="margin:0 0 .5rem">' + E.cart.count() + ' item' + (E.cart.count() === 1 ? '' : 's') + '</p>' + items.map(function (l) { return E.lineHTML(l); }).join('') +
      '<p style="margin-top:1.5rem"><a class="link-arrow" href="shop.html">Continue shopping</a></p>';
    sumBox.innerHTML = E.totalsHTML(E.cart.totals()) +
      '<a class="btn btn--block" style="margin-top:1.25rem" href="checkout.html">Proceed to checkout</a>' +
      '<p class="demo-note">Shipping method is chosen at checkout. Tax is shown at a flat demonstration rate. This is a simulated store — no payment is taken.</p>';
  }
  document.addEventListener('elvare:update', render);
  render();
})();
