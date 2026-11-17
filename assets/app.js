// The Morning Commit: registers the service worker (offline reading) from any page depth.
(function () {
  if (!('serviceWorker' in navigator)) return;
  var me = document.currentScript || document.querySelector('script[src$="assets/app.js"]');
  var root = new URL('../', me.src);            // site root, e.g. /morning-commit/
  window.addEventListener('load', function () {
    navigator.serviceWorker.register(new URL('sw.js', root).href, { scope: root.pathname }).catch(function () {});
  });
})();
