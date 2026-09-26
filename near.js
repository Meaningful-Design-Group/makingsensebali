// near.js — Making Sense Bali · "what is near me", by representativeness scale
//
// WHY THIS EXISTS
// ---------------
// The home page used to answer "how is the air where I am?" with a flat 3 km
// radius and an average. That is the wrong question answered confidently.
//
// A sensor reading represents an area, and how big that area is depends on the
// scale of the sources around it. Bali's dominant PM2.5 source is open burning:
// intermittent, and a point. A sensor 2 km away cannot see your neighbour's
// fire, and averaging it into a single number tells you the opposite of the
// truth at the moment you most want to know.
//
// So we do not average across a radius. We sort what exists into the standard
// monitoring scales and say, for each one, what it can and cannot tell you.
//
// Scales follow the EPA siting taxonomy (40 CFR 58 App. D). MIDDLE is included
// deliberately: with only MICRO, NEIGHBOURHOOD and URBAN there is a hole
// between 100 m and 500 m, and real sensors fall in it — Denpasar centre's
// nearest station is 190 m away.
//
// PRIVACY
// -------
// The coordinate never leaves the device. We fetch EVERY station — the request
// carries no position and is identical for every visitor — and do the distance
// arithmetic locally. That is why full precision is safe here, and why the
// micro band is possible at all: rounding the position to ~1 km first, as the
// old code did, put a 1 km floor under every distance it could report.
//
// DATA
// ----
// Bali Air Dispatch, https://baliairdispatch.com/api  (CORS: *, no key).
//   GET /api/v1/latest    most recent reading held for each station
//
// ONE request, deliberately. /latest already carries latitude, longitude, name,
// source and both provenance flags, so /stations adds nothing this page needs
// except days_of_data — which was only ever a dedupe tie-break, and recency
// breaks ties better anyway.
//
// Measured from Bali, 2026-09-24, brotli on the wire:
//   own data/sensors.json   2.7 KB   TTFB 112 ms   (same origin, Pages CDN)
//   BAD /latest             7.2 KB   TTFB 258 ms
//   BAD /stations           6.4 KB   TTFB 254 ms
// So this is not a heavy dependency — it is seven kilobytes and a quarter
// second. Dropping /stations halves the round trips and saves 6.4 KB, and the
// caller warms this at idle so the button press itself costs nothing.
//
// (An earlier note here claimed the API served no compression. That was wrong:
// Content-Encoding is not readable cross-origin and encodedBodySize is 0
// without Timing-Allow-Origin, so the browser cannot see it. curl can — the
// responses are brotli, 65 KB down to 7.)
//
// Readings originate from independent networks (Nafas, IQAir, PurpleAir,
// AQICN, OpenAQ, AirGradient, Smart Citizen, Airly) and remain subject to
// their terms. Attribute Bali Air Dispatch AND the network in each row.
(function(){
'use strict';

var API = 'https://baliairdispatch.com/api/v1';

// Distinct physical sensors closer than this are the same box reaching us
// through two networks. 105 outdoor records collapse to 70 real locations:
// AirGradient units are relayed by OpenAQ, and several Airly sites also
// publish through Nafas. Counting the records instead of the boxes overstates
// coverage by half.
var DUPLICATE_RADIUS_KM = 0.05;

// A reading older than this is shown, but greyed and excluded from any figure
// we put a number on. Roughly 20 of 105 stations are stale at any moment.
var FRESH_HOURS = 6;

// Networks that republish other networks' boxes rather than running their own.
var RELAYS = { 'OpenAQ': true };

// Four scopes the reader picks between, NESTED rather than disjoint rings.
// Nesting matters: with disjoint bands (<=100 m, 500 m - 2 km, 2-5 km) there is
// a hole between 100 m and 500 m, and real sensors fall in it — Denpasar
// centre's nearest station is 190 m away and would have appeared nowhere.
// Nested, "my street / my banjar / my region / the island" is also how somebody
// actually asks the question, and nothing can be silently dropped.
//
// maxKm is what the scope INCLUDES. The representativeness radius each scope is
// named for is the separate thing the copy explains: a 2 km scope is
// neighbourhood-scale, which the EPA siting taxonomy puts at 500 m - 2 km.
var SCALES = [
  { id:'street',       maxKm:0.1      },
  { id:'neighbourhood',maxKm:2        },
  { id:'regional',     maxKm:5        },
  { id:'island',       maxKm:Infinity }
];

function haversineKm(lat1, lon1, lat2, lon2){
  var R = 6371, r = Math.PI/180;
  var dLat = (lat2-lat1)*r, dLon = (lon2-lon1)*r;
  var a = Math.sin(dLat/2)*Math.sin(dLat/2) +
          Math.cos(lat1*r)*Math.cos(lat2*r)*Math.sin(dLon/2)*Math.sin(dLon/2);
  return 2*R*Math.asin(Math.min(1, Math.sqrt(a)));
}

function usable(s){
  return s && typeof s.latitude === 'number' && typeof s.longitude === 'number'
    && !s.suspected_indoor && !s.suspected_malfunctioning;
}

// Normalise /latest rows into what this page works with.
function toStation(r){
  var ageH = typeof r.age_hours === 'number' ? r.age_hours : null;
  return {
    id: r.station_id,
    name: r.name,
    source: r.source,
    lat: r.latitude,
    lng: r.longitude,
    pm25: typeof r.pm25 === 'number' ? r.pm25 : null,
    pm25Raw: typeof r.pm25_raw === 'number' ? r.pm25_raw : null,
    corrected: !!r.pm25_corrected,
    fromAqi: !!r.pm25_from_aqi,
    observedAt: r.observed_at || null,
    ageHours: ageH,
    fresh: ageH != null && ageH <= FRESH_HOURS,
    sources: [r.source]
  };
}

function normalise(readings){
  return readings.filter(usable).map(toStation);
}

// Stations BAD flags as probably indoor. They never enter a scale median —
// an indoor box describes one room — but a resident may own one and want it
// on their Home tab next to the outdoor air, which is exactly the comparison
// (outside 58, inside 9) that teaches seal-first.
function indoorOnly(readings){
  return readings.filter(function(r){
    return r && typeof r.latitude === 'number' && typeof r.longitude === 'number'
      && r.suspected_indoor && !r.suspected_malfunctioning;
  }).map(function(r){ var s = toStation(r); s.indoor = true; return s; });
}

// Collapse co-located records into one physical sensor. The survivor is the
// one we would rather quote: fresh beats stale, then longest record. The
// networks that were folded in are kept in .sources so the popup can say
// "AirGradient · OpenAQ" rather than silently dropping an attribution we owe.
function dedupe(list){
  var out = [];
  list.forEach(function(s){
    for (var i = 0; i < out.length; i++){
      var o = out[i];
      if (haversineKm(s.lat, s.lng, o.lat, o.lng) <= DUPLICATE_RADIUS_KM){
        if (o.sources.indexOf(s.source) < 0) o.sources.push(s.source);
        // Fresher wins; then the more recent observation. (This used to
        // tie-break on days_of_data, which cost a whole second request.)
        // On a tie, the network's own record beats a relay of it. OpenAQ
        // republishes AirGradient boxes, and on 26 Sep 2026 the two copies of
        // one box read 48 and 112: the native record is the one to quote.
        var sa = s.ageHours == null ? Infinity : s.ageHours;
        var oa = o.ageHours == null ? Infinity : o.ageHours;
        var tie = s.fresh === o.fresh && Math.abs(sa - oa) <= 0.5;
        var better = (s.fresh && !o.fresh) ||
                     (tie && RELAYS[o.source] && !RELAYS[s.source]) ||
                     (!tie && s.fresh === o.fresh && sa < oa);
        if (better){
          var keep = o.sources;
          out[i] = s; out[i].sources = keep;
        }
        return;
      }
    }
    out.push(s);
  });
  return out;
}

var _cache = null, _inflight = null, _fetchedAt = 0;

// force=true drops the cached copy so the page can poll for a new reading.
// Deliberately NOT cache-busted with a query parameter: the API is edge-cached
// at s-maxage=300 and the browser holds it for max-age=60, so a plain fetch
// after a minute costs an edge hit and after five a fresh origin read. Adding
// ?t=<now> would bypass both and push every visitor's poll onto their origin,
// which is a rude way to treat somebody else's free API.
function load(force){
  if (_cache && !force) return Promise.resolve(_cache);
  if (_inflight) return _inflight;
  _inflight = fetch(API + '/latest')
    .then(function(r){ if(!r.ok) throw new Error('latest HTTP '+r.status); return r.json(); })
    .then(function(j){
      var rows = normalise(j.readings || []);
      _cache = {
        sensors: dedupe(rows),
        indoor: indoorOnly(j.readings || []),
        records: rows.length,
        generatedAt: j.generated_at || null
      };
      _fetchedAt = Date.now();
      _inflight = null;
      return _cache;
    }).catch(function(e){
      _inflight = null;
      throw e;
    });
  return _inflight;
}

// Returns one entry per scope, IN ORDER, including empty ones — an empty
// street scope is the most important thing this page can tell somebody in Bali,
// so it is never silently dropped.
function bandsFor(lat, lng, sensors){
  var withD = sensors.map(function(s){
    return { s: s, km: haversineKm(lat, lng, s.lat, s.lng) };
  }).sort(function(a,b){ return a.km - b.km; });

  var bands = SCALES.map(function(sc){
    return {
      id: sc.id, maxKm: sc.maxKm,
      sensors: withD.filter(function(o){ return o.km <= sc.maxKm; })
    };
  });

  return { bands: bands, nearest: withD.length ? withD[0] : null, all: withD };
}

// Only fresh readings carry a number. A band of three sensors where two are
// stale reports one, and says so.
// True median: the average of the middle pair for an even count. It used to
// take the upper middle value, which with two sensors at 10 and 40 put 40 on
// the hero while understand.js (which averages) said 25 underneath it.
function median(sorted){
  if (!sorted.length) return null;
  var m = Math.floor(sorted.length/2);
  return sorted.length % 2 ? sorted[m] : (sorted[m-1] + sorted[m]) / 2;
}

function bandSummary(band){
  var fresh = band.sensors.filter(function(o){ return o.s.fresh && o.s.pm25 != null; });
  if (!fresh.length) return { count: band.sensors.length, freshCount: 0, pm25: null };
  var vals = fresh.map(function(o){ return o.s.pm25; }).sort(function(a,b){ return a-b; });
  return {
    count: band.sensors.length,
    freshCount: fresh.length,
    pm25: median(vals),   // median, not mean: one bad box must not move it
    closest: fresh[0]
  };
}


// Hourly history for one station, for the "is this usual for this hour here?"
// test. Fetched lazily, after first paint and only once somebody is located,
// for at most a couple of stations. Both sides of that comparison come from
// this endpoint, so they share one basis — /latest is humidity-corrected and
// the hourly archive may not be, and mixing the two would invent a peak.
var _hourly = {}, HOURLY_TTL_MS = 30*60*1000;
function hourly(stationId, days){
  days = days || 7;
  var key = stationId + ':' + days, hit = _hourly[key];
  // A tab left open must not compare "now" against an archive frozen at
  // page load; after half an hour the archive is fetched again.
  if (hit && Date.now() - hit.at < HOURLY_TTL_MS) return hit.p;
  var from = new Date(Date.now() - days*86400000).toISOString().slice(0,10);
  var p = fetch(API + '/measurements?station=' + encodeURIComponent(stationId) +
                       '&interval=hourly&from=' + from)
    .then(function(r){ if(!r.ok) throw new Error('measurements HTTP '+r.status); return r.json(); })
    .then(function(j){
      return (j.measurements || []).filter(function(m){ return typeof m.pm25 === 'number'; })
        .map(function(m){ return { t: Date.parse(m.observed_at), pm25: m.pm25 }; })
        .filter(function(m){ return isFinite(m.t); })
        .sort(function(a,b){ return a.t - b.t; });
    })
    .catch(function(e){ delete _hourly[key]; throw e; });
  _hourly[key] = { p: p, at: Date.now() };
  return p;
}

window.SCB_NEAR = {
  API: API,
  SCALES: SCALES,
  FRESH_HOURS: FRESH_HOURS,
  load: load,
  refresh: function(){ return load(true); },
  fetchedAt: function(){ return _fetchedAt; },
  bandsFor: bandsFor,
  bandSummary: bandSummary,
  distanceKm: haversineKm,
  islandMedian: function(sensors){
    var v = sensors.filter(function(s){ return s.fresh && s.pm25 != null; })
                   .map(function(s){ return s.pm25; }).sort(function(a,b){ return a-b; });
    return median(v);
  },
  _dedupe: dedupe,
  hourly: hourly,
  _normalise: normalise,
  _indoorOnly: indoorOnly
};

})();
