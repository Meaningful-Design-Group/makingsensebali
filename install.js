// install.js — Making Sense Bali · "Add to home screen"
//
// The link to this site mostly travels through WhatsApp, and a link in a chat
// is a link that gets lost. So the page offers, in one visible place, to live
// on the phone's home screen like an app: no app store, nothing to download,
// and the location still never leaves the phone.
//
// What each phone can actually do, because they differ:
//   Android Chrome / Edge / Samsung: the browser's own install prompt
//     (beforeinstallprompt). One tap on our button opens it.
//   iPhone / iPad (Safari): no prompt exists, on any iOS browser. The button
//     opens two lines of instructions: Share, then "Add to Home Screen".
//   Inside WhatsApp, Instagram or Facebook: in-app browsers cannot install
//     anything. The button says to open the page in the real browser first.
//     On Android these are usually Chrome Custom Tabs, which send Chrome's
//     own user agent and cannot be told apart from Chrome by it. The one tell
//     is document.referrer ("android-app://com.whatsapp"), when the app sends
//     it; the Android instructions cover the case where it does not.
//   Chrome only offers its install prompt after the reader has interacted
//     with the page for a while (roughly 30 seconds and a tap, Chrome's own
//     engagement rule). Somebody who taps our button in the first seconds
//     gets the menu instructions, and if Chrome's prompt becomes available
//     while those are open, an "Install now" button appears in the sheet.
//   Already installed (running standalone): the button never appears.
//
// Any element with [data-install] is a button this file shows and wires up.
(function(){
'use strict';

var ua = navigator.userAgent || '';
var isIOS = /iPhone|iPad|iPod/.test(ua) || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
var isInApp = /FBAN|FBAV|FB_IAB|Instagram|Line\/|WhatsApp|; wv\)/.test(ua);
var isAndroid = /Android/.test(ua);
var isMobile = isIOS || isAndroid || /Mobi/.test(ua);
var fromApp = /^android-app:\/\//.test(document.referrer || '');
var standalone = (window.matchMedia && matchMedia('(display-mode: standalone)').matches) || navigator.standalone === true;
var deferred = null;

function t(k){ return window.SCB_I18N ? window.SCB_I18N.t(k) : k; }
function buttons(){ return document.querySelectorAll('[data-install]'); }
function show(on){ buttons().forEach(function(b){ b.hidden = !on; }); }

// Registered on every page so the site is installable from wherever the
// reader happens to be. The worker caches nothing (see sw.js).
if ('serviceWorker' in navigator){
  addEventListener('load', function(){
    navigator.serviceWorker.register('sw.js').catch(function(e){ console.warn('[install] service worker not registered:', e); });
  });
}

var sheet = null;
function closeSheet(){ if (sheet){ sheet.remove(); sheet = null; } }
function openSheet(){
  closeSheet();
  var how = (isInApp || fromApp) ? (isAndroid ? 'install.inapp_android' : 'install.inapp')
          : isIOS ? 'install.ios' : isAndroid ? 'install.android' : 'install.other';
  sheet = document.createElement('div');
  sheet.className = 'install-sheet';
  sheet.setAttribute('role', 'dialog');
  sheet.setAttribute('aria-modal', 'true');
  sheet.setAttribute('aria-labelledby', 'install-title');
  sheet.innerHTML =
    '<div class="install-card">' +
      '<img src="icon-192.png" alt="" width="48" height="48">' +
      '<h2 id="install-title"></h2>' +
      '<p class="install-why"></p>' +
      '<p class="install-how"></p>' +
      '<button type="button" class="btn btn-fill btn-report install-now" hidden></button>' +
      '<button type="button" class="btn btn-fill install-close"></button>' +
    '</div>';
  sheet.querySelector('h2').textContent = t('install.title');
  sheet.querySelector('.install-why').textContent = t('install.why');
  sheet.querySelector('.install-how').textContent = t(how);
  var now = sheet.querySelector('.install-now');
  now.textContent = t('install.now');
  now.addEventListener('click', function(){ closeSheet(); onClick(); });
  now.hidden = !deferred;
  var close = sheet.querySelector('.install-close');
  close.textContent = t('install.close');
  close.addEventListener('click', closeSheet);
  sheet.addEventListener('click', function(e){ if (e.target === sheet) closeSheet(); });
  document.addEventListener('keydown', function esc(e){
    if (e.key === 'Escape'){ closeSheet(); document.removeEventListener('keydown', esc); }
  });
  document.body.appendChild(sheet);
  close.focus();
}

function onClick(){
  if (deferred){
    var d = deferred; deferred = null;
    d.prompt();
    d.userChoice.then(function(c){ if (c && c.outcome === 'accepted') show(false); }).catch(function(){});
    return;
  }
  openSheet();
}

addEventListener('beforeinstallprompt', function(e){
  e.preventDefault();          // we show our own button instead of the mini-infobar
  deferred = e;
  if (!standalone) show(true);
  // The reader may already be looking at the menu instructions.
  var now = sheet && sheet.querySelector('.install-now');
  if (now){ now.hidden = false; now.focus(); }
});
addEventListener('appinstalled', function(){ deferred = null; show(false); closeSheet(); });

function wire(){
  buttons().forEach(function(b){ b.addEventListener('click', onClick); });
  if (standalone) { show(false); return; }
  // On a phone the button is always there, prompt or not: iOS never fires
  // beforeinstallprompt, and a button that only sometimes exists is one
  // nobody learns to find. On a desktop it appears only if the browser
  // actually offers an install.
  if (isMobile) show(true);
}
if (document.readyState !== 'loading') wire(); else addEventListener('DOMContentLoaded', wire);


// ---------------------------------------------------------------------------
// Diagnostics: open the site with ?debug=install on the phone that will not
// install, and this panel shows what the browser is actually reporting —
// which of the conditions above holds, whether Chrome has offered its
// prompt yet, and the service worker's state — so a screenshot says why.
var firedAt = null, installedAt = null, t0 = Date.now();
addEventListener('beforeinstallprompt', function(){ firedAt = Date.now(); });
addEventListener('appinstalled', function(){ installedAt = Date.now(); });
if (/[?&]debug=install\b/.test(location.search)) {
  addEventListener('load', function(){
    var box = document.createElement('div');
    box.setAttribute('style', 'position:fixed;left:8px;right:8px;bottom:8px;z-index:2000;background:#16171a;color:#f6efe1;' +
      'font:12px/1.5 ui-monospace,Menlo,monospace;padding:12px 14px;border-radius:10px;max-height:60vh;overflow:auto;box-shadow:0 10px 30px rgba(0,0,0,.4)');
    document.body.appendChild(box);
    var manifestStatus = '…', swState = '…';
    var link = document.querySelector('link[rel="manifest"]');
    if (link) fetch(link.href, { cache: 'no-store' }).then(function(r){ manifestStatus = r.status + ' ' + (r.headers.get('content-type') || ''); }).catch(function(e){ manifestStatus = 'error ' + e; });
    else manifestStatus = 'no <link rel=manifest>';
    function sw(){
      if (!('serviceWorker' in navigator)) { swState = 'not supported'; return; }
      navigator.serviceWorker.getRegistration().then(function(r){
        swState = !r ? 'not registered' : (r.active ? 'active' : r.installing ? 'installing' : r.waiting ? 'waiting' : 'registered') +
                  (navigator.serviceWorker.controller ? ', controlling' : ', not controlling yet');
      });
    }
    function row(k, v){ return '<div><span style="color:#9a948a">' + k + '</span> ' + String(v).replace(/</g,'&lt;') + '</div>'; }
    function paint(){
      sw();
      var secs = Math.round((Date.now() - t0) / 1000);
      box.innerHTML = '<div style="color:#e9a05a;margin-bottom:6px">install diagnostics · screenshot this</div>' +
        row('ua', ua) +
        row('android / ios / in-app / from-app', [isAndroid, isIOS, isInApp, fromApp].join(' / ')) +
        row('referrer', document.referrer || '(none)') +
        row('standalone', standalone) +
        row('secure context', window.isSecureContext) +
        row('manifest', manifestStatus) +
        row('service worker', swState) +
        row('seconds on page', secs + (secs < 30 ? '  (Chrome wants ~30 s and a tap)' : '')) +
        row('install prompt offered', firedAt ? 'YES, after ' + Math.round((firedAt - t0)/1000) + ' s' : 'not yet') +
        row('prompt held for our button', deferred ? 'yes' : 'no') +
        row('installed event', installedAt ? 'yes' : 'no') +
        '<button type="button" id="dbg-try" style="margin-top:8px;padding:8px 12px;border-radius:6px;border:0;background:#b8472b;color:#fff">Try install now</button>';
      var b = document.getElementById('dbg-try'); if (b) b.onclick = onClick;
    }
    paint(); setInterval(paint, 1000);
  });
}

window.SCB_INSTALL = { open: onClick, standalone: standalone };
})();
