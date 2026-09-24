# Handoff: Making Sense Bali DIY-node enclosure — v8, validate & finalize

**From:** Claude (Cowork session with Tomas, 2026-06-09)
**To:** the next agent
**Mandate:** v8 is designed, both variants, and **assembly-simulated**. The CAD is as
far as it can go on a screen. Your job is to get it into plastic and finalize it —
coupons → fits → section prints → full prints → hose test → freeze. Do **not** redesign
v8; validate it. The repo: `hardware/diy-node/enclosure/`. Local on Tomas's Mac:
`~/Documents/Claude/Projects/MDG/smartcitizenbali/`.

---

## 0. Where this is
Eight generations happened before v8 (box → lantern → gourd → column → pine-cone →
candi/meru → pucuk → v6 box → v7 additive-native Basic). Tomas **approved the v8 base
form** and the features pass (bayonet + panel seat) on 2026-06-09. Then I ran an
**assembly simulation** of the fully-populated Plus — and it caught three real bugs that
had survived to here (see §2). All three are fixed and re-verified **digitally**.

The unbroken pattern of this whole project: lots of rendering, **nothing ever printed.**
That is still true. The simulation proves geometry and assembly logic; it does **not**
prove plastic. The gate has not moved: **print the coupons.**

## 1. State of v8 (validated digitally)
One parametric generator, two variants, additive-native (gyroid breathing window,
lifted feet, shadow-gap, domed hood + drip-lip, print-in-place added-tab bayonet). Plus
separates the PM air path (HM3301 front bay + down-duct) from the T/RH air (BME680 side
gyroid window).

| part | size (mm) | PETG | print | supports | watertight | solids |
|---|---|---|---|---|---|---|
| Basic body | 56×44×105 | 46.6 g | ~2h10 | 0 | yes | 1 |
| Plus body | 56×56×115 | 61.4 g | ~2h40 | 0 | yes | 1 |
| Cap (shared) | Ø35 | 2.9 g | 13 m | 0 | yes | 1 |
| Gyroid panel | 33.6×31.5×8 | 5.6 g | 27 m | 0 | yes | 1 |

Verified: interference 0.000 (body vs perfboard / BME680 / HM3301, and sensor-vs-sensor);
cap inserts + twist-locks (cap-locked ∩ body = 0.000 by trimesh containment; lug rests on
tab top +0.3 mm; capture 1.7 mm radial × 34°); BME680 behind its panel with a 2.9 mm
foil-liner gap; both bodies one solid + support-free; both under the 140 mm limit. Gyroid
panel: 48% open, ~3% straight sightline through the thickness (handled by the foil liner +
air gap behind it).

## 2. The 3 bugs the assembly sim found + fixed — do NOT reintroduce
1. **Solid bottom (the big one).** The base below the cavity floor was a solid block; the
   bayonet socket was never carved through it, so the cap could not insert and there was no
   bottom intake path. Inherited from v6/v7, undetected for 8 generations because the cap
   was never test-fit. Fix in `enclosure_v8.py`: a socket bore (Ø32.6) is cut through the
   base right after the cavity subtraction. If you refactor, keep that cut.
2. **Bayonet couldn't lock.** Cap lugs were at the same height as the socket tabs → they
   collided on the twist. Fix: lugs raised (`BAYO_LUG_LOCAL_Z`) to rest ON the tab tops;
   cap placed at `cap_rest_z`. Keep lug-bottom ≥ tab-top.
3. **BME680 ↔ panel collision.** Sensor too far outboard, edge inside the 8 mm-thick seated
   panel. Fix: BME680 moved inboard to x = −5 (plus branch). Keep ≥3 mm panel-to-sensor gap.

## 3. What is NOT done (your work, in order of the gate)
- **Coupons → ICD §5.1 (BLOCKING).** `coupons/` is sliced and ready (~84 min). Print,
  caliper, write the 7 numbers into `ICD.md §5.1`. Every fit in the generators is a named
  `COUPON_TBD_*` placeholder until then. **Nothing fit-critical is real, and nothing has
  been printed.**
- **Section prints before any full body** (cheap, decisive): the gyroid panel (27 min — does
  it breathe + print), the bayonet socket + cap (does the twist actually hold; tune the
  lock feel / add a detent if needed — none is modeled, rotation is just bounded by tab
  spacing), the BME680 shield zone.
- **Fold coupon numbers** into `COUPON_TBD_SLIDE / _PRESS / _PILOT_M2 / _PANEL`, re-slice,
  re-verify.
- **Print one Plus + one Basic + caps**; hang on the keyholes; **hose-test** the water path;
  rehearse assembly + monthly mesh service in hand with Tomas.
- **Basic assembly sim**: `simulate_plus.py` is Plus-only. The Basic shares the generator +
  the bayonet/socket fix, but run a quick Basic interference/insert check too.
- **ICD.md**: §5.1 still TBD; add a v8 entry to the change log (I only wrote `v8/BUILD.md`,
  not ICD). Freeze the spec on Tomas's sign-off + coupon numbers.
- **Craft pass** (hood proportions / radius polish) was deliberately light — optional, form
  approved as-is. Don't redesign the silhouette.
- **Sourcing (bought, honest)**: ePTFE membrane vent, stainless insect mesh 0.4–0.6 mm,
  cable gland (the #1 leak path).
- **Firmware**: BME680 T-offset; correct PM for RH in the dashboard, not firmware.

## 4. Toolchain (run on the Mac, not the sandbox)
- venv: `~/Documents/Claude/Projects/MDG/.cad-venv` (build123d 0.10, trimesh 4.12, skimage,
  scipy, numpy, Pillow). `manifold3d` would NOT install — do **not** rely on mesh booleans;
  the gyroid panel uses a single padded marching-cubes scalar field instead.
- Render: `tools/preview.py model.stl --views multi` (pyrender; macOS default backend).
- Slice: PrusaSlicer CLI at `/Applications/Original Prusa Drivers/PrusaSlicer.app/Contents/MacOS/PrusaSlicer`,
  `-g part.stl --printer-profile "Prusa CORE One HF0.4 nozzle" --print-profile "0.15mm SPEED @COREONE HF0.4" --material-profile "Generic PETG @COREONE HF0.4" -o part.gcode`.
  Output is **binary gcode** — read mass/time with `strings -n5 … | grep "filament used"`;
  supports via `grep -ac ";TYPE:Support"` (must be 0).
- **Run all CAD / render / slice on the Mac** (Macos shell + the venv). The sandbox has no
  GPU, blocked egress, and **no trimesh**. **Never run git in the sandbox** — Tomas commits
  on the Mac.
- The build123d `&` interference in `simulate_plus.py` is **flaky** on the cap/HM pairs
  (returns −1). Trust the generator's own `chk()` (prints 0.000) and **trimesh
  point-containment** (`mesh.contains(points)` on watertight meshes) for assembly checks.

## 5. First moves
1. Ask Tomas to **print the coupons** (`coupons/`, ~84 min) and the **gyroid panel section**
   (27 min) — the two cheapest things that turn guesses into numbers.
2. Fill `ICD.md §5.1` from the coupons; fold into the `COUPON_TBD_*` params; re-slice.
3. Section-print the **bayonet socket + cap**; confirm the twist-lock holds; tune the lock.
4. Print one **Plus** + one **Basic** + caps; hang; hose-test; review in hand.
5. Freeze ICD; finalize; **commit on the Mac** (not the sandbox).

## 6. Files
- `tools/enclosure_v8.py` — parametric Basic+Plus body+cap generator (the bayonet + socket
  bore + BME position fixes live here).
- `tools/gyroid_panel.py` — the breathing panel (watertight single-field gyroid).
- `tools/bayonet_test.py` — isolated bayonet interface test (added-tab topology).
- `tools/simulate_plus.py` — the Plus assembly simulator (interference, bayonet kinematics,
  panel↔sensor, overhang). Plus-only.
- `tools/show_seated.py` — renders the panel seated in each body.
- `tools/preview.py` · `run_model.py` · `mesh_io.py` — render + watertight/gate utilities.
- `v8/` — bodies, caps, panel (STL/STEP/gcode), `review/` (assembly + cutaway + seated
  renders), and **`v8/BUILD.md`** (the canonical state doc — read it).
- `ICD.md` — verified dims (§2), frozen decisions, **§5.1 fits (TBD — fill from coupons)**.
- `coupons/` — calibration set, sliced, **print first**.
- `v6/`, `v7/`, `pucuk/`, `efficient/`, `archive/` — earlier directions; read for why they
  were rejected, reuse nothing wholesale. (`v7/`'s gyroid STLs are broken — ignore them.)

The epitaph still holds, and it's the whole game: **the parts are proven on a screen and in
the assembly logic — not in plastic. Print the coupons. Verify in the medium that matters.**
