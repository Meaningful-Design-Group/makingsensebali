#!/usr/bin/env python3
"""K1H3 Phase-1 — "meru" massing.
Open-bottom irregular HEX PYRAMID (apex over the stack) + drop-in carrier
(deck high: shield+stack; low: HM3301 rails, BME680 cradle) + OPTIONAL
perforated base plate. Plan = K1H2 proven hex 72/57/48/88/41/64.
Facets spring from a plumb rim band z0..10; every facet >=47 deg. SHELL prints
rim-down, CARRIER prints deck-down (flipped export), BASE flat.
Amendments A-1..A-7 (see SPEC_K1H3_PHASE0.md) pending ratification.
"""
import json, os
from math import tan, radians, degrees, atan2, cos, sin, sqrt, pi
from build123d import *

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "v3")
os.makedirs(OUT, exist_ok=True)

WALL, CLR = 1.6, 0.45      # 1.6 = 4 perimeters @0.4 nozzle: the honest minimum for a
                           # weather-facing PETG wall (watertight recipe). Thinner = 3
                           # perimeters, which we do not trust in monsoon.
SPRING = 10.0
SLOPE_MIN = 47.0
APEX_XY = (90.0, 45.0)   # over the stack top-E; pushed E so the near-vertical e1/e2 walls
                         # clear the 24 mm stack reserve near the apex (Phase-1 clearance probe)

EDGES = [(0, 72), (60, 57), (120, 48), (180, 88), (240, 41), (300, 64)]
pts = [(0.0, 0.0)]
for ang, L in EDGES:
    x, y = pts[-1]
    pts.append((x + L * cos(radians(ang)), y + L * sin(radians(ang))))
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
    sols = list(x) if isinstance(x, ShapeList) else x.solids()
    if len(sols) > 1:
        info = []
        for sol in sols:
            b = sol.bounding_box()
            info.append(f"v={sol.volume:.0f} @({b.min.X:.0f}..{b.max.X:.0f},{b.min.Y:.0f}..{b.max.Y:.0f},{b.min.Z:.0f}..{b.max.Z:.0f})")
        raise RuntimeError(f"{name} loose solids:\n" + "\n".join(info))
    return x

F_ext = poly_face(pts)
CEN = Vector(45.0, 45.0, 0)

def gusset_S(x0, xlen, ywall, ytip, ztop, tall):
    """45deg gusset in Y-Z, extruded +X: full at the wall (ywall), tapering to a tip at
    ytip (ytip>ywall), top flat at ztop. Underside wall->tip is 45deg (self-supporting,
    walls-down print)."""
    prof = [(ywall, ztop - tall), (ywall, ztop), (ytip, ztop)]
    assert tall >= (ytip - ywall) - 1e-6                       # <=45deg underside
    return Plane(origin=(x0, 0, 0), x_dir=(0, 1, 0), z_dir=(1, 0, 0)) * extrude(poly_face(prof), xlen)

def gusset_N(x0, xlen, ywall, ytip, ztop, tall):
    """mirror: full at ywall (large y), tip at ytip (ytip<ywall)."""
    prof = [(ywall, ztop - tall), (ywall, ztop), (ytip, ztop)]
    assert tall >= (ywall - ytip) - 1e-6
    return Plane(origin=(x0, 0, 0), x_dir=(0, 1, 0), z_dir=(1, 0, 0)) * extrude(poly_face(prof), xlen)

def yprism(y0, ln, pf):
    """profile pts given as (x, z), extruded +y from y0 (K1H2 helper)."""
    return Plane(origin=(0, y0, 0), x_dir=(1, 0, 0), z_dir=(0, 1, 0)) * \
        extrude(poly_face([(px, -pz) for px, pz in pf]), ln)

def prism(profile_pts, plane, length):
    return plane * extrude(poly_face(profile_pts), length)

# --- apex height from the shallowest facet (e5 governs by geometry) ---
def edge_frame(i):
    A = Vector(*verts[i], 0); B = Vector(*verts[i + 1], 0)
    t = (B - A).normalized()
    nin = Vector(-t.Y, t.X, 0)                    # inward for CCW plan
    return A, B, t, nin

def dist_to_edge(i, p):
    A, B, t, nin = edge_frame(i)
    return (Vector(*p, 0) - A).dot(nin)

d_edges = [dist_to_edge(i, APEX_XY) for i in range(6)]
H = tan(radians(SLOPE_MIN)) * max(d_edges)   # farthest edge = shallowest facet = pins 47 deg
APEX_Z = SPRING + H
APEX = Vector(APEX_XY[0], APEX_XY[1], APEX_Z)
slopes = [degrees(atan2(H, d)) for d in d_edges]
assert min(slopes) >= SLOPE_MIN - 1e-6

def facet_cutters(shift=0.0):
    cs = []
    for i in range(6):
        A, B, t, nin = edge_frame(i)
        Az = A + Vector(0, 0, SPRING)
        n = t.cross(APEX - Az).normalized()
        if n.Z < 0:
            n = -n                                # outward-up
        cs.append(Plane(origin=Az - n * shift, x_dir=t, z_dir=n) *
                  Box(700, 700, 300, align=(Align.CENTER, Align.CENTER, Align.MIN)))
    return cs

def pt_on_facet(i, s, z):
    """point on facet i at height z, on the apex-ray through edge-parameter s.
    Rays through the apex lie IN the facet plane and stay inside the triangle for
    any 0<=s<=edge_len — robust for skewed facets (apex offset along the edge)."""
    A, B, t, nin = edge_frame(i)
    e = A + t * s
    sc = (APEX_Z - z) / (APEX_Z - SPRING)
    return Vector(APEX_XY[0] + (e.X - APEX_XY[0]) * sc,
                  APEX_XY[1] + (e.Y - APEX_XY[1]) * sc, z)

def facet_normal(i):
    A, B, t, nin = edge_frame(i)
    n = t.cross(APEX - (A + Vector(0, 0, SPRING))).normalized()
    return (n if n.Z > 0 else -n)

# ---- rounded apex v4: TANGENT-CONTINUOUS dome. The cosine cap of v3 started with a
# vertical silhouette at the joint (ds/dz=0) -> read as a bump/cap. Now the cap is a
# cubic Hermite z(s): slope at the joint MATCHES the linear facet taper (G1 smooth),
# and ends horizontal at the crown (true rounded top, like a sphere pole). ----
# The dome TRUNCATES the pyramid, so cutting it lower is the material lever: the facets
# keep their 47 deg (printable, rain-shedding) and the object just gets shorter.
Z_ROUND = 40.0
CAP_TOP = 50.0    # v7: pushed to the physical floor -> shell top ~52.7. The binding
                  # constraint is the stack: grille top z20 + 21 mm reserve = z41 must
                  # clear the dome's inner surface.
# level plan (single source of truth): sensors hang in the skirt z0..17, grille floor
# 17..20, shield board sits on the grille top at z20, stack rises to ~z43.
FLOOR_Z0, FLOOR_Z1 = 17.0, 20.0
SHZ = FLOOR_Z1
def offset_poly(poly, d):
    """inward offset of a CCW polygon by d (per-edge normal, consecutive-line intersect)."""
    n = len(poly); out = []
    lines = []
    for i in range(n):
        ax, ay = poly[i]; bx, by = poly[(i + 1) % n]
        tx, ty = bx - ax, by - ay; L = (tx*tx + ty*ty) ** 0.5; tx, ty = tx/L, ty/L
        nx, ny = -ty, tx                       # inward for CCW
        lines.append((ax + nx*d, ay + ny*d, tx, ty))
    for i in range(n):
        px, py, tx, ty = lines[i]; qx, qy, ux, uy = lines[(i - 1) % n]
        den = ux*(-ty) - uy*(-tx)
        s = ((px - qx)*(-ty) - (py - qy)*(-tx)) / den if abs(den) > 1e-9 else 0.0
        out.append((qx + ux*s, qy + uy*s))
    return out

def scaled_face(poly, s, z):
    p = [(APEX_XY[0] + s*(x - APEX_XY[0]), APEX_XY[1] + s*(y - APEX_XY[1])) for x, y in poly]
    return Pos(0, 0, z) * poly_face(p)

def rounded_solid(poly, z_round=Z_ROUND, z_top=CAP_TOP, s_top=0.03, nsec=14):
    """sharp faceted frustum up to z_round, then a G1-continuous Hermite cap:
    z(s) cubic with z'(s0) = -(APEX_Z-SPRING) (the linear taper slope -> smooth joint)
    and z'(s_top) = 0 (horizontal crown -> genuinely round top)."""
    sol = extrude(poly_face(poly), APEX_Z + 5)
    vv = poly + [poly[0]]
    for i in range(len(poly)):
        A = Vector(*vv[i], 0); B = Vector(*vv[i + 1], 0); t = (B - A).normalized()
        nrm = t.cross(APEX - (A + Vector(0, 0, SPRING))).normalized()
        if nrm.Z < 0:
            nrm = -nrm
        sol -= Plane(origin=A + Vector(0, 0, SPRING), x_dir=t, z_dir=nrm) * \
               Box(900, 900, 400, align=(Align.CENTER, Align.CENTER, Align.MIN))
    frustum = sol - (Pos(-300, -300, z_round) * Box(600, 600, 400, align=(Align.MIN, Align.MIN, Align.MIN)))
    s0 = (APEX_Z - z_round) / (APEX_Z - SPRING)
    h = s0 - s_top
    m0 = h * (APEX_Z - SPRING)                       # dz/dt at the joint = taper slope (G1)
    secs = []
    for k in range(nsec + 1):
        t_ = k / nsec
        h00 = 2*t_**3 - 3*t_**2 + 1
        h10 = t_**3 - 2*t_**2 + t_
        h01 = -2*t_**3 + 3*t_**2
        z = h00 * z_round + h10 * m0 + h01 * z_top   # m1 = 0 (horizontal crown)
        secs.append(scaled_face(poly, s0 - h * t_, z))
    return no_loose(frustum + loft(secs), "rounded_solid")

# ================= SHELL (continuous rounded apex) =================
inner_pts = offset_poly(pts, WALL)
outer = rounded_solid(pts)
inner = rounded_solid(inner_pts, z_top=CAP_TOP - 2.8)      # crown wall ~2.5-2.8
shell = no_loose(outer - inner, "shell")

# ---- ADDITIONS (all bed-rooted or 45-safe; every add overlaps its host >=0.5) ----
# grille support columns: plumb, bed-rooted, trimmed flush to the facets; top z19.7
# carries the grille floor edge (the shell inner face has leaned inward by z20).
for (ei, s) in [(0, 64.0), (2, 10.0), (3, 44.0), (5, 20.0)]:
    A, B, t, nin = edge_frame(ei)
    P = A + t * s + nin * 2.0
    col = Plane(origin=P, x_dir=t, z_dir=Vector(0, 0, 1)) * \
          Box(10, 6.0, FLOOR_Z0, align=(Align.CENTER, Align.MIN, Align.MIN))
    shell += (col & outer)                          # flush with the exterior facets
# wall-mount keyhole blisters on the e3 band inner face (bed-rooted, into wall 0.5)
for kx in (10.0, 62.0):
    shell += Pos(kx - 7, 83.43, 0) * Box(14, 5.5, FLOOR_Z0 - 1.0, align=(Align.MIN, Align.MIN, Align.MIN))
# grille retention nibs: flat-bottomed wedges on the leaning inner facets, 0.5 over the
# floor top — floor cams past on insertion, sits captured under (COUPON engagement)
NIB_Z = FLOOR_Z1 + 0.5
for (ei, s) in [(0, 64.0), (3, 44.0)]:
    A, B, t, nin = edge_frame(ei)
    f0 = WALL / sin(radians(slopes[ei])) + (NIB_Z - SPRING) / tan(radians(slopes[ei]))
    shell += prism([(f0 - 0.6, NIB_Z), (f0 + 0.8, NIB_Z), (f0 - 0.6, NIB_Z + 1.6)],
                   Plane(origin=A + t * (s - 4), x_dir=nin, z_dir=t), 8.0)
# SMA boss on e5 at z70, mid-facet (K1H2 recipe: pad + 45 downhill wedge + inner pad)
t5A, t5B, t5, nin5 = edge_frame(5)
n5 = facet_normal(5)
up5 = (Vector(0, 0, 1) - n5 * Vector(0, 0, 1).dot(n5)).normalized()
sp = pt_on_facet(5, 26.0, 30.0)                    # SMA boss on e5, mid-facet, below the dome
shell += Plane(origin=sp + n5 * 2.5, x_dir=t5, z_dir=n5) * \
         Cylinder(7.5, 5.5, align=(Align.CENTER, Align.CENTER, Align.MAX))
wedge = prism([(0.0, 0.0), (0.0, 8.0), (8.0, 0.0)],
              Plane(origin=sp - up5 * 7.0, x_dir=-up5, z_dir=t5) * Pos(0, 0, -7.5), 15.0)
shell += (wedge & (Plane(origin=sp + n5 * 2.5, x_dir=t5, z_dir=n5) *
                   Cylinder(9.0, 30, align=(Align.CENTER, Align.CENTER, Align.MAX))))
shell += Plane(origin=sp - n5 * (WALL + 0.5), x_dir=t5, z_dir=-n5) * \
         Cylinder(7.5, 2.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
# USB corner brow: mitred roof wrapping the e1/e2 arris above the window — each half
# runs ALONG its facet (rooted 0.5 in), trimmed flush by the neighbouring facet plane
_fc0 = facet_cutters(0.0)
def brow(i, s0, ln, z):
    A, B, t, nin = edge_frame(i)
    n_i = facet_normal(i)
    pl = Plane(origin=pt_on_facet(i, s0, z), x_dir=n_i, z_dir=t)
    u = 1.0 if pl.y_dir.dot(Vector(0, 0, 1)) > 0 else -1.0
    return prism([(-0.5, -2.0 * u), (-0.5, 6.0 * u), (4.0, 2.0 * u)], pl, ln)
b1 = brow(1, 30.0, 15.0, 32.0) - _fc0[2]           # e1 half, mitred at the arris by e2
b2 = brow(2, 0.0, 8.0, 32.0) - _fc0[1]             # e2 half, mitred by e1
shell += b1 + b2
shell = no_loose(shell, "shell+adds")

# ---- CUTS ----
cuts = []
# apex exhaust gills (A-1): 45-down-out slots high on e0 + e2, below the dome (z<92)
def gill_cutters(i, zws):
    """RAIN-PROOF vents (no opening near the top, nothing water can fall into):
    the passage runs UP-AND-INWARD at 45 deg, so its outer mouth looks DOWN-and-out and
    a droplet would have to climb ~4 mm to get in. Rain running down the facet passes
    over the mouth; warm air still leaves by buoyancy (the passage is the chimney's
    last leg). Both passage walls sit at 45 deg -> self-supporting, no bridge."""
    A, B, t, nin = edge_frame(i)
    n_o = facet_normal(i)
    hh = Vector(n_o.X, n_o.Y, 0).normalized()
    a = (-hh + Vector(0, 0, 1)).normalized()       # inward AND upward: water cannot follow
    out = []
    for (z, w) in zws:
        P = pt_on_facet(i, EDGES[i][1] / 2.0, z)
        out.append(Plane(origin=P - a * 3.0, x_dir=t, z_dir=a) *
                   Box(w, 2.6, 14.0, align=(Align.CENTER, Align.CENTER, Align.MIN)))
    return out
# vents live LOW on the two lee facets (well under the dome), never on top
cuts += gill_cutters(0, [(24.0, 16.0), (30.0, 13.0)])
cuts += gill_cutters(2, [(24.0, 10.0), (30.0, 8.0)])
# USB service window: cut SQUARE to the plug, tilted 12 deg DOWN-AND-OUT (D-3 spirit:
# the port looks downward, water cannot sit in it, the cable leaves with a drip loop)
WIN_AX = Vector(cos(radians(12)), 0, -sin(radians(12)))
win = Plane(origin=(80.0, 44.5, SHZ + 8.0), x_dir=(0, 1, 0), z_dir=WIN_AX) * \
      extrude(poly_face([(-7, -6), (7, -6), (7, 5), (0, 10.5), (-7, 5)]), 30.0)
cuts.append(win)
# wall-mount keyholes in the e3 band (entry O8.8 @z12, slot 4.6 down to z4, head cavity in blister)
for kx in (10.0, 62.0):
    cuts.append(Pos(kx - 4.8, 85.03, 3.5) * Box(9.6, 3.4, 12.0, align=(Align.MIN, Align.MIN, Align.MIN)))
    cuts.append(yprism(85.03, 3.4, [(kx - 4.8, 15.5), (kx + 4.8, 15.5), (kx, 20.3)]))    # cavity gable
    cuts.append(Plane(origin=Vector(kx, 92.0, 12.0), x_dir=(1, 0, 0), z_dir=(0, -1, 0)) *
                Cylinder(4.4, 9.0, align=(Align.CENTER, Align.CENTER, Align.MIN)))        # entry
    cuts.append(yprism(83.0, 9.0, [(kx - 3.11, 15.11), (kx + 3.11, 15.11), (kx, 18.2)]))  # entry teardrop gable
    cuts.append(Pos(kx - 2.3, 83.0, 4.0) * Box(4.6, 9.0, 8.0, align=(Align.MIN, Align.MIN, Align.MIN)))  # slot down
# zip-tie conduit pairs through the e3 band (pole mount), gabled tops
for zx in (26.0, 34.0, 42.0, 50.0):
    cuts.append(Pos(zx, 83.0, 6.0) * Box(3.5, 9.0, 5.0, align=(Align.MIN, Align.MIN, Align.MIN)))
    cuts.append(yprism(83.0, 9.0, [(zx, 11.0), (zx + 3.5, 11.0), (zx + 1.75, 12.75)]))
# SMA teardrop bore O6.65 along the e5 facet normal
tear = Circle(3.33) + Polygon((-2.36, 2.36), (2.36, 2.36), (0, 4.71), align=None)
cuts.append(Plane(origin=sp - n5 * 8.0, x_dir=t5, z_dir=n5) * extrude(tear, 14))
# drip groove in the rim underside (K1H2 recipe)
cuts.append(extrude(inset(F_ext, 0.8), 1.2) - extrude(inset(F_ext, 1.8), 1.2))
# datum reveal: 0.8x0.8 shadow groove where the plumb band meets the facets (z9.2..10) —
# turns the spring line into a designed plinth datum instead of an accidental crease
cuts.append(Pos(0, 0, 9.2) * (extrude(F_ext, 0.8) - extrude(inset(F_ext, 0.8), 0.8)))
shell = shell.cut(*cuts).clean()
try:
    shell = chamfer(shell.edges().group_by(Axis.Z)[0], 0.4)
except Exception as e:
    print("shell rim chamfer skipped:", repr(e))
shell = no_loose(shell, "shell final")
APEX_Z_ROUNDED = shell.bounding_box().max.Z

# ================= CARRIER = TRAY (walls-down) + DECK (flat) =================
# Why two parts: the shield floats directly over the HM3301, so every inward rail support
# collides with a Grove plug corridor. A one-piece edge-rail carrier can't dodge both plug
# windows without long structural bridges (proven: deck-down slice hid a 2432 mm2 roof over
# 224 mm2 of bed). Split instead: a walls-down TRAY (HM rails + BME cradle + 4 corner posts,
# support-free like the K1H2 tub) and a FLAT-printed DECK (shield rails + plug cutouts + stack
# bay + corner sockets, zero bridges). Deck drops onto the tray posts; shield onto the deck.
SKIRT_TOP = FLOOR_Z0                    # (levels hoisted to the top of the file)
DECK_Z0, DECK_Z1 = FLOOR_Z1, FLOOR_Z1  # deck deleted (2-part design): kept as aliases
ring_cut = Pos(0, 0, -2) * (extrude(F_ext, APEX_Z) - extrude(inset(F_ext, WALL + CLR), APEX_Z))

# ---------- GRILLE (recessed perforated deck; sensors HANG below into the skirt) ----------
# Tomas iter-2/3: the perforated base recesses UP inside the pyramid by >= the PM-sensor height,
# and the sensors zip-tie to it HANGING BELOW into the open-bottom skirt (z0..20) — the pyramid
# walls shade/baffle them, intakes face down, exhaust rises through the perforations into the
# chimney. This removes the molded cradle AND frees the whole underside for both sensors (the
# deck-walls now sit ABOVE the sensors, z23..44). One part: perforated deck + deck-walls + rim tabs.
gr = []
# perforated deck z20..23 (hex cells; 6 mm solid margin; solid pad strips left under the tie lines)
floor = Pos(0, 0, FLOOR_Z0) * extrude(inset(F_ext, WALL + CLR), FLOOR_Z1 - FLOOR_Z0)
cellR = 2.5 / cos(radians(30))
keep = Pos(0, 0, FLOOR_Z0 - 1) * extrude(inset(F_ext, 9.0), 6.0)
bb = floor.bounding_box(); cells = []; pitch, row = 6.7, 0
zy = bb.min.Y + 4
while zy < bb.max.Y - 3:
    zx = bb.min.X + 4 + (pitch / 2 if row % 2 else 0)
    while zx < bb.max.X - 3:
        cells.append(Pos(zx, zy, FLOOR_Z0 - 1) * extrude(RegularPolygon(cellR, 6, rotation=90), FLOOR_Z1 - FLOOR_Z0 + 2))
        zx += pitch
    zy += pitch * 0.866
    row += 1
cin = [c & keep for c in cells]
cin = [c for c in cin if getattr(c, "volume", 0.0) > 1.0]
floor -= Compound(children=cin)
gr.append(floor)
# SHIELD LOCATORS on the grille TOP (2-part design: the main board zip-ties up here, the
# sensors hang below the same plate). Low curbs on 3 sides — ties do the holding.
for (x0, y0, w, dd) in [(25, 30.0, 58, 1.6),      # S curb (board y32..57)
                        (25, 57.4, 58, 1.6),      # N curb
                        (23.4, 32, 1.6, 25)]:     # W end curb (E end open: USB faces the port)
    gr.append(Pos(x0, y0, FLOOR_Z1) * Box(w, dd, 2.4, align=(Align.MIN, Align.MIN, Align.MIN)))
# WiFi antenna landing tab (N of the shield, thin upstand, foil-free zone)
gr.append(Pos(58, 60.5, FLOOR_Z1) * Box(22, 1.2, 10.0, align=(Align.MIN, Align.MIN, Align.MIN)))
# (grille rests on 4 shell support columns at z17; 2 shell nibs capture the floor edge)
# zip-tie slot pairs through the floor (ties loop DOWN around each hanging sensor)
ties = []
for (x0, y0) in [(12, 29.5), (12, 71), (60, 29.5), (60, 71),          # HM: fore+aft x2 ends (board y31.5..71.5)
                 (24, 9), (48, 9), (24, 28), (48, 28),                # BME: 2 ties (S strip, y11..31)
                 (27, 29.5), (27, 58.5), (75, 29.5), (75, 58.5)]:     # spare shield-on-grille field (58x25)
    ties.append(Pos(x0, y0, FLOOR_Z0 - 1) * Box(2.0, 2.5, FLOOR_Z1 - FLOOR_Z0 + 2, align=(Align.MIN, Align.MIN, Align.MIN)))
# cable aperture: stadium slot N of the N wall — Grove plugs + USB pass PRE-CONNECTED
apert = Pos(35, 73, FLOOR_Z0 - 1) * Box(18, 10, 5, align=(Align.MIN, Align.MIN, Align.MIN))
apert += Pos(35, 78, FLOOR_Z0 - 1) * Cylinder(5.0, 5.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
apert += Pos(53, 78, FLOOR_Z0 - 1) * Cylinder(5.0, 5.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
# fan relief: O24 clear bore over the HM3301's can-top fan (webs would choke it and
# re-ingest exhaust) + O29 x 1.2 mesh rebate on the floor top (insect scrim, retainer P2b)
fan = Pos(46, 51.6, FLOOR_Z0 - 1) * Cylinder(12.0, 6.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
fan += Pos(46, 51.6, FLOOR_Z1 - 1.2) * Cylinder(14.5, 2.5, align=(Align.CENTER, Align.CENTER, Align.MIN))
grille = gr[0].fuse(*gr[1:]).clean()
grille -= Compound(children=ties)
grille -= apert
grille -= fan
# N curb notch at the two used Grove ports (plugs insert over the curb, K1H2 recipe)
grille -= Pos(32.5, 57.0, FLOOR_Z1 - 0.5) * Box(24.0, 2.6, 4.0, align=(Align.MIN, Align.MIN, Align.MIN))
GCLR = CLR + 0.4              # grille sits 0.85 clear of the shell (vertex-safe: the
                              # two-plane offset at a sharp arris needs the extra margin)
grille = grille.cut(Pos(0, 0, -2) * (extrude(F_ext, APEX_Z) - extrude(inset(F_ext, WALL + GCLR), APEX_Z)),
                    *facet_cutters(WALL + GCLR)).clean()
# belt-and-braces: subtract the REAL shell solid. Analytic offsets mis-handle the sharp
# arris where two leaning facets meet, so let the actual geometry have the last word.
grille = (grille - shell).clean()
grille = no_loose(grille, "grille")

# ---------- (DECK DELETED — 2-part design per Tomas iter-5) ----------
carrier = grille

# ================= component envelopes (keep-outs) =================
PH = {                         # SHZ = grille top = shield rest plane
    "shield_board": Pos(25, 32, SHZ) * Box(58, 25, 1.6, align=(Align.MIN, Align.MIN, Align.MIN)),
    "stack_keepout": Pos(60.5, 34, SHZ + 1.6) * Box(21.5, 22, 21.0, align=(Align.MIN, Align.MIN, Align.MIN)),  # honest reserve 21 (measured 19.5-20)
    "plug_corridor_N": Pos(33, 57.4, SHZ + 1.7) * Box(23, 12.0, 7.0, align=(Align.MIN, Align.MIN, Align.MIN)), # both plugs N-row
    "usb_keepout":  Pos(83, 37, SHZ + 3.0) * Box(11, 15, 12.0, align=(Align.MIN, Align.MIN, Align.MIN)),
    "hm_can":       Pos(16.6, 32.7, 2.0) * Box(40, 38, 15.0, align=(Align.MIN, Align.MIN, Align.MIN)),   # HANGS: fan-top at z17 under the relief
    "hm_board":     Pos(2, 31.5, 0.4) * Box(80, 40, 1.6, align=(Align.MIN, Align.MIN, Align.MIN)),       # PCB under the can, in the skirt (ray-verified covered)
    "hm_intake_S":  Pos(16.6, 27.2, 2.0) * Box(40, 5.5, 13.0, align=(Align.MIN, Align.MIN, Align.MIN)),  # can S-face intake, open skirt
    "bme_env":      Pos(18, 11.0, 9.0) * Box(40, 20.0, 7.0, align=(Align.MIN, Align.MIN, Align.MIN)),    # S strip at the HM intake, fully under roof cover (ray-verified)
    "foil_card":    Pos(19, 12.0, 7.6) * Box(38, 18.0, 1.2, align=(Align.MIN, Align.MIN, Align.MIN)),
    "wifi_landing": Pos(58, 59.0, SHZ + 0.5) * Box(22, 1.2, 9.5, align=(Align.MIN, Align.MIN, Align.MIN)),
    "stack_headroom": Pos(60.5, 34, SHZ + 23.1) * Box(21.5, 22, 0.5, align=(Align.MIN, Align.MIN, Align.MIN)),
}
# hm_intake_N deleted: TBC-01 handled by flipping the board so the slot faces the S standoff.

report = {
    "name": "K1H3 meru Phase-1 massing",
    "plan_edges": EDGES, "apex_xy": APEX_XY, "apex_z_mm": round(APEX_Z, 1),
    "facet_slopes_deg": [round(s, 1) for s in slopes],
    "ext_bbox": None, "parts_g": {},
}
b = shell.bounding_box()
report["ext_bbox"] = [round(q, 1) for q in (b.max.X - b.min.X, b.max.Y - b.min.Y, b.max.Z - b.min.Z)]
report["apex_z_rounded_mm"] = round(APEX_Z_ROUNDED, 1)
for nm, sol in [("shell", shell), ("grille", grille)]:
    report["parts_g"][nm] = round(float(sol.volume) / 1000 * 1.27, 1)

# interference gates
def iv(a, bs):
    try:
        return round(float((a & bs).volume), 3)
    except Exception as e:
        print("IV_BOOLEAN_FAILED (NOT a pass):", repr(e))
        return -1.0                                  # loud failure, never a silent 0
# part-pair interference is checked post-export with mesh booleans (manifold engine):
# OCC common() throws on legitimate coincident contact faces (deck-on-wall, floor-on-column).
env = shell + grille
env_nc = grille
inter = {}
for k, ph in PH.items():
    tgt = env_nc if k == "usb_keepout" else env      # USB passes THROUGH the e1 wall (P2 pocket cut)
    v = iv(ph, tgt)
    inter[k] = v
    if v > 0.001:
        ob = (ph & tgt).bounding_box()
        inter[k + "_bbox"] = [round(q, 1) for q in (ob.min.X, ob.max.X, ob.min.Y, ob.max.Y, ob.min.Z, ob.max.Z)]
report["placeholder_vs_parts_mm3_MUST_BE_0"] = inter
report["usb_pocket_thru_shell_mm3_P2cut"] = iv(PH["usb_keepout"], shell)

# SMA boss point + F2 distances
report["sma_boss_e5_xyz"] = [round(sp.X, 1), round(sp.Y, 1), round(sp.Z, 1)]
report["sma_whip_elev_deg"] = round(90 - slopes[5], 1) + 0.0
sock = Vector(57.65, 52.1, 44)                  # XIAO socket nearest corner (high)
bme_near = Vector(58, 27, 20); bme_sense = Vector(18, 7, 13)     # BME hangs low in the S strip
report["bme_module_to_socket_mm"] = round((bme_near - sock).length, 1)
report["bme_sensing_to_socket_mm"] = round((bme_sense - sock).length, 1)
report["bme_vertical_below_stack_mm"] = round(45.6 - 20, 1)      # BME top ~z20, stack base z45.6
report["grille_recess_z"] = FLOOR_Z0
report["pm_sensor_hangs_z"] = "5..20 (can), 3.4 board — within skirt z0..20"
report["gill_area_mm2"] = round(3 * 16 * 3 / 0.7071 + 3 * 10 * 3 / 0.7071, 0)   # e0 + e2 fields, 45-down (A-1: >=300)
report["wallmount"] = "2 keyholes (entry O8.8, slot 4.6, blister cavity) + 2 zip pairs, e3 plumb band"
report["usb_window"] = "straight +x window sq. to plug, 14x15 gabled, drip fin above; bung P2b"

# ================= export =================
VER = "v7"                     # bump every geometry change: filenames stay unambiguous
for nm, sol in [("shell", shell), ("grille", grille)]:
    try:
        sol = sol.clean()
    except Exception:
        pass
    export_stl(sol, os.path.join(OUT, f"k1h3_{nm}_{VER}.stl"))
    export_stl(sol, os.path.join(OUT, f"k1h3_{nm}.stl"))
    try:
        export_step(sol, os.path.join(OUT, f"k1h3_{nm}.step"))
    except Exception as e:
        print(f"step {nm}:", repr(e))
# print orientation (rebase to bed; grille floor-down as modelled)
for nm, sol in [("grille", grille)]:
    pb = sol.bounding_box()
    export_stl(Pos(0, 0, -pb.min.Z) * sol, os.path.join(OUT, f"k1h3_{nm}_print_{VER}.stl"))
    export_stl(Pos(0, 0, -pb.min.Z) * sol, os.path.join(OUT, f"k1h3_{nm}_print.stl"))
report["shell_height_mm"] = round(float(shell.bounding_box().max.Z), 1)

# part-pair interference via mesh booleans (manifold engine, tolerant of contact faces)
import trimesh
_m = {nm: trimesh.load(os.path.join(OUT, f"k1h3_{nm}.stl")) for nm in ("shell", "grille")}
for a, bnm in [("shell", "grille")]:
    try:
        ix = trimesh.boolean.intersection([_m[a], _m[bnm]], engine="manifold")
        v = float(ix.volume) if ix is not None and hasattr(ix, "volume") else 0.0
    except Exception as e:
        v = -1.0
        print("MESH_PAIR_FAIL:", a, bnm, repr(e))
    report[f"{a}_{bnm}_mm3"] = round(v, 3)
print(json.dumps(report, indent=1))

viz = Compound(children=[shell, grille] + list(PH.values()))
export_stl(viz, os.path.join(OUT, "k1h3_asm_viz.stl"))
try:
    export_step(Compound(children=[shell, grille]), os.path.join(OUT, "k1h3_asm.step"))
except Exception as e:
    print("asm step:", repr(e))
halfY = Pos(-200, 45, -10) * Box(600, 400, 300, align=(Align.MIN, Align.MIN, Align.MIN))
halfX = Pos(60, -200, -10) * Box(600, 400, 300, align=(Align.MIN, Align.MIN, Align.MIN))
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
export_stl(Compound(children=cut_list([shell, grille] + list(PH.values()), halfY)),
           os.path.join(OUT, "k1h3_sectionY.stl"))
export_stl(Compound(children=cut_list([shell, grille] + list(PH.values()), halfX)),
           os.path.join(OUT, "k1h3_sectionX.stl"))
