# concepts — three directions, sketched as cheap massing

*June 2026. Outputs not tracked — see [why](#why-this-folder-looks-empty).*

Three concept directions were sketched as cheap massing before any of them was
built at fidelity, from
[`../concept-sketch_pucuk-anyaman-tumpang.svg`](../concept-sketch_pucuk-anyaman-tumpang.svg):

| Direction | Form |
|---|---|
| **Pucuk** | Twisted faceted shard |
| **Anyaman** | Woven lattice over a liner |
| **Tumpang** | Faceted meru tiers |

Tomas picked **Pucuk**, which was then built at fidelity in [`../pucuk/`](../pucuk/).
The other two were not taken further.

Generator: [`../tools/concepts.py`](../tools/concepts.py) and
[`../tools/concepts_meru.py`](../tools/concepts_meru.py).

## Why this folder looks empty

It held only `.stl`, `.step` and `.png` — all build outputs, all gitignored since
the design record was committed. Regenerate them:

```bash
~/Documents/Claude/Projects/MDG/.cad-venv/bin/python ../tools/concepts.py
```

The full arc is in [`../DESIGN_LOG.md`](../DESIGN_LOG.md).
