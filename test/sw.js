// sw.js: the bench moved to planetai.fab.city/sensors/ (19 Oct 2026). A browser that kept the old bench offline
// fetches this file on its next visit; it clears the old cache, removes itself and reloads the page, which is now a
// redirect. Nothing is cached here any more.
self.addEventListener('install', () => self.skipWaiting());
self.addEventListener('activate', e => e.waitUntil((async () => {
  const ks = await caches.keys();
  await Promise.all(ks.filter(k => k.startsWith('msb-bench-')).map(k => caches.delete(k)));
  await self.registration.unregister();
  for (const c of await self.clients.matchAll({type: 'window'})) c.navigate(c.url);
})()));
