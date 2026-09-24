# Handoff — v12 modular enclosure, and where to take it next

**Date:** 2026-06-11 · **From:** Claude (Cowork session with Tomas) · **To:** next agent
**Status:** v12 modular stacking system built and geometry-verified in build123d. **STAGING —
nothing has been printed.** The gate (ICD §5.1) is still open. Read this before touching CAD.

---

## 1. The one-paragraph picture

The DIY air-quality node enclosure is now a **stack of interchangeable tier-modules**, not a
monolithic body. The stack grows with the number of sensors and the deployment (indoor vs
outdoor), and the stacking *is* a Balinese meru. Modules are clean **gyroid-breathing boxes**
on one standard **press-fit keyed-rim** interface; only the **crown** carries the faceted
meru eaves/finial; indoor gets a low **gyroid cap** instead. Everything is parametric
build123d run on Tomas's Mac; the organic crown form is shaped in Rhino (live MCP). The whole
arc v8→v12 is in `ICD.md` (now 1.11-DRAFT) — read its change log.

## 2. Locked decisions (do NOT re-litigate without Tomas)

- **Modular tower** on a standard interface; stack = meru. (Tomas, 2026-06-11)
- Interface = **press-fit keyed rim**: bottom spigot → open-cavity socket, central air+cable
  pass-through, flat back + keyholes. (Quarter-turn detent is an *option* if press-fit loosens.)
- Modules are **clean gyroid-window boxes; only the crown has eaves/finial.** Indoor top = a
  **low gyroid-vented cap**.
- **Gyroid is INTEGRATED, not a separate panel** (Tomas, latest): the lattice is fused into
  the part. Proven on the cap (`integrate_cap()` / `gyroid_mesh()` in `enclosure_v12.py`:
  marching-cubes lattice + `trimesh.boolean.union`, manifold3d backend → one watertight solid,
  48% open). Apply the same fuse-into-window technique to the module side windows next.
- **Sensor set = current build**: XIAO ESP32-S3 + BME680 (+ HM3301 on Plus). No SEN54 (still
  validation-pending; if it passes, one ~40×40 SEN54 module would replace BME680+HM3301).
- **Crown form = faceted meru**, 3 tiers, generous eaves, **inverted water-shed** (eaves are
  the widest point, body sits in the rain shadow, water travels the least surface).
- Material **PETG only** (PLA softens on Bali roofs). Flat back + keyholes for wall mount.

## 3. Components (verified) — and the caliper-pending bit

| Part | Dimensions | Note |
|---|---|---|
| XIAO ESP32-S3 | 21.0 × 17.8 mm, USB-C on a short edge | shares footprint with the C3 |
| BME680 breakout | ~16 × 12.5 mm (clone variance ±2) | size by envelope |
| **HM3301 (Plus)** | **80 × 40 × 18 mm — confirmed by Tomas 2026-06-11** | mounts vertical. The earlier "40×40" was an error; the original ICD 80×40 was right. **Still need: which can port is inlet vs outlet, and can orientation.** |
| Perfboard (Basic) | 40 × 60 × 1.6 (or a 40×40 board) | XIAO + BME on female headers |

## 4. What's built and verified (build123d, interference 0.000, watertight)

Generator: `tools/enclosure_v12.py` → `v12/`. Common footprint 46 × 26 mm.

| Part | Role | Size (mm) |
|---|---|---|
| Basic | XIAO + BME680, base intake grille, indoor core | 46 × 26 × 58 |
| Plus | HM3301 80×40×18 + own PM intake/exhaust | 48 × 26 × 99 |
| Crown | faceted 3-tier meru, eaves overhang to 66 × 50 | ~40 tall |
| Cap | low cap, **gyroid integrated** (one watertight solid, 48% open) | 46 × 26 × 29 |

Variants (stacks rendered in `v12/review/`): indoor Basic (Basic+cap, ~80 mm) · outdoor Basic
(Basic+crown) · indoor Plus (Basic+Plus+cap) · outdoor Plus (Basic+Plus+crown, ~197 mm tower).

Airflow: base intake → open central cavity + per-module gyroid windows → crown/cap exhaust;
the Plus PM bay keeps its own front intake + exhaust (the v11 two-system logic, per-module).
Full airflow rationale: `AIRFLOW_REVIEW_v10.md` + `v10/review/v10_airflow_review.png`.

## 5. Toolchain & workflow (how to actually run things)

- **build123d** lives in `~/Documents/Claude/Projects/MDG/.cad-venv` (build123d 0.10, trimesh
  4.12, skimage, scipy, **manifold3d** — booleans work). **Run everything on the Mac** via the
  Macos Shell MCP (`.cad-venv/bin/python tools/…`). The Linux sandbox has no GPU and can't
  install packages — do not try to run the CAD there.
- **Renders:** `tools/preview.py model.stl out.png --views multi|iso --resolution N`. Keep
  viewport/preview images **≤ ~480 px** or the MCP image payload overflows the token limit.
- **Dimensioned maps:** `tools/dimension_render.py` (to-scale matplotlib layout, mm callouts).
- **Rhino MCP** is live (official mcneel `Rhino-MCP-Platform` 0.1.5). To use it: run **`MCPStart`**
  in Rhino (server on `localhost:10501`) **then restart Claude Desktop** — connection is made on
  startup; first calls cold-time-out then work. **Rhino = organic skin; build123d = fits.** Setup
  + gotchas: `RHINO_MCP_SETUP.md`.
- **Process gates (ICD §8):** coupons → §5.1 → fits; slicer-in-loop per STL; multi-view +
  watertight gate; **section prints before whole prints**; Tomas approves at each checkpoint.

## 6. THE GATE — nothing fit-critical prints yet

`ICD.md §5.1` (measured clearances) is **still TBD**. The coupons are printed
(`coupons/coupon_A_fits.bgcode`, `coupon_B_print.bgcode`) but **not measured**. Every fit is a
named `COUPON_TBD_*` parameter (`COUPON_TBD_STACK` = the press fit the whole tower rides on,
plus pilots, slide, etc.). **First print = the press-fit rim section**, not a whole tower.
See `coupons/README.md` for the 7 numbers to measure.

## 7. Assembly & hardware — Tomas's directive, BUILD THIS OUT

The design is currently press-fit + open mounts; the next agent should make it **assemblable
by a non-expert in a workshop**. Two workstreams:

**(a) Fasteners / hardware BOM.** Decide and model real hardware, don't hand-wave:
- **Wall mount:** the keyholes take wall screws — spec the screw + the keyhole slot geometry.
- **Module locks:** press-fit is the default; if outdoor handling loosens the stack, add a
  **quarter-turn detent** to the keyed rim, or **2× M3** per joint. Pick one and model it.
- **Board retention:** **M2 self-tap or M2 heat-set inserts** into the printed standoffs
  (PETG holds threads poorly — heat-set inserts are the robust answer; model the boss bores
  for the insert size). HM3301 uses its 4× Ø3.2 holes — model **registration pegs** + clip.
- **Membranes/mesh:** ePTFE vent membrane (pressure equalisation), insect mesh on intakes
  (aperture ≤1.2 mm), seats sized for both. Spec adhesive vs captive.
- Produce a real **hardware BOM** (qty, size, source) alongside the printed-parts BOM.

**(b) Printed board placeholders (idiot-proof assembly).** Carry forward the v4/v5.1
"footprint guide" idea (see `archive/`): the user should never guess where a board goes.
- Debossed **component outlines** on the mounting face: XIAO outline + 2×7-pin rows @2.54 +
  USB-C oval on the cable side; BME680 outline + 6-pin row; HM3301 outline + 4 peg positions.
- **No text labels** — locate by printed footprint (ICD F-10); add "this side up" / cable-exit
  cues geometrically.
- A defined **cable route + strain relief** up the central pass-through, with **Grove connector
  clearance** at each module interface (the I²C 4-wire + power runs Basic→Plus).
- Mesh/membrane seats that drop in and are retained at monthly service.

## 8. Open items / next moves (roughly in priority order)

1. **Caliper the HM3301 can ports** (inlet vs outlet, orientation) — gates correct PM airflow.
2. **Fill ICD §5.1** from the coupons → real values for every `COUPON_TBD_*`; then **section-
   print the press-fit rim** to validate the stack joint before any full module.
3. **Hardware + board placeholders** (§7) — the biggest gap for real-world buildability.
4. **Integrate gyroid into the module side windows** (technique proven on the cap; same
   `gyroid_mesh()` + union, sized per window) so the whole tower breathes through integrated
   gyroid, not open windows.
5. **Inter-module cable route** — retained path + Grove clearance through the interface.
6. **Plus rail bump** — the HM rails sit at ±22, ~2 mm past the 46 wall; tuck the rails or
   widen the Plus footprint by 2 mm.
7. **Crown form in Rhino** — refine eave depth / tier spacing / finial against the real
   modular proportions (it's currently a parametric meru rebuilt from the Rhino study).
8. **Proportion check** — outdoor Plus is a tall ~197 mm meru (the 80 mm HM drives it); tune
   module heights if it reads too slender.
9. **SEN54 decision** — if Tomas validates SEN54, a single ~40×40 module replaces BME680+HM3301
   and the Plus tier collapses into the Basic.

## 9. Lessons / gotchas (do NOT repeat)

- **Digital sim proves geometry + interference, NOT printability.** v8 printed and failed on
  (1) a sealed body with no board-access path and (2) a ~43 mm unsupported floor bridge.
  Check bridge spans by hand; "0 supports" ≠ printable; never seal the board-entry path.
- **Don't override a sourced dimension on an assumption** — the HM3301 80×40×18 episode.
- **Feet under a floor force a feet-down print** that re-creates unsupported spans — removed.
- **Run CAD/render on the Mac venv**, not the sandbox. Preview images **≤480 px**.
- **Rhino:** `MCPStart` in Rhino *then* restart Claude Desktop; cold first-calls time out;
  viewport images ≤480 px.
- **Never run git in the sandbox** — it leaves stale `.git/index.lock` that blocks Tomas's next
  commit. Verify file changes via sha256/`diff`, and let Tomas do git on the Mac.
- **manifold3d is installed** in the venv → `trimesh.boolean.union` works for fusing gyroid
  lattices into parts (that's how the integrated cap is made).

## 10. File map

- `ICD.md` — the spec + full change log (v1.0 → 1.11-DRAFT). Single source of truth.
- `tools/enclosure_v12.py` — the modular generator (Basic/Plus/Crown/Cap + integrated cap).
- `tools/breathing_panel_v{9,10,11,12}.py` — gyroid generators (drop-in; v12 cap is now fused).
- `tools/dimension_render.py`, `preview.py`, `run_model.py`, `airflow_diagram.py` — tooling.
- `v12/` — current parts + `v12/review/` stacks & previews. `v12/BUILD.md` — v12 state.
- `v9/`–`v11/` + their `BUILD.md` — prior staging builds (v11 = last single-body, corrected
  airflow + HM 80×40×18). `AIRFLOW_REVIEW_v10.md`, `RHINO_MCP_SETUP.md`.
- `coupons/` — calibration coupons (printed, unmeasured) + `README.md` (the 7 numbers).
- `archive/` — v1–v5.1 form/footprint-guide lessons.

**The unbroken rule:** prove it in the medium that matters before committing material. Coupons
before fits; sections before whole prints; the Mac/slicer before "it'll print." v8 proved
geometry and still failed — don't make that mistake again.
