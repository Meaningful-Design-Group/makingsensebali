// sw.js — the sensor bench, offline. Scope is /test/ only, so the site's own sw.js (which answers every navigation
// with "no connection" when offline) never takes this page. The page is one file: cache it, serve it from the cache,
// refresh the cache in the background whenever the network answers. Fonts are cached the first time they load.
const CACHE = 'msb-bench-v1';
const CORE = ['./', './index.html', './manifest.webmanifest'];
self.addEventListener('install', e => { e.waitUntil(caches.open(CACHE).then(c => c.addAll(CORE)).then(() => self.skipWaiting())); });
self.addEventListener('activate', e => { e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k.startsWith('msb-bench-') && k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim())); });
self.addEventListener('fetch', e => {
  const u = new URL(e.request.url);
  if (e.request.method !== 'GET') return;
  const font = /fonts\.(googleapis|gstatic)\.com$/.test(u.hostname);
  const mine = u.origin === location.origin && u.pathname.startsWith(new URL('./', self.registration.scope).pathname);
  if (!font && !mine) return;
  e.respondWith(caches.open(CACHE).then(async c => {
    const key = e.request.mode === 'navigate' ? './index.html' : e.request;
    const hit = await c.match(key, {ignoreSearch: e.request.mode === 'navigate'});
    const net = fetch(e.request).then(r => { if (r && (r.ok || r.type === 'opaque')) c.put(e.request.mode === 'navigate' ? './index.html' : e.request, r.clone()); return r; }).catch(() => null);
    return hit || (await net) || new Response('offline', {status: 503});
  }));
});
