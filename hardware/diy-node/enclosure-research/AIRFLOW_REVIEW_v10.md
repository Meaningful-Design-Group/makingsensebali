# v10 air-circulation review — and why it's wrong

Date 2026-06-10. Diagram: `v10/review/v10_airflow_review.png`. This reviews the v10
airflow honestly and sets the corrected strategy for the next build (Rhino skin +
build123d chassis).

## How v10 moves air now

- **Intake:** the whole base is a large down-facing gyroid panel (~35×25 Basic / ~35×37 Plus).
- **Exhaust:** small down-facing louvers high on one side wall, plus an ePTFE membrane boss.
- **Intent:** a base→top buoyancy chimney — cool air in low, past BME680 (low), past XIAO
  (high, heat), out the top.
- **HM3301 (Plus):** vertical in front rails, its can facing a single front "can grille".

## What's wrong (ranked)

**1. The chimney is throttled — big intake, small high exhaust.** A passive buoyancy
chimney is limited by its *smallest* opening and by the *vertical distance* between intake
and exhaust. v10 pairs a very large base intake with a small, not-very-high exhaust. Result:
almost no through-draft — the big base panel mostly does slow diffusion, not flow. A giant
intake doesn't help if nothing pulls air through the top. **Fix: size the exhaust ≥ the
effective intake and push it to the very top, under the eave.** Intake area can actually be
*smaller* than it is now; what matters is a matched, high exhaust and a tall column.

**2. The PM air and the climate/MCU air are merged into one cavity.** v8's design explicitly
*separated* the HM3301 PM air system from the BME680 T/RH air (ICD F-04). Consolidating
breathing to the base re-merged them. Now the HM3301 samples cavity air contaminated by the
BME's local VOC plume, the XIAO's heat, and the HM's own laser-warmed exhaust — and the BME's
temperature/humidity is biased by that same shared heat. The low-BME / high-XIAO split was
meant to keep MCU heat *off* the BME; merging the columns partly defeats it.

**3. The HM3301 inlet and outlet are not separated.** The HM-3301's fan pulls air in one port
and pushes it out another (both on the can). With a single front grille, the can's warm
exhaust sits right next to its intake and gets re-ingested — the sensor measures its own
recirculated air, not ambient PM. This is the clearest *correctness* error: PM readings will
read low and lag. **Fix: a dedicated, isolated PM duct — a fresh down-facing intake straight
to the can's inlet, and a separate outlet dumping the exhaust outside, the two not
short-circuiting.**

**4. Down-facing top exhaust fights buoyancy (minor).** Warm air wants to leave straight up;
down-and-out louvers make it turn down to exit, costing some draw. Acceptable for rain
protection, but the exhaust should still be as high as possible and generously sized to
compensate. The ePTFE boss is a pressure-equalising breather, not a flow path — don't count
it as exhaust.

## The corrected strategy — two separate air systems

**A. Climate/MCU chimney (BME680 + XIAO), passive.**
- Low intake near the BME680 (can be a modest down-facing opening, not the whole base).
- **High exhaust, area ≥ intake, at the very top under the hood**, so buoyancy actually draws.
- BME680 low in the fresh stream; XIAO high so its heat exits without crossing the BME.
- Maximise the vertical intake→exhaust distance — that height *is* the pump.

**B. PM duct (HM3301), fan-driven and isolated.**
- A short, dedicated path: fresh outside air → can inlet; can outlet → separate outside vent.
- A baffle/wall isolates the PM bay from the climate column so heat and gas don't cross-bias.
- Can ports face down/side, never up (rain).

**C. Water (kept).** All apertures down-facing or in the hood's rain-shadow; ePTFE membrane
boss for pressure/vapour; weep at the low point.

## Net change to the form

The "breathing panel as the base" idea still works — but the base becomes the **climate
intake** (low), not the whole airflow story, and it must be *paired with a real high exhaust*.
The PM sensor gets its own little isolated duct off to one side. So the next body wants: a
tall column (max intake→exhaust height), a generous top exhaust under the eave, a low base
intake by the BME, and a partitioned PM bay. That's the airflow brief for the organic
redesign — whether we cut it in Rhino or build123d.

## Caveat

This is first-principles buoyancy + datasheet reasoning, not CFD. The ranking (PM separation
and exhaust sizing first) is robust; exact opening areas should be tuned on a printed unit
against the reference SCK once we're past the ICD §5.1 gate.
