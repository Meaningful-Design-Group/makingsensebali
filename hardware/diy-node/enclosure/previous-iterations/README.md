**English** · [Bahasa Indonesia](README.id.md) · [Español](README.es.md)

# Previous iterations

Retired enclosure designs, kept because the failures are the most reusable
knowledge in this repository. Requirements in
[`../node-v3.2/`](../node-v3.2/) exist because one of these designs taught them.

> **None of these is the current design.** Build [`../node-v3.2/`](../node-v3.2/).

| Iteration | What it was | Retired because |
|---|---|---|
| [v5 "pine cone"](README.v5-and-earlier.md) | Parametric OpenSCAD shell, ten overlapping leaves; rain shedding and ventilation were the same geometry. Source: [`enclosure.scad`](enclosure.scad) · STLs in [`stl/`](stl/) · renders in [`img/`](img/) | Superseded by the Fab Lab Bali V3 line, which is what Fab Lab Bali actually builds and deploys. v5 solved the airflow brief more convincingly than V3 does — see the note below. |
| [`archive/`](archive/) — v1-box, v2-lantern, v3-gourd, v4-column | Four earlier shapes, each with its own notes | Each superseded by the next; kept as a record of what was tried |

**Node V2 is not in here.** It lives at [`../node-v2/`](../node-v2/), a sibling of the
current design, because it is a *node* generation rather than an enclosure iteration and
because its field evaluation is still the most cited document in this tree.

## The v5 note worth keeping

v5 put every breathing slot in a scale's rain shadow and ran a chimney from a low intake at
the BME680's level to a high exhaust under the cap. That is precisely the airflow topology
Node V2's co-location asked for, and the V3 line — which supersedes v5 — does **not** carry
it forward: V3 keeps an underside intake and leaves the BME680 beside the radio.

So v5 is retired for good reasons (it is not what Fab Lab Bali builds, and it was never
co-located either), but it is not simply worse than what replaced it. Anyone picking the
airflow problem back up should read [`README.v5-and-earlier.md`](README.v5-and-earlier.md)
and [`../../enclosure-research/DESIGN_LOG.md`](../../enclosure-research/DESIGN_LOG.md)
before starting from scratch.

## Naming

Two unrelated countings pass through this folder.

- **The enclosure line**, which is what `archive/` and v5 belong to:
  v1-box → v2-lantern → v3-gourd → v4-column → v5 "pine cone". It stops at v5.
  Later designs in this repo were briefly numbered `bayu-v6` and `bayu-v7`; that scheme is
  retired and those folders are now [`../node-v3.1/`](../node-v3.1/) and
  [`../node-v3.2/`](../node-v3.2/). The mapping table is in [`../README.md`](../README.md).
- **Fab Lab Bali's node generations**: Node V1 → V2 → V3.1 → V3.2. A separate track that
  shares electronics and firmware.

Do not read `archive/v2-lantern/` and [`../node-v2/`](../node-v2/) as the same generation.
They share a number and nothing else.
