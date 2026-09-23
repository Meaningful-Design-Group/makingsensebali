# Handoff: v8 post-mortem + v9 redesign mandate
**Date:** 2026-06-10
**From:** Claude (Cowork session with Tomas)
**To:** next agent
**Status:** v8 printed and failed. v9 must fix two root causes before any print.

---

## What was printed and what failed

Tomas printed the v8 Basic body, the shared cap, and the gyroid panels. Photos document:

1. **Massive stringing** from hood/shadow-gap area — cosmetic but bad
2. **Floor plate bridge collapse** (photo: bottom view) — the ~43mm unsupported bridge across the cavity floor failed completely; the bayonet socket area is a nest of failed filament
3. **No assembly access** — the body is a sealed box; the bayonet bore is Ø32.6mm and the perfboard is 40×60mm; it cannot enter; this was never caught
4. **Clearances never calibrated** — coupons were printed but ICD §5.1 was never filled; all fits ran on `COUPON_TBD` guesses

What worked: walls, exhaust slots, keyholes, ePTFE boss, gyroid panels (fit not yet tested).

---

## Root causes — do not paper over these in v9

### RC-1: Sealed monocoque with no board-access path
The v8 hood was fused to the body in one print (`body = body + roof`). This lost the DEC-03 provision: "2× M3 release the crown." With the hood sealed, the only openings are Ø32.6mm (bayonet) and 30×28mm (gyroid window) — both smaller than the 40×60mm perfboard. The electronics have no entry path. This is the primary failure.

### RC-2: Unsupported floor plate bridge
The floor plate at `fz = 12.5mm` must span the full cavity width (~43mm Plus, ~38mm Basic) with nothing below it. The slicer accepted it as bridge geometry, but in practice PETG at this span fails. The previous simulation checked geometric interference, not printability mechanics (bridging, stringing). Zero-supports claim was wrong.

### RC-3: Stringing generators baked into geometry
Shadow-gap groove + small window openings + hood loft transition = travel moves over open air = PETG strings. Secondary to the two fatal issues above, but must be addressed in v9.

---

## v9 architecture — two mandatory changes

### Change 1: Separate hood (restores DEC-03)
The body prints **open-top** (no roof in the body STL). The hood is a **separate STL** that attaches with 2× M3 screws into threaded bosses on the top rim of the body walls. Electronics load from the open top, hood screws on last. This is what DEC-03 specified and what v8 dropped.

**Implementation:**
- In `enclosure_v8.py`: remove `body = body + roof` from the body build
- Add 2× cylindrical bosses on the top rim (e.g. x=±20, y=back of body, M3 tap depth 6mm)
- Create `roof` as a separate exported STL (already lofted in the code, just separate it)
- Add M3 clearance holes in the hood base flange to align with the body bosses
- Hood print orientation: flat base down (the wide loft base goes on the bed)

### Change 2: Remove floor plate from body; redesign cap as full-footprint base
The body cavity must be **open at the bottom** — no floor plate in the body. The current floor plate is what bridges and fails.

The cap must become a **full rectangular base plate** (~56×56mm Plus) rather than the Ø35mm disc. This base plate:
- Closes the full bottom opening of the body (replaces the body floor)
- Carries the 4 feet (move feet from body to cap)
- Has a central mesh intake window (can be a simple rectangular grid or keep the circular window)
- Attaches to the body with a mechanism that is **actually testable** — start simple: 4× snap clips at the body bottom rim corners, or 2× M3 screws at the back, or a friction press-fit. The bayonet is complex; consider deferring it to a section test before committing to the full base.
- The USB-C chase exits through the base plate (angled chase, same geometry as before)

**The electronics assembly sequence then becomes:**
1. Print body (open top + open bottom)
2. Hang body on wall via keyholes
3. Load HM3301 down the front rails (Plus)
4. Lower perfboard onto standoffs from the open top
5. Screw hood on with 2× M3 (crown goes on last)
6. Separately: attach base plate from below (mesh + USB-C already routed)

**Monthly service:** remove base plate from below (2 screws or snap clips) — no need to disturb the hood or electronics.

---

## What to keep from v8 (do not redesign these)

- Body wall geometry, cavity, wall thickness (2.5mm) — walls printed clean
- Exhaust slot geometry — worked
- Keyhole geometry — worked  
- ePTFE boss — worked
- Gyroid panel + rebate — geometry is correct, test fit when ICD §5.1 is filled
- Standoff geometry (back wall posts for perfboard) — keep as-is
- HM3301 rail + peg system — keep
- Hood shape (loft geometry) — keep, just separate it from the body

---

## Before printing v9

**Fill ICD §5.1 first.** The coupons are printed. Tomas has coupon_A_fits and coupon_B_print. Measure them (instructions in `coupons/README.md`) and put the 7 numbers into `ICD.md §5.1`. Every COUPON_TBD_* parameter in `enclosure_v8.py` then gets a real value.

**Print section tests before full bodies:**
1. Gyroid panel → test fit in the body window rebate (already have the body, test now)
2. Hood section (the lower 20mm of the hood, with M3 bosses) → confirm boss print quality and M3 thread
3. Base plate section (the attachment mechanism zone) → confirm clips/screws before full base plate

**Stringing — slicer settings to adjust (CORE One, PETG):**
- Enable combing (avoid crossing perimeters/gaps)
- Retraction: ~1mm, 35mm/s (direct drive on CORE One)
- Lower print temp by 5°C if currently ≥235°C
- Wipe on retraction: on
- Avoid crossing perimeters: on
These are secondary — fix the architecture first.

---

## Files to modify

- `tools/enclosure_v8.py` — separate `roof` from `body`; remove floor plate; add M3 bosses on top rim; move feet to the base plate function; add `body_base` export
- Create `tools/body_base_v9.py` (or add a `build_base()` function to enclosure_v9.py) for the full-footprint base plate
- `ICD.md` — fill §5.1 from coupons; add v9 change log entry; update DEC-03 (bayonet → simpler base attachment)
- `v8/BUILD.md` → update to "FAILED — see HANDOFF_v9"
- Create `v9/BUILD.md` after first successful v9 build

---

## Gate (unchanged)

Nothing fit-critical prints without ICD §5.1 filled. No full body prints before section tests. No section tests before coupon numbers.

The unbroken rule: **prove in the medium that matters before committing material.**

The v8 simulation proved geometry. It did not prove assembly access or printability mechanics. v9 must earn both.
