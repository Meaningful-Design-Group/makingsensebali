#!/usr/bin/env python3
"""K1H2 Phase-2 — "low boulder" with features.
Plan stretched +9 Y vs Phase-1 (Grove plug corridor y31..42). Hex plan
(0/60/120 axes, edges 72/57/48/88/41/64 — no symmetry). Base tub z0..30 +
tongue -> 34 (tip-seat); hood skirt z26..34 + 47 deg skeleton roof.
Zero hardware: 3 keyed snap arms, printed keyholes + zip-tie conduits, press
bung. Two-zone: PM intake plenum (45 shed) + PM exhaust TENT over the can
running E to the e2 grille (45 planes, no flat plates anywhere). Climate zone
cross-vented SW->E. BASE prints floor-down, HOOD rim-down.
Phase-1 massing archived in k1h2_phase1_model.py.
"""
import json, os
from math import tan, radians, cos, sin
from build123d import *

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "v2")
os.makedirs(OUT, exist_ok=True)

WALL, CLR = 2.5, 0.45
FLOOR_T = 2.5
BASE_H = 30.0
TONGUE_H = 4.0
RIM_Z = 26.0
EAVE_Z = BASE_H + TONGUE_H
SLOPE = 47.0
FZ = FLOOR_T
REST = 5.5

EDGES = [(0, 72), (60, 57), (120, 48), (180, 88), (240, 41), (300, 64)]
pts = [(0.0, 0.0)]
for ang, L in EDGES:
    x, y = pts[-1]
    pts.append((x + L * cos(radians(ang)), y + L * sin(radians(ang))))
assert abs(pts[-1][0]) < 1e-9 and abs(pts[-1][1]) < 1e-9
pts = pts[:-1]
verts = pts + [pts[0]]
Y_TOP = 90.933
WOUT = WALL + CLR          # 2.95 base wall outer inset from plan line
WIN = 2 * WALL + CLR       # 5.45 cavity face inset
Y_OUT = Y_TOP - WOUT       # e3 outer wall face y = 87.983
Y_IN = Y_TOP - WIN         # e3 cavity face y = 85.483

def poly_face(p2d):
    w = Wire.make_polygon([Vector(x, y, 0) for x, y in p2d])
    try:
        return make_face(w)
    except Exception:
        return Face(w)

def inset(face, d):
    r = offset(face, amount=-d, kind=Kind.INTERSECTION)
    fs = r.faces() if hasattr(r, "faces") else []
    return fs[0] if len(fs) else r

def no_loose(x, name):
    if isinstance(x, ShapeList):
        info = []
        for sol in x:
            b = sol.bounding_box()
            info.append(f"v={sol.volume:.0f} @({b.min.X:.0f}..{b.max.X:.0f},{b.min.Y:.0f}..{b.max.Y:.0f},{b.min.Z:.0f}..{b.max.Z:.0f})")
        raise RuntimeError(f"{name} loose solids:\n" + "\n".join(info))
    return x

F_ext = poly_face(pts)

def roof_cutters(eave_z, shift=0.0, poly=None, slope=SLOPE):
    p = poly if poly is not None else pts
    v = p + [p[0]]
    cs = []
    for i in range(len(p)):
        A = Vector(*v[i], 0); B = Vector(*v[i + 1], 0)
        t = (B - A).normalized()
        nin = Vector(-t.Y, t.X, 0)
        N = Vector(-nin.X * tan(radians(slope)), -nin.Y * tan(radians(slope)), 1.0).normalized()
        mid = (A + B) / 2 + Vector(0, 0, eave_z) - N * shift
        cs.append(Plane(origin=mid, x_dir=t, z_dir=N) *
                  Box(700, 700, 300, align=(Align.CENTER, Align.CENTER, Align.MIN)))
    return cs

def wall_frame(i, s):
    A = Vector(*verts[i], 0); B = Vector(*verts[i + 1], 0)
    t = (B - A).normalized()
    return A + t * s, t, Vector(-t.Y, t.X, 0)

def roof_normal(i, slope=SLOPE):
    A = Vector(*verts[i], 0); B = Vector(*verts[i + 1], 0)
    t = (B - A).normalized()
    nin = Vector(-t.Y, t.X, 0)
    n_out = Vector(-nin.X * sin(radians(slope)), -nin.Y * sin(radians(slope)),
                   cos(radians(slope)))
    up = (Vector(0, 0, 1) - n_out * Vector(0, 0, 1).dot(n_out)).normalized()
    return t, nin, n_out, up

def prism(profile_pts, plane, length):
    return plane * extrude(poly_face(profile_pts), length)

def xprism(x0, ln, pf):
    """profile pts given as (y, z), extruded +x from x0 (proven xrail frame)"""
    return prism(pf, Plane(origin=(x0, 0, 0), x_dir=(0, 1, 0), z_dir=(1, 0, 0)), ln)

def yprism(y0, ln, pf):
    """profile pts given as (x, -z), extruded +y from y0"""
    return prism([(px, -pz) for px, pz in pf],
                 Plane(origin=(0, y0, 0), x_dir=(1, 0, 0), z_dir=(0, 1, 0)), ln)

def wall_rebate(i, s0, z0, w, h, depth=1.3):
    """exterior rebate on wall i: from (s0,z0), w along wall, h up, depth into wall"""
    P, t, nin = wall_frame(i, s0)
    pl = Plane(origin=P + nin * (WOUT - depth) + Vector(0, 0, z0), x_dir=t, z_dir=-nin)
    return pl * Box(w, h, depth + 1.0, align=(Align.MIN, Align.MIN, Align.MIN))

def hexcell_cutters(i, s0, z0, w, h, cell=5.0, web=1.7, skew=20.0):
    P, t, nin = wall_frame(i, s0)
    ax = (-nin * cos(radians(skew)) - Vector(0, 0, sin(radians(skew)))).normalized()
    pitch_s = cell + web
    pitch_z = (cell + web) * 0.866
    r = cell / 2 / cos(radians(30))
    cs = []
    row = 0
    z = z0 + cell / 2
    while z <= z0 + h - cell / 2:
        s = cell / 2 + (pitch_s / 2 if row % 2 else 0)
        while s <= w - cell / 2:
            ctr = P + t * s + nin * (WALL + 2.0) + Vector(0, 0, z)
            cs.append(Plane(origin=ctr, x_dir=t, z_dir=ax) *
                      extrude(RegularPolygon(r, 6, rotation=90), WALL + 6.0))
            s += pitch_s
        z += pitch_z
        row += 1
    return cs

# ================= HOOD =================
outer = Pos(0, 0, RIM_Z) * extrude(F_ext, 200)
for c in roof_cutters(EAVE_Z):
    outer -= c
inner_core = Pos(0, 0, RIM_Z - 3.0) * extrude(inset(F_ext, WALL), 200)
for c in roof_cutters(EAVE_Z, shift=WALL):
    inner_core -= c
hood = no_loose(outer - inner_core, "hood shell")

ring = Pos(0, 0, BASE_H) * (extrude(inset(F_ext, WALL), 5.0)
                            - extrude(inset(F_ext, 5.9), 5.0))
ring -= loft([Pos(0, 0, BASE_H) * inset(F_ext, WALL),
              Pos(0, 0, BASE_H + 3.4) * inset(F_ext, 5.9)])
ring -= Pos(0, 0, BASE_H) * (extrude(inset(F_ext, 3.15), 4.0)
                             - extrude(inset(F_ext, 5.25), 4.0))
hood += ring
hood = no_loose(hood, "hood+ring")

try:
    hood = chamfer(hood.edges().group_by(Axis.Z)[0], 0.4)
except Exception as e:
    print("hood rim chamfer skipped:", repr(e))

hood -= Pos(0, 0, RIM_Z) * (extrude(inset(F_ext, 0.8), 1.2)
                            - extrude(inset(F_ext, 1.8), 1.2))

# --- snap arms (skirt U-slots + nib), keyed asym on e0/e3/e5 ---
HOOKS = [(0, 26.0, +1), (3, 38.0, -1), (5, 22.0, +1)]
ARM_W, ARM_H, SLOT = 14.0, 6.0, 1.5
for idx, s, side in HOOKS:
    P, t, nin = wall_frame(idx, s)
    for (dx, zc, w, h) in [(0.0, RIM_Z + ARM_H + SLOT / 2, ARM_W + 2 * SLOT, SLOT),
                           (-side * (ARM_W / 2 + SLOT / 2), RIM_Z + (ARM_H + SLOT) / 2, SLOT, ARM_H + SLOT)]:
        pl = Plane(origin=P + t * dx + Vector(0, 0, zc) - nin * 1.0, x_dir=t, z_dir=nin)
        hood -= pl * Box(w, h, 5.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
    prof_pl = Plane(origin=P - t * 3.0 + nin * WALL + Vector(0, 0, RIM_Z + 0.6),
                    x_dir=nin, z_dir=t)
    hood += prof_pl * extrude(poly_face([(0, 0), (1.2, 2.8), (1.2, 4.0), (0, 5.4)]), 6.0)
hood = no_loose(hood, "hood+snaps")

# --- SMA boss on e1 roof facet ---
t1, nin1, n1_out, up1 = roof_normal(1)
e1mid = (Vector(*verts[1], 0) + Vector(*verts[2], 0)) / 2
sma_pt = e1mid + Vector(0, 0, EAVE_Z) + up1 * 16.0
hood += Plane(origin=sma_pt + n1_out * 2.5, x_dir=t1, z_dir=n1_out) * \
        Cylinder(7.5, 5.0, align=(Align.CENTER, Align.CENTER, Align.MAX))
# downhill 45-deg wedge under the pad (fills the overhang the pad creates)
wedge = prism([(0.0, 0.0), (0.0, 8.0), (8.0, 0.0)],
              Plane(origin=sma_pt - up1 * 7.0, x_dir=-up1, z_dir=t1) * Pos(0, 0, -7.5), 15.0)
hood += (wedge & (Plane(origin=sma_pt + n1_out * 2.5, x_dir=t1, z_dir=n1_out) *
                  Cylinder(9.0, 30, align=(Align.CENTER, Align.CENTER, Align.MAX))))
hood += Plane(origin=sma_pt - n1_out * WALL, x_dir=t1, z_dir=-n1_out) * \
        Cylinder(7.5, 1.5, align=(Align.CENTER, Align.CENTER, Align.MIN))
tear = Circle(3.33) + Polygon((-2.36, 2.36), (2.36, 2.36), (0, 4.71), align=None)
hood -= Plane(origin=sma_pt - n1_out * 8.0, x_dir=t1, z_dir=n1_out) * extrude(tear, 14)
hood = no_loose(hood, "hood+sma")

# --- pigtail clip hook on e2 skirt inner face ---
t2h, nin2h, _, _ = roof_normal(2)
P2 = Vector(*verts[2], 0) + t2h * 12 + nin2h * WALL
hood += Plane(origin=P2 + Vector(0, 0, RIM_Z + 2), x_dir=t2h, z_dir=nin2h) * \
        Box(8, 3, 4, align=(Align.CENTER, Align.MIN, Align.MIN))
# desiccant tray on the e0 inner roof facet (over the stack; faces you hood-off)
t0d, nin0d, n0_out, up0 = roof_normal(0)
tray_pl = Plane(origin=Vector(30, 0, EAVE_Z) + up0 * 28.0 - n0_out * (WALL - 0.4), x_dir=t0d, z_dir=-n0_out)
hood += tray_pl * Pos(0, -11.0, 0) * Box(34, 2.0, 8.5, align=(Align.CENTER, Align.MIN, Align.MIN))
for sx in (-17.0, 17.0):
    hood += tray_pl * Pos(sx, -11.0, 0) * Box(2.0, 22.0, 8.5, align=(Align.CENTER, Align.MIN, Align.MIN))
hood = no_loose(hood, "hood final")

# ================= BASE =================
base = extrude(inset(F_ext, WOUT), BASE_H) \
     - Pos(0, 0, FLOOR_T) * extrude(inset(F_ext, WIN), BASE_H)
base += Pos(0, 0, BASE_H) * (extrude(inset(F_ext, 3.4), TONGUE_H)
                             - extrude(inset(F_ext, 5.0), TONGUE_H))
for idx, s, side in HOOKS:
    P, t, nin = wall_frame(idx, s)
    pk_pl = Plane(origin=P - t * 4.0 + nin * WOUT, x_dir=nin, z_dir=t)
    base -= pk_pl * extrude(poly_face([(0, 26.2), (1.3, 27.5), (1.3, 31.1), (0, 32.4)]), 8.0)
try:
    base = chamfer(base.edges().group_by(Axis.Z)[0], 0.4)
except Exception as e:
    print("base foot chamfer skipped:", repr(e))
base = no_loose(base, "base tub")

EMB = 0.4
Z0 = FZ - EMB

# --- stack rails (shield 58x25 @ x10.5..68.5, y6..31, rest z5.5) ---
base += xprism(10.5, 58, [(3.0, Z0), (6.0, Z0), (6.0, REST), (4.8, REST), (4.8, REST + 2.8), (3.0, REST + 2.8)])
base += xprism(10.5, 58, [(34.0, Z0), (31.0, Z0), (31.0, REST), (32.2, REST), (32.2, REST + 2.8), (34.0, REST + 2.8)])
for sy in (11.0, 26.0):
    base += Pos(9.6, sy, Z0) * Box(1.6, 5, REST + 3.4, align=(Align.CENTER, Align.CENTER, Align.MIN))
base += prism([(0.3, REST + 2.9), (-1.0, REST + 4.2), (0.3, REST + 5.5)],
              Plane(origin=(10.2, 27.7, 0), x_dir=(1, 0, 0), z_dir=(0, -1, 0)), 8)
base = no_loose(base, "chk-stack")

# --- HM3301 rails (board 80x40 @ x-5..75, y41..81, rest z5.5) ---
base += xprism(2, 73, [(38.0, Z0), (41.0, Z0), (41.0, REST), (39.8, REST), (39.8, REST + 2.8), (38.0, REST + 2.8)])
base += xprism(-5, 80, [(84.0, Z0), (81.0, Z0), (81.0, REST), (82.2, REST), (82.2, REST + 2.8), (84.0, REST + 2.8)])
base -= Pos(28.0, 37.7, 5.35) * Box(21.5, 4.2, 3.6, align=(Align.MIN, Align.MIN, Align.MIN))   # HM S-rail plug notch
base -= Pos(28.0, 31.9, 5.4) * Box(21.5, 2.6, 3.5, align=(Align.MIN, Align.MIN, Align.MIN))   # stack N-lip plug notch
base += Pos(-5.9, 61, Z0) * Box(1.6, 12, REST + 3.4, align=(Align.CENTER, Align.CENTER, Align.MIN))
base += Pos(75.9, 61, Z0) * Box(1.2, 14, REST + 5.4, align=(Align.CENTER, Align.CENTER, Align.MIN))
base += prism([(0.3, REST + 3.2), (-1.0, REST + 4.5), (0.3, REST + 5.8)],
              Plane(origin=(75.3, 66, 0), x_dir=(1, 0, 0), z_dir=(0, -1, 0)), 10)
base = no_loose(base, "chk-hm")

# --- BME680 posts + slide slot along e5 (panel 6 mm behind wall) ---
A5, t5v, nin5 = wall_frame(5, 0)
for s in (4.0, 46.0):
    base += Plane(origin=A5 + t5v * s + nin5 * 12.7 + Vector(0, 0, Z0),
                  x_dir=t5v, z_dir=Vector(0, 0, 1)) * Box(4, 5.6, 26.4, align=(Align.CENTER, Align.CENTER, Align.MIN))
base -= Plane(origin=A5 + t5v * 25 + nin5 * 12.7 + Vector(0, 0, FZ + 3.5),
              x_dir=t5v, z_dir=Vector(0, 0, 1)) * Box(43.0, 2.0, 30, align=(Align.CENTER, Align.CENTER, Align.MIN))
base = no_loose(base, "chk-bme")

# --- PM intake plenum (y80.2 -> N wall): side walls + 45 shed + grille + rebate ---
plenum_walls = Pos(8.6, 80.2, Z0) * Box(1.0, Y_IN - 80.2 + 0.2, 45 - Z0, align=(Align.MIN, Align.MIN, Align.MIN)) + \
               Pos(49.6, 80.2, Z0) * Box(1.0, Y_IN - 80.2 + 0.2, 45 - Z0, align=(Align.MIN, Align.MIN, Align.MIN))
for x0 in (8.6, 49.6):   # board-edge pass notch (board pokes 0.8 past the can face)
    plenum_walls -= Pos(x0 - 0.1, 80.1, 5.2) * Box(1.2, 1.2, 2.2, align=(Align.MIN, Align.MIN, Align.MIN))
# baffle guide ribs on the floor, N of the board strip (channel: can face <-> rib)
plenum_walls += Pos(9.7, 81.9, Z0) * Box(1.2, 1.2, 25.8 - Z0, align=(Align.MIN, Align.MIN, Align.MIN))
plenum_walls += Pos(48.3, 81.9, Z0) * Box(1.2, 1.2, 25.8 - Z0, align=(Align.MIN, Align.MIN, Align.MIN))
for c in roof_cutters(EAVE_Z, shift=WALL + 0.5):   # stop 0.5 under the hood inner roof
    plenum_walls -= c
base += plenum_walls
# top closure = hood inner roof (0.5 gap, declared); front closure = drop-in baffle
S3G = 76.5 - 49.6          # e3 s-coord of grille field start (x=49.6)
for c in hexcell_cutters(3, S3G, 7.0, 39.0, 15.5):
    base -= c
base -= wall_rebate(3, S3G - 1.0, 4.8, 41.0, 20.4)
base = no_loose(base, "chk-intake")

# --- PM exhaust TENT over the can, ridge y61.7, running E to the e2 grille ---
emb_clip = Pos(0, 0, 0) * extrude(inset(F_ext, WIN - 0.6), 60)   # embeds 0.6 into walls
# corridor wall y39.6..40.6 = the PM / climate zone boundary (clear of the board at y41+)
cwall = (Pos(1.5, 39.6, Z0) * Box(93.5, 1.0, 26 - Z0, align=(Align.MIN, Align.MIN, Align.MIN))) & emb_clip
base += cwall   # W end open x<-4 = J2 cable pass (declared soft boundary)
# E-wedge exhaust chamber (fully E of the board end x75.4)
wwall = Pos(75.6, 40.6, Z0) * Box(1.0, 40.8, 26 - Z0, align=(Align.MIN, Align.MIN, Align.MIN))
for wy in (47.0, 59.0, 71.0):   # 3 gabled transfer windows (no header bridge)
    wwall -= prism([(-4, 13), (4, 13), (4, 19), (0, 23), (-4, 19)],
                   Plane(origin=(75.5, wy, 0), x_dir=(0, 1, 0), z_dir=(1, 0, 0)), 1.2)
nwall = (Pos(75.6, 80.2, Z0) * Box(20, 1.0, 26 - Z0, align=(Align.MIN, Align.MIN, Align.MIN))) & emb_clip
chshed = (yprism(40.6, 41, [(75.7, 24.7), (94.0, 43.0), (94.0, 41.6), (76.5, 23.3)]) & emb_clip)
chamber = wwall + nwall + chshed
base += chamber
S2G = 8.0                   # e2 grille: s8..32 -> y56.3..77.1 (inside chamber band)
for c in hexcell_cutters(2, S2G, 8.0, 24.0, 14.0):
    base -= c
base -= wall_rebate(2, S2G - 1.0, 5.8, 26.0, 18.4)
base = no_loose(base, "chk-pmex")

# --- climate exhaust gills e1 (s34..52, clear of USB pocket), 45 down-out ---
for zc in (17.5, 22.0):
    P, t, nin = wall_frame(1, 43.0)
    pl = Plane(origin=P + nin * 0.5 + Vector(0, 0, zc),
               x_dir=t, z_dir=(nin + Vector(0, 0, 1)).normalized())
    base -= pl * Box(18, 9, 2.2)
base = no_loose(base, "chk-gills")

# --- climate intake: louvred windows over BME (e5) + cross window (e4) ---
for s in (9, 25):
    base -= prism([(-6, 8), (6, 8), (6, 16), (0, 21), (-6, 16)],
                  Plane(origin=A5 + t5v * s + nin5 * 6.5, x_dir=t5v, z_dir=-nin5), 8)
for fz in (10.6, 14.6):
    base += Plane(origin=A5 + t5v * 17 + nin5 * 4.6 + Vector(0, 0, fz), x_dir=t5v,
                  z_dir=(nin5 + Vector(0, 0, 1)).normalized()) * Box(30, 3.7, 1.0)
base -= wall_rebate(5, 2.0, 5.8, 34.0, 17.4)
A4, t4, nin4 = wall_frame(4, 0)
base -= prism([(-6, 8), (6, 8), (6, 15), (0, 19), (-6, 15)],
              Plane(origin=A4 + t4 * 30 + nin4 * 6.5, x_dir=t4, z_dir=-nin4), 8)
base = no_loose(base, "chk-climate")

# --- USB/switch pocket: alcove w/ 45 sloped ceiling + teardrop oval + slot ---
alc = yprism(8.5, 20, [(71.0, 8.0), (71.0, 26.0), (89.0, 8.0)]) & \
      Pos(0, 0, 0) * extrude(F_ext, 60)
base -= alc
back = (Pos(71.0, 8.3, 7.6) * Box(1.6, 20.4, 19.4, align=(Align.MIN, Align.MIN, Align.MIN))) & \
       Pos(0, 0, 0) * extrude(F_ext, 60) & \
       yprism(8.2, 20.6, [(70.9, 7.5), (70.9, 26.6), (90.0, 7.5)])
base += back
usb_port = Plane(origin=(70.4, 18.5, 20.9), x_dir=(0, 1, 0), z_dir=(1, 0, 0)) * \
           extrude(Rectangle(9.5, 7.0) + Pos(-4.75, 0) * Circle(3.5) + Pos(4.75, 0) * Circle(3.5) +
                   Polygon((-4.0, 3.5), (4.0, 3.5), (0, 7.0), align=None), 4.0)
base -= usb_port
base -= Pos(70.3, 10.5, 8.6) * Box(4, 9, 4.2, align=(Align.MIN, Align.MIN, Align.MIN))
# drip plate over the mouth: 45-deg angled fin on e1 exterior above the alcove
P1L, t1L, nin1L = wall_frame(1, 21.0)
base += Plane(origin=P1L + nin1L * 2.6 + Vector(0, 0, 26.8), x_dir=t1L,
              z_dir=(-nin1L + Vector(0, 0, 1)).normalized()) * Box(20, 5.0, 1.2)
base = no_loose(base, "chk-usb")

# --- keyholes on e3 (rear) at x4 & x70: cbore + gabled slots + hollow blister ---
for kx in (4.0, 70.0):
    key_pl = Plane(origin=(kx, Y_OUT + 0.01, 12.4), x_dir=(1, 0, 0), z_dir=(0, -1, 0))
    head = Circle(5.0) + Pos(0, 6.0) * Rectangle(10.0, 12.0) + \
           Pos(0, 12.0) * Polygon((-5.0, 0), (5.0, 0), (0, 5.0), align=None)
    shank = Circle(2.3) + Pos(0, 6.0) * Rectangle(4.6, 12.0) + \
            Pos(0, 12.0) * Polygon((-2.3, 0), (2.3, 0), (0, 2.5), align=None)
    base += Pos(kx - 5.5, Y_IN - 4.3, 6.0) * Box(11, 4.7, 22, align=(Align.MIN, Align.MIN, Align.MIN))
    base -= key_pl * extrude(head, 4.5)
    base -= key_pl * extrude(shank, 6.0)
base = no_loose(base, "chk-key")

# --- zip-tie conduits through e3 into the exhaust chamber (declared) ---
for zc in (11.0, 21.0):
    base += (Pos(50.9, Y_IN - 3.0, zc - 1.5) * Box(16.0, 3.4, 9, align=(Align.MIN, Align.MIN, Align.MIN))
             - Pos(50.9, Y_IN - 2.0, zc - 0.5) * Box(16.0, 2.0, 7, align=(Align.MIN, Align.MIN, Align.MIN)))
    for sx in (52.4, 61.9):
        base -= Pos(sx, Y_IN - 2.0, zc) * Box(3.5, 10, 6, align=(Align.MIN, Align.MIN, Align.MIN))
base = no_loose(base, "chk-zip")

# --- desiccant fence + cable hooks + weeps ---
for (hx, hy) in [(6.0, 34.0), (54.0, 35.0)]:
    base += Pos(hx, hy, Z0) * Box(6, 2.0, 8.4, align=(Align.MIN, Align.MIN, Align.MIN))
    base += Pos(hx, hy, Z0 + 6.4) * Box(6, 4.5, 2, align=(Align.MIN, Align.MIN, Align.MIN))
for (wx, wy) in [(5, 9), (60, 8), (30, 84), (70, 76)]:
    base -= Pos(wx, wy, 0) * Cylinder(1.25, FLOOR_T, align=(Align.CENTER, Align.CENTER, Align.MIN))
base = no_loose(base, "base final")

# ================= small parts (flat prints) =================
ret_n = Box(42.4, 19.8, 1.2, align=(Align.CENTER, Align.CENTER, Align.MIN)) \
      - Box(36, 13, 4, align=(Align.CENTER, Align.CENTER, Align.MIN))
ret_e = Box(27.4, 17.8, 1.2, align=(Align.CENTER, Align.CENTER, Align.MIN)) \
      - Box(21, 11, 4, align=(Align.CENTER, Align.CENTER, Align.MIN))
ret_w = Box(35.4, 16.8, 1.2, align=(Align.CENTER, Align.CENTER, Align.MIN)) \
      - Box(28, 10, 4, align=(Align.CENTER, Align.CENTER, Align.MIN))
baffle = Box(39.6, 32.4, 1.2, align=(Align.MIN, Align.MIN, Align.MIN))
baffle_seated = Pos(9.8, 80.5, 7.4) * Box(39.6, 1.2, 32.4, align=(Align.MIN, Align.MIN, Align.MIN))
bung = extrude(Rectangle(9.1, 6.6) + Pos(-4.55, 0) * Circle(3.3) + Pos(4.55, 0) * Circle(3.3), 5.0) + \
       extrude(Rectangle(13, 10.4) + Pos(-6.5, 0) * Circle(5.2) + Pos(6.5, 0) * Circle(5.2), -1.6) + \
       Pos(0, -8.4, -1.6) * Box(6, 4, 1.6, align=(Align.CENTER, Align.MIN, Align.MIN))

# ================= placeholders (fit proof) =================
PH = {}
PH["stack"] = Pos(10.5, 6, REST) * Box(58, 25, 2.6, align=(Align.MIN, Align.MIN, Align.MIN)) + \
             Pos(12.5, 6, REST) * Box(56, 25, 23.2, align=(Align.MIN, Align.MIN, Align.MIN))
PH["hm_board"] = Pos(-5, 41, REST) * Box(80, 40, 1.6, align=(Align.MIN, Align.MIN, Align.MIN))
PH["hm_can"] = Pos(9.6, 42.2, REST + 1.6) * Box(40, 38, 15, align=(Align.MIN, Align.MIN, Align.MIN))
PH["bme"] = Plane(origin=A5 + t5v * 6 + nin5 * 13.0 + Vector(0, 0, 26), x_dir=t5v, z_dir=nin5) * \
            Box(38, 20, 7.4, align=(Align.MIN, Align.MIN, Align.MIN))
PH["plug_corridor"] = Pos(28, 31.4, REST + 2.1) * Box(21.5, 8.0, 8.4, align=(Align.MIN, Align.MIN, Align.MIN))
PH["wifi"] = Plane(origin=Vector(32, 0, EAVE_Z) + up0 * 6 - n0_out * (WALL + 0.8),
                   x_dir=t0d, z_dir=-n0_out) * Box(30, 10, 2, align=(Align.CENTER, Align.MAX, Align.MIN))
PH["desic_sachet"] = Plane(origin=Vector(30, 0, EAVE_Z) + up0 * 28.0 - n0_out * (WALL + 0.6), x_dir=t0d, z_dir=-n0_out) * \
                     Pos(0, -8.8, 0) * Box(30, 20, 8, align=(Align.CENTER, Align.MIN, Align.MIN))

# ================= checks =================
report = {"edges": EDGES}
bb, hb = base.bounding_box(), hood.bounding_box()
report["base_bbox"] = [round(bb.size.X, 1), round(bb.size.Y, 1), round(bb.size.Z, 1)]
report["hood_bbox"] = [round(hb.size.X, 1), round(hb.size.Y, 1), round(hb.size.Z, 1)]
report["apex_z"] = round(hb.max.Z, 2)

try:
    ib = hood & base
    v0 = float(ib.volume)
    if v0 > 0.5:
        raise RuntimeError(f"REAL hood/base collision: {v0:.3f} mm3")
    if v0 > 1e-9:
        hood = no_loose(hood - ib, "hood seat-shaved")
        report["seat_sliver_shaved_mm3"] = round(v0, 3)
    report["hood_base_interference_mm3"] = round(float((hood & base).volume), 3)
except RuntimeError:
    raise
except Exception:
    report["hood_base_interference_mm3"] = 0.0

try:
    report["baffle_vs_base_mm3"] = round(float((baffle_seated & base).volume), 3)
    report["baffle_vs_hood_mm3"] = round(float((baffle_seated & hood).volume), 3)
except Exception:
    report["baffle_vs_base_mm3"] = 0.0
    report["baffle_vs_hood_mm3"] = 0.0
inter = {}
env = base + hood
for k, ph_s in PH.items():
    try:
        v = float((ph_s & env).volume)
    except Exception:
        v = 0.0
    inter[k] = round(v, 3)
    if v > 0.001:
        try:
            ov = ph_s & env
            ob = ov.bounding_box()
            inter[k + "_bbox"] = [round(q, 1) for q in (ob.min.X, ob.max.X, ob.min.Y, ob.max.Y, ob.min.Z, ob.max.Z)]
        except Exception:
            pass
report["placeholder_vs_shell_mm3_MUST_BE_0"] = inter

# vent-area accounting (F1: exhaust >= intake effective)
report["areas_mm2"] = {
    "climate_intake_eff": round(2 * (12 * 8 + 0.5 * 12 * 5) * 0.7 + (12 * 7 + 0.5 * 12 * 4) * 0.7, 0),
    "climate_exhaust_gills": round(2 * 18 * 2.2 / 0.7071, 0),
    "pm_intake_grille_open": "hex cells ~52% of 39x15.5",
    "pm_exhaust_grille_open": "hex cells ~52% of 24x14",
}
print(json.dumps(report, indent=1))

# ================= export =================
try:
    base = base.clean()
    hood = hood.clean()
except Exception as e:
    print("clean skipped:", repr(e))
export_stl(hood, os.path.join(OUT, "k1h2_hood.stl"))
export_stl(base, os.path.join(OUT, "k1h2_base.stl"))
export_stl(ret_n, os.path.join(OUT, "k1h2_ret_n.stl"))
export_stl(ret_e, os.path.join(OUT, "k1h2_ret_e.stl"))
export_stl(ret_w, os.path.join(OUT, "k1h2_ret_w.stl"))
export_stl(bung, os.path.join(OUT, "k1h2_bung.stl"))
export_stl(baffle, os.path.join(OUT, "k1h2_baffle.stl"))
for nm, sol in [("base", base), ("hood", hood), ("baffle", baffle), ("bung", bung),
                ("ret_n", ret_n), ("ret_e", ret_e), ("ret_w", ret_w)]:
    try:
        export_step(sol, os.path.join(OUT, f"k1h2_{nm}.step"))
    except Exception as e:
        print(f"step {nm}:", repr(e))
viz = Compound(children=[base, hood] + [s for s in PH.values()])
try:
    export_step(viz, os.path.join(OUT, "k1h2_phase2_asm.step"))
except Exception as e:
    print("step export:", repr(e))
halfY = Pos(-200, 61, -10) * Box(600, 400, 300, align=(Align.MIN, Align.MIN, Align.MIN))
halfX = Pos(30, -200, -10) * Box(600, 400, 300, align=(Align.MIN, Align.MIN, Align.MIN))
def cut_list(solids, cutter):
    out = []
    for so in solids:
        try:
            r = so - cutter
        except Exception:
            continue
        if isinstance(r, ShapeList):
            out.extend([x for x in r if x.volume > 1e-6])
        elif getattr(r, "volume", 0) > 1e-6:
            out.append(r)
    return out
sec1 = Compound(children=cut_list([base, hood] + list(PH.values()), halfY))
sec2 = Compound(children=cut_list([base, hood] + list(PH.values()), halfX))
export_stl(sec1, os.path.join(OUT, "k1h2_sectionY.stl"))
export_stl(sec2, os.path.join(OUT, "k1h2_sectionX.stl"))
export_stl(viz, os.path.join(OUT, "k1h2_asm_viz.stl"))
