---
name: outdoor-sensor-enclosure
description: >-
  Design additive-native 3D-printed product enclosures for electronics / environmental
  sensor nodes (air quality, weather, IoT) that must breathe, stay dry, read true
  ambient, AND look like a designed product. Use when housing a PM / temp-humidity /
  gas sensor + MCU for outdoor deployment — especially tropical/monsoon — where
  airflow, water exclusion, sensor accuracy, 3D-print manufacturability, zero-hardware
  assembly, and product-grade finish all matter at once. Triggers: "design an
  enclosure", "weatherproof housing", "sensor case", "radiation shield", "vented
  enclosure", "make it look like a real product", "use the best of 3D printing".
  Carries Design-for-Additive-Manufacturing (DfAM) + product-design craft, a
  fail-closed printability gate (NEVER print filament into open air — orientation
  and support are calculated for every part before it slices), and a Rhino /
  Rhino-MCP organic-surface workflow. Pairs with the build123d + Rhino + gyroid
  (marching-cubes / Grasshopper) + PrusaSlicer toolchain.
---

# Additive-native sensor-enclosure / product design

**The core principle: design what could only be 3D printed.** If the part is a box
with a lid, screws, brass inserts and a bought gasket, you designed an
injection-mold and printed it — that wastes the medium. An additive-native part
uses **print-in-place mechanisms (no hardware), lattices that are structure +
ventilation + shade at once, monocoque forms whose shape sheds water, and sealing
that is printed geometry.** Function and the print process are the form-givers; the
result should look intentional, not like an engineer's box.

## Process (unchanged, still law)
1. Research before CAD (DfAM + the domain). 2. Write the 4-fundamental spec with
numbers. 3. Let function + the print process author the form. 4. **Verify in plastic
early** (coupons, section-prints). 5. **Checkpoint with the human** at base-form →
features → final. Don't render-spiral; don't hand over a box and call it done.

---

## DfAM toolkit — the additive-native moves (with numbers)

### A. Zero-hardware assembly (no screws, inserts, or bought gaskets)
- **Print-in-place bayonet / twist-lock** = the default weatherproof closure: support-free, no fasteners, fast service, seals behind a lip. Clearance **0.4–0.5 mm** (≈1–1.25× extrusion width) frees the parts with a first twist.
- **Cantilever snap latches:** PETG, **L/h ≈ 10:1**, ~1 mm thick, deflect ~10% of length, **taper to 0.5× at the tip**, **root fillet ≥ 0.5× thickness**, **lead-in 15–30° / return 30–45°** (reusable) — size to **~1.8% working strain** (0.6× the reuse-derated allowable). **Print flexing features FLAT in XY** (never standing in Z — ~50% weaker across layers).
- **Segmented annular snap (3–4 arcs)** for round lids: 360° hold, low open force, add a finger nib.
- **Print-in-place pin hinge:** axle bore **cut at the 40° overhang point (>60% circumference intact)**, ~1 mm bridge fins, 0.4–0.5 mm clearance. Living hinges (0.4–0.6 mm web, length 8–12× web) only for **low-cycle** doors — FDM PETG hinges are hundreds of cycles, not molded-PP's 100k.
- Threaded fasteners are the fallback only: as-printed threads **≥ M6** for a screw cap; one heat-set insert (M3 → 4.0 mm hole, wall ≥ 1.6 mm) only at a high-load, frequently-opened joint.

### B. Lattices as function (the signature additive move)
- **Sheet (walled) gyroid = one surface that is structure + ventilation + sun-shade + rain-baffle**, because a gyroid has **no straight line of sight** — air threads the helical channel, photons and droplets hit wall. Generate it (see toolchain): start **cell ~6–8 mm, wall ~1.0–1.5 mm, ~60–70% porosity**, keep open pores **≥ 2 mm** (print open + shed water, not hold a film).
- **Grade porosity by function** (only additive gives this): denser/thicker on the sun- and rain-facing side; open on the shaded intake and the PM-sensor port.
- **IR caveat:** filament is IR-transparent — a gyroid shades *visible* sun but the T/RH sensor still needs a **reflective foil liner + 2–3 mm air gap** behind the lattice.
- Solid gyroid infill (15–25%) inside closed structural walls = stiff, low-warp, light.

### C. Monocoque + orientation-as-formgiver
- **Pick the no-support orientation first; let it be the form.** Print upright, dome/cone up; a self-supporting sloped shell **sheds rain because of its shape** (the form *is* the rain hat).
- **No flat top** (water sits and wicks the layer lines) — dome or slope it. **Teardrop every horizontal hole.** **Chamfer downward-facing edges (45°), fillet seen/touched edges.** Stiffness from **curvature/flutes**, not wall mass. Layer lines run horizontal → shed sideways; keep the **Z-seam off weather faces**, in a designed gutter.

### D. Printed weatherproofing (breathe, don't seal)
- **Roof, don't seal:** overhanging eave/shingle, **≥8–10 mm skirt overlap**, **30–45° shed**, parting line faces down-and-out. **Drip edge:** sharp (un-filleted) bottom lip + a 1–2 mm groove to break the water film.
- **Labyrinth tongue-and-groove**, **groove female-DOWN so it can't fill**: tongue 1.2–1.6 mm, +0.2–0.25 mm/side, engagement 3–5 mm. **Downward louvres ≤45°, slots ≥1.5–2 mm.**
- **Don't seal airtight** (tropics → condensation trap): pressure-equalize + drain (weep 2.5 mm at the low point). Watertight wall recipe when needed: **4 PETG perimeters, 0.15 mm layers, nozzle +5–10 °C, flow +5–10%, Linear Advance OFF, staggered inner seams**.
- **Still bought, honestly:** a fine insect mesh scrap (FDM can't print mosquito-grade apertures — a printed infill-pattern grille only does ~1–2 mm holes), a cable gland (the #1 leak path), and an ePTFE vent only if you must jump to IP65+.

### E. Product-design craft (box → designed product)
- **A radius SYSTEM** (e.g. R1 inner / R2 standard / R4 corner) on every edge — no raw 90°.
- **1–2° draft** on tall walls; **lifted base / feet**; a **0.5–1 mm shadow-gap reveal** at the lid line.
- **Painted fuzzy skin** on the body (hides layer lines + seam, reads as matte soft-touch), smooth on mating faces; **monotonic top + ironing** on flats.
- **Openings on a shared grid**, aligned, equal margins. **Tight CMF:** one matte body colour + one accent.
- **System over one-off:** Basic and Plus share one radius scale, one vent module, one closure, one CMF → they read as a product family (Gridfinity/Framework lesson). Beauty is a consequence of solving function cleanly under a small rule set (Bambu/Prusa).

---

## 3D-printing law — NEVER print into air (fail-closed gate)

**The single hardest rule: no part reaches the printer until its orientation is
chosen and every gram of filament has solid geometry, a self-supporting feature,
or the bed underneath it.** Filament extruded over open air — an overhang nobody
checked, a bridge too long, a feature whose first layer floats — is a failed print
and a part you can't trust for a weatherproof seal. This is the *model's* job to
never need rescuing, **not the slicer's job to patch with auto-support.** The gate
fails closed: if a part can't pass, it is **reoriented or redesigned, never shipped
with supports as a crutch.**

- **Orientation is decided in the model and declared per part.** Pick the
  no-support orientation FIRST (it's also the form-giver, §C). State which face is
  on the bed and *why* that orientation is support-free. If no orientation is
  support-free, the part is split or redesigned — not propped.
- **Overhang gate.** Map every downward-facing surface; each must sit at **≥ the
  material/printer self-support angle** (default **≤45° from vertical**). Anything
  shallower needs a *designed* fix in the model — 45° chamfer, fillet, teardrop
  hole, gusset, sacrificial rib — **not slicer support.**
- **Bridge gate.** Every unsupported horizontal span ≤ the **coupon-measured max
  bridge** (**≤5 mm until measured**). Longer → add a bridge anchor / centre pillar,
  reorient, or split the part. A *deliberately modelled* print-in-place bridge
  (e.g. a hinge-bore fin) counts as designed geometry — it must be in the CAD, not
  generated by the slicer.
- **Island / floating-feature gate.** No disconnected geometry on any layer — no
  feature that begins mid-air with nothing beneath it. Step through the slicer's
  bottom-up layer preview; a first layer that floats is a redesign, not a support
  candidate.
- **Slicer gate (the hard stop).** The G-code **`;TYPE:Support` count MUST be 0.**
  If the slicer inserts support, the orientation or the geometry is wrong →
  reorient or redesign and re-slice. Support material is never an accepted shipping
  state for these parts.
- **Per-part Print Plan — required before "done":** (1) bed face + orientation;
  (2) overhang map: every face ≥ self-support angle, or the named fix for each;
  (3) max bridge span vs. coupon limit; (4) Z-seam location (off weather faces, in
  a designed gutter); (5) first-layer adhesion / brim note; (6) supports = 0
  confirmed in the slicer report. **No Print Plan, no print.**

---

## Domain rules — the enclosure fundamentals (still apply)
- **Don't bury the T/RH sensor** — shield it (lattice/louvre + foil liner + air gap) or externalize it; buried sensors read +2.7…+5.3 °C hot. Bali is low-wind → consider micro-aspiration (25–80 mA).
- **PM sensor on its own dedicated, separated, down-facing duct**; sense RH at its inlet; correct PM for RH in the dashboard.
- **Two zones:** sealed/conformal-coated electronics brain + a breathing sensor zone; never one airtight box.

## Toolchain
- **build123d** (BREP) for solids; `run_model.py --preview --strict` (6-view + watertight); **PrusaSlicer CLI** report (time, mass, `;TYPE:Support` MUST be 0) on every STL. No STL is "done" without its slicer report AND its Print Plan (see the printing-law gate).
- **Gyroid pipeline (proven):** numpy field `g = sin x cos y + sin y cos z + sin z cos x`; **sheet = marching_cubes(|g| − t)** via `skimage.measure` → `trimesh` → STL; spatially vary `t` for a solid frame at panel edges and open centre; combine with the BREP body as a snap-in panel (avoid fragile mesh↔BREP booleans) or union via `manifold3d` (installed in the `.cad-venv`, works).
- Run all CAD/render/slice on the Mac; never git in the sandbox; clearances stay `COUPON_TBD_*` until coupons measured.

### Rhino + Rhino-MCP (organic skin) — paired with build123d (fits)
Use **two tools, each for what it's best at — don't fight one to do the other's job.**
- **Division of labour.** **Rhino owns the organic / aesthetic surfaces** the BREP
  kernel can't author cleanly: the meru crown, monocoque shells, SubD/NURBS skins,
  swept eaves, blended multi-edge fillets. **build123d owns the functional solids:**
  fits, bores, snap features, parametric clearances (`COUPON_TBD_*`), interference
  checks, STEP. Rhino makes it beautiful; build123d makes it fit.
- **Tools (Rhino-MCP-Platform 0.1.5, via the Cowork Rhino connector).** `run_python`
  (rhinoscriptsyntax / RhinoCommon) and `run_csharp` for geometry; `run_command`
  for native commands; **`get_viewport_image` to actually SEE the model** — treat it
  as the render-check, the Rhino equivalent of run_model's 6-view; `list_objects`,
  `set_camera`, `zoom_to_object`, `zoom_to_layer` to inspect; `set_layer_material`
  for CMF preview; **the `g1_*` family to drive Grasshopper** (`g1_start`,
  `g1_place_component`, `g1_place_slider`, `g1_connect[_many]`, `g1_solve_graph`,
  `g1_apply_graph`, `g1_search_components`, `g1_get_canvas_graph`). **Cold-start
  calls time out — retry once after a few seconds.** Setup notes live in
  `RHINO_MCP_SETUP.md`.
- **Lattices in Grasshopper** = the live-tunable alternative to the numpy
  marching-cubes pipeline: build the gyroid as a parametric GH definition (cell,
  wall-thickness, porosity sliders), tune it on screen with the human, then bake →
  mesh. Use whichever path is faster for the part; both must clear the print gate.
- **Handoff is watertight or it doesn't count.** Export Rhino → **STEP** (into
  build123d for the functional merge) or → **mesh STL** only after `Check` /
  `MeshRepair` confirms closed, manifold, **zero naked edges**. Prefer a **snap-in /
  keyed interface** between a Rhino skin and a build123d core over a boolean —
  mesh↔BREP booleans are fragile; union only via `manifold3d` when unavoidable.
- **The Rhino part takes the SAME printability gate.** A pretty `get_viewport_image`
  is **not** a substitute for the overhang map + slicer `;TYPE:Support`=0 + Print
  Plan. Organic skins are the easiest place to sneak in a shallow overhang or a
  floating finial — check orientation and supports before it slices, every time.
- Run Rhino on the Mac (the connector talks to the local instance); never git in the sandbox.

## Hard lessons (don't repeat)
- **Don't design molding-logic boxes.** Lid + screws + inserts + bought gasket = the failure. Use print-in-place + lattices + printed seals.
- **Don't form-find for its own sake** either — the additive moves must serve function.
- **Don't trust renders** — coupons, section-prints, hose test.
- **Right-size to the boards**, and **make the closure hardware-free**.

## Verification checklist
- [ ] 4-fundamental spec written + signed off.
- [ ] **Additive-native:** zero/minimal bought hardware? a lattice or print-in-place feature doing real work? self-supporting form that sheds water?
- [ ] **Craft:** one radius system, lifted base, shadow-gap, fuzzy/CMF, openings on a grid, Basic+Plus a family?
- [ ] Watertight; interference 0.000; ≤ envelope.
- [ ] **Print gate (every part, fail-closed):** orientation declared; overhang map all ≥ self-support angle (or named designed fix); bridges ≤ coupon limit; no floating islands; slicer `;TYPE:Support` = **0**; Print Plan written. Rhino-authored parts pass this too — viewport image ≠ proof.
- [ ] T/RH shielded + isolated (+ foil/air-gap if lattice); PM duct separated.
- [ ] Eave + drip + labyrinth + weep; mesh removable; not airtight.
- [ ] Coupons measured → fits no longer `COUPON_TBD_*`; section-prints validated; hose test passed; reviewed in hand.
