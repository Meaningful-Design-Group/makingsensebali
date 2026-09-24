**English** · [Bahasa Indonesia](README.id.md) · [Español](README.es.md)

# Enclosures

Outdoor housings for the Making Sense Bali DIY air quality node. Everything in this
folder has been printed and deployed.

> ## Build [`node-v3.2/`](node-v3.2/).
> Screwless assembly, mounting moulded into the body, five printed parts.
> Fab Lab Bali, September 2026.

| | |
|---|---|
| [`node-v3.2/`](node-v3.2/) | **Canonical.** Full screwless snap-fit, integrated wall and pole mounting. Eight STLs published, CAD source still missing. |
| [`node-v3.1/`](node-v3.1/) | Superseded by v3.2. The same body assembled with 11 screws plus a separate wall bracket. Kept because units are in the field. |
| [`node-v2/`](node-v2/) | Retired. Built, deployed, co-located against a Smart Citizen Kit, and **failed twice**. Kept for the failure notes, which are the most reusable thing here. |
| [`previous-iterations/`](previous-iterations/) | The pre-V3 enclosure lineage: v1-box → v2-lantern → v3-gourd → v4-column → v5 pine cone. Retired, documented. |
| [`LICENSES/`](LICENSES/) | CERN-OHL-W-2.0 hardware · CC-BY-SA-4.0 docs · MIT software |

**Looking for the parametric meru-tower work?** That is a separate, unprinted design
study and it lives in [`../enclosure-research/`](../enclosure-research/). See
[Two tracks](#two-tracks-and-why-they-are-separate) below.

## Naming

Fab Lab Bali numbers whole node generations. This repo used to number enclosure
iterations separately as `bayu-vN`, which produced two names for one object and a
collision with the research line. **The `bayu-vN` scheme is retired.** The mapping,
for anyone reading older commits, issues or Drive folders:

| Folder now | Was | Fab Lab Bali calls it |
|---|---|---|
| `node-v3.2/` | `node-v3.2/` | Node V3.2 |
| `node-v3.1/` | `node-v3.1/` | Node V3.1 |
| `node-v2/` | `node-v2/` | Node V2 |

`node-v3.1/` and Node V3.1 are the same six STL files, verified byte-for-byte against
Fab Lab Bali's release — not inferred from filenames.

Note that `previous-iterations/archive/v2-lantern/` is **not** `node-v2/`. The old
enclosure lineage and the node generations both pass through the number 2 and are
unrelated.

## Two tracks, and why they are separate

| | This folder | [`../enclosure-research/`](../enclosure-research/) |
|---|---|---|
| Origin | Fab Lab Bali | June 2026 parametric study |
| Form | Compact horizontal body | Modular meru tower, gyroid lattice |
| Airflow | Underside intake; BME680 beside the radio | Chimney: BME680 low, XIAO high, all openings down |
| Toolchain | Hand CAD, STL releases | build123d generators + Rhino |
| **Printed** | **Yes — deployed** | **No. Nothing.** |
| Thermally validated | No | No |

Both numbering systems use bare `vN`, which is why they no longer share a folder.

**The honest position.** Node V2's field evaluation produced two requirements:
intake from the top or open sides, and the BME680 out of the electronics bay under a
shield. The V3 generation meets neither — it fixes a third problem, exhaust
re-suction, with a duct. The research track meets both, on screen, having never been
printed. Neither track is finished. `node-v3.2/` is canonical because it is the only
design anyone can build today, not because the airflow question is settled.

Until a v3.2 has been co-located against an SCK, **treat its temperature and humidity
channels as unverified and expect PM peaks to read low.** That is not a reason to
stop deploying — it is the reason the campaign requires a first week of co-location
for every new node.

## Before this is replication-ready

Ordered by what blocks reuse, not by effort:

1. **Publish the CAD source for v3.2** (and v3.1). STL-only means nobody outside Fab
   Lab Bali can modify it. This matters more on v3.2: every joint is a tuned snap
   fit, and a cantilever hook cannot be retuned from a triangle soup.
2. **Co-locate a v3.2 against an SCK for a week** and publish the Δ°C and the PM lag.
   Either the compact body reproduces V2's errors or it does not, and nobody knows.
3. **Re-export `OUTFLOW_DUCT_HM3301.stl`** — 1 open edge, 1 degenerate triangle,
   carried unchanged from v3.1 where it was already flagged.
4. **Print settings.** Material first: PLA will not survive a tropical roof, and on a
   snap-fit design the print orientation decides whether the hooks survive assembly.
5. **Cost.** No price exists for this build in any currency. It is the first question
   every banjar asks.
6. **Assembly photographs.** Every image in both folders is a CAD render.

Items 1 and 2 decide whether another Fab Lab can build this and trust what it
reports, or is just looking at pictures of it.

## Node V2 CAD

`Meaningful-Design-Group/Enclosure-DIY-Node-V2` contains exactly one file,
`Enclosure DIY Node V2.f3z`, with no README and no licence. It answers the Node V2
docs' own blocking TODO:

```bash
git clone https://github.com/Meaningful-Design-Group/Enclosure-DIY-Node-V2 /tmp/v2cad
mkdir -p hardware/diy-node/enclosure/node-v2/cad
cp "/tmp/v2cad/Enclosure DIY Node V2.f3z" hardware/diy-node/enclosure/node-v2/cad/
```

Then archive that repo with its description pointing here. One public home per design.

## Licence texts

See [`LICENSES/README.md`](LICENSES/README.md) — two `curl` commands. Don't
transcribe them by hand.
