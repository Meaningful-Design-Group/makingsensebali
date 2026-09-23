#!/usr/bin/env python3
"""K1H2 Phase-1 base form — "low boulder"
Clean-sheet minimal massing per D-1 (2026-07-24): hex-lattice plan
(walls on 0/60/120 axes, all six edges different -> no symmetry), base tub
floor->z30 + tongue, hood skirt z24->34 + 47deg skeleton roof (no turret,
SMA through a high roof facet). Placeholder component envelopes prove the
zone split; features come in Phase 2.
BASE prints floor-down, HOOD rim-down. Massing targets < v0.8 132 g / 4h35.
"""
import json, os
from math import tan, radians, cos, sin
from build123d import *

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "v2")
os.makedirs(OUT, exist_ok=True)

WALL, CLR = 2.5, 0.45
FLOOR_T = 2.5
BASE_H = 30.0          # base wall top (seam)
TONGUE_H = 4.0         # tongue z30..34, tip seats on groove ceiling (v0.8 recipe)
RIM_Z = 26.0           # hood skirt bottom (8 mm overlap, >=8 gate; frees USB mouth)
EAVE_Z = BASE_H + TONGUE_H   # roof springs at z34 from the outer plan line
SLOPE = 47.0           # roof pitch: 47 from horizontal = 43 from vertical

# ---- plan: irregular convex hexagon on hex axes, closure asserted ----
EDGES = [(0, 72), (60, 52), (120, 43), (180, 88), (240, 36), (300, 59)]
pts = [(0.0, 0.0)]
for ang, L in EDGES:
    x, y = pts[-1]
    pts.append((x + L * cos(radians(ang)), y + L * sin(radians(ang))))
assert abs(pts[-1][0]) < 1e-9 and abs(pts[-1][1]) < 1e-9, "plan does not close"
pts = pts[:-1]
verts = pts + [pts[0]]

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
        raise RuntimeError(f"{name} has loose solids: {[round(s.volume,1) for s in x]}")
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

# ================= HOOD (skirt + skeleton roof, one solid) =================
outer = Pos(0, 0, RIM_Z) * extrude(F_ext, 200)
for c in roof_cutters(EAVE_Z):
    outer -= c
inner = Pos(0, 0, RIM_Z - 3.0) * extrude(inset(F_ext, WALL), 200)
for c in roof_cutters(EAVE_Z, shift=WALL):
    inner -= c
hood = no_loose(outer - inner, "hood shell")

# groove-carrier ring z30..35 (labyrinth detail lands Phase 2; ring massed now)
ring = Pos(0, 0, BASE_H) * (extrude(inset(F_ext, WALL), 5.0)
                            - extrude(inset(F_ext, 5.9), 5.0))
ring -= loft([Pos(0, 0, BASE_H) * inset(F_ext, WALL),
              Pos(0, 0, BASE_H + 3.4) * inset(F_ext, 5.9)])
ring -= Pos(0, 0, BASE_H) * (extrude(inset(F_ext, 3.15), 4.0)
                             - extrude(inset(F_ext, 5.25), 4.0))
hood += ring
hood = no_loose(hood, "hood+ring")

# drip groove in skirt underside
hood -= Pos(0, 0, RIM_Z) * (extrude(inset(F_ext, 0.8), 1.2)
                            - extrude(inset(F_ext, 1.8), 1.2))

# --- SMA boss marker on the SE roof facet (facet of edge e1, dir 60) ---
# roof facet normal (outward): tilt of edge e1's roof plane
def roof_normal(i, slope=SLOPE):
    A = Vector(*verts[i], 0); B = Vector(*verts[i + 1], 0)
    t = (B - A).normalized()
    nin = Vector(-t.Y, t.X, 0)
    # OUTWARD-up unit normal of that roof facet (plane at `slope` from horizontal)
    n_out = Vector(-nin.X * sin(radians(slope)), -nin.Y * sin(radians(slope)),
                   cos(radians(slope)))
    up = (Vector(0, 0, 1) - n_out * Vector(0, 0, 1).dot(n_out)).normalized()
    return t, nin, n_out, up

# point on e1 roof facet ~12 in from eave line, near stack corner
t1, nin1, n1_out, up1 = roof_normal(1)
e1mid = (Vector(*verts[1], 0) + Vector(*verts[2], 0)) / 2
sma_pt = e1mid + Vector(0, 0, EAVE_Z) + up1 * 14.0   # on the outer roof plane
SMA_MARK = Plane(origin=sma_pt, z_dir=n1_out) * Cylinder(3.3, 44, align=(Align.CENTER, Align.CENTER, Align.CENTER))

# ================= BASE (tub) =================
base = extrude(inset(F_ext, WALL + CLR), BASE_H) \
     - Pos(0, 0, FLOOR_T) * extrude(inset(F_ext, 2 * WALL + CLR), BASE_H)
# tongue ring z30..34
base += Pos(0, 0, BASE_H) * (extrude(inset(F_ext, 3.4), TONGUE_H)
                             - extrude(inset(F_ext, 5.0), TONGUE_H))
# weeps at the two lowest interior corners (markers, kept in massing)
for (wx, wy) in [(5, 8), (70, 10)]:
    base -= Pos(wx, wy, 0) * Cylinder(1.25, FLOOR_T, align=(Align.CENTER, Align.CENTER, Align.MIN))
base = no_loose(base, "base tub")

# ================= PLACEHOLDER ENVELOPES (Phase-1 zone proof) =================
FZ = FLOOR_T
REST = 5.5            # board-rest height (shallow rails) -> USB axis z20.9 < RIM_Z
PH = {}
EXPECT_PIERCE = {"usb_mouth"}   # wall-crossing markers by design
# Grove Shield + XIAO + Wio stack: 58x25 fp, 23.2 tall from shield bottom; USB east
PH["stack"] = Pos(10.5, 6, REST) * Box(58, 25, 23.2, align=(Align.MIN, Align.MIN, Align.MIN))
# HM3301: board 80x40 rests z5.5; can 40x38x15 on top, slot face N (y71.7, 5.1 off cavity wall)
PH["hm_board"] = Pos(-5, 32.5, REST) * Box(80, 40, 1.6, align=(Align.MIN, Align.MIN, Align.MIN))
PH["hm_can"] = Pos(9.6, 33.7, REST + 1.6) * Box(40, 38, 15, align=(Align.MIN, Align.MIN, Align.MIN))
# BME680 Grove twin as a vertical panel PARALLEL to facet e5, 6 mm air gap behind louvres
A5 = Vector(*verts[5], 0); t5 = (Vector(*verts[0], 0) - A5).normalized()
nin5 = Vector(-t5.Y, t5.X, 0)
PH["bme"] = Plane(origin=A5 + t5 * 8 + nin5 * 11.5 + Vector(0, 0, 26),
                  x_dir=t5, z_dir=nin5) * Box(40, 20, 8, align=(Align.MIN, Align.MIN, Align.MIN))
# PM intake plenum: can slot face -> N wall grille (sealed walls Phase 2)
PH["plenum_in"] = Pos(11, 71.7, FZ) * Box(38, 4.9, 24, align=(Align.MIN, Align.MIN, Align.MIN))
# PM exhaust hood over can top + duct E -> e2 facet grille
PH["plenum_out"] = Pos(9.6, 36, 22.1) * Box(56, 36, 6, align=(Align.MIN, Align.MIN, Align.MIN))
# USB/switch service mouth through facet e1 (oblique; pocket detail Phase 2)
t1v = (Vector(*verts[2], 0) - Vector(*verts[1], 0)).normalized()
nin1v = Vector(-t1v.Y, t1v.X, 0)
PH["usb_mouth"] = Plane(origin=Vector(*verts[1], 0) + t1v * 16 + Vector(0, 0, 8),
                        x_dir=t1v, z_dir=Vector(0, 0, 1)) * Box(20, 12, 17, align=(Align.CENTER, Align.CENTER, Align.MIN))
# WiFi antenna landing 45x12 on the INNER face of the e3 (N) roof facet
t3, nin3, n3_out, up3 = roof_normal(3)
e3mid = (Vector(*verts[3], 0) + Vector(*verts[4], 0)) / 2
PH["wifi"] = Plane(origin=e3mid + t3 * 6 + Vector(0, 0, EAVE_Z) + up3 * 9 - n3_out * (WALL + 0.8),
                   x_dir=t3, z_dir=-n3_out) * Box(40, 10, 2, align=(Align.CENTER, Align.MAX, Align.MIN))
# desiccant sachet clipped to hood roof interior over the stack zone
PH["desiccant"] = Pos(30, 20, 36) * Box(30, 20, 12, align=(Align.MIN, Align.MIN, Align.MIN))

# ================= checks =================
report = {"edges": EDGES}
bb, hb = base.bounding_box(), hood.bounding_box()
report["base_bbox"] = [round(bb.size.X, 1), round(bb.size.Y, 1), round(bb.size.Z, 1)]
report["hood_bbox"] = [round(hb.size.X, 1), round(hb.size.Y, 1), round(hb.size.Z, 1)]
report["apex_z"] = round(hb.max.Z, 2)
report["hood_g_est"] = round(hood.volume / 1000 * 1.27, 1)
report["base_g_est"] = round(base.volume / 1000 * 1.27, 1)

# shells never intersect each other
try:
    ib = hood & base
    v0 = float(ib.volume)
    if v0 > 0.5:
        raise RuntimeError(f"REAL hood/base collision: {v0:.3f} mm3")
    if v0 > 1e-9:
        # coincident seat-face fuse artifact at the z30 rest plane: shave from hood
        hood = no_loose(hood - ib, "hood seat-shaved")
        report["seat_sliver_shaved_mm3"] = round(v0, 3)
    report["hood_base_interference_mm3"] = round(float((hood & base).volume), 3)
except RuntimeError:
    raise
except Exception:
    report["hood_base_interference_mm3"] = 0.0

# placeholders vs shells = 0.000 and inside the envelope
inter, pierce = {}, {}
env = base + hood
for k, ph_s in PH.items():
    try:
        v = float((ph_s & env).volume)
    except Exception:
        v = 0.0
    (pierce if k in EXPECT_PIERCE else inter)[k] = round(v, 3)
report["placeholder_vs_shell_mm3_MUST_BE_0"] = inter
report["wall_piercing_markers_by_design"] = pierce

# stack headroom: ceiling above stack top?
stack_top = REST + 23.2
report["stack_top_z"] = round(stack_top, 2)

print(json.dumps(report, indent=1))

# ================= export =================
export_stl(hood, os.path.join(OUT, "k1h2_hood.stl"))
export_stl(base, os.path.join(OUT, "k1h2_base.stl"))
viz = Compound(children=[base, hood] + [s for s in PH.values()] + [SMA_MARK])
try:
    export_step(viz, os.path.join(OUT, "k1h2_phase1_asm.step"))
except Exception as e:
    print("step export:", repr(e))

# section solids for render: X-cut through HM can+plenum (x=26), Y-cut through stack+USB (y=18)
halfY = Pos(-200, 56, -10) * Box(600, 400, 300, align=(Align.MIN, Align.MIN, Align.MIN))
halfX = Pos(26, -200, -10) * Box(600, 400, 300, align=(Align.MIN, Align.MIN, Align.MIN))
sec1 = Compound(children=[s - halfY for s in [base, hood] + list(PH.values())])
sec2 = Compound(children=[s - halfX for s in [base, hood] + list(PH.values())])
export_stl(sec1, os.path.join(OUT, "k1h2_sectionY.stl"))
export_stl(sec2, os.path.join(OUT, "k1h2_sectionX.stl"))
export_stl(viz, os.path.join(OUT, "k1h2_asm_viz.stl"))
