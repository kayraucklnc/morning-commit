// The Morning Commit service worker.
// - Shell is precached on install.
// - Pages (navigations) and editions.json: network-first, fall back to cache (so new editions appear).
// - Same-origin images/CSS/JS and Google Fonts: stale-while-revalidate (visited editions work offline).
const VERSION = 'mc-1794935286';
const SHELL = ['./', './archive/', './editions.json', './assets/style.css', './assets/app.js',
  './manifest.webmanifest', './assets/icons/icon-192.png', './assets/icons/icon-512.png'];
const PAGES = 'mc-pages', ASSETS = 'mc-assets';

self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(PAGES).then((c) => c.addAll(SHELL.map((u) => new Request(u, { cache: 'reload' })))).then(() => self.skipWaiting()));
});
self.addEventListener('activate', (e) => {
  e.waitUntil(caches.keys().then((ks) => Promise.all(ks.filter((k) => ![PAGES, ASSETS].includes(k)).map((k) => caches.delete(k))))
    .then(() => self.clients.claim()));
});

async function networkFirst(req) {
  const cache = await caches.open(PAGES);
  try {
    const res = await fetch(req, { cache: 'no-cache' });
    if (res.ok) cache.put(req, res.clone());
    return res;
  } catch (err) {
    const hit = await cache.match(req, { ignoreSearch: true });
    if (hit) return hit;
    if (req.mode === 'navigate') return (await cache.match('./')) || Response.error();
    throw err;
  }
}
async function staleWhileRevalidate(req, event) {
  const cache = await caches.open(ASSETS);
  const hit = await cache.match(req);
  const net = fetch(req).then((res) => { if (res.ok || res.type === 'opaque') cache.put(req, res.clone()); return res; }).catch(() => hit);
  if (hit) { event.waitUntil(net); return hit; }
  return net;
}

self.addEventListener('fetch', (event) => {
  const req = event.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  const scope = new URL(self.registration.scope);
  const sameSite = url.origin === scope.origin && url.pathname.startsWith(scope.pathname);
  const fonts = url.hostname === 'fonts.googleapis.com' || url.hostname === 'fonts.gstatic.com';
  if (sameSite && (req.mode === 'navigate' || url.pathname.endsWith('/editions.json') || url.pathname.endsWith('.html') || url.pathname.endsWith('/'))) {
    event.respondWith(networkFirst(req));
  } else if (sameSite || fonts) {
    event.respondWith(staleWhileRevalidate(req, event));
  }
});
