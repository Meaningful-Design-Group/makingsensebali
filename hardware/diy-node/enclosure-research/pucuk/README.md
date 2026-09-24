# pucuk — the twisted faceted shard

*June 2026. Superseded. Outputs not tracked — see [why](#why-this-folder-looks-empty).*

The concept Tomas picked from the three in [`../concepts/`](../concepts/), built at
fidelity: twisted faceted octagonal shard, fractal-graded louvers, sealed venting
finial, validated internals, bottom bayonet.

| | |
|---|---|
| Body | 84.6 g / 3 h 36 m |
| Cap | 10.8 g / 23 m |
| Envelope | 82 × 71 × 129 mm |
| Parts | 2 · Supports 0 · Watertight yes · Interference 0.000 |

Section test-prints were generated in `pucuk/sections/`.

**Why it was dropped.** On review, Tomas: *"all these designs do not make sense…
too much focus on the form finding."* The work had chased silhouette while the four
fundamentals were inherited from the old candi build rather than designed. The Ø71
cavity that drove the 84 g existed because a faceted body wanted it, not because the
boards needed it. The reset produced [`../efficient/`](../efficient/).

That correction is the most useful thing in this folder and it is written up in
[`../DESIGN_LOG.md`](../DESIGN_LOG.md).

Generator: [`../tools/enclosure_pucuk.py`](../tools/enclosure_pucuk.py).

## Why this folder looks empty

It held only `.stl`, `.step`, `.png` and `.gcode` — all build outputs, all
gitignored. Regenerate:

```bash
~/Documents/Claude/Projects/MDG/.cad-venv/bin/python ../tools/enclosure_pucuk.py
```
