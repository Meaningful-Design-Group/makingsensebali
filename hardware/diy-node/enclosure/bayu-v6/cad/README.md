# CAD source — MISSING

<!-- TODO: add the editable source for every part in ../stl/ -->

Six STLs are published in `../stl/`. **No editable source is here yet.**

STL is a build file, not a source file: it is a triangle soup with no
features, no parameters and no dimensions. A lab can print Bayu v6 from
`../stl/` but cannot change a wall thickness, resize a sensor pocket, or
adapt it to a different board — which is most of the reason to open-source
an enclosure at all.

Add, for each part, whichever applies:

- Fusion 360 → `.f3z` **and** a neutral `.step` (`.f3z` needs proprietary
  software; `.step` does not)
- OpenSCAD → `.scad`
- FreeCAD → `.FCStd`

A `.step` export alongside the native file is the minimum that makes this
design genuinely modifiable by someone who does not own your CAD licence.
