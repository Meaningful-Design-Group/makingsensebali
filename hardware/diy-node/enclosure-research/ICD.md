# Interface Control Document — Making Sense Bali DIY-Node Enclosure

**Version:** SPEC-1.0-DRAFT (becomes 1.0-FROZEN on Tomas's sign-off + coupon numbers)
**Date:** 2026-06-08
**Rule:** No enclosure CAD is modeled against this spec until it is FROZEN. Any later change is a versioned spec change (1.1, 1.2…), recorded in the change log at the bottom — not a vibe.

---

## 1. Mission

Wall-mounted outdoor enclosure for a workshop-built air-quality node. Bali climate: hot (to ~35°C ambient, hotter under roofs), ~80%+ RH, monsoon rain, insects. Deployed under eaves. Two variants from one design. The printed object must read as a product someone is proud to hang on their house — not a programmer's geometry exercise.

## 2. Components (verified dimensions)

| Component | Dimensions (mm) | Source | Notes |
|---|---|---|---|
| Seeed XIAO ESP32-S3 | 21.0 × 17.8, USB-C on short edge | Seeed datasheet | On female headers, perfboard top zone (exhaust side) |
| GY-BME680 breakout | ~16 × 12.5, 6-pin | measured; clones ±2 mm | On female headers, perfboard bottom zone (intake side). Clone variance → footprint guide sized for envelope |
| Perfboard | 40 × 60 × 1.6 | spec (frozen v3) | Carries both modules on female headers |
| Grove HM3301 module (Plus only) | **80 × 40 × 18 mm — confirmed by Tomas 2026-06-11; geometry now fully resolved from Seeed Eagle board file + HM-3300/3600 datasheet V2.1 (2026-06-11, `ref_hm3301_eagle/`).** Board exactly 80.00 × 40.00 (origin center, X −40..+40). Can = 40(L)×38(W)×15(H), footprint X −25.39..+14.61, Y −18.79..+19.21 → **14.6 mm clear board at the Grove end, 25.4 mm clear at the electronics end.** Grove 4P right-angle connector exits the LEFT short edge (J2 @ x=−30.33); can's 8P connector J1 @ (+37.72, 0). **NO Ø3.2 mounting holes exist — the only board cutouts are 2× Ø2.4 at the can's diagonal corners ((−23.62,−17.02), (+12.57,+17.14)): M2.5 screws pass through the board into the can's bottom positioning holes.** Air ports: BOTH on the can's one 40×15 narrow face, flush with ONE long edge of the board, one port near each end of that face; which long edge is unknown from files → **bay symmetric, install rule "vent face toward front grille"; in/out direction confirmed by feel at power-up (ducts mirror-symmetric, work either way).** Siting rules: isolate inlet from outlet with a structure; product vent ≥ port size; ports never face up. | Seeed Eagle .brd (parsed 2026-06-11) + HM-3300/3600 datasheet V2.1 §7; total thickness Tomas | Vertical in rails; v11/v12 Plus bay 80×40×18 stands. **Retention = rails + edge capture (NOT pegs — no peg holes exist); optionally 2× M2.5 through-screws into the can if the module needs hard mounting** |
| LiPo 803040 (provision only) | 40 × 30 × 8 | standard cell spec | DEC-04: floor lip/frame + cable space designed in; no battery in v1 build |
| Insect mesh | aperture ≤ 1.2 mm | — | Stainless or nylon; serviceable monthly |
| USB-C cable | Ø ~4.5 boot, bend radius ≥ 15 | typical | Exit with drip loop, faces down |

## 3. Frozen decisions (2026-06-08, Tomas)

| ID | Decision | Value |
|---|---|---|
| DEC-01 | Form reference | **v1.1 (2026-06-08): Batik-fractal meru.** Self-similar stacked tiers (meru/pagoda logic) carry rain + airflow; pierced batik-derived pattern bands (kawung-class geometry, abstracted — no sacred motif copied) in the rain-shadow under each tier. Organic, curved tier profiles — not hard cones. Register: batik language, pan-Indonesian. ~~v1.0: banana flower (jantung pisang)~~ → archived in `archive/concept-jantung-2026-06/` |
| DEC-02 | Size envelope | **≤ 140 mm tall**, target footprint ≤ Ø100 incl. tiers |
| DEC-03 | Service gesture | **v1.7 (2026-06-10): split access, base = press-fit.** Monthly (mesh, USB): remove the **full-footprint base plate from below** (press-fit spigot, `COUPON_TBD_PRESSFIT`) — no tools. Deep (boards, rare): unhook from keyholes, **2× M3** release the hood/crown (restored — v8 had fused it shut). ~~v1.3 bottom bayonet cap~~ retired: the print-in-place bayonet was complex and its bore blocked board entry; press-fit is testable in a section first. Bayonet may return as a section-tested option. Clearances from coupons only |
| DEC-04 | Battery | **v1.3: provision deferred entirely.** Interference math: no LiPo placement coexists with the vertical HM3301 in a Ø76 body. Future battery = a deeper **battery-cap** variant of the bottom bayonet cap. Plus v1 is USB-C only |
| DEC-05 | Variant strategy | **v1.3 (Tomas): TWO bodies.** Plus = full N1 lima with PM bay; Basic = own smaller enclosure, no PM bay (family proposal: Basic as tumpang telu). Plus designed and validated first; Basic derived |
| DEC-06 | Mechanical CAD | **build123d** (BREP kernel, STEP+STL out). OpenSCAD CSG retired for enclosure bodies |
| DEC-07 | Skin method | Bracts as **BREP lofts/sweeps in build123d** first; Blender geometry-nodes is plan B if BREP reads too geometric in hand |
| DEC-08 | Material | **PETG only.** PLA banned (softens on Bali roofs) |
| DEC-09 | ~~Phase-1 base form: N1 lima meru~~ | Superseded by DEC-10 (v2). N1 was a single smooth-revolve tower; v1 functional build archived in `archive/v1-candi-tower-2026-06/` |
| DEC-10 | **v2 architecture (2026-06-08, Tomas): function-first, modular, faceted** | Four-part family: (a) **spine** — open chassis + flat back + keyholes + HM3301 rails + perfboard standoffs (validated internals carried from v1); (b) **shell** — faceted octagonal louver sleeve, the variant + aesthetic part, slides over spine, D-open back; (c) **base cap** — down-intake + cable + bayonet (shared); (d) **crown cap** — exhaust finial (shared). Basic = short spine+shell; Plus = tall. Decouples validated chassis from evolving aesthetic skin |
| DEC-11 | **Aesthetic: octagonal fractal-subdivided, triangulated** | 8-fold faceted body, twisted ruled-loft facets read as low-poly triangulation; batik/fractal lineage via self-similar (fractal-graded) louver rhythm. "Semi-organic digital" |
| DEC-12 | **Louvers = the facets** | Down-and-out angled triangular louver slots in fractal-graded bands ARE the skin: rain sheds off every facet, air enters the gaps, chimney draws bottom→top. Form=function=aesthetic. Thin-wall, support-free, material-minimal |
| DEC-13 | **Performance priorities (Tomas, explicit)** | 1) sensor airflow (chimney: BME680 low/intake, XIAO high/exhaust, HM3301 own duct); 2) zero water ingress (no up-facing apertures, louver shed, back-seam in wall shadow); 3) material + print-time economy (thin faceted walls, no infill, modular reprints); 4) modularity |

## 4. Environmental + functional requirements

| Req | Statement | Verification |
|---|---|---|
| F-01 | Rain shall have no sight line to any opening at any angle ≥ horizontal | Section render + hose test on printed unit |
| F-02 | All primary apertures face down or into bract rain-shadow (AirGradient pattern: down-only is the benchmark) | Geometry review |
| F-03 | Passive chimney: intake low (BME680 zone), exhaust high (XIAO zone); XIAO/regulator heat must not bake the BME680 | Temp cross-check vs reference sensor after deploy |
| F-04 | HM3301 fan gets a dedicated aperture path; can ports face down/sideways per datasheet, never up; inlet and outlet airflow separated; ports close to product aperture | Geometry review + PM co-location sanity check |
| F-05 | USB-C exits downward with drip loop space | Geometry review |
| F-06 | Keyhole wall mount behind boards: hang shell first, boards in after (v4 pattern, validated) | Hang test |
| F-07 | Insect mesh on all apertures, replaceable at monthly service | Service rehearsal |
| F-08 | Monthly service one-handed: bayonet open, mesh + battery check, close — no tools, nothing dropped | Service rehearsal on ladder |
| F-09 | Workshop-printable: support-free, fits 220 × 220 bed, ≤ 2 print plates per variant | Slicer report |
| F-10 | No text labels on parts; components locate by printed footprints (real outlines, real pin patterns — v5.1 spec) | Assembly rehearsal by a non-expert |

## 5. Printer truth (Tomas's machine — prototyping reference)

| Item | Value |
|---|---|
| Printer | Prusa CORE One, enclosed chamber |
| Nozzle | HF 0.4 mm (high-flow) |
| Bed | 250 × 220 × 270 (workshop constraint remains 220 × 220) |
| Slicer | PrusaSlicer 2.9.5, CLI in loop |
| Material profile | Generic PETG @COREONE HF0.4 |
| Draft profile | 0.15mm SPEED (prototypes) |
| Finish profile | 0.15mm or 0.10mm QUALITY-class for visible bract surfaces (seam paint/rear, slowed external perimeters) — to be defined at first skin print |

### 5.1 Fit numbers — **INFERRED (Tomas waived coupon measurement, 2026-06-11)**

Derived from Prusa CORE One + Generic PETG @HF0.4 published behavior and community
tolerance data, NOT measured. Confidence ±0.1 mm. **Mitigation: the press-fit rim
SECTION PRINT is the de-facto coupon — it validates COUPON_TBD_STACK before any full
module prints.** If the section print binds or rattles, adjust here and regenerate.

| Parameter | Inferred value | Basis |
|---|---|---|
| Sliding fit clearance (per side) | **0.25 mm** | ±0.2 mm FDM deviation; 0.2 binds when seams land in the joint |
| Free fit clearance (lids, inserts, per side) | **0.40 mm** | 1× extrusion width rule |
| Stack press fit `COUPON_TBD_STACK` (spigot/socket, per side) | **0.15 mm** | long-perimeter PETG press: 0.1 jams, 0.2 is a slide |
| ~~Press-fit pegs in Ø3.2 PCB holes~~ **VOID 2026-06-11** — no Ø3.2 holes on the HM carrier (Eagle file); retention = rails + edge capture | — | see component table |
| M2 self-tap pilot `COUPON_TBD_PILOT_M2` | **Ø1.75** | standard M2 self-tap in printed boss |
| HM rail slide `COUPON_TBD_SLIDE` | **0.30 mm** | sliding + seam allowance on long rails |
| Vertical hole shrink | **design +0.2 mm dia** | holes print undersized (nozzle path) |
| Horizontal hole shrink | **design +0.3 mm dia; expect oval (height < width)** | gravity sag on horizontal bores |
| Max clean overhang angle | **50° from vertical** (design to 45°) | enclosed chamber + PETG cooling |
| Min self-supporting edge thickness | **0.8 mm** (2 perimeters) | HF0.4 perimeter pair |
| Elephant-foot compensation | **0.4 × 45° chamfer on all bottom edges** | ~0.2 mm first-layer spread |

## 6. Wall + structure rules (from AirGradient teardown, 2026-06-08)

Measured from their published outdoor enclosure STLs (`ref_airgradient/`, CC BY-SA 4.0):

- **Nominal wall: 2.5 mm** (their median 2.49–2.82; we adopt 2.5). Not 1.6. This is half the gap between "prototype" and "product."
- Bosses/ribs: 4–6 mm where fasteners or stress concentrate.
- Their architecture: perforated functional floor + collar + blind slide-over hood; **structure and weather skin are separate parts**. Validates our v4-core + bract-skin split.
- Every fillet visible. No raw cylinder bosses, no knife-edge wall junctions in the rebuild. Min visible fillet R1.5; structural junctions R2+.

## 7. Validated architecture carried forward (do not re-litigate)

From v4/v5 (see `archive/`): vertical HM3301 in front rails beside perfboard; keyholes behind boards; footprint guides (XIAO outline + 2×7-pin rows @2.54 + USB-C oval; BME680 outline + 6-pin row; battery frame); chimney stack BME-low/XIAO-high; apertures in bract rain-shadows. **Correction 2026-06-11: the v4/v5 "2 pegs into carrier Ø3.2 holes" was wrong — the Eagle file shows no such holes; HM module retention is rails + edge capture.**

## 8. Process gates (how this stays professional)

1. **Coupons before fits** — §5.1 filled, then CAD.
2. **Slicer in loop** — every candidate STL gets a PrusaSlicer CLI report (time, mass, thin walls, seam, supports) before Tomas sees it. No STL ships without it.
3. **Multi-view render + watertight gate** — `tools/run_model.py --preview --strict` on every iteration.
4. **Section prints before whole prints** — bayonet ring alone, one bract band alone, grille alone. Plastic validates each interface; full body prints once.
5. **Checkpoint reviews** — base form → features → final, Tomas approves at each gate (cad-skill pattern). No full-fidelity surprises.

## 9. Open items

| ID | Item | Owner | Status |
|---|---|---|---|
| OPEN-01 | DEC-05 variant strategy sign-off | Tomas | ✅ resolved v1.3: two bodies |
| OPEN-02 | Failure decomposition of previous prints (surfaces / fits / gestalt) + photos | Tomas | ⏭️ waived 2026-06-08 (Tomas: proceed on coupons alone) |
| OPEN-03 | ~~Banana flower reference~~ → superseded by meru form (DEC-09) | — | closed |
| OPEN-04 | Coupon measurements → §5.1 | — | ✅ closed-by-inference 1.12 (Tomas waived; §5.1 INFERRED ±0.1; **rim section print = de-facto coupon, still gates full modules**) |
| OPEN-05 | PETG brand/color for final units (Generic profile now) | Tomas | pending |
| OPEN-06 | Section prints of bayonet / reveal band / crown skirt before full Plus | Tomas prints, review | pending |
| OPEN-07 | ~~Phase-2 kawung pattern~~ → replaced by v2 chevron-louver skin (DEC-12) | — | closed |
| OPEN-08 | Section-print one chevron louver band — confirm down-out overhangs print clean (Pucuk base+neck sections sliced support-free, `pucuk/sections/`) | Tomas | STL ready, print pending |
| OPEN-09 | Lighten spine_plus (38 g/2h15 solid back plate) — rib + DRAFT profile | Claude | pending |
| OPEN-10 | v2 fits (bayonet, rails, back-lip capture, crown legs) ← coupons §5.1 | Tomas + Claude | pending |
| OPEN-11 | Pick Plus concept direction (C1 Pucuk / C2 Anyaman / C3 Tumpang massing) — gates the fidelity build → **C1 Pucuk**, fidelity build done, form LOCKED 2026-06-08 | Tomas | ✅ resolved |
| OPEN-12 | **Hardware / fastener BOM** (Tomas 2026-06-11): wall screws (keyholes), module-lock choice (press-fit detent vs 2× M3), board retention (M2 heat-set inserts in PETG standoffs), HM3301 module retention = rails + edge capture, optional 2× M2.5 through-screws into can (**Ø3.2 peg holes DO NOT EXIST — Eagle file 2026-06-11**), ePTFE membrane + insect-mesh seats. Model real hardware + a qty/size/source BOM. | next agent | pending |
| OPEN-13 | **Printed board placeholders / footprint guides** (Tomas 2026-06-11): debossed XIAO/BME680/HM3301 outlines + pin rows + USB-C oval + peg positions, cable route + strain relief + Grove clearance up the central pass-through, mesh seats. Locate by footprint, no text (F-10). Carry the v4/v5.1 footprint-guide idea forward. | next agent | pending |
| OPEN-14 | v12 modular: integrate gyroid into module side windows (cap technique proven); inter-module cable route; Plus rail ±22 bump; press-fit rim section print after §5.1 | next agent | pending |

## 10. Change log

| Version | Date | Change |
|---|---|---|
| 1.0-DRAFT | 2026-06-08 | Initial spec from handover §1 + frozen DEC-01…08 + AirGradient teardown numbers |
| 1.1-DRAFT | 2026-06-08 | DEC-01 re-frozen by Tomas: banana flower → batik-fractal meru (tiered self-similar form, pierced batik-derived vent bands, organic profiles). Engineering decisions DEC-02…08 unchanged; USB-at-tip superseded (silhouette freed — cable exit returns to underside, F-05 unchanged). Jantung arc archived: `archive/concept-jantung-2026-06/` |
| 1.2-DRAFT | 2026-06-08 | DEC-09: Tomas picked N1 lima (5 roofs) as Phase-1 base form, after gen3 retune (crisper flatter roofs, murda spire). Meru arc: gen1 ground-up taper rejected (pine tree), gen2 body+crown composition, gen3 approved |
| 1.3-DRAFT | 2026-06-08 | DEC-03 refined (bottom bayonet cap + screwed crown — wall blocks crown rotation); DEC-05 resolved by Tomas: two bodies, Plus first. Functional CAD authorized with placeholder clearances as named COUPON-TBD parameters; nothing fit-critical prints before §5.1 is measured |
| 1.4-DRAFT | 2026-06-08 | Direction reset (Tomas, post-handover): v2 four-part chevron-louver skin (DEC-10/DEC-12) retired as the frozen form — explore 2–3 fresh concept massing studies for the Plus body instead. Retained: faceted/triangulated principle (DEC-11), two bodies / Plus-first (DEC-05), all performance priorities (DEC-13), validated internals (§7). OPEN-02 failure-photo decomposition waived by Tomas — proceed on coupon numbers alone. New gating design decision = concept pick (OPEN-11) |
| 1.5-DRAFT | 2026-06-08 | C1 Pucuk built at fidelity (`tools/enclosure_pucuk.py`) and base-form gate CLEARED by Tomas — silhouette LOCKED. Twisted faceted octagonal shard (85° twist), fractal-graded louver bands, sealed side-venting finial, faceted inner cavity, validated candi internals transplanted, bottom bayonet. Watertight, interference 0.000 cm³, support-free (slicer); 82×71×129 mm; body 84.6 g/3h36m + cap 10.8 g/23m. Mass parked (grams are in the 2.5 mm wall perimeters of a tall shell, not the cavity). Section test-prints sliced support-free in `pucuk/sections/`: base (bayonet+floor+intake louvers, 32 g/1h21m), neck (exhaust louvers+finial, 22.6 g/1h). DEC-01 form ref now = Pucuk. |
| 1.6-DRAFT | 2026-06-09 | Research-grounded reset (`DESIGN_RESEARCH.md`: 22 designs) + `outdoor-sensor-enclosure` skill. DEC-05 superseded by Tomas: ONE SHARED PLATFORM — Basic = Core (brain + BME680 radiation-shield bay + hood + cap); Plus = Core + a stacked HM3301 PM-duct module that physically separates the PM air system from the T/RH system. Core/Basic built (`tools/enclosure_v6.py` → `v6/`): 56×45×102 mm, watertight, interference 0.000, support-free; body 50.8 g/2h17m + cap 5.9 g/17m. BME680 moved LOW into a down-louvered, foil-lined front bay; XIAO HIGH so the chimney carries MCU heat away; firmware T-offset planned. Hood drip-lip, side exhaust louvers, 2.5 mm weep, ePTFE membrane boss. Pucuk/efficient shards retired. NEXT: Plus PM-module; optional full stacked-disc shield pod; coupons gate fits. |
| 1.7-DRAFT | 2026-06-10 | **v8 PRINTED → FAILED → v9 architecture reset.** v8 fused the hood to the body (sealed monocoque, no board-access path — Ø32.6 bayonet bore < 40×60 perfboard) and printed the cavity floor as a ~43 mm unsupported bridge that collapsed (see `HANDOFF_v9_redesign.md`). v9 (`tools/enclosure_v9.py` → `v9/`) splits the design into THREE printed parts: (a) **body** — open-top AND open-bottom hollow tube, all validated v8 internals carried verbatim (standoffs, keyholes, gyroid window, HM rails+pegs, exhaust slots, ePTFE boss, can grille + down PM duct); (b) **hood** — separate domed crown, 2× M3 into top-rim bosses (restores the DEC-03 crown release v8 dropped), prints flat-base-down; (c) **base plate** — full-footprint, prints flat on the bed (kills the floor bridge), carries the 4 feet + mesh-grille intake + angled USB-C chase + weep, mates via a **press-fit spigot** (`COUPON_TBD_PRESSFIT`). DEC-03 base attach: bottom bayonet → **press-fit** (Tomas, 2026-06-10), bayonet deferred to a section test. STAGING build: both variants watertight single solids, interference 0.000, fit the bed (basic 50×40×86 / plus 50×52×96; bases ~48×52×11). **NOT FOR PRINT — §5.1 still TBD.** rev2 (Tomas review, same day): **feet REMOVED** — they hung below the grille and forced a feet-down print that re-creates the v8 unsupported-floor span; node is wall-hung on keyholes, never rests on feet, so base now prints grille-down (grille = supported first layer). Intake **doubled** (~30×30, 6 slots) on a **full 2.5 mm wall-thickness grille floor** + a real **2 mm seat** for a drop-in mesh/grid panel. rev3 (Tomas review, same day): the BME680 breathing-window insert is now a **35×35×7 plate** (`tools/breathing_panel_v9.py` → `v9_breathing_panel.stl`, gyroid vent + 2.5 mm solid border, watertight, 48% open) that **slides into a vertical rail on the outside of the window wall and grips by friction** (`COUPON_TBD_RAIL`), replacing the seat-against-a-ledge rebate. Rail is outboard because an inward mount leaves only ~1.5 mm to the Plus BME680. Plate-in-rail fit checked = 0.000; one plate fits both variants; body footprint grows on the window axis (basic +Y, plus −X). |
| 1.8-DRAFT | 2026-06-10 | **v10: organic shell + base breathing + sensor-layout review** (`tools/enclosure_v10.py`, `breathing_panel_v10.py`, `dimension_render.py` → `v10/`). Sensor set confirmed by Tomas = **current build** (XIAO ESP32-S3 + BME680 + HM3301; no SEN54 — repo README/firmware run this; SEN54 still validation-pending). Three changes: (1) **breathing relocated to the BASE** — side window retired; bottom is now a large drop-in gyroid panel (Basic vent ~35×25, Plus ~35×37), BME680 dropped LOW (bme_z 30→26) into the base-intake stream, XIAO high, base→top chimney; (2) **HM3301 envelope corrected 80×40 → ~40×40×16** (the 80×40 was schematic-only, never a mechanical drawing — see §2 flag, caliper-confirm); (3) **organic shell over kept guts** (Tomas's choice) — softly-lofted front-leaning pod, flat back retained, soft corners; width held constant so the perfboard always fits; all validated internals carried verbatim. Mounting strategy: one 40×60 perfboard (XIAO+BME on headers) + HM3301 as the only separate module in front rails. Both variants watertight single solids, interference 0.000 incl. seated base panel; basic 50×42×84 / plus 50×54×94; bases ~48×52×11. **Dimensioned to-scale layout maps** added (`v10_*_layout.png`) so fits read in mm. Map flags: HM3301 40-wide in a 43 cavity = ~1.5 mm/side (tight). **NOT FOR PRINT** — §5.1 TBD, HM envelope caliper-confirm, organic form is a first pass. |
| 1.9-DRAFT | 2026-06-11 | **v11: corrected two-system airflow** (`tools/enclosure_v11.py`, `breathing_panel_v11.py` → `v11/`; analysis in `AIRFLOW_REVIEW_v10.md` + `v10/review/v10_airflow_review.png`). Tomas flagged v10 circulation as wrong — confirmed four errors: throttled chimney (huge base intake + tiny low exhaust → diffusion), PM air re-merged with climate air (lost F-04), HM3301 inlet/outlet not separated (recirculates), XIAO+HM heat biasing BME. Fixes: (1) climate HIGH exhaust enlarged + raised both sides to area ≥ intake open (basic 420 vs ~420 eff; plus 420 vs ~277 eff → balanced/exhaust-biased); (2) full-height **baffle** re-separates back climate column (perfboard/BME/XIAO) from front PM bay (HM3301); (3) HM gets a **separate base fresh-intake grille + separate front-wall exhaust** (120 mm²) so it stops re-ingesting exhaust; (4) BME low in intake, XIAO high. Both variants watertight, interference 0.000. Organic surfacing DEFERRED to Rhino (mcneel/rhinomcp, see `RHINO_MCP_SETUP.md`); v11 keeps v10's first-pass shell. **NOT FOR PRINT** — §5.1 TBD; **HM3301 envelope + can-port inlet/outlet mapping caliper-confirm** (the aperture separation is architectural; physical in/out mapping needs the real unit). |
| 1.10-DRAFT | 2026-06-11 | **HM3301 size correction — 80 × 40 × 18 confirmed by Tomas.** The v10/v11 "correction" to ~40×40 was wrong (I wrongly dismissed the original 80×40 as schematic-only); the original ICD figure was right. Reverted in `enclosure_v11.py`: HM module 80×40×18, mounted vertically. Plus body refit to accommodate the 80 mm-tall module: FRONT 36→40, FRONT_IN 33.5→37.5, body_top 94→110, front lean reduced to 2 mm (was 9) so the tall front-bay sensor clears the leaning front wall. Rebuilt: both variants watertight, interference 0.000 (incl. the 80×40×18 HM); Plus now 50×58×110. Airflow (baffle + separate PM intake/exhaust + balanced high exhaust) preserved, PM exhaust raised to suit the taller can. Dimensioned map updated (`v11/review/v11_plus_layout.png`). Lesson: don't override a sourced dimension on assumption — caliper/measure first. |
| 1.11-DRAFT | 2026-06-11 | **v12: MODULAR STACKING SYSTEM** (`tools/enclosure_v12.py` → `v12/`). Major architecture shift (Tomas): not one body with variants but a **tower of interchangeable tier-modules** on one standard **press-fit keyed-rim** interface (bottom spigot → open-cavity socket, `COUPON_TBD_STACK`, central air+cable pass-through, flat back + keyholes). Stack grows with sensor count + indoor/outdoor. Decisions: modules are **clean gyroid-window boxes, only the crown has meru eaves/finial**; **press-fit** join; **indoor top = low gyroid-vented cap**. Parts (common 46×26 footprint): Basic (XIAO+BME, base intake, 46×26×58), Plus (HM3301 80×40×18 + own PM intake/exhaust, 48×26×99), Crown (faceted 3-tier meru, eaves to 66×50, 40 tall), Cap (low gyroid cap, 29 tall). All watertight, interference 0.000. Variants: indoor Basic (Basic+cap ~80mm), outdoor Basic, indoor Plus, outdoor Plus (~197mm meru tower). Airflow: base intake → central cavity + per-module gyroid side windows → crown/cap exhaust; Plus PM bay keeps its own front intake+exhaust (v11 two-system, per-module). Crown form developed live in Rhino then rebuilt parametrically. NOT FOR PRINT. Open: gyroid drop-in panels per window; inter-module cable route; Plus rail ±22 bump (tuck/widen 2mm); optional quarter-turn detent; §5.1. |
| 1.12-DRAFT | 2026-06-11 | **§5.1 filled with INFERRED values (Tomas waived coupon measurement)** — derived from Prusa CORE One + PETG community tolerance data, confidence ±0.1; the press-fit rim SECTION PRINT becomes the de-facto coupon. `COUPON_TBD_STACK` 0.20→0.15. **HM3301 module geometry fully resolved without calipers**: HM-3300/3600 datasheet V2.1 (can 40×38×15, both air ports on one 40×15 narrow face one per end, isolate in/out, never face up) + Seeed Eagle .brd parsed (board exactly 80×40; can footprint X −25.39..+14.61 → 14.6 clear at Grove end / 25.4 at electronics end; Grove 4P exits left short edge; **NO Ø3.2 mounting holes — only 2× Ø2.4 can-screw pass-throughs at (−23.62,−17.02)/(+12.57,+17.14), M2.5 into can bottom**). Consequences: §5.1 peg row VOID, retention = rails + edge capture (+optional M2.5); PM ducts designed mirror-symmetric since in-vs-out port direction is unlabeled — confirm by feel at power-up, build works either way. Eagle ref saved to `ref_hm3301_eagle/`. OPEN-04 closed-by-inference; OPEN-01 (can ports) closed-by-design. |

---
*References: `ref_hm3301_board.pdf` (Seeed Eagle dims), `ref_airgradient/` (CC BY-SA 4.0 AirGradient Co. Ltd.), `archive/` (v1–v5.1 lessons), AirGradient Open Air assembly docs, HM3301 datasheet siting rules.*
