/* ÉLVARÉ — wishlist page. */
(function () {
  'use strict';
  var E = window.Elvare; if (!E) return;
  var grid = E.$('[data-wishlist-grid]'), empty = E.$('[data-wishlist-empty]');
  if (!grid) return;
  function render() {
    var ids = E.wish.ids();
    grid.innerHTML = ids.map(function (id) { return E.cardHTML(E.byId[id]); }).join('');
    grid.hidden = !ids.length; empty.hidden = !!ids.length;
  }
  document.addEventListener('elvare:update', render);
  render();
})();
