#!/usr/bin/env python3
"""Print-in-place bottom bayonet — isolated interface test (v8 features pass).

The v6/v7 bayonet CUT entry/turn slots through a thin seat ring, which fragments
the ring into disconnected arcs (Basic 3 islands, Plus 4 — masked by mesh-clean,
but it means the printed ledge loses segments). This inverts the topology: a
CONTINUOUS socket skirt with ADDED inward tabs (nothing is cut into islands) and
cap lugs that pass up through the gaps and twist UNDER the tabs to lock.

Validate here, in isolation, before porting into enclosure_v8.py:
  - socket body is ONE solid (no mesh-clean needed)
  - cap is ONE solid
  - locked position: lug<->tab radial+angular overlap (engaged, can't pull out)
  - entry position: lugs clear the tabs (pass through the gaps)
All clearances COUPON_TBD_*.
"""
import os
import math
from build123d import *  # noqa: F403

OUT = os.path.join(os.path.dirname(__file__), "..", "v8", "bayonet_test")
os.makedirs(OUT, exist_ok=True)

COUPON_TBD_SLIDE = 0.30
wall = 2.5

Rb = 16.0                 # socket bore (cap plug slides in here)
Rp = 13.0                 # cap plug radius (well below bore -> room for lugs)
skirt_outer = Rb + wall   # 18.5  (<21.5 inner half-width -> never grazes wall)
Hsk = 10.0                # skirt depth
floor_t = 2.5

tab_inner = Rb - 2.0      # 14.0  inward reach of the locking tabs
tab_arc = 52.0            # deg
tab_t = 2.6               # tab thickness (z)
tab_z0 = 2.6              # tab sits low in the skirt; its TOP is the rest ledge
lug_outer = Rb - 0.3      # 15.7  lug reaches just under the bore
lug_arc = 34.0            # deg  (< gap between tabs so it passes through)
lug_t = 2.4
n = 3


def largest_solid(x):
    try:
        solids = list(x.solids())
    except (AttributeError, TypeError):
        solids = [s for item in x for s in item.solids()]
    if not solids:
        raise ValueError("no solids")
    return max(solids, key=lambda s: s.volume)


def arc_tab(r_in, r_out, arc_deg, z0, t, ang):
    """A clean annular-sector solid from r_in..r_out over arc_deg, at angle ang."""
    # build the sector by boolean of an annulus and a wedge triangle
    annulus = largest_solid(Cylinder(r_out, t, align=(Align.CENTER, Align.CENTER, Align.MIN))
                            - Cylinder(r_in, t + 0.2, align=(Align.CENTER, Align.CENTER, Align.MIN)))
    # wedge: a big isoceles triangle spanning arc_deg, apex at origin
    R = r_out + 5
    a0 = math.radians(-arc_deg / 2)
    a1 = math.radians(arc_deg / 2)
    pts = [(0, 0),
           (R * math.cos(a0), R * math.sin(a0)),
           (R * math.cos(a1), R * math.sin(a1))]
    with BuildPart() as wp:
        with BuildSketch(Plane.XY):
            with BuildLine():
                Polyline(*pts, close=True)
            make_face()
        extrude(amount=t)
    wedge = wp.part
    sector = largest_solid(annulus & wedge)
    return Pos(0, 0, z0) * Rot(0, 0, ang) * sector


def build_socket():
    # floor disk on top + bore through it
    floor = Pos(0, 0, Hsk) * Cylinder(skirt_outer + 3, floor_t, align=(Align.CENTER, Align.CENTER, Align.MIN))
    body = floor + (Cylinder(skirt_outer, Hsk, align=(Align.CENTER, Align.CENTER, Align.MIN))
                    - Cylinder(Rb, Hsk + 0.1, align=(Align.CENTER, Align.CENTER, Align.MIN)))
    body = largest_solid(body)
    body = largest_solid(body - Pos(0, 0, Hsk - 0.1) * Cylinder(Rb, floor_t + 0.2, align=(Align.CENTER, Align.CENTER, Align.MIN)))
    # add 3 inward locking tabs at 60/180/300 (gaps at 0/120/240 for lugs)
    for k in range(n):
        ang = 60 + k * 120
        body = body + arc_tab(tab_inner, Rb + 0.6, tab_arc, tab_z0, tab_t, ang)
    return largest_solid(body)


def build_cap():
    cap = Cylinder(Rp + 3.0, 2.0, align=(Align.CENTER, Align.CENTER, Align.MIN))         # base/brim
    plug = (Cylinder(Rp, 9.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
            - Cylinder(Rp - wall, 9.2, align=(Align.CENTER, Align.CENTER, Align.MIN)))
    cap = cap + Pos(0, 0, 2.0) * largest_solid(plug)
    # 3 lugs at 0/120/240, sitting at the lock height (rest on tab tops)
    lug_z = tab_z0 + tab_t  # lug bottom rests on tab top
    for k in range(n):
        ang = k * 120
        cap = cap + Pos(0, 0, 2.0 + lug_z) * arc_tab(Rp - 0.5, lug_outer, lug_arc, 0, lug_t, ang)
    return largest_solid(cap)


def overlap_cm3(a, b):
    try:
        return sum(s.volume for s in (a & b).solids()) / 1000.0
    except Exception:
        return 0.0


socket = build_socket()
cap = build_cap()

# tabs as standalone solids for the engagement check
tabs = None
for k in range(n):
    t = arc_tab(tab_inner, Rb + 0.6, tab_arc, tab_z0, tab_t, 60 + k * 120)
    tabs = t if tabs is None else tabs + t

# cap lugs alone, at lock height, in ENTRY angle (0/120/240) vs LOCKED angle (+60)
def lugs_at(angle_off):
    L = None
    lug_z = tab_z0 + tab_t
    for k in range(n):
        l = Pos(0, 0, lug_z) * arc_tab(Rp - 0.5, lug_outer, lug_arc, 0, lug_t, k * 120 + angle_off)
        L = l if L is None else L + l
    return L

# raise lugs to tab z-band for a co-planar engagement test
def lugs_band(angle_off):
    L = None
    for k in range(n):
        l = arc_tab(Rp - 0.5, lug_outer, lug_arc, tab_z0, lug_t, k * 120 + angle_off)
        L = l if L is None else L + l
    return L

eng_locked = overlap_cm3(tabs, lugs_band(60))   # locked: lugs under/over tabs -> overlap > 0
eng_entry = overlap_cm3(tabs, lugs_band(0))      # entry: lugs in gaps -> ~0

print(f"socket: solids={len(socket.solids())}")
print(f"cap:    solids={len(cap.solids())}")
print(f"engagement locked (want >0.3): {eng_locked:.3f} cm3")
print(f"engagement entry  (want ~0):   {eng_entry:.3f} cm3")

export_stl(socket, os.path.join(OUT, "bayo_socket.stl"))
export_stl(cap, os.path.join(OUT, "bayo_cap.stl"))
asm = Compound([socket, Pos(0, 0, 0) * cap])
export_stl(asm, os.path.join(OUT, "bayo_assembly.stl"))
print("exported ->", OUT)
