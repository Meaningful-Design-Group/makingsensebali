// node tools/tests/understand.test.js
const U = require('../../understand.js');
let fails = 0;
const ok = (name, cond, got) => { console.log((cond ? '  PASS ' : '  FAIL ') + name + (cond ? '' : '  got: ' + JSON.stringify(got))); if (!cond) fails++; };

const HERE = { lat: -8.79, lng: 115.16 };
// offset in km -> degrees (roughly, near Bali)
const at = (dkmN, dkmE) => ({ lat: HERE.lat + dkmN / 111, lng: HERE.lng + dkmE / 110 });
let id = 0;
const S = (pos, pm, extra) => Object.assign({ id: 's' + (++id), name: 'S' + id, fresh: true, pm25: pm }, pos, extra || {});
const island = (pm, n) => Array.from({ length: n }, (_, i) => S(at(30 + i * 3, 20), pm));

// 12:00 WITA = 04:00 UTC ; 19:00 WITA = 11:00 UTC
const NOON = Date.UTC(2026, 8, 26, 4, 0), DUSK = Date.UTC(2026, 8, 26, 11, 0);
const series = (vals, endMs) => vals.map((v, i) => ({ t: endMs - (vals.length - 1 - i) * 3600000, pm25: v }));
// 8 days of hourly data where every hour reads `base`, except the last hour = `last`
const flat = (base, last, endMs) => { const v = Array(8 * 24).fill(base); v[v.length - 1] = last; return series(v, endMs); };

console.log('\n[1] no data');
ok('nodata', U.diagnose({ sensors: [] }).kind === 'nodata');
ok('stale sensors ignored', U.diagnose({ sensors: [S(at(0, 0), 50, { fresh: false })] }).kind === 'nodata');

console.log('\n[2] regional event');
let d = U.diagnose({ here: HERE, sensors: [...island(45, 14), S(at(0.5, 0), 48)], now: NOON });
ok('regional when most of Bali is high', d.kind === 'regional', d.kind);
ok('why mentions regional', d.why[0] === 'regional', d.why);

console.log('\n[3] local source');
d = U.diagnose({ here: HERE, sensors: [...island(10, 14), S(at(0.4, 0), 70), S(at(0.8, 0.3), 60), S(at(4, 0), 12), S(at(6, 1), 11)], now: NOON });
ok('local when your area stands out from the ring', d.kind === 'local', d);
ok('local vars', d.vars.localMed >= 60 && d.vars.ringMed <= 12, d.vars);

console.log('\n[4] not local when ring is also high');
d = U.diagnose({ here: HERE, sensors: [...island(10, 14), S(at(0.4, 0), 40), S(at(4, 0), 38), S(at(6, 0), 36)], now: NOON });
ok('elevated, not local', d.kind === 'elevated', d.kind);

console.log('\n[5] usual for this hour vs above usual');
const near = S(at(0.3, 0), 40);
d = U.diagnose({ here: HERE, sensors: [...island(10, 14), near], hourly: flat(38, 40, DUSK - 600000), now: DUSK });
ok('usual_high when it reads like this every evening', d.kind === 'usual_high', d);
ok('window = dusk at 19:00 WITA', d.window === 'dusk', d.window);
ok('why includes window', d.why.includes('window'), d.why);
d = U.diagnose({ here: HERE, sensors: [...island(10, 14), near], hourly: flat(12, 40, DUSK - 600000), now: DUSK });
ok('above_usual when it is normally 12 at this hour', d.kind === 'above_usual', d);
ok('hour vars', d.vars.usual === 12 && d.vars.hourNow === 40 && d.vars.hour === 18, d.vars);

console.log('\n[6] history too old or too short is ignored');
d = U.diagnose({ here: HERE, sensors: [...island(10, 14), near], hourly: flat(12, 40, DUSK - 5 * 3600000), now: DUSK });
ok('stale archive -> no hour verdict', d.kind === 'elevated' && d.hour == null, d.kind);
ok('short series -> null', U.hourCompare(series([1, 2, 3], NOON), NOON) === null);

console.log('\n[7] clean');
d = U.diagnose({ here: HERE, sensors: [...island(8, 14), S(at(0.3, 0), 6)], now: NOON });
ok('clean', d.kind === 'clean', d.kind);
ok('no window line when clean', !d.why.includes('window'), d.why);
d = U.diagnose({ here: HERE, sensors: [...island(8, 14), S(at(0.3, 0), 6)], hourly: flat(25, 6, NOON - 600000), now: NOON });
ok('clean + cleaner than usual uses hour', d.kind === 'clean' && d.why[0] === 'hour' && d.hour.verdict === 'below', d);

console.log('\n[8] suspect sensor');
d = U.diagnose({ here: HERE, sensors: [...island(10, 14), S(at(0.2, 0), 95), S(at(0.6, 0), 12), S(at(1.0, 0.2), 14), S(at(1.3, 0), 11)], now: NOON });
ok('high outlier flagged', d.suspect && d.suspect.direction === 'high' && d.suspect.value === 95, d.suspect);
d = U.diagnose({ here: HERE, sensors: [...island(30, 14), S(at(0.2, 0), 2), S(at(0.6, 0), 40), S(at(1.0, 0.2), 45), S(at(1.3, 0), 38)], now: NOON });
ok('low outlier flagged (a sensor reading clean inside a smoky area)', d.suspect && d.suspect.direction === 'low', d.suspect);
d = U.diagnose({ here: HERE, sensors: [...island(10, 14), S(at(0.2, 0), 95)], now: NOON });
ok('lone sensor is never called suspect', d.suspect === null, d.suspect);

console.log('\n[9] not located: island only, no local claims');
d = U.diagnose({ sensors: [...island(9, 14)], now: NOON });
ok('clean island', d.kind === 'clean' && d.why[0] === 'island', d);
d = U.diagnose({ sensors: [...island(30, 5)], now: NOON });
ok('few sensors: no regional claim below 10 boxes', d.kind === 'elevated', d.kind);

console.log('\n[10] banjar (1 km) empty -> widens to village (3 km), not silently island');
d = U.diagnose({ here: HERE, sensors: [...island(10, 14), S(at(2.5, 0), 60), S(at(8, 0), 11), S(at(12, 0), 12)], now: NOON });
ok('widened local radius', d.vars.rLocal === 3 && d.vars.localMed === 60, d.vars);
ok('and still finds the local source', d.kind === 'local', d.kind);

console.log('\n[11] median, not mean');
ok('even-length median', U._median([1, 2, 3, 100]) === 2.5);


console.log('\n[12] nearby reports: desa-level, dated honestly');
const NOW = Date.UTC(2026, 8, 26, 4, 0);
const day = n => new Date(NOW - n * 86400000).toISOString().slice(0, 10) + 'T00:00:00+00:00';
const R = (pos, cat, daysAgo, loc) => Object.assign({ category: cat, submittedAt: day(daysAgo), locality: loc }, pos);
const reps = [R(at(1, 0), 'burning', 1, 'Jimbaran'), R(at(2, 0), 'burning', 3, 'Jimbaran'), R(at(3, 1), 'burning', 5, 'Ungasan'),
              R(at(1, 0), 'trash', 1, 'Jimbaran'), R(at(40, 0), 'burning', 1, 'Ubud'), R(at(1, 0), 'burning', 20, 'Jimbaran')];
let nr = U.nearbyReports(HERE, reps, NOW, 2);
ok('counts only burning within max(scale,5 km) in 7 days', nr.week === 3, nr);
ok('places ranked', nr.places[0] === 'Jimbaran' && nr.places[1] === 'Ungasan', nr.places);
ok('street scale still uses 5 km floor', U.nearbyReports(HERE, reps, NOW, 0.1).week === 3);
ok('island counts everything burning this week', U.nearbyReports(HERE, reps, NOW, Infinity).week === 4);
nr = U.nearbyReports(HERE, [R(at(1, 0), 'burning', 16, 'Jimbaran')], NOW, 2);
ok('nothing this week -> dated last report', nr.week === 0 && nr.last && nr.last.days === 16 && nr.last.locality === 'Jimbaran', nr);
ok('not located -> nothing local', U.nearbyReports(null, reps, NOW, 2).week === 0);

console.log('\n[13] patterns');
const doc = { patterns: [{ id: 'p1', centroid: at(2, 0), window: 'dusk' }, { id: 'p2', centroid: at(50, 0), window: 'dawn' }] };
ok('pattern within radius', U.nearbyPatterns(HERE, doc, 2).map(p => p.id).join() === 'p1');
ok('island shows all', U.nearbyPatterns(HERE, doc, Infinity).length === 2);
ok('missing doc -> empty', U.nearbyPatterns(HERE, null, 2).length === 0);

console.log('\n[14] coverage gap');
let cv = U.coverage(HERE, [S(at(3, 0), 10), S(at(9, 0), 10)]);
ok('gap when nothing within 1 km', cv.gap === true && cv.nearestKm === 3, cv);
cv = U.coverage(HERE, [S(at(0.6, 0), 10), S(at(0.8, 0), 10, { fresh: false })]);
ok('stale sensor does not count as coverage', cv.gap === false && cv.within1 === 1, cv);
cv = U.coverage(HERE, [S(at(0.6, 0), 10, { ambient: false }), S(at(9, 0), 10)]);
ok('an indoor or community sensor is not coverage', cv.gap === true, cv);
cv = U.coverage(HERE, [S(at(1.5, 0), 10)]);
ok('1.5 km away is outside the banjar: still a gap', cv.gap === true, cv);


console.log('\n[15] regional, but your area is doing better');
d = U.diagnose({ here: HERE, sensors: [...island(45, 14), S(at(0.5, 0), 14)], now: NOON });
ok('regional_lower when local <= 0.6x island', d.kind === 'regional_lower', d.kind);
ok('why shows regional + a comparison (ring empty here, so compare_clean)', d.why.join() === 'regional,compare_clean', d.why);

console.log('\n[16] nothing within 5 km: says so, uses the ring, not the island');
d = U.diagnose({ here: HERE, sensors: [...island(10, 14), S(at(8, 0), 40), S(at(9, 0), 42)], now: NOON });
ok('nolocal first in why', d.why[0] === 'nolocal', d.why);
ok('value from ring (8–15 km), not island median', d.value === 41, d.value);
ok('nearestKm reported', Math.abs(d.vars.nearestKm - 8) < 0.3, d.vars.nearestKm);


console.log('\n[17] review fixes');
d = U.diagnose({ here: HERE, sensors: [...island(8, 14), S(at(0.3, 0), 13.5)], now: NOON });
ok('13.5 is near_line, not "clean, open up"', d.kind === 'near_line', d.kind);
d = U.diagnose({ here: HERE, sensors: [...island(10, 14), S(at(0.3, 0), 40)], hourly: flat(60, 20, NOON - 600000), now: NOON });
ok('above the line but below usual -> elevated, never "normal for this hour"', d.kind === 'elevated' && d.why.includes('hour') && d.hour.verdict === 'below', d);
d = U.diagnose({ here: HERE, sensors: [...island(60, 14), S(at(0.3, 0), 12)], now: NOON });
ok('regional_lower with empty ring uses compare_clean (no blank "Out to 10 km: .")', d.kind === 'regional_lower' && d.why.includes('compare_clean') && !d.why.includes('compare'), d.why);
d = U.diagnose({ here: { lat: -8.1, lng: 115.1 }, sensors: [...island(30, 14)], now: NOON });
ok('nothing within 15 km -> nolocal_island', d.why[0] === 'nolocal_island', d.why);

console.log('\n' + (fails ? fails + ' FAILED' : 'ALL PASS'));
process.exit(fails ? 1 : 0);
