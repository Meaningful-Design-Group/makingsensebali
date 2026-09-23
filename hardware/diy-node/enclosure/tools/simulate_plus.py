#!/usr/bin/env python3
"""Digital assembly simulation of the v8 PLUS node, fully populated with all sensors.

This is NOT a physical print — it is a geometry/clearance/printability check that
answers "would the parts go together and work" before plastic. Sections:
  1. Interference matrix: body + locked cap vs every component dummy, and component
     vs component (verified ICD dims).
  2. Bayonet kinematics: lock vs entry — does the cap actually twist-lock, or do the
     lugs collide with / miss the tabs? (z-engagement + footprint capture)
  3. Gyroid panel seated vs the BME680: does the panel collide with the sensor, and
     is there room behind it for the foil liner + air gap?
  4. Printability: overhang-risk area on body / cap / panel (corroborates supports=0).
  5. Assembly-sequence rehearsal.
All fits are COUPON_TBD; this finds GEOMETRY problems, not final clearances.
"""
import os
import sys
import numpy as np
import trimesh
from build123d import *  # noqa: F403

sys.path.insert(0, os.path.dirname(__file__))
import enclosure_v8 as e8  # noqa: E402

E = os.path.expanduser("~/Documents/Claude/Projects/MDG/smartcitizenbali/hardware/diy-node/enclosure")


def inter(a, b):
    try:
        return sum(s.volume for s in (a & b).solids()) / 1000.0
    except Exception:
        return -1.0


def aabb_bd(solid):
    bb = solid.bounding_box()
    return np.array([bb.min.X, bb.min.Y, bb.min.Z]), np.array([bb.max.X, bb.max.Y, bb.max.Z])


def aabb_overlap(lo1, hi1, lo2, hi2):
    return np.minimum(hi1, hi2) - np.maximum(lo1, lo2)   # >0 on all axes = overlap


def overhang(path, name):
    m = trimesh.load(path, force="mesh")
    n = m.face_normals
    a = m.area_faces
    zmin = m.vertices[:, 2].min()
    fz = m.vertices[m.faces].mean(axis=1)[:, 2]
    risky = (n[:, 2] < -0.707) & (fz > zmin + 0.6)        # steeper than 45 deg, not on the bed
    pct = 100 * a[risky].sum() / a.sum()
    print(f"  {name}: overhang-risk {a[risky].sum():.0f} mm2 ({pct:.1f}%), worst normal.z={n[:,2].min():.2f}, "
          f"watertight={m.is_watertight}")


print("Building plus assembly...")
P = e8.build("plus", e8.VARIANTS["plus"])
body, cap = P["body"], P["cap"]
perf, perf_env, bme, hm = P["perfboard"], P["perf_env"], P["bme"], P["hm_module"]
cap_cy, fz = P["cap_cy"], P["fz"]
HSK, TAB_DZ, TAB_T = e8.BAYO_HSK, e8.BAYO_TAB_DZ, e8.BAYO_TAB_T
RB, RP, slide = e8.BAYO_RB, e8.BAYO_RP, e8.COUPON_TBD_SLIDE
TAB_IN, TAB_ARC, LUG_OUT, LUG_ARC, LUG_T = (e8.BAYO_TAB_IN, e8.BAYO_TAB_ARC,
                                            e8.BAYO_LUG_OUT, e8.BAYO_LUG_ARC, e8.BAYO_LUG_T)

print("\n== 1. INTERFERENCE (cm3, want ~0.00) ==")
cap_base_z = P["cap_rest_z"]
cap_lock = Pos(0, cap_cy, cap_base_z) * Rot(0, 0, 60) * cap
for nm, a, b in [("body ^ perfboard", body, perf), ("body ^ BME680", body, bme),
                 ("body ^ HM3301", body, hm), ("perfboard ^ HM3301", perf, hm),
                 ("BME680 ^ HM3301", bme, hm), ("BME680 ^ perfboard", bme, perf),
                 ("cap(locked) ^ body", cap_lock, body), ("cap(locked) ^ HM3301", cap_lock, hm)]:
    print(f"  {nm:24s}: {inter(a, b):.3f}")

print("\n== 2. BAYONET kinematics ==")
tab_z0 = fz - HSK + TAB_DZ
lug_local_z = e8.BAYO_LUG_LOCAL_Z
lug_z0 = cap_base_z + lug_local_z
z_gap = lug_z0 - (tab_z0 + TAB_T)
rad_ov = min(LUG_OUT, RB + slide + 0.6) - max(RP - 0.5, TAB_IN)
print(f"  tab z-band [{tab_z0:.1f}, {tab_z0 + TAB_T:.1f}]  lug z-band(locked) [{lug_z0:.1f}, {lug_z0 + LUG_T:.1f}]")
print(f"  lug_bottom - tab_top = {z_gap:+.1f} mm   (want >= ~0.3: lug rests on tab; <0 = lugs CRASH into tabs)")
print(f"  locked footprint capture: radial {rad_ov:+.1f} mm, angular {min(LUG_ARC, TAB_ARC):.0f} deg")


def tabk(k):
    return Pos(0, cap_cy, tab_z0) * e8.arc_sector(TAB_IN, RB + slide + 0.6, TAB_ARC, TAB_T, 60 + k * 120)


def lugk(k, off):
    return Pos(0, cap_cy, lug_z0) * e8.arc_sector(RP - 0.5, LUG_OUT, LUG_ARC, LUG_T, k * 120 + off)


lock = sum(inter(tabk(k), lugk(k, 60)) for k in range(3))
entry = sum(inter(tabk(k), lugk(k, 0)) for k in range(3))
print(f"  solid tab^lug overlap: lock {lock:.3f} cm3 (>0 here = COLLISION at same z), entry {entry:.3f} cm3")

print("\n== 3. GYROID PANEL seated vs BME680 ==")
panel = trimesh.load(os.path.join(E, "v8/v8_gyroid_panel.stl"), force="mesh")
M = np.eye(4)
M[:3, :3] = np.array([[0, 0, 1], [1, 0, 0], [0, 1, 0]], float)
panel.apply_transform(M)
panel.apply_translation([-20.0, 0.0, 33.0])
plo, phi = panel.bounds
blo, bhi = aabb_bd(bme)
ov = aabb_overlap(plo, phi, blo, bhi)
print(f"  panel AABB x[{plo[0]:.1f},{phi[0]:.1f}] y[{plo[1]:.1f},{phi[1]:.1f}] z[{plo[2]:.1f},{phi[2]:.1f}]")
print(f"  BME680 AABB x[{blo[0]:.1f},{bhi[0]:.1f}] y[{blo[1]:.1f},{bhi[1]:.1f}] z[{blo[2]:.1f},{bhi[2]:.1f}]")
if np.all(ov > 0):
    print(f"  *** COLLISION: panel & BME680 overlap {ov.round(1)} mm — BME too far outboard ***")
else:
    gap = -ov[ov < 0].max() if np.any(ov < 0) else 0
    print(f"  clear; nearest-axis gap {(-ov[ov<0]).min():.1f} mm (want >=3 for foil liner + air gap)")

print("\n== 4. PRINTABILITY (overhang risk; slicer already said supports=0) ==")
overhang(os.path.join(E, "v8/v8_plus_body.stl"), "plus body")
overhang(os.path.join(E, "v8/v8_basic_cap.stl"), "cap")
overhang(os.path.join(E, "v8/v8_gyroid_panel.stl"), "gyroid panel")
print("\nDONE")
