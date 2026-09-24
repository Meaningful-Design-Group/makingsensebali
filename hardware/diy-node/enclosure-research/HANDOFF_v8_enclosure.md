# Handoff: Making Sense Bali DIY-node enclosure — v8 (deliver a *good*, printed enclosure)

**From:** Claude (Cowork session with Tomas Diez, June 2026)
**To:** the next agent
**Mandate:** Use the `outdoor-sensor-enclosure` skill and the proven gyroid pipeline
to design a **genuinely good, additive-native, product-grade** enclosure for the
DIY node — **both variants** — and **get it into plastic and validated.** Seven
design generations have happened. Tomas has rejected the last four. **None of the
seven were ever printed.** That is the failure to break.

Repo: `hardware/diy-node/enclosure/` · local: `~/Documents/Claude/Projects/MDG/smartcitizenbali/`
Hardware being enclosed: https://github.com/Meaningful-Design-Group/makingsensebali/tree/main/hardware/diy-node

---

## 0. Read this first — why you exist

The enclosure has been redesigned seven times and rejected repeatedly. The honest
pattern of *why*:

- **v1–v5 (OpenSCAD):** "programmer geometry," guessed tolerances, printed badly —
  "disappointing and unprecise."
- **Pucuk / efficient (build123d):** I chased *form* ("does the twist read?") and
  then shipped a plain box. Tomas: *"too much focus on the form finding."*
- **v6 (efficient box):** competent but, in his words, *"a terrible design… I don't
  see how this is using the best of 3D printing technology."* It was an injection-
  molded box printed on an FDM machine — lid, bayonet, walls. Mold-thinking.
- **v7 (additive-native):** finally the right language — a monocoque shell, a
  sheet-gyroid breathing skin, zero-hardware closure, product craft. **But still
  only rendered, not printed.**

Two failure modes to never repeat: **(a) designing a box with a lid** (mold logic
instead of additive-native), and **(b) designing only in renders and never
printing.** The skill fixes (a). Only you can fix (b). **If you produce a v8 that
is beautiful on screen and never touches a bed, you have failed exactly as I did.**

---

## 1. Use the skill — it is the capability, hard-won

Invoke **`outdoor-sensor-enclosure`** (installed; source in
`enclosure/outdoor-sensor-enclosure-skill/SKILL.md` + `reference.md`). It is a
Design-for-Additive-Manufacturing *product-design* skill, not a checklist. It
encodes, with numbers:
- **Additive-native moves:** print-in-place bayonet/snap (zero hardware — no
  screws, inserts, or bought gasket); **sheet-gyroid skin** = structure + vent +
  shade + baffle in one surface; monocoque forms whose shape sheds water.
- **Product craft:** a radius system, draft, lifted feet, shadow-gap reveal,
  painted fuzzy skin, one CMF, **Basic + Plus as a family.**
- **Weatherproofing by geometry:** eave + drip-edge + labyrinth + downward
  louvres + weep + ePTFE vent; **breathe, don't seal** (tropics).
- The domain fundamentals (below) and the verification checklist.

The evidence behind it: **`DESIGN_RESEARCH.md`** (22 real enclosures surveyed) and
**`DESIGN_RESEARCH_DFAM.md`** (DfAM + craft, cited). Read both. **Don't redo the
research** — extend it only if the node changes.

---

## 2. The hardware (ground truth — do not re-derive)

From `hardware/diy-node/README.md` + `schematic.svg`. **Two variants, one platform,
same firmware:**

- **Basic** — Seeed **XIAO ESP32-S3** + **GY-BME680** on a **40 × 60 mm perfboard**. 5 V/1 A. Indoor/T-RH-VOC/mold/dengue/heat.
- **Plus** — Basic **+ Grove HM3301** PM sensor. 5 V/2 A (fan ~80 mA peaks). Outdoor PM.

Verified component dimensions (mm) — trust these (ICD §2; HM3301 from Seeed Eagle `ref_hm3301_board.pdf`):

| Component | Dimensions | Notes |
|---|---|---|
| XIAO ESP32-S3 | 21 × 17.8 | USB-C on a short edge |
| GY-BME680 breakout | ~16 × 12.5, 6-pin | clones ±2 mm — size to envelope |
| Perfboard | 40 × 60 × 1.6 | both boards on female headers; 5×7 (50×70) is a parametric option |
| HM3301 module (Plus) | carrier **80 × 40 × 1.6**; 4× Ø3.2 holes at (±36, ±16); metal can **40 × 38 × 15.2** on top | can ports face **down/side, never up**; Grove socket left, 1.25 mm pigtail right |
| USB-C | Ø~4.5 boot, bend radius ≥15 | exits **down**, drip loop |

I²C: BME680 `0x76`, HM3301 `0x40`, shared bus, XIAO `D4`/`D5`. No battery in scope
(USB-powered; the README's LiPo is optional/future — confirm with Tomas).

The README itself prescribes the design intent, in Tomas's words: BME680 needs *"a
Stevenson-screen-like louvered approach,"* HM3301 inlet faces *"down or sideways,
never up,"* thermal isolation (a bare roof makes the BME680 read **15 °C high**),
conformal-coat the board.

---

## 3. The four fundamentals (binding spec — write them with numbers before CAD)

1. **Sensor airflow.** Passive chimney: cool ambient in low past the BME680, warm
   air (XIAO, regulator) out high. HM3301 has its own fan + its own air path.
2. **Self-heat / radiation — the one every version under-served.** The BME680 must
   be **shielded and thermally isolated** from the MCU and PM fan, or it reads
   **+2.7…+5.3 °C hot** (RH off −10…−24 %). Shield it (gyroid/louvre + **reflective
   foil liner + 2–3 mm air gap** — filament is IR-transparent) or externalize it.
   Bali is low-wind → passive error climbs; consider **micro-aspiration (25–80 mA
   fan on its own intake)** for reference sites; at minimum a firmware T-offset.
3. **Water + humidity.** No opening faces up. Down-louvres/gyroid, hood + **drip-
   lip curl**, **labyrinth (groove female-down)**, **2.5 mm weep** at the low
   point, an **ePTFE membrane vent** — and **do not seal airtight** (condensation
   trap). Bought, honestly: a fine **insect-mesh** scrap and a **cable gland** (the
   #1 leak path). Target IP54-by-geometry + breathe-and-drain, not submersion.
4. **Particulate path (Plus).** HM3301 on a **dedicated, separated, down-facing
   duct**; correct PM for RH **in the dashboard**, not firmware.

Hard constraints: **PETG** (workshop reality; ASA hood optional), **support-free**,
**≤ 140 mm tall**, **2.5–3 mm wall**, **zero/minimal hardware**, **Basic + Plus a
family**, **fab-lab-printable** in a workshop.

---

## 4. The agreed direction (v7 DNA — Tomas approved "balanced")

Build on this; don't restart it.

- **Monocoque shell** that sheds rain by its shape (domed hood + drip-lip), printed
  upright, support-free, right-sized to the boards.
- **Sheet-gyroid breathing skin over the sensor zone only** (clean monocoque
  elsewhere — Tomas chose "balanced," not whole-shell lattice). The gyroid is a
  snap-in panel; foil-lined with an air gap behind it for the BME680.
- **Zero-hardware closure** (print-in-place bayonet is proven and fine; a snap is
  also on the table). No screws, inserts, or bought gasket.
- **Product craft:** lifted feet, shadow-gap reveal, radius system, fuzzy-skin-
  ready, one CMF, so Basic and Plus read as one family.

Current best = **`v7/`**: `v7_basic_body` (50 g / 2h21m, watertight, support-free,
56×45×105), `v7_basic_cap`, **`v7_basic_gyroid_panel`** (the breathing skin, 4.5 g).
**`v7` has no Plus yet, and the gyroid panel's frame/snap needs a cleanup pass** —
that's your starting point, not your endpoint.

---

## 5. The toolchain works — use it, don't rebuild it (run on the Mac)

- **venv:** `~/Documents/Claude/Projects/MDG/.cad-venv` (build123d 0.10, OCP,
  trimesh, **scikit-image**, Pillow). Run everything with this interpreter.
- **build123d** (BREP) for solids — `tools/enclosure_v7.py` (additive-native Basic),
  `tools/enclosure_v6.py` (parametric Basic+Plus), `tools/enclosure_pucuk.py` /
  `enclosure_efficient.py` (the **validated internals**: HM3301 front C-rails + 2
  pegs into the Ø3.2 holes, perfboard back-wall standoffs, keyholes behind the
  boards, bottom bayonet — reuse verbatim).
- **Gyroid pipeline (proven):** `g = sinx·cosy + siny·cosz + sinz·cosx`; **sheet =
  `skimage.measure.marching_cubes(|g| − t)`** → `trimesh` → STL; vary `t` spatially
  for a solid frame + open centre. See `v7/v7_basic_gyroid_panel` and
  `v7/gyroid_test`. Combine with the BREP body as a **snap-in panel** (avoid fragile
  mesh↔BREP booleans; or union via `manifold3d`).
- **`tools/run_model.py --preview --strict`** — re-runs a generator, 6-view render,
  watertight gate. **`tools/preview.py`**, **`tools/mesh_io.py`** (merge-before-
  watertight).
- **Slicer in the loop (mandatory, every part):** PrusaSlicer CLI at
  `/Applications/Original Prusa Drivers/PrusaSlicer.app/Contents/MacOS/PrusaSlicer`,
  `-g part.stl --printer-profile "Prusa CORE One HF0.4 nozzle" --print-profile "0.15mm SPEED @COREONE HF0.4" --material-profile "Generic PETG @COREONE HF0.4" -o part.gcode`.
  Confirm filament(g), time, and **`;TYPE:Support` count = 0**. No STL ships without it.
- **Run all CAD/render/slice on the Mac via the Macos shell** (the sandbox has no
  GPU and blocked egress). **Never run git in the sandbox** (stale `.git/index.lock`
  blocks Tomas's next commit) — git only on the Mac.
- Keep every fit a named **`COUPON_TBD_*`** parameter until the coupons are measured.

---

## 6. Process — not optional (it's in the skill; here's the short version)

1. **Invoke the skill.** Read `ICD.md`, both research docs, and the `v7/` files.
2. **Coupons FIRST.** `coupons/` is sliced and ready (~84 min, ~31 g). Print, caliper,
   write the seven numbers into **`ICD.md §5.1`**. Nothing fit-critical is modelled
   before that.
3. **Cheap concept/section before full bodies.** Section-print the **gyroid panel**,
   the **closure (bayonet/snap)**, and the **BME680 shield zone** in PETG *before*
   any full enclosure. Renders lie about overhangs, snap force, and whether a gyroid
   actually breathes and sheds.
4. **Checkpoint with Tomas** at base-form → features → final. He has rejected four
   finished designs — **do not hand him a completed v8 cold.** Show the direction,
   get the nod, then build.
5. **Verify in plastic, then review in hand.** Print Basic + Plus, hang them,
   **hose-test** the water path, rehearse assembly/service. *This is the step the
   whole project has never reached.*

---

## 7. What "good" means — Tomas's bar (he rejected four; clear the bar)

A v8 is done only when it is **all** of:
- **Additive-native** — gyroid skin + print-in-place/zero-hardware closure; *not* a
  box with a lid. If the part could be injection-molded unchanged, it's wrong.
- **Product-grade** — reads as a designed object (radius system, feet, shadow-gap,
  CMF); Basic + Plus are one family.
- **Functionally honest** — the four fundamentals solved, **especially the BME680
  radiation shield + isolation** (the recurring miss).
- **Proven in plastic** — printed, support-free, hose-tested, reviewed in hand with
  Tomas. Not "watertight in the slicer." Printed.
- **Signed off by Tomas at each checkpoint**, not as a surprise reveal.

---

## 8. What NOT to do

Design a box with a lid + screws + inserts + bought gasket. Form-find for its own
sake. Bury the T/RH sensor. Seal the box airtight. Oversize the cross-section to a
shape instead of the boards. Design only in renders. Re-derive the component dims.
Run CAD or git in the sandbox. Hand Tomas a finished design without a base-form
checkpoint. Skip the coupons. Skip the hose test.

---

## 9. What's in the repo

- `outdoor-sensor-enclosure-skill/` — the skill (SKILL.md + reference.md). **Use it.**
- `ICD.md` — verified dims (§2), frozen decisions, **§5.1 fits table (TBD — fill from coupons)**, change log to 1.6-DRAFT.
- `DESIGN_RESEARCH.md` — 22 enclosures surveyed, cited. `DESIGN_RESEARCH_DFAM.md` — DfAM + product craft, cited.
- `v7/` — current best: additive-native Basic shell + gyroid breathing panel + cutaway. **Your starting point.**
- `v6/` — parametric Basic+Plus (clean boxes; the validated parametric two-variant generator + internals; mine for reuse).
- `coupons/` — calibration set, sliced, **print first**.
- `tools/` — build123d generators + the gyroid pipeline + run_model/preview/mesh_io.
- `archive/`, `pucuk/`, `efficient/` — the rejected directions, each with honest notes. Read for what failed and why; reuse nothing wholesale.
- `DESIGN_LOG.md` — the honest narrative of the whole exercise.

---

## 10. First moves

1. Ask Tomas: **PETG-only or an ASA sun-hood?**, **battery in scope?** (current: no),
   **5×7 perfboard option?**, and get him to **print the coupons** so §5.1 can be filled.
2. Invoke the skill; read the ICD + research + `v7/`.
3. Clean up the **gyroid panel** into a crisp, watertight, snap-in insert; **derive Plus**
   (HM3301 behind its own gyroid duct, same family); refine the form + craft to product grade.
4. **Section-print** the gyroid panel, the closure, and the BME680 shield zone. Fix in plastic.
5. Print one **Basic** + one **Plus**; hang; **hose-test**; review in hand with Tomas.
6. Fill §5.1, lock fits, finalize, document in a `v8/BUILD.md`, then commit + push.

The epitaph from the first handover still holds, and it's the whole game now:
**design for the full purchased module, joints need hard stops and measured
clearances, rain protection is geometry — and verify in the medium that matters.
Be more honest, earlier, in plastic than the seven before you.**
