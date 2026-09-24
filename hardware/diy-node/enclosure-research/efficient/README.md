# efficient — designed from the components out

*June 2026. Outputs not tracked — see [why](#why-this-folder-looks-empty).*

The reset after [`../pucuk/`](../pucuk/): stop drawing a silhouette, size the box to
the boards.

| Fundamental | Decision |
|---|---|
| Cross-section | ~49 × 45.5 cavity, ~54 × 50.5 body — a compact filleted box, **not** a Ø71 shape |
| Sensor placement = chimney | BME680 low (cool intake, true ambient); XIAO high (heat rises away from it); HM3301 vertical with its own fan duct so its exhaust never crosses the BME680 |
| Water | Every opening faces **down**. Intake = bottom cap. Exhaust = slots through the underside of the roof eave. No upward hole |
| Print efficiency | Filleted box + hollow hipped roof, 45° support-free eave flare, 2.5 mm wall, two parts, prints upright |

| | Pucuk shard | **Efficient box** |
|---|---|---|
| Body | 84.6 g / 3 h 36 m | **75.2 g / 3 h 03 m** |
| Cap | 10.8 g / 23 m | 7.9 g / 19 m |
| Envelope | 82 × 71 × 129 mm | **54 × 55 × 114 mm** (62 wide incl. eave) |

**Honest limitations.** Mass only dropped ~11%, not the third first claimed — the
grams are floored by a 114 mm height (the 80 mm HM3301 carrier forces it) against a
2.5 mm wall. The real wins are simplicity, footprint and function-first venting.
Water protection is geometry on screen, untested in rain. All fits are
`COUPON_TBD_*` placeholders until [`../coupons/`](../coupons/) are printed and
measured into `ICD.md` §5.1.

Generator: [`../tools/enclosure_efficient.py`](../tools/enclosure_efficient.py).

## Why this folder looks empty

It held only `.stl`, `.step` and `.png` — all build outputs, all gitignored.
Regenerate:

```bash
~/Documents/Claude/Projects/MDG/.cad-venv/bin/python ../tools/enclosure_efficient.py
```
