#!/usr/bin/env python3
"""KIT1-HEX v0.8 base-form — 'basalt hood'
Hex-grid plan (walls on 0/60/120 axes). Roof = lower envelope of 52deg planes
(straight-skeleton-by-CSG). SMA on a printed DORMER on the SE facet: vertical
hex-legal front face (nut seat), 45deg shed cap, all self-supporting.
BASE prints floor-down, HOOD rim-down, support-free by design.
"""
import json, os
from math import tan, radians, cos, sin
from build123d import *

OUT = os.path.dirname(os.path.abspath(__file__))

WALL, CLR = 2.5, 0.45
RIM_Z, BASE_H, EAVE_Z, SLOPE = 24.0, 34.0, 46.0, 52.0
PAD_H, FLOOR_T = 2.0, 2.5

# convex irregular hexagon, all edges different -> no mirror, no point symmetry
EDGES = [(0,74),(60,70),(120,30),(180,100),(240,44),(300,56)]
pts = [(0.0, 0.0)]
for ang, L in EDGES:
    x, y = pts[-1]
    pts.append((x + L*cos(radians(ang)), y + L*sin(radians(ang))))
assert abs(pts[-1][0]) < 1e-9 and abs(pts[-1][1]) < 1e-9
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

def roof_cutters(eave_z, shift=0.0, poly=None):
    p = poly if poly is not None else pts
    v = p + [p[0]]
    cs = []
    for i in range(len(p)):
        A = Vector(*v[i], 0); B = Vector(*v[i+1], 0)
        t = (B - A).normalized()
        nin = Vector(-t.Y, t.X, 0)
        N = Vector(-nin.X*tan(radians(SLOPE)), -nin.Y*tan(radians(SLOPE)), 1.0).normalized()
        mid = (A + B)/2 + Vector(0, 0, eave_z) - N*shift
        cs.append(Plane(origin=mid, x_dir=t, z_dir=N) *
                  Box(700, 700, 300, align=(Align.CENTER, Align.CENTER, Align.MIN)))
    return cs

def wall_frame(i, s):
    A = Vector(*verts[i], 0); B = Vector(*verts[i+1], 0)
    t = (B - A).normalized()
    return A + t*s, t, Vector(-t.Y, t.X, 0)

# ================= HOOD =================
outer = Pos(0, 0, RIM_Z) * extrude(F_ext, 140)
for c in roof_cutters(EAVE_Z):
    outer -= c

# --- SMA turret: small asymmetric hex column through the roof, east ---
T_EDGES = [(0,13),(60,8),(120,7),(180,14),(240,7),(300,8)]
tp = [(87.8, 53.6)]
for ang, L in T_EDGES:
    x, y = tp[-1]
    tp.append((x + L*cos(radians(ang)), y + L*sin(radians(ang))))
assert abs(tp[-1][0]-tp[0][0]) < 1e-6 and abs(tp[-1][1]-tp[0][1]) < 1e-6
tp = tp[:-1]
# every turret vertex >= 3.5 inside the main plan
for tx, ty in tp:
    for i in range(len(pts)):
        A = Vector(*verts[i], 0); B = Vector(*verts[i+1], 0)
        t = (B - A).normalized(); nin = Vector(-t.Y, t.X, 0)
        dd = (Vector(tx, ty, 0) - A).dot(nin)
        assert dd >= 3.5, f"turret vertex ({tx},{ty}) only {dd:.2f} from main edge {i}"
F_t = poly_face(tp)
T_EAVE = 94.0
t_outer = Pos(0, 0, 35.0) * extrude(F_t, 85)
for c in roof_cutters(T_EAVE, poly=tp):
    t_outer -= c
outer += t_outer
outer = no_loose(outer, "outer+dormer")

inner = Pos(0, 0, RIM_Z - 3.0) * extrude(inset(F_ext, WALL), 140)
for c in roof_cutters(EAVE_Z, shift=WALL):
    inner -= c
t_inner = Pos(0, 0, 35.0) * extrude(inset(F_t, 2.5), 85)
for c in roof_cutters(T_EAVE, shift=WALL, poly=tp):
    t_inner -= c
hood = outer - inner - t_inner

# groove-carrier ring z34..39, 45deg underside, groove to z38 (tongue seats)
ring = Pos(0,0,BASE_H) * (extrude(inset(F_ext, WALL), 5.0)
                          - extrude(inset(F_ext, 5.9), 5.0))
ring -= loft([Pos(0,0,BASE_H) * inset(F_ext, WALL),
              Pos(0,0,BASE_H+3.4) * inset(F_ext, 5.9)])
ring -= Pos(0,0,BASE_H) * (extrude(inset(F_ext, 3.15), 4.0)
                           - extrude(inset(F_ext, 5.25), 4.0))
hood += ring
hood = no_loose(hood, "hood+ring")

# elephant-foot chamfer at rim BEFORE detail cuts
try:
    hood = chamfer(hood.edges().group_by(Axis.Z)[0], 0.4)
except Exception as e:
    print("rim chamfer skipped:", repr(e))

# drip groove in skirt underside
hood -= Pos(0,0,RIM_Z) * (extrude(inset(F_ext, 0.8), 1.2)
                          - extrude(inset(F_ext, 1.8), 1.2))

# SMA teardrop bore through turret south face (wall 2.5 + pad 1.5 = 4.0)
b_t = Vector(1, 0, 0); b_n = Vector(0, 1, 0)          # south face: inward = +Y
b_ctr = Vector(tp[0][0] + 5.5, tp[0][1], 72.0)
hood += Plane(origin=b_ctr + b_n*WALL, x_dir=b_t, z_dir=-b_n) * \
        Box(12, 12, 1.5, align=(Align.CENTER, Align.CENTER, Align.MAX))
hood += Plane(origin=Vector(b_ctr.X - 6.0, tp[0][1] + WALL, 0),
              x_dir=b_n, z_dir=b_t) * \
        extrude(poly_face([(0.0,64.5),(1.5,66.0),(0.0,66.0)]), 12.0)
tear = Circle(3.33) + Polygon((-2.36,2.36),(2.36,2.36),(0,4.71), align=None)
hood -= Plane(origin=b_ctr - b_n*2.0, x_dir=-b_t, z_dir=b_n) * extrude(tear, 8)

# snap arms in skirt (U-slot at rim, nib inward), asym keying
HOOKS = [(0, 24.0, +1), (3, 30.0, -1), (5, 20.0, +1)]
ARM_W, ARM_H, SLOT = 14.0, 6.0, 1.5
for idx, s, side in HOOKS:
    P, t, nin = wall_frame(idx, s)
    for (dx, zc, w, h) in [(0.0, RIM_Z+ARM_H+SLOT/2, ARM_W+2*SLOT, SLOT),
                            (-side*(ARM_W/2+SLOT/2), RIM_Z+(ARM_H+SLOT)/2, SLOT, ARM_H+SLOT)]:
        pl = Plane(origin=P + t*dx + Vector(0,0,zc) - nin*1.0, x_dir=t, z_dir=nin)
        hood -= pl * Box(w, h, 5.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
    prof_pl = Plane(origin=P - t*3.0 + nin*WALL + Vector(0,0,RIM_Z+0.6),
                    x_dir=nin, z_dir=t)
    hood += prof_pl * extrude(poly_face([(0,0),(1.2,2.8),(1.2,4.0),(0,5.4)]), 6.0)
hood = no_loose(hood, "hood final")

# ================= BASE =================
# flat base on bed (kit1 lesson: no feet), countersunk mounts + weeps
base = extrude(inset(F_ext, WALL+CLR), BASE_H) \
     - Pos(0,0,FLOOR_T) * extrude(inset(F_ext, 2*WALL+CLR), BASE_H)
for (px, py) in [(7,11),(52,21),(84,70),(-14,52)]:
    base -= Pos(px,py,0) * Cylinder(2.25, FLOOR_T, align=(Align.CENTER,Align.CENTER,Align.MIN))
    base -= Pos(px,py,0) * Cone(4.75, 2.25, 2.5, align=(Align.CENTER,Align.CENTER,Align.MIN))
for (wx, wy) in [(12,7),(94,68)]:
    base -= Pos(wx,wy,0) * Cylinder(1.25, FLOOR_T, align=(Align.CENTER,Align.CENTER,Align.MIN))
base += Pos(0,0,BASE_H) * (extrude(inset(F_ext, 3.4), 4.0)
                           - extrude(inset(F_ext, 5.0), 4.0))
for idx, s, side in HOOKS:
    P, t, nin = wall_frame(idx, s)
    pk_pl = Plane(origin=P - t*4.0 + nin*(WALL+CLR), x_dir=nin, z_dir=t)
    base -= pk_pl * extrude(poly_face([(0,24.2),(1.3,25.5),(1.3,29.1),(0,30.4)]), 8.0)
try:
    base = chamfer(base.edges().group_by(Axis.Z)[0], 0.4)
except Exception as e:
    print("pad chamfer skipped:", repr(e))
base = no_loose(base, "base final")


# ================= FEATURES =================
FZ, EMB = FLOOR_T, 0.4           # floor top; embed depth for fusion

def prism(profile_pts, plane, length):
    return plane * extrude(poly_face(profile_pts), length)

# --- HM3301 rails (board x10..90, y39..79, rests z6.5) ---
def xrail(x0, ln, pf):
    return prism(pf, Plane(origin=(x0, 0, 0), x_dir=(0,1,0), z_dir=(1,0,0)), ln)
Z0 = FZ - EMB
base += xrail(10, 80, [(36.9,Z0),(39.9,Z0),(39.9,FZ+4),(38.7,FZ+4),(38.7,FZ+6.8),(36.9,FZ+6.8)])
base += xrail(10, 80, [(81.0,Z0),(78.1,Z0),(78.1,FZ+4),(79.3,FZ+4),(79.3,FZ+6.8),(81.0,FZ+6.8)])
for nx in (30, 62):    # cable notches in south rail top
    base -= Pos(nx, 38.4, FZ+5.3) * Box(6, 5, 6, align=(Align.CENTER, Align.CENTER, Align.MIN))
base += Pos(9.2, 59, Z0) * Box(1.6, 24, 8.9, align=(Align.CENTER, Align.CENTER, Align.MIN))
base += Pos(90.9, 59, Z0) * Box(1.2, 14, 10.9, align=(Align.CENTER, Align.CENTER, Align.MIN))
base += prism([(0.3,8.4),(-1.0,9.7),(0.3,11.0)],
              Plane(origin=(90.3, 64, 0), x_dir=(1,0,0), z_dir=(0,-1,0)), 10)

# --- stack rails (shield x14.5..72.5, y9..34, rests z6.5, USB west) ---
base += xrail(14.5, 58, [(6.9,Z0),(9.9,Z0),(9.9,FZ+4),(8.7,FZ+4),(8.7,FZ+6.8),(6.9,FZ+6.8)])
base += xrail(14.5, 58, [(36.1,Z0),(33.1,Z0),(33.1,FZ+4),(34.3,FZ+4),(34.3,FZ+6.8),(36.1,FZ+6.8)])
for sy in (12.5, 30.5):
    base += Pos(13.9, sy, Z0) * Box(1.6, 5, 8.9, align=(Align.CENTER, Align.CENTER, Align.MIN))
base += Pos(73.4, 21.5, Z0) * Box(1.2, 12, 10.6, align=(Align.CENTER, Align.CENTER, Align.MIN))
base += prism([(0.3,8.4),(-1.0,9.7),(0.3,11.0)],
              Plane(origin=(72.8, 26.5, 0), x_dir=(1,0,0), z_dir=(0,-1,0)), 10)

# --- BME680: vertical panel x=-6, board y32..72, z6..26, posts + gussets ---
for py in (28.2, 71.8):
    base += Pos(-6, py, Z0) * Box(8, 3.2, 26.4, align=(Align.CENTER, Align.CENTER, Align.MIN))
base -= Pos(-6, 50, FZ+3.5) * Box(2.0, 45.2, 30, align=(Align.CENTER, Align.CENTER, Align.MIN))

# --- desiccant fence x82..94 y44..62 h10 + air notches ---
base += Pos(88, 53, Z0) * Box(12, 18, 10.4, align=(Align.CENTER, Align.CENTER, Align.MIN))       - Pos(88, 53, Z0) * Box(9.6, 15.6, 12, align=(Align.CENTER, Align.CENTER, Align.MIN))
for nps in [Pos(88, 44, Z0), Pos(88, 62, Z0), Pos(82, 53, Z0), Pos(94, 53, Z0)]:
    base -= nps * Box(5, 5, 3.4, align=(Align.CENTER, Align.CENTER, Align.MIN))

# --- N intake: 3 gabled windows + 45deg fins + mesh rebate (edge3 wall) ---
def gabled_window(cx, w, z0, z1, gable):
    p = [(cx-w/2, z0), (cx+w/2, z0), (cx+w/2, z1), (cx, z1+gable), (cx-w/2, z1)]
    return prism(p, Plane(origin=(0, 84.6, 0), x_dir=(1,0,0), z_dir=(0,-1,0)), 8)
for wx in (24.6, 40.6, 56.6):
    base -= gabled_window(wx, 12, 10, 20, 6)
for fz in (13.2, 17.2):
    base += Plane(origin=(40.6, 80.7, fz), x_dir=(1,0,0),
                  z_dir=(0, 0.7071, 0.7071)) * Box(46, 3.7, 1.0)
base -= Pos(40.6, 83.0, 17.75) * Box(50, 1.302, 19.5)

# --- W louvres for BME (edge5): 2 gabled windows + fins + rebate ---
e5A = Vector(-28, 48.4974, 0)
d300 = Vector(0.5, -0.8660254, 0); nin5 = Vector(0.8660254, 0.5, 0)
def w5(s, dz):
    return e5A + d300*s + Vector(0, 0, dz)
for s in (10, 24):
    base -= prism([(-5,9),(5,9),(5,17),(0,22),(-5,17)],
                  Plane(origin=w5(s, 0) + nin5*6.5, x_dir=d300, z_dir=-nin5), 8)
for fz in (11.6, 15.6):
    base += Plane(origin=w5(17, fz) + nin5*4.6, x_dir=d300,
                  z_dir=(nin5 + Vector(0,0,1)).normalized()) * Box(26, 3.7, 1.0)
base -= Plane(origin=w5(17, 15) + nin5*(2.95-0.651), x_dir=d300, z_dir=nin5) * Box(26, 16, 1.302)

# --- cable grommet bore, W wall, teardrop O6.7, z12 ---
gtear = Circle(3.35) + Polygon((-2.37,2.37),(2.37,2.37),(0,4.74), align=None)
base -= Plane(origin=Vector(-5.7, 9.9, 12) - nin5*4.0, x_dir=-d300, z_dir=nin5) * extrude(gtear, 12)
base -= Pos(-2, 26, 0) * Cylinder(1.25, FLOOR_T, align=(Align.CENTER, Align.CENTER, Align.MIN))
base = no_loose(base, "base+features")

# --- hood gills, 45deg down-out, above seam ring (z>=39.6): NE x2, W x2 ---
e2A = Vector(109, 60.6218, 0)
d120 = Vector(-0.5, 0.8660254, 0); nin2 = Vector(-0.8660254, -0.5, 0)
for s in (10, 26):
    pl = Plane(origin=e2A + d120*(s+6) + Vector(0,0,41.8) + nin2*0.5,
               x_dir=d120, z_dir=(nin2 + Vector(0,0,1)).normalized())
    hood -= pl * Box(12, 9, 2.2)
for s in (16, 30):
    pl = Plane(origin=w5(s+6, 41.8) + nin5*0.5,
               x_dir=d300, z_dir=(nin5 + Vector(0,0,1)).normalized())
    hood -= pl * Box(12, 9, 2.2)
hood = no_loose(hood, "hood+gills")

# --- mesh retainer frames (flat parts, FC-hue accent) ---
ret_n = Box(49.4, 18.9, 1.2, align=(Align.CENTER, Align.CENTER, Align.MIN))       - Box(42, 10, 4, align=(Align.CENTER, Align.CENTER, Align.MIN))
ret_w = Box(25.4, 15.4, 1.2, align=(Align.CENTER, Align.CENTER, Align.MIN))       - Box(18, 9, 4, align=(Align.CENTER, Align.CENTER, Align.MIN))
export_stl(ret_n, os.path.join(OUT, "kit1hex_retainer_n.stl"))
export_stl(ret_w, os.path.join(OUT, "kit1hex_retainer_w.stl"))

# ================= checks + export =================
try:
    ib = hood & base
    inter = float(ib.volume)
except Exception as e:
    inter = 0.0
    print("no boolean overlap (disjoint):", repr(e))
hb, bb = hood.bounding_box(), base.bounding_box()
print(json.dumps({
 "hood_bbox": [round(hb.size.X,1), round(hb.size.Y,1), round(hb.size.Z,1)],
 "apex_z": round(hb.max.Z,2),
 "base_bbox": [round(bb.size.X,1), round(bb.size.Y,1), round(bb.size.Z,1)],
 "hood_g": round(hood.volume/1000*1.27,1),
 "base_g": round(base.volume/1000*1.27,1),
 "interference_mm3": round(inter,3)}, indent=1))

export_stl(hood, os.path.join(OUT, "kit1hex_hood.stl"))
export_stl(base, os.path.join(OUT, "kit1hex_base.stl"))
try:
    export_step(Compound(children=[hood, base]), os.path.join(OUT, "kit1hex_asm.step"))
except Exception as e:
    print("step export:", repr(e))
