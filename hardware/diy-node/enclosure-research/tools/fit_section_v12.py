#!/usr/bin/env python3
"""v12 press-fit rim SECTION PRINT — the de-facto §5.1 coupon (ICD 1.12-DRAFT).

Two short rings cut from the REAL module geometry (same code path as the tower):
  * v12_fit_section_socket.stl : top 14 mm of a standard module tube (the socket IS
    the open cavity — the spigot presses into it over IFACE_H).
  * v12_fit_section_spigot.stl : 6 mm of tube + the standard bottom spigot.
    PRINT NOTE: flip 180° in the slicer (spigot up) — the flat tube top goes on the bed.

Test: press the spigot into the socket top. Target = firm hand press, no rattle, no
flex-crack. If it binds -> increase COUPON_TBD_STACK by 0.05 and regenerate; if it
rattles -> decrease by 0.05. This GATES all full-module prints.
"""
import os
import trimesh as _tm
from build123d import *  # noqa: F403
import enclosure_v12 as E

socket = E.base_tube(14.0)
spigot = E.bottom_spigot(E.base_tube(6.0))

for nm, part in (("socket", socket), ("spigot", spigot)):
    p = os.path.join(E.OUT, f"v12_fit_section_{nm}.stl")
    export_stl(part, p)
    m = _tm.load(p, force="mesh")
    cs = m.split(only_watertight=False)
    if len(cs) > 1:
        keep = max(cs, key=lambda c: c.area)
        keep.fix_normals()
        keep.export(p)
        m = keep
    bb = m.bounds
    print(f"  {nm}: {bb[1][0]-bb[0][0]:.1f} x {bb[1][1]-bb[0][1]:.1f} x {bb[1][2]-bb[0][2]:.1f} mm  "
          f"watertight={m.is_watertight}  vol={m.volume/1000:.1f} cm3")
print(f"STACK fit = {E.COUPON_TBD_STACK} mm/side (INFERRED §5.1) — this print validates it.")
