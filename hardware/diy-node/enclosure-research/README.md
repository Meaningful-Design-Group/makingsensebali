# Enclosure research — the parametric meru tower

*A design study, June 2026. **Nothing here has been printed.***

> **This is not the buildable enclosure.** For a node you can print and hang today,
> go to [`../enclosure/node-v3.2/`](../enclosure/node-v3.2/). This folder is where the
> next generation is being reasoned out.

A stack of interchangeable tier-modules on one standard press-fit keyed rim, where the
stacking *is* a Balinese meru. Modules are gyroid-breathing boxes with the lattice
**fused into the part**, not bolted on as a panel; only the crown carries the faceted
eaves and finial, and indoor builds get a low gyroid cap instead. Parametric in
build123d; the organic crown is shaped in Rhino over MCP.

## Why this track exists

Node V2 was co-located against a Smart Citizen Kit and failed twice — the ESP32 radio
heated the BME680 through a divider wall, and the underside intake flattened PM peaks.
That produced two requirements. **The Fab Lab Bali V3 line does not meet either.**
This line is designed against both from the first line of the brief:

> Passive chimney: cool air in low, warm air (XIAO, regulator) out high, so component
> heat never bakes the BME680. […] No upward-facing aperture; rain sheds off every
> surface; no straight sightline into any opening.

That is the whole reason to keep this folder alive.

## The gate — nothing fit-critical prints yet

`ICD.md` §5.1 is open. Every fit in this line is a `COUPON_TBD_*` placeholder. The
calibration coupons in [`coupons/`](coupons/) are sliced and **have not been printed
or measured**, and until they are, no dimension here is trustworthy. Water protection
is geometry on screen, untested in rain.

**Printing the coupons is the cheapest unblock in this folder** and has been since
8 June 2026.

## Read in this order

| | |
|---|---|
| [`DESIGN_LOG.md`](DESIGN_LOG.md) | The honest record, including the wrong turn. Start here. |
| [`ICD.md`](ICD.md) | Interface control doc — verified component dims, frozen decisions, fits table, change log. The authority. |
| [`AIRFLOW_REVIEW_v10.md`](AIRFLOW_REVIEW_v10.md) | Why the air moves the way it does. |
| [`HANDOFF_v12.md`](HANDOFF_v12.md) | Current state and locked decisions. Read before touching CAD. |
| [`DESIGN_RESEARCH.md`](DESIGN_RESEARCH.md) · [`DESIGN_RESEARCH_DFAM.md`](DESIGN_RESEARCH_DFAM.md) | Background and design-for-additive-manufacture notes. |
| [`RHINO_MCP_SETUP.md`](RHINO_MCP_SETUP.md) | Getting the Rhino bridge running. |

Earlier handoffs: [`HANDOVER_v3_redesign.md`](HANDOVER_v3_redesign.md),
[`HANDOFF_v8_enclosure.md`](HANDOFF_v8_enclosure.md),
[`HANDOFF_v8_validate_and_finalize.md`](HANDOFF_v8_validate_and_finalize.md),
[`HANDOFF_v9_redesign.md`](HANDOFF_v9_redesign.md).

## The arc

| | |
|---|---|
| [`concepts/`](concepts/) | Three directions sketched as massing: Pucuk, Anyaman, Tumpang |
| [`pucuk/`](pucuk/) | The picked one, built at fidelity — then rejected for chasing silhouette |
| [`efficient/`](efficient/) | The reset: designed from the components out |
| [`v2/`](v2/) [`v6/`](v6/) [`v7/`](v7/) [`v8/`](v8/) [`v9/`](v9/) [`v10/`](v10/) [`v11/`](v11/) [`v12/`](v12/) | The modular sequence, ending in the v12 tower |
| [`plus/`](plus/) | The Plus variant (+ HM3301) |
| [`coupons/`](coupons/) | Calibration coupons — **print these first** |
| [`archive/`](archive/) | Dead directions: candi tower, meru gen 1, jantung |
| [`tools/`](tools/) | The build123d generators and render helpers |
| [`outdoor-sensor-enclosure-skill/`](outdoor-sensor-enclosure-skill/) | The design rules, as a skill |

Most version folders carry a `BUILD.md`. Several folders contain only a README,
because they held nothing but build outputs — see below.

## Build outputs are not tracked

`.stl`, `.gcode`, `.3mf`, and — under this folder — `.step`, `.bgcode` and `.png` are
gitignored. They are regenerable from [`tools/`](tools/), and there were 617 MB of
them. The generators and the markdown are the source; everything else is an export.

Folders that held *only* outputs lost their contents when this record was committed:
[`concepts/`](concepts/), [`pucuk/`](pucuk/), [`efficient/`](efficient/) and
[`v7/`](v7/) each now carry a README explaining what was there and which generator
rebuilds it.

```bash
~/Documents/Claude/Projects/MDG/.cad-venv/bin/python tools/enclosure_v12.py
```

<!-- TODO: tools/requirements.txt does not exist. The claim that everything here is
     regenerable depends on a virtualenv that lives outside this repo and is pinned
     nowhere - build123d 0.10, trimesh 4.12, skimage, scipy, manifold3d. If that env
     breaks, these generators stop being a source. Pin it. -->

## Relationship to the buildable line

| | [`../enclosure/`](../enclosure/) | Here |
|---|---|---|
| Airflow | Underside intake; BME680 beside the radio | Chimney; BME680 low, XIAO high, openings down |
| Printed | Yes, deployed | **No** |
| Thermally validated | No | No |

Neither is finished. One can be built but may misreport temperature; the other reasons
correctly and has never met plastic.

---

*Making Sense Bali · Chapter Fab City Bali. Hardware CERN-OHL-W-2.0 · documentation
CC-BY-SA-4.0.*
