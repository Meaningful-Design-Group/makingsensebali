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
// Bali Air Dispatch, https://baliairdispatch.com  (CORS: *, no key).
//   GET /api/live          the live station set the BAD homepage itself reads
//   GET /api/v1/stations   station registry, carrying the indoor / faulty flags
//   GET /api/v1/measurements  hourly archive, fetched lazily (see hourly())
//
// WHY /api/live AND NOT /api/v1/latest (changed 26 Sep 2026)
// The page used to read /api/v1/latest and apply its own filter: drop the two
// provenance flags, merge records within 50 m, call anything older than 6 h
// stale. Bali Air Dispatch publishes its headline figures from a different
// set: /api/live, merged within 300 m on their side, stale by each network's
// own freshness limit, and then filtered by one predicate (isAmbient on their
// homepage): not stale, not indoor, not faulty, not community-contributed.
// The two sets disagreed — 69 boxes against their 57 live sensors, and a
// median of 19.3 against their 20.1 — and a visitor who opened both sites
// saw two numbers for the same island. Reading the same endpoint and
// applying the same predicate reproduces their 57 / 20.1 / worst exactly.
//
// The indoor and faulty lists come from /api/v1/stations (suspected_indoor,
// suspected_malfunctioning), which BAD documents as mirroring the lists on
// their homepage. That file changes on a scale of weeks, so it is fetched
// once per page view, in parallel, and a mirrored copy below is used if it
// cannot be reached — so a hiccup there can never let an indoor box back
// into the median.

// Readings originate from independent networks (Nafas, IQAir, PurpleAir,
// AQICN, OpenAQ, AirGradient, Smart Citizen, Airly) and remain subject to
// their terms. Attribute Bali Air Dispatch AND the network in each row.
(function(){
'use strict';

var API  = 'https://baliairdispatch.com/api/v1';
var LIVE = 'https://baliairdispatch.com/api/live';

// Kept for the copy ("N sensors silent for more than 6 h" on older strings)
// and for the hourly archive; freshness itself now comes from BAD's own
// per-network stale flag.
var FRESH_HOURS = 6;

// Used only when /api/v1/stations cannot be reached. Mirrors INDOOR_IDS and
// MALFUNCTION_IDS on baliairdispatch.com as of 26 Sep 2026.
var FALLBACK_INDOOR = {
  'nafas-ba19b143-3580-4a60-a3ce-135a5e5936dd': 1,   // Pemogan (Nafas)
  'pa-36601': 1,                                     // Jimbaran by Lumi Clinic
  'iqs-jimbaran-s': 1                                // the same unit via IQAir
};
var FALLBACK_FAULTY = { 'pa-46949': 1 };             // Klungkung by Lumi Clinic

// Four scopes the reader picks between, NESTED rather than disjoint rings, and
// named the way somebody in Bali places themselves (Tomas, 26 Sep 2026):
//   street   <= 200 m   the lane and the houses on it — micro scale.
//   banjar   <= 1 km    the hamlet, the unit that actually decides things
//                       about waste and burning.
//   village  <= 5 km    the desa, or the part of the city you live in.
//   island   region     the whole administrative province: Bali.
// The reader's own pinned sensors are not a distance and get their own Home
// tab, shown only to somebody who has pinned one (see index.html).
// Nesting matters: with disjoint rings there are holes real sensors fall into,
// and nothing can be silently dropped when each scope includes the last.
var SCALES = [
  { id:'street',  maxKm:0.2      },
  { id:'banjar',  maxKm:1        },
  { id:'village', maxKm:5        },
  { id:'island',  maxKm:Infinity }
];

function haversineKm(lat1, lon1, lat2, lon2){
  var R = 6371, r = Math.PI/180;
  var dLat = (lat2-lat1)*r, dLon = (lon2-lon1)*r;
  var a = Math.sin(dLat/2)*Math.sin(dLat/2) +
          Math.cos(lat1*r)*Math.cos(lat2*r)*Math.sin(dLon/2)*Math.sin(dLon/2);
  return 2*R*Math.asin(Math.min(1, Math.sqrt(a)));
}

var _flags = null;
function loadFlags(){
  if (_flags) return Promise.resolve(_flags);
  return fetch(API + '/stations')
    .then(function(r){ if(!r.ok) throw new Error('stations HTTP '+r.status); return r.json(); })
    .then(function(j){
      var f = { indoor: {}, faulty: {}, fallback: false };
      (j.stations || []).forEach(function(s){
        if (s.suspected_indoor) f.indoor[s.station_id] = 1;
        if (s.suspected_malfunctioning) f.faulty[s.station_id] = 1;
      });
      _flags = f;
      return f;
    })
    .catch(function(e){
      console.warn('[near] station flags unavailable, using the mirrored list:', e);
      return { indoor: FALLBACK_INDOOR, faulty: FALLBACK_FAULTY, fallback: true };
    });
}

// One /api/live row into what this page works with. `ambient` is BAD's
// isAmbient, and it is the only gate on any figure this site computes: the
// scale medians, the island median, the diagnosis, coverage.
function toStation(r, flags){
  var seen = Date.parse(r.lastSeen);
  var indoor = !!flags.indoor[r.id], faulty = !!flags.faulty[r.id];
  var contributed = !!r.contributed || /^cs-/.test(String(r.id));
  var fresh = !r.stale && typeof r.pm25 === 'number';
  return {
    id: r.id,
    name: r.name,
    source: r.source,
    lat: r.lat,
    lng: r.lon,
    pm25: typeof r.pm25 === 'number' ? r.pm25 : null,
    pm25Raw: typeof r.pm25_raw === 'number' ? r.pm25_raw : null,
    corrected: !!r.pm25_corrected,
    estimated: !!r.pm25_estimated,
    observedAt: r.lastSeen || null,
    ageHours: isFinite(seen) ? (Date.now() - seen) / 3600000 : null,
    fresh: fresh,
    indoor: indoor,
    faulty: faulty,
    contributed: contributed,
    ambient: fresh && !indoor && !faulty && !contributed,
    // Shown, labelled, never counted — in the order BAD gives the reasons.
    excluded: !fresh ? 'stale' : indoor ? 'indoor' : faulty ? 'faulty' : contributed ? 'community' : null,
    sources: [r.source]
  };
}

var _cache = null, _inflight = null, _fetchedAt = 0;

// force=true drops the cached copy so the page can poll for a new reading.
// Deliberately NOT cache-busted with a query parameter: /api/live is edge-cached
// at s-maxage=120 and held by the browser for max-age=60, so a plain fetch is
// cheap for everyone. Adding ?t=<now> would push every visitor's poll onto
// their origin, which is a rude way to treat somebody else's free API.
function load(force){
  if (_cache && !force) return Promise.resolve(_cache);
  if (_inflight) return _inflight;
  var live = fetch(LIVE)
    .then(function(r){ if(!r.ok) throw new Error('live HTTP '+r.status); return r.json(); });
  _inflight = Promise.all([live, loadFlags()])
    .then(function(res){
      var d = res[0], flags = res[1];
      // off:true rows are BAD's tombstones for dead units: never live.
      var all = (d.stations || []).filter(function(s){
        return s && !s.off && typeof s.lat === 'number' && typeof s.lon === 'number';
      }).map(function(s){ return toStation(s, flags); });
      var live = all.filter(function(s){ return s.fresh; });
      var nets = {}; live.forEach(function(s){ nets[s.source] = 1; });
      _cache = {
        // Every live sensor, as BAD counts "live sensors". Figures are taken
        // from the ambient subset only; the rest are listed and labelled.
        sensors: live,
        ambient: live.filter(function(s){ return s.ambient; }),
        excluded: live.filter(function(s){ return !s.ambient; }),
        // Home can pin anything, including an indoor or community unit that
        // is the reader's own, and one that has gone quiet.
        all: all,
        indoor: live.filter(function(s){ return s.indoor; }),
        networks: Object.keys(nets).length,
        flagsFallback: !!flags.fallback,
        generatedAt: d.ts || null,
        degraded: !!d.degraded
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

// Only ambient readings carry a number. A band of three sensors where one is
// indoor reports two, and says so.
// True median: the average of the middle pair for an even count. It used to
// take the upper middle value, which with two sensors at 10 and 40 put 40 on
// the hero while understand.js (which averages) said 25 underneath it.
function median(sorted){
  if (!sorted.length) return null;
  var m = Math.floor(sorted.length/2);
  return sorted.length % 2 ? sorted[m] : (sorted[m-1] + sorted[m]) / 2;
}

function bandSummary(band, anyFresh){
  // Figures come from the ambient set only (BAD's isAmbient). anyFresh is for
  // the Home tab, where an indoor unit is exactly what the reader pinned.
  var use = band.sensors.filter(function(o){
    return o.s.pm25 != null && (anyFresh ? o.s.fresh : o.s.ambient);
  });
  if (!use.length) return { count: band.sensors.length, freshCount: 0, pm25: null };
  var vals = use.map(function(o){ return o.s.pm25; }).sort(function(a,b){ return a-b; });
  return {
    count: band.sensors.length,
    freshCount: use.length,
    pm25: median(vals),   // median, not mean: one bad box must not move it
    closest: use[0]
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
  LIVE: LIVE,
  SCALES: SCALES,
  FRESH_HOURS: FRESH_HOURS,
  load: load,
  refresh: function(){ return load(true); },
  fetchedAt: function(){ return _fetchedAt; },
  bandsFor: bandsFor,
  bandSummary: bandSummary,
  distanceKm: haversineKm,
  islandMedian: function(sensors){
    var v = sensors.filter(function(s){ return s.ambient && s.pm25 != null; })
                   .map(function(s){ return s.pm25; }).sort(function(a,b){ return a-b; });
    return median(v);
  },
  hourly: hourly,
  _toStation: toStation,
  _fallbackFlags: { indoor: FALLBACK_INDOOR, faulty: FALLBACK_FAULTY }
};

})();
