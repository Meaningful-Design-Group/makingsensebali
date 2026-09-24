# v11 — DIY-node enclosure (BUILD): corrected two-system airflow

> 🟡 **STAGING — NOT FOR PRINT.** v11 fixes the v10 air-circulation errors
> (`../AIRFLOW_REVIEW_v10.md`). Functional airflow only; the **organic surfacing is deferred
> to Rhino** (per the plan). Fits are `COUPON_TBD_*`, ICD §5.1 still TBD.
> **HM3301 = 80 × 40 × 18 mm (Tomas measured 2026-06-11)** — the v10 "40×40" was my error,
> reverted here; only the can-port inlet/outlet positions still need caliper. Generators:
> `tools/enclosure_v11.py`, `breathing_panel_v11.py`. Built 2026-06-11, HM refit same day.

## What v11 fixes (from the airflow review)

1. **Balanced, top-biased climate chimney.** The high exhaust is enlarged (3 louvers/side,
   both sides, pushed to the very top) so its area ≥ the base intake's *open* area — the v10
   chimney was throttled (huge intake, tiny exhaust → diffusion, not flow).
   - Basic: intake open 875 mm² (~420 effective at 48% gyroid) vs exhaust **420 mm²** → balanced.
   - Plus: intake open 578 mm² (~277 effective) vs exhaust **420 mm²** → exhaust-biased (good draw).
2. **PM air re-separated from climate air.** A full-height **baffle** splits the back climate
   column (perfboard, BME680, XIAO) from the front PM bay (HM3301). The XIAO/HM heat and the
   BME's VOC plume no longer cross-contaminate.
3. **HM3301 inlet ≠ outlet.** The PM bay gets a **separate fresh intake** (down-grille in the
   front base zone, under the can) and a **separate exhaust** (front wall, above the can,
   120 mm²) — so the sensor stops re-ingesting its own exhaust. This was the clearest v10 error.
4. **BME680 low** in the fresh base intake; **XIAO high** by the exhaust. Vertical separation =
   the chimney's pump.

## Air paths (Plus)

- **Climate (passive):** base climate gyroid panel (back) → up past BME (low) and XIAO (high) →
  out the enlarged top side louvers.
- **PM (fan-driven, isolated):** front base grille → HM3301 can (fan) → out the front-wall
  exhaust above the can. Walled off from the climate column by the baffle.

## Build result (2026-06-11, staging)

Both variants: **single watertight solids, interference 0.000 cm³**.

| Variant | body (mm) | climate intake | high exhaust | PM bay |
|---|---|---|---|---|
| basic | 50 × 42 × 84 | 875 mm² open (panel 41×31) | 420 mm² | — |
| plus  | 50 × 58 × 110 | 578 mm² open (panel 41×22) | 420 mm² | baffle + 120 mm² front exhaust + base grille; **80×40×18 HM** |

(Plus grew to 50×58×110 to fit the real 80 mm-tall HM3301; front lean cut to 2 mm so the
tall front-bay sensor clears the leaning front wall.)

Renders: `review/v11_plus_cutaway_preview.png` (baffle + split base + separated vents),
`review/v11_plus_assembly_preview.png`.

## Open items

1. **HM3301 ports** — size is confirmed (80×40×18); still need **which can port is inlet vs
   outlet** and the can orientation, so the fresh intake actually feeds the inlet. v11
   separates the apertures architecturally; the physical mapping needs the real unit.
2. **Organic surfacing in Rhino** — v11 keeps v10's first-pass organic shell; refine the form
   in Rhino (see `../RHINO_MCP_SETUP.md`) and reconcile against this chassis.
3. **Tune opening areas on a printed unit** vs the reference SCK once past ICD §5.1. The
   balance here is first-principles, not CFD.
4. Fill **ICD §5.1** → press-fit, panel seat, HM rail, pegs, standoffs get real values.
