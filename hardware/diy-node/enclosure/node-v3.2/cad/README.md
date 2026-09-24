# CAD source — MISSING

<!-- TODO: add the editable source for every part in ../stl/ -->

Eight STLs are published in `../stl/`. **No editable source is here yet.**

STL is a build file, not a source file: it is a triangle soup with no
features, no parameters and no dimensions. A lab can print Bayu v7 from
`../stl/` but cannot change a wall thickness, resize a sensor pocket, or
adapt it to a different board — which is most of the reason to open-source
an enclosure at all.

This matters more on v7 than it did on v6. Every internal joint is now a
snap fit, and a cantilever hook is a *tuned* feature: its length, root
thickness and undercut set how much force the joint takes and how many
times it can be opened before it fatigues. Without the source, nobody can
retune a hook for a stiffer filament, a different nozzle, or a sensor
breakout that is half a millimetre thicker than the one it was drawn
around. A screwed design tolerates being un-parametric. This one does not.

Add, for each part, whichever applies:

- Fusion 360 → `.f3z` **and** a neutral `.step` (`.f3z` needs proprietary
  software; `.step` does not)
- OpenSCAD → `.scad`
- FreeCAD → `.FCStd`

A `.step` export alongside the native file is the minimum that makes this
design genuinely modifiable by someone who does not own your CAD licence.

While it is missing, the upstream release folder is the only other copy:
[DIY NODE V3.2 ENCLOSURE](https://drive.google.com/drive/folders/19pD4BeuOpY_0triBJ3mBPUKyIiY4P5IC)
(Google Drive, owned by Fab Lab Bali). It contains the same eight STLs and
no source either. The files in `../stl/` are the repo's own copy so the
design survives that link rotting.
