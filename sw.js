// sw.js — Making Sense Bali
//
// This worker exists so that phones treat the site as an installable app
// ("Add to home screen" / "Install app"). Chrome only offers that for a page
// whose service worker actually handles requests.
//
// It CACHES NOTHING, on purpose. This site has already been bitten by a new
// page meeting an old script (see the ?v= note in index.html), and a caching
// worker is the most reliable way to make that permanent for somebody's
// phone. So every request goes to the network exactly as if there were no
// worker at all. The one thing it adds: when the phone is offline, opening
// the app shows a short page saying so, instead of the browser's error.
var OFFLINE = '<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">' +
  '<title>Making Sense Bali · offline</title>' +
  '<body style="margin:0;font-family:system-ui,sans-serif;background:#f6efe1;color:#16171a;display:flex;min-height:100vh;align-items:center;justify-content:center;padding:24px;text-align:center">' +
  '<div><p style="font-size:13px;letter-spacing:.14em;text-transform:uppercase;color:#3f8a5b">Making Sense Bali</p>' +
  '<h1 style="font-weight:400;font-size:26px;line-height:1.25;margin:12px 0">No connection right now.</h1>' +
  '<p style="line-height:1.6;color:#3a3a3e">The air readings are live, so they need the network. Try again when you are back online.<br>' +
  'Tidak ada koneksi. Data udara bersifat langsung, coba lagi saat Anda kembali online.</p>' +
  '<p><a href="./" style="color:#1e5959">Try again · Coba lagi</a></p></div></body>';

self.addEventListener('install', function(){ self.skipWaiting(); });
self.addEventListener('activate', function(e){ e.waitUntil(self.clients.claim()); });
self.addEventListener('fetch', function(e){
  // Scripts, data files and the Bali Air Dispatch API are never touched.
  if (e.request.mode !== 'navigate') return;
  e.respondWith(fetch(e.request).catch(function(){
    return new Response(OFFLINE, { headers: { 'Content-Type': 'text/html; charset=utf-8' } });
  }));
});
