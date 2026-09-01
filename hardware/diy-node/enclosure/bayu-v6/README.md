# Bayu Sensor Enclosure v6 — current canonical enclosure

3D-printed outdoor housing for the Making Sense Bali DIY air quality node.
*Bayu* — wind. Airflow is the design brief: the two failures that retired
the previous generation were both airflow failures.

**Stage:** prototyping — printable, not yet replication-ready. See *Honest state* below.
**Supersedes:** everything in [`../previous-iterations/`](../previous-iterations/)
**Licence:** CERN-OHL-W-2.0 (hardware) · CC-BY-SA-4.0 (this documentation)

<!-- TODO: photo of an assembled, deployed unit goes here -->

## What problem it solves

The previous node was evaluated against a co-located Smart Citizen Kit and
failed twice, both times because of air:

1. **Self-heating.** The ESP32's Wi-Fi radio warmed the BME680 through the
   divider wall. Temperature read well above ambient, and because relative
   humidity is derived from temperature, RH followed it down. Both channels
   were wrong.
2. **Intake lag.** The underside air inlet restricted circulation. PM spikes
   arrived late and flattened — fatal for a campaign whose whole purpose is
   catching short open-burning events.

The resulting requirements were vertical airflow from the top or open sides,
and the BME680 out of the electronics bay under a shield. Bayu v6 is the
design against those requirements.

<!-- TODO: state how v6 actually meets each requirement — the air path in one
     paragraph, and where the BME680 sits relative to the electronics. This is
     the single most useful paragraph in the document and only you can write it. -->

## Parts

Six printed parts. Measurements below are read from the STLs, so they are
real; everything else in this section is a TODO.

| Part | Bounding box (mm) | Triangles | Role |
|---|---|---|---|
| `Main_Body.stl` | 113.9 × 92.0 × 28.9 | 5,242 | Main chassis |
| `Main_Body_Cover.stl` | 117.9 × 88.0 × 51.9 | 13,324 | Top cover / shroud |
| `HM_Cover_and_Mainboard_Mount.stl` | 83.9 × 40.1 × 8.9 | 1,522 | HM3301 PM sensor cover + mainboard mount |
| `Body_Air_Outlet.stl` | 46.0 × 26.0 × 12.0 | 1,548 | Air outlet |
| `BME_Cover.stl` | 44.0 × 24.0 × 2.0 | 984 | BME680 cover |
| `Body_Bracket.stl` | 76.4 × 15.0 × 28.0 | 882 | Mounting bracket |

Roles are inferred from filenames — correct them if wrong.

Parts are exported in assembly coordinates, not print coordinates (most have
a negative Z minimum). Slicers will drop them to the bed; it does mean the
files are not pre-oriented for printing.

<!-- TODO: assembled outer dimensions and mass -->

## Print settings

<!-- TODO: none of this is known. Nothing below is a real value. -->

| | |
|---|---|
| Material | TODO — PETG or ASA is usual for tropical outdoor; PLA will creep and sag in a parked vehicle or direct sun |
| Layer height | TODO |
| Walls / perimeters | TODO |
| Infill | TODO |
| Nozzle / bed temperature | TODO |
| Supports | TODO — state per part |
| Print orientation | TODO — state per part; matters for both watertightness and the strength of the bracket |
| Estimated print time / filament | TODO |

State machine requirements in workshop terms (minimum build volume, nozzle
diameter) rather than by printer brand — a lab in another city has a
different machine.

## Assembly

<!-- TODO: step sequence, naming the joining technology at each step
     (screwed / snap-fit / glued), with a photo for any step where
     orientation is ambiguous. Include screw sizes and counts. -->

See [`bom.csv`](bom.csv) for parts. See
[`../../firmware/`](../../firmware/) for the node firmware.

## Known issues with these files

Found by mesh inspection on 2026-09-01, before publication:

- **`Main_Body.stl` is not watertight** — 4 open edges. Slicers will usually
  repair it silently, but the result is then whatever that slicer decided.
  Re-export from source.
- **`Body_Air_Outlet.stl` has 4 degenerate (zero-area) triangles.** Harmless
  in practice, cosmetically wrong.
- **No CAD source is published.** See [`cad/README.md`](cad/README.md). This
  is the blocker on calling the design replication-ready.

## Honest state of this documentation

Printable today: yes, six valid STLs.
Reproducible by another lab today: **no** — no source, no print settings, no
BoM, no assembly steps, no photos.

That gap is deliberate and visible rather than papered over with invented
numbers. Everything above marked TODO is a real unknown.
