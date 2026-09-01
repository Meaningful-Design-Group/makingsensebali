# Licences

| What | Licence | SPDX |
|---|---|---|
| Hardware — CAD, STL, mechanical design | CERN Open Hardware Licence v2 — Weakly Reciprocal | `CERN-OHL-W-2.0` |
| Documentation — READMEs, guides, images | Creative Commons Attribution-ShareAlike 4.0 | `CC-BY-SA-4.0` |
| Software — firmware, tools, dashboard | MIT | `MIT` |

CERN-OHL-W means anyone may build, sell and modify the enclosure, and
modifications to the design itself must be shared back — but it can be
combined with proprietary parts. That is the variant that lets a Bali
workshop sell nodes commercially while improvements still return to the
project.

## Getting the licence texts

CERN-OHL-W requires the full text be distributed with the design, so fetch
the official copy rather than transcribing it:

```bash
curl -o CERN-OHL-W-2.0.txt \
  https://raw.githubusercontent.com/spdx/license-list-data/main/text/CERN-OHL-W-2.0.txt
curl -o CC-BY-SA-4.0.txt https://creativecommons.org/licenses/by-sa/4.0/legalcode.txt
```

Verify both against https://cern.ch/cern-ohl and
https://creativecommons.org before committing. A mistranscribed licence is
worse than no licence.

## Required notice

CERN-OHL-W asks for a notice in the source. Put this at the top of each CAD
source file, and on the hardware itself where there is room:

```
Copyright <YEAR> Meaningful Design Group / Fab Lab Bali
Licensed under CERN-OHL-W-2.0. Source: https://github.com/Meaningful-Design-Group/makingsensebali
```

Put a version marker on the physical object — embossed or on a label — so a
device in the field can be matched to the documentation that describes it.
