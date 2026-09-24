# Previous iterations

Retired enclosure designs, kept because the failures are the most reusable
knowledge in this repository. Every requirement in
[`../node-v3.2/`](../node-v3.2/) exists because one of these designs taught it.

**None of these is the current design.** Build
[Bayu Sensor Enclosure v7](../node-v3.2/).

Note that [`../node-v3.1/`](../node-v3.1/) is also superseded but is *not* in here: units
are in the field and it still needs its assembly steps findable.

| Iteration | Retired because | Files |
|---|---|---|
| Node V2 (triangular shell, Fab Lab Bali) | Self-heating: the ESP32-C3 radio warmed the BME680 through the divider wall, so temperature read high and RH followed it down. Intake lag: the underside inlet restricted circulation, so PM spikes arrived late and flattened. Co-located against an SCK; failed twice. | TODO: move `Enclosure DIY Node V2.f3z` here from the standalone repo |
| v5 "pine cone" | TODO — superseded by Bayu v6; state what it did well and what it didn't | TODO |
| v1–v4 | TODO — one line each | TODO |

<!-- TODO: as each folder is moved in, add a row above and a short note inside
     the folder saying what it taught. A retired design with no explanation is
     just clutter; a retired design with its failure written down is a design
     rationale. -->

## Naming

**One sequence: the enclosure line.** v1 → v5 ("pine cone") → v6 "Bayu" →
**v7**, the current design. Versions are bare numbers; *Bayu* is the design's
name, not a restart of the count. A design that supersedes v5 is v6.

Fab Lab Bali runs a second, unrelated counting for whole-node generations:
v6 is their **Node V3.1** and v7 is their **Node V3.2**. See the mapping table
in [`../README.md`](../README.md).

The Node line (V1, V2) is a separate design track that shares electronics
and firmware. Node V2's shell is filed here because it is retired, but its
numbering is not this sequence — do not read "Node V2" as older or newer
than any enclosure version.
