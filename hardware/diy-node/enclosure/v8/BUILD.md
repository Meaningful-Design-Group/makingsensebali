> ⛔ **FAILED — 2026-06-10.** Printed and failed on two root causes: (1) hood fused to
> body = sealed box, no board-access path (bayonet bore Ø32.6 < 40×60 perfboard);
> (2) cavity floor printed as a ~43 mm unsupported bridge → collapsed. Superseded by
> the three-part v9 architecture. See `../HANDOFF_v9_redesign.md` and `../v9/BUILD.md`.

# v8 — Making Sense Bali DIY-node enclosure (BUILD)

One additive-native, parametric generator, two variants. Basic = XIAO ESP32-S3 +
BME680. Plus = + Grove HM3301. Status: **base form approved by Tomas; features pass
done (bayonet + panel seat). All fits COUPON_TBD — nothing fit-critical is final
until the coupons are printed and ICD §5.1 is filled.**

## What v8 is
- `tools/enclosure_v8.py` — the two-variant body+cap generator.
- `tools/gyroid_panel.py` — the breathing panel (rebuilt; see below).
- `tools/bayonet_test.py` — the isolated bayonet interface test.
- `tools/show_seated.py` — renders the panel seated in each body.

Additive-native moves (the v7 language Tomas approved): sheet-gyroid breathing
window (front on Basic, side on Plus), lifted feet that also hold the bottom
intake off a flush surface, shadow-gap reveal, domed hood + drip-lip, print-in-place
bayonet (zero hardware). On the Plus the BME680 window is on the side so the
particulate air path (HM3301 front bay + down-duct) never crosses the T/RH air.

## Numbers (PrusaSlicer CORE One HF0.4, Generic PETG, 0.15 SPEED)
| part | size (mm) | PETG | time | supports | watertight | solids |
|---|---|---|---|---|---|---|
| Basic body | 56×44×105 | 46.6 g | ~2h10 | 0 | yes | 1 |
| Plus body | 56×56×115 | 61.4 g | ~2h40 | 0 | yes | 1 |
| Cap (shared) | Ø35 | 2.9 g | 13 m | 0 | yes | 1 |
| Gyroid panel | 33.6×31.5×8 | 5.6 g | 27 m | 0 | yes | 1 |

Interference vs verified component dummies (perfboard, BME680, HM3301 module): 0.000 cm³.
Both bodies under the 140 mm height limit; fit the 220×220 bed.

## Two things rebuilt / fixed in v8
1. **Gyroid panel was broken, not "cleanup."** The three v7 gyroid STLs were
   non-watertight, negative-volume open sheets, and the generator that made them was
   never saved (no file in the repo contains `marching_cubes`). `tools/gyroid_panel.py`
   rebuilds it as one watertight solid in a single marching-cubes pass over a scalar
   field (frame + solid rim + lattice together — no fragile mesh booleans). `t`
   auto-tunes to 48% open. ~3% straight line-of-sight through the thickness, caught
   by the foil liner + air gap behind the panel (the real IR/light barrier).
2. **Bayonet topology reworked (latent v6 bug).** v6/v7 CUT entry/turn slots through
   a thin seat ring, which fragmented it into disconnected arcs (Basic 3 islands,
   Plus 4 — silently dropped by mesh-clean, i.e. the printed ledge lost segments).
   v8 inverts it: a CONTINUOUS skirt with 3 ADDED inward tabs and cap lugs that pass
   up through the gaps and twist under the tabs (~37°). Nothing is cut into islands,
   so both bodies are natively one solid. Also unified the cap (one fits both
   variants) — its old width punched the side wall on the Plus.

## Assembly simulation (2026-06-09) — 3 bugs found and fixed
`tools/simulate_plus.py` populates the Plus with every sensor (verified ICD dims) and
checks interference, bayonet lock kinematics, panel-vs-sensor, and overhang. It caught
three real bugs that survived to here, before any plastic:
1. **Solid bottom (the big one).** The base below the cavity floor was a SOLID block —
   the bayonet socket was never carved through it, so the cap could not insert and there
   was no bottom intake path. Inherited from v6/v7; undetected for 8 generations because
   the cap was never test-fit. Fix: carve the socket bore (Ø32.6) through the base.
   Bodies dropped ~2 g. Verified: probe points in the base now read "outside".
2. **Bayonet couldn't lock.** Cap lugs sat at the SAME height as the socket tabs, so the
   twist drove them into each other (cap↔body 1.5 cm³ collision, confirmed by trimesh
   point-containment, not a boolean artifact). Fix: lugs raised to rest ON the tab tops.
   Verified: cap-locked ∩ body = 0.000; lug-bottom − tab-top = +0.3 mm; capture 1.7 mm × 34°.
3. **BME680 ↔ panel collision.** The sensor sat too far outboard; its edge was inside the
   8 mm-thick seated gyroid panel (overlap 4×7×12.5 mm). Fix: BME680 moved inboard (x −12
   → −5) → 2.9 mm gap, the foil-liner zone.

After fixes (digital): interference 0.000 across body / perfboard / BME680 / HM3301; cap
inserts + twist-locks; BME680 sits behind its panel with the foil gap; the HM3301 PM duct
is separated from the BME680 air; both bodies one solid, support-free. **This proves the
geometry and assembly logic — NOT plastic behaviour. Clearances are COUPON_TBD; the
bayonet feel, the panel snap, and whether the gyroid actually breathes are only settled by
the printed coupons + section tests.** Reliable interference came from the generator's own
checks + trimesh point-containment; the build123d `&` in the simulator is flaky on the
cap/HM pairs (returns −1) — prefer trimesh containment.

## OPEN items (gate = coupons)
- **Coupons → ICD §5.1 (BLOCKING all fit-critical work).** Bayonet slide, panel snap,
  HM peg press, hole shrink, overhang, elephant-foot — all `COUPON_TBD_*` today.
- **Section prints before any full body** (per the skill): the gyroid panel (27 min),
  the bayonet socket + cap engagement, the BME680 shield zone.
- **BME680 radiation shield**: foil liner + 3–5 mm air gap behind the gyroid window;
  firmware T-offset; consider micro-aspiration for reference sites.
- **Craft**: hood proportions / radius system is a light optional pass — form approved as-is.
- **Sourcing (bought, honest)**: ePTFE membrane vent, stainless insect mesh 0.4–0.6 mm,
  cable gland (the #1 leak path).

## Print order
1. Coupons (`coupons/`, ~84 min) → measure → fill ICD §5.1.
2. Section tests: gyroid panel; bayonet socket + cap.
3. One Basic + one Plus body + caps; hang; hose-test; review in hand.
