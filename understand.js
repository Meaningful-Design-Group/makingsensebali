// understand.js — Making Sense Bali · "what's going on with this reading?"
//
// Rules, not a model. Every conclusion here is arithmetic a reader can check
// against the map: whether the whole island rose together, whether your area
// stands out from the ring around it, whether this spot usually reads like
// this at this hour, and whether one sensor disagrees with all its neighbours.
//
// Why not ask a language model to explain the number: the campaign's rules are
// "no fake numbers" and "do not blame a source the data cannot name". A model
// asked "why is it high?" will produce a confident cause. These rules can only
// say what the data shows — and they say it the same way every time.
//
// Pure functions. No DOM, no fetch. Runs in the browser (window.SCB_UNDERSTAND)
// and in node for tests (module.exports).
(function(root){
'use strict';

var WHO_24H = 15;          // µg/m³, WHO 2021 24-hour guideline
var LOCAL_KM = 1;          // "your area" — the banjar scale on the page
var LOCAL_KM_WIDE = 3;     // fallback when the banjar is empty — the village scale
var RING_KM = 10;          // the ring you are compared against
var RING_KM_WIDE = 15;
var WITA_OFFSET_H = 8;     // Bali is UTC+8, no DST

function km(a, b, c, d){
  var R = 6371, r = Math.PI/180, dLa = (c-a)*r, dLo = (d-b)*r;
  var s = Math.sin(dLa/2)*Math.sin(dLa/2) + Math.cos(a*r)*Math.cos(c*r)*Math.sin(dLo/2)*Math.sin(dLo/2);
  return 2*R*Math.asin(Math.min(1, Math.sqrt(s)));
}
function median(v){
  if (!v.length) return null;
  var x = v.slice().sort(function(p,q){ return p-q; });
  var m = Math.floor(x.length/2);
  return x.length % 2 ? x[m] : (x[m-1] + x[m]) / 2;
}
function r1(x){ return x == null ? null : Math.round(x*10)/10; }
function witaHour(ms){ return new Date(ms + WITA_OFFSET_H*3600000).getUTCHours(); }
function witaDay(ms){ return Math.floor((ms + WITA_OFFSET_H*3600000) / 86400000); }

// Dawn and dusk are the burning windows the community documented. Traffic
// peaks overlap both, which is why the copy never claims to know which it is.
function windowOf(hour){
  if (hour >= 5 && hour < 10) return 'dawn';
  if (hour >= 17 && hour < 23) return 'dusk';
  return null;
}

// The same gate Bali Air Dispatch uses for every island-wide figure
// (isAmbient): fresh, and not indoor, faulty or community-contributed. near.js
// sets .ambient; objects without the field (tests, older data) count if fresh.
function live(sensors){
  return (sensors || []).filter(function(s){
    return s && s.fresh && s.ambient !== false && typeof s.pm25 === 'number' && typeof s.lat === 'number';
  });
}

// One sensor far from every neighbour — high OR low — with at least two
// neighbours to disagree with. A lone sensor cannot be called suspect: with
// nothing to compare, "unusual" and "right" look identical.
function findSuspect(here, sensors){
  var near = here
    ? sensors.map(function(s){ return { s:s, d:km(here.lat, here.lng, s.lat, s.lng) }; })
             .filter(function(o){ return o.d <= LOCAL_KM_WIDE; })
             .sort(function(a,b){ return a.d - b.d; })
    : [];
  for (var i = 0; i < near.length; i++){
    var s = near[i].s;
    var nb = sensors.filter(function(o){
      return o !== s && km(s.lat, s.lng, o.lat, o.lng) <= 3;
    }).map(function(o){ return o.pm25; });
    if (nb.length < 2) continue;
    var m = median(nb);
    var high = s.pm25 >= 3*m && s.pm25 - m >= 20;
    var low  = m >= 15 && s.pm25 <= m/3 && m - s.pm25 >= 15;
    if (high || low){
      return { id: s.id, name: s.name, value: r1(s.pm25), neighbours: r1(m),
               n: nb.length, direction: high ? 'high' : 'low', km: r1(near[i].d) };
    }
  }
  return null;
}

// "Is this usual for this hour, here?" — the latest hourly value against the
// same WITA hour on earlier days, from one station's own archive.
function hourCompare(series, now){
  if (!series || series.length < 24) return null;
  var last = series[series.length-1];
  if (now - last.t > 3*3600000) return null;           // archive too far behind
  var h = witaHour(last.t), today = witaDay(last.t);
  var same = series.filter(function(p){
    return witaHour(p.t) === h && witaDay(p.t) !== today;
  }).map(function(p){ return p.pm25; });
  if (same.length < 3) return null;
  var usual = median(same), cur = last.pm25, verdict = 'usual';
  if (cur >= 1.6*usual && cur - usual >= 10) verdict = 'above';
  else if (cur <= usual/1.6 && usual - cur >= 8) verdict = 'below';
  else if (Math.abs(cur - usual) > Math.max(8, 0.35*usual)) verdict = cur > usual ? 'above' : 'below';
  return { verdict: verdict, hour: h, usual: r1(usual), now: r1(cur), days: same.length };
}

// Main entry.
//   opts.here     {lat,lng} or null
//   opts.sensors  stations from near.js (fresh, pm25, lat, lng, name, id)
//   opts.hourly   hourly series [{t,pm25}] for the nearest live station, or null
//   opts.hourlyName  that station's name
//   opts.now      ms (defaults to Date.now())
function diagnose(opts){
  var now = opts.now || Date.now();
  var all = live(opts.sensors);
  var out = { kind: 'nodata', vars: {}, why: [], suspect: null,
              window: windowOf(witaHour(now)), value: null, who: WHO_24H };
  if (!all.length) return out;

  var islandMed = median(all.map(function(s){ return s.pm25; }));
  var above = all.filter(function(s){ return s.pm25 > WHO_24H; }).length;
  var share = above / all.length;
  out.vars.islandMed = r1(islandMed);
  out.vars.above = above;
  out.vars.total = all.length;

  // Your area, and the ring around it.
  var here = opts.here, local = [], ring = [], rLocal = LOCAL_KM, rRing = RING_KM;
  if (here){
    var withD = all.map(function(s){ return { s:s, d:km(here.lat, here.lng, s.lat, s.lng) }; });
    local = withD.filter(function(o){ return o.d <= LOCAL_KM; });
    if (!local.length){
      rLocal = LOCAL_KM_WIDE; rRing = RING_KM_WIDE;
      local = withD.filter(function(o){ return o.d <= LOCAL_KM_WIDE; });
    }
    ring = withD.filter(function(o){ return o.d > rLocal && o.d <= rRing; });
  }
  var localMed = local.length ? median(local.map(function(o){ return o.s.pm25; })) : null;
  var ringMed  = ring.length  ? median(ring.map(function(o){ return o.s.pm25; }))  : null;
  // With nothing live near the reader, say so rather than quietly passing the
  // island median off as their air.
  var value = localMed != null ? localMed : (here && ringMed != null ? ringMed : islandMed);
  var nearestKm = null;
  if (here){ all.forEach(function(s){ var d = km(here.lat, here.lng, s.lat, s.lng); if (nearestKm == null || d < nearestKm) nearestKm = d; }); }
  out.vars.nearestKm = r1(nearestKm);
  out.value = r1(value);
  out.vars.localMed = r1(localMed); out.vars.ringMed = r1(ringMed);
  out.vars.rLocal = rLocal; out.vars.rRing = rRing;
  out.vars.nLocal = local.length; out.vars.nRing = ring.length;

  out.suspect = findSuspect(here, all);
  var hc = here ? hourCompare(opts.hourly, now) : null;
  out.hour = hc;
  if (hc){ out.vars.hour = hc.hour; out.vars.usual = hc.usual; out.vars.hourNow = hc.now;
           out.vars.station = opts.hourlyName || ''; out.vars.days = hc.days; }

  var regional = all.length >= 10 && islandMed >= 25 && share >= 0.6;
  var localSrc = localMed != null && ringMed != null && localMed >= 25 &&
                 localMed >= 1.8*ringMed && localMed - ringMed >= 12;

  if (regional && localMed != null && localMed <= 0.6*islandMed){
    // Most of Bali is smoky and your area is clearly doing better. Telling a
    // Jimbaran reader at 17 that "it's island-wide, not just you" is true of
    // Bali and wrong about them.
    out.kind = 'regional_lower';
    out.why.push('regional');
    out.why.push(ringMed != null ? 'compare' : 'compare_clean');
  } else if (regional){
    out.kind = 'regional';
    out.why.push('regional');
    if (localSrc) out.why.push('local');
  } else if (localSrc){
    out.kind = 'local';
    out.why.push('local');
  } else if (value > WHO_24H && hc && hc.verdict === 'above'){
    out.kind = 'above_usual';
    out.why.push('hour');
  } else if (value > WHO_24H && hc && hc.verdict === 'usual'){
    out.kind = 'usual_high';
    out.why.push('hour');
  } else if (value > WHO_24H && hc){
    // Above the line but below this spot's own usual for the hour: still
    // elevated, and the bullet says it is cleaner than usual.
    out.kind = 'elevated';
    out.why.push('hour');
  } else if (value > WHO_24H){
    out.kind = 'elevated';
    if (here && localMed != null && ringMed != null) out.why.push('compare');
    else out.why.push('island');
  } else if (value > 12){
    // Under the WHO day line but over the page's own "good" band. Calling
    // this "clean, open up" put it in contradiction with the hero ("some
    // haze") and the advice ("close windows").
    out.kind = 'near_line';
    if (hc && hc.verdict === 'below') out.why.push('hour');
    else if (here && localMed != null) out.why.push('compare_clean');
    else out.why.push('island');
  } else {
    out.kind = 'clean';
    if (hc && hc.verdict === 'below') out.why.push('hour');
    else if (here && localMed != null) out.why.push('compare_clean');
    else out.why.push('island');
  }
  if (here && localMed == null) out.why.unshift(ringMed != null ? 'nolocal' : 'nolocal_island');
  if (value > WHO_24H && out.window) out.why.push('window');
  return out;
}


// ---------------------------------------------------------------------------
// Resident reports near you.
//
// Public reports are placed at the centroid of their desa and dated to the
// day — deliberately, so no report can point at a house or a routine. That
// sets what this can honestly say: "reported in Jimbaran this week", never
// "200 m from you", and nothing at street scale at all. The radius is the
// larger of the selected scale and REPORT_MIN_KM, because a desa centroid can
// sit a few km from the lane the smoke was actually in.
var REPORT_MIN_KM = 5;
var REPORT_CATS = { burning: 1 };

function nearbyReports(here, reports, now, scaleKm){
  now = now || Date.now();
  var radius = scaleKm === Infinity ? Infinity : Math.max(scaleKm || 0, REPORT_MIN_KM);
  var rel = (reports || []).filter(function(r){
    if (!r || !REPORT_CATS[r.category]) return false;
    if (radius === Infinity) return true;
    if (!here || typeof r.lat !== 'number' || typeof r.lng !== 'number') return false;
    return km(here.lat, here.lng, r.lat, r.lng) <= radius;
  }).map(function(r){ return { r: r, t: Date.parse(r.submittedAt) }; })
    .filter(function(o){ return isFinite(o.t) && o.t <= now + 86400000; })
    .sort(function(a,b){ return b.t - a.t; });
  var week = rel.filter(function(o){ return now - o.t <= 7*86400000; });
  var places = {};
  week.forEach(function(o){ var k = o.r.locality || ''; if (k) places[k] = (places[k]||0) + 1; });
  var top = Object.keys(places).sort(function(a,b){ return places[b]-places[a]; }).slice(0,3);
  return {
    week: week.length,
    places: top,
    radius: radius,
    // When nothing came in this week, the most recent one is still worth a
    // line — dated, so it cannot be mistaken for now.
    last: rel.length ? { at: rel[0].r.submittedAt, locality: rel[0].r.locality || '',
                          days: Math.floor((now - rel[0].t) / 86400000) } : null
  };
}

// ---------------------------------------------------------------------------
// Patterns published by the insight agent (data/patterns.json). The agent
// works on the full-resolution private data on the node and publishes only
// coarsened conclusions — area, time window, counts. See docs/patterns.md.
function nearbyPatterns(here, doc, scaleKm){
  var list = (doc && Array.isArray(doc.patterns)) ? doc.patterns : [];
  var radius = scaleKm === Infinity ? Infinity : Math.max(scaleKm || 0, REPORT_MIN_KM);
  return list.filter(function(p){
    if (!p || !p.centroid) return false;
    if (radius === Infinity) return true;
    if (!here) return false;
    return km(here.lat, here.lng, p.centroid.lat, p.centroid.lng) <= radius;
  }).map(function(p){
    return here ? Object.assign({ km: r1(km(here.lat, here.lng, p.centroid.lat, p.centroid.lng)) }, p) : p;
  }).sort(function(a,b){ return (a.km||0) - (b.km||0); });
}

// Nearest live sensor, for the coverage-gap line: "no sensor within 1 km (the banjar) of
// you — you are exactly where one is needed".
function coverage(here, sensors){
  var l = live(sensors);
  if (!here || !l.length) return null;
  var best = null;
  l.forEach(function(s){ var d = km(here.lat, here.lng, s.lat, s.lng); if (!best || d < best.km) best = { km: d, s: s }; });
  // The gap is judged at banjar scale (1 km): that is the unit a resident can
  // organise, and a sensor there is what makes a banjar conversation possible.
  var within1 = l.filter(function(s){ return km(here.lat, here.lng, s.lat, s.lng) <= 1; }).length;
  return { nearestKm: r1(best.km), nearest: best.s, within1: within1, gap: within1 === 0 };
}

var API = { diagnose: diagnose, nearbyReports: nearbyReports, nearbyPatterns: nearbyPatterns,
            coverage: coverage, hourCompare: hourCompare, findSuspect: findSuspect,
            windowOf: windowOf, WHO_24H: WHO_24H, _median: median };
if (typeof module !== 'undefined' && module.exports) module.exports = API;
if (root) root.SCB_UNDERSTAND = API;
})(typeof window !== 'undefined' ? window : null);
