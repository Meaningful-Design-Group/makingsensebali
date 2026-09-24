# Enclosures

**Current design: [Bayu Sensor Enclosure v7](bayu-v7/).** Build that one.

| | |
|---|---|
| [`bayu-v7/`](bayu-v7/) | **Canonical.** Five printed parts per node, screwless assembly, mounting moulded into the body. STLs published, CAD source still missing. |
| [`bayu-v6/`](bayu-v6/) | Superseded by v7. The same body assembled with screws, plus a separate wall bracket. Documented because units are in the field. |
| [`previous-iterations/`](previous-iterations/) | Node V2, v5 pine cone, v1–v4. Retired, kept for their failure notes. |
| [`LICENSES/`](LICENSES/) | CERN-OHL-W-2.0 hardware · CC-BY-SA-4.0 docs · MIT software |

## Two naming systems, one mapping table

The repo counts enclosure iterations. Fab Lab Bali counts whole-node generations.
Both numbers appear in conversation and in the Drive folders, so keep this to hand:

| This repo | Fab Lab Bali | Status |
|---|---|---|
| `bayu-v7/` | **Node V3.2** | Current |
| `bayu-v6/` | **Node V3.1** | Superseded |
| `previous-iterations/node-v2/` | **Node V2** | Retired, failed field evaluation |

`bayu-v6/` and Node V3.1 are the same six STL files — verified byte-for-byte against
Fab Lab Bali's V3.1 release, not inferred from filenames. The meshes reached this repo
in September 2026 ahead of the document that described them; the documentation landed
in September 2026 and the two folders were reconciled then.

Note that `previous-iterations/node-v2/` is *not* `previous-iterations/archive/v2-lantern/`.
The node counting and the enclosure counting collide at the number 2 and at the number 3,
and neither side is going to renumber. The table above is the only reliable mapping.

## What the V3 generation fixed, and what it did not

Node V2 was co-located against a Smart Citizen Kit and failed twice: the ESP32 radio
heated the BME680 through a divider wall, and the underside intake flattened PM peaks.

The V3 bodies (v6 and v7) fix a *third* airflow problem — the PM sensor re-ingesting its
own exhaust — with a duct that carries the outflow sideways. They do not address either
of the two documented failures: the intake is still on the underside, and the BME680 still
sits in the same sealed volume as the radio. This is stated plainly in
[v7's README](bayu-v7/README.md#what-this-design-does-and-does-not-fix) and it needs a
decision from Fab Lab Bali rather than a documentation fix.

**Until a v7 has been co-located against an SCK, treat its temperature and humidity
channels as unverified and expect PM peaks to read low.** That is not a reason to stop
deploying — it is the reason the campaign already requires a first week of co-location
for every new node.

## Before this is replication-ready

Ordered by what blocks reuse, not by effort:

1. **Publish the CAD source for v7** (and v6). STL-only means nobody outside Fab Lab Bali
   can modify the design. `.step` alongside the native file is the minimum. This matters
   more on v7 than it did on v6: every joint is now a tuned snap fit, and a cantilever hook
   cannot be retuned from a triangle soup.
2. **Co-locate a v7 against an SCK for a week** and publish the Δ°C and the PM lag. Either
   the compact body reproduces V2's errors or it does not, and right now nobody knows which.
3. **Re-export `OUTFLOW_DUCT_HM3301.stl`** — 1 open edge and 1 degenerate triangle, carried
   unchanged from v6 where it was already flagged.
4. **Print settings** — material first. PLA will not survive a tropical roof, and on a
   snap-fit design the print orientation decides whether the hooks survive assembly.
5. **Cost.** No price exists for this build in any currency. It is the first question every
   banjar asks.
6. **Assembly photographs.** Every image in both folders is a CAD render.

Items 1 and 2 decide whether another Fab Lab can build this and trust what it reports, or
is just looking at pictures of it.

## Node V2 CAD

`Meaningful-Design-Group/Enclosure-DIY-Node-V2` contains exactly one file —
`Enclosure DIY Node V2.f3z` — with no README and no licence. That file answers the Node V2
docs' own blocking TODO. Moving it in:

```bash
git clone https://github.com/Meaningful-Design-Group/Enclosure-DIY-Node-V2 /tmp/v2cad
mkdir -p hardware/diy-node/enclosure/previous-iterations/node-v2/cad
cp "/tmp/v2cad/Enclosure DIY Node V2.f3z" \
   hardware/diy-node/enclosure/previous-iterations/node-v2/cad/
```

Then archive the standalone repo with its description pointing here. One public home per
design.

## Licence texts

See [`LICENSES/README.md`](LICENSES/README.md) — two `curl` commands. Don't transcribe them
by hand.
