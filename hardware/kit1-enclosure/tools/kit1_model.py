#!/usr/bin/env python3
"""
KIT 1 enclosure — Making Sense Bali — "faceted lantern"  (v1)
Parametric build123d model. SPEC_KIT1.md is the contract.

Exports (print orientation, zero-support by design):
  kit1_lower.stl    bowl            prints base-down
  kit1_upper.stl    dome + spire    prints rim-down (= deployed orientation)
  kit1_tray.stl     internal tray   prints flat
  kit1_grommet.stl  USB-C collet    prints flat
  kit1_meshring.stl mesh retainer   prints flat
  kit1_assembly.step (deployed)     editable source companion

BREP only; halves cut BEFORE hollow-subtraction; largest-fragment after booleans.
"""
import math
import numpy as np
from build123d import *  # noqa

# ---------------------------------------------------------------- parameters
P = dict(
    N=10, WALL=2.5,
    RINGS=[  # (radius, z, azimuth offset deg)
        (44.0, -66.0, 0.0),   # R0 base
        (53.0, -53.0, 18.0),  # R1
        (71.7, -22.0, 0.0),   # R2
        (75.0,   0.0, 18.0),  # R3 split
        (71.7,  22.0, 0.0),   # R4
        (53.0,  53.0, 18.0),  # R5
        (20.0,  94.0, 0.0),   # R6
        (6.0,  110.0, 18.0),  # R7
    ],
    # bayonet (lower tongue enters upper's down-opening groove)
    TONGUE_RI=64.4, TONGUE_RO=66.0, TONGUE_H=8.0,
    CH_IN_RI=61.5, CH_IN_RO=63.95,      # upper inner ring wall
    CH_OUT_RI=66.45, CH_OUT_RO=68.9,    # upper outer ring wall
    CH_H=10.5, WEB_Z0=8.5,              # web ties rings to shell, closes groove
    LUG_N=4, LUG_R=1.5, LUG_T=1.55, LUG_Z=4.6,        # teardrop lug
    SLOT_DEPTH=1.3, SLOT_CLEAR=0.45, TURN_DEG=20.0,   # COUPON_TBD_BAYONET
    # tray / deck  (bosses live in the bay-free quadrant; pins can't block the
    # HM board slide)
    DECK_R=46.0, DECK_TOP=-40.0, DECK_T=3.0,
    BOSSES=((30.0, 30.0), (85.0, 32.0), (130.0, 30.0)), BOSS_W=14.0,
    # feature azimuths (snapped to facets)
    AZ_WALL=0.0, AZ_USB=36.0, AZ_BME=144.0, AZ_CONV=216.0,
    AZ_PM_IN=252.0, AZ_PM_EX=324.0,
    TRI_INSET_OPEN=5.0, TRI_INSET_REB=2.6, MESH_T=1.2,
    GRID_HOLE=4.2, GRID_PITCH=6.0, GRID_INSET=4.5,
    LOUVRE_T=1.3, LOUVRE_PITCH=4.6, LOUVRE_ANG=50.0,
    USB_BORE=6.9, USB_BOSS_D=16.0, USB_BOSS_T=3.0, GROMMET_GRIP=4.3,
    KEY_HOLE_D=9.0, KEY_SLOT_W=4.5, KEY_SLOT_L=8.0,
    WEEP_D=3.0,
    # boards
    HM_L=80.0, HM_W=40.0, HM_PCB_T=1.6, HM_CAN_H=15.0,
    HM_CAN_X0=-25.39, HM_CAN_X1=14.61, HM_CAN_Y0=-18.79, HM_CAN_Y1=19.21,
    SHIELD_W=25.0, SHIELD_L=39.5, STACK_H=25.0,   # break-off Grove shield
    BME_W=20.0, BME_L=40.0,
    RAIL_CLEAR=0.30,
)
N = P["N"]; STEP = 360.0 / N; RINGS = P["RINGS"]; WALL = P["WALL"]

# ------------------------------------------------------------ solid builders
def ring_pts(r, z, off):
    return [(r * math.cos(math.radians(off + STEP * k)),
             r * math.sin(math.radians(off + STEP * k)), z) for k in range(N)]

def offset_profile(rings, t):
    pts = [(r, z) for r, z, _ in rings]
    segs = []
    for (r0, z0), (r1, z1) in zip(pts, pts[1:]):
        dr, dz = r1 - r0, z1 - z0
        L = math.hypot(dr, dz)
        nr, nz = dz / L, -dr / L
        if nr > 0:
            nr, nz = -nr, -nz
        segs.append(((r0 + nr * t, z0 + nz * t), (r1 + nr * t, z1 + nz * t)))
    def isect(s1, s2):
        (x1, y1), (x2, y2) = s1
        (x3, y3), (x4, y4) = s2
        den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if abs(den) < 1e-9:
            return s1[1]
        px = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / den
        py = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / den
        return (px, py)
    out = []
    (a, b) = segs[0]
    zb = pts[0][1] + t
    r_first = a[0] + (b[0] - a[0]) * (zb - a[1]) / (b[1] - a[1]) if abs(b[1] - a[1]) > 1e-9 else a[0]
    out.append((r_first, zb, rings[0][2]))
    for i in range(1, len(pts) - 1):
        p = isect(segs[i - 1], segs[i])
        out.append((p[0], p[1], rings[i][2]))
    (a, b) = segs[-1]
    zt = pts[-1][1] - t
    r_last = a[0] + (b[0] - a[0]) * (zt - a[1]) / (b[1] - a[1]) if abs(b[1] - a[1]) > 1e-9 else a[0]
    out.append((max(r_last, 1.0), zt, rings[-1][2]))
    return out

def facet_tris(rings):
    layers = [ring_pts(*rg) for rg in rings]
    tris = []
    for i in range(len(layers) - 1):
        A, B = layers[i], layers[i + 1]
        offA = rings[i][2]; offB = rings[i + 1][2]
        d = (offB - offA) % 360.0
        for k in range(N):
            k1 = (k + 1) % N
            if 0 < d <= STEP:      # B rotated +half step
                tris.append((A[k], A[k1], B[k]))
                tris.append((B[k], A[k1], B[k1]))
            else:                   # A rotated +half step
                tris.append((A[k], B[k1], B[k]))
                tris.append((A[k], A[k1], B[k1]))
    return tris, layers[0][::-1], layers[-1]

def make_faceted_solid(rings):
    tris, base, top = facet_tris(rings)
    faces = []
    for t in tris:
        f = Face(Wire.make_polygon([Vector(*p) for p in t], close=True))
        c = f.center(); n = f.normal_at(c)
        ref = Vector(c.X, c.Y, 0)
        if ref.length > 1e-6 and n.dot(ref) < 0:
            f = f.reversed()
        faces.append(f)
    fb = Face(Wire.make_polygon([Vector(*p) for p in base], close=True))
    if fb.normal_at(fb.center()).Z > 0:
        fb = fb.reversed()
    ft = Face(Wire.make_polygon([Vector(*p) for p in top], close=True))
    if ft.normal_at(ft.center()).Z < 0:
        ft = ft.reversed()
    faces += [fb, ft]
    sol = Solid(Shell(faces))
    if sol.volume < 0:
        sol = Solid(Shell([f.reversed() for f in faces]))
    return sol

def largest(shape):
    try:
        sols = shape.solids()
    except Exception:
        return shape
    return max(sols, key=lambda s: s.volume) if len(sols) else shape

# ------------------------------------------------------------- facet frames
TRIS, _, _ = facet_tris(RINGS)

def band_of(z):
    for i in range(len(RINGS) - 1):
        if RINGS[i][1] - 1e-6 <= z <= RINGS[i + 1][1] + 1e-6:
            return i
    raise ValueError(z)

def facet_frame(az, zp):
    band = band_of(zp)
    zlo, zhi = RINGS[band][1], RINGS[band + 1][1]
    best = None
    for t in TRIS:
        zs = [p[2] for p in t]
        if min(zs) < zlo - 1e-6 or max(zs) > zhi + 1e-6:
            continue
        c = np.mean(np.array(t), axis=0)
        caz = math.degrees(math.atan2(c[1], c[0])) % 360
        d = min(abs(caz - az % 360), 360 - abs(caz - az % 360))
        if best is None or d < best[0]:
            best = (d, t, c)
    _, t, c = best
    p0, p1, p2 = [np.array(p) for p in t]
    nrm = np.cross(p1 - p0, p2 - p0); nrm /= np.linalg.norm(nrm)
    if np.dot(nrm, np.array([c[0], c[1], 0.0])) < 0:
        nrm = -nrm
    n = Vector(*nrm)
    # x_dir horizontal tangent, so plane-local +Y points up-slope (print up)
    xd = Vector(-math.sin(math.atan2(c[1], c[0])), math.cos(math.atan2(c[1], c[0])), 0)
    pl = Plane(origin=Vector(*c), x_dir=xd, z_dir=n)
    return pl, [Vector(*p) for p in t]

def tri_local_2d(pl, tp):
    o = pl.origin
    return [((p - o).dot(pl.x_dir), (p - o).dot(pl.y_dir)) for p in tp]

def inset_tri_2d(p2d, inset):
    tri = np.array(p2d)
    c = tri.mean(axis=0)
    # inradius
    a = np.linalg.norm(tri[1] - tri[2]); b = np.linalg.norm(tri[0] - tri[2])
    cc = np.linalg.norm(tri[0] - tri[1])
    s = (a + b + cc) / 2
    A = max(s * (s - a) * (s - b) * (s - cc), 1e-9) ** 0.5
    rin = A / s
    k = max(1.0 - inset / rin, 0.05)
    return [(c[0] + (p[0] - c[0]) * k, c[1] + (p[1] - c[1]) * k) for p in tri]

def tri_prism(pl, pts2d, depth_in, depth_out):
    poly = Polygon(*pts2d, align=None)
    return (pl * Pos(0, 0, -depth_in)) * extrude(poly, depth_in + depth_out)

def vert_frame(wp):
    """Vertical cutting frame at world point wp: x = horizontal tangent,
    z = horizontal radial (outward). Teardrop/kite roofs keep true world angle."""
    azr = math.atan2(wp.Y, wp.X)
    xd = Vector(-math.sin(azr), math.cos(azr), 0)
    zd = Vector(math.cos(azr), math.sin(azr), 0)
    return Plane(origin=wp, x_dir=xd, z_dir=zd)

def diamond_grid(pl, tp, hole, pitch, inset):
    p2d = tri_local_2d(pl, tp)
    tri = np.array(p2d)
    c = tri.mean(axis=0)
    def ok(pt):
        for i in range(3):
            a, b = tri[i], tri[(i + 1) % 3]
            e = b - a
            nl = np.array([-e[1], e[0]]); nl /= np.linalg.norm(nl)
            if np.dot(nl, c - a) < 0:
                nl = -nl
            if np.dot(nl, pt - a) < inset:
                return False
        return True
    hh2 = hole / 2 * 1.4142
    kite = Polygon((-hh2, 0), (0, -hh2), (hh2, 0), (0, hh2 * 1.24), align=None)
    cutters = []
    rng = np.arange(-60, 60 + 1e-9, pitch)
    for u in rng:
        for v in rng:
            if ok(np.array([u + c[0], v + c[1]])):
                wp = pl.origin + pl.x_dir * (u + c[0]) + pl.y_dir * (v + c[1])
                cutters.append((vert_frame(wp) * Pos(0, 0, -WALL - 8)) *
                               extrude(kite, WALL + 16))
    return cutters

# ------------------------------------------------------------------- shells
print("== faceted solids ==")
outer = make_faceted_solid(RINGS)
inner = make_faceted_solid(offset_profile(RINGS, WALL))
clear_in = make_faceted_solid(offset_profile(RINGS, WALL + 1.0))   # tray clip
print(f"outer {outer.volume/1000:.1f} cm3 valid={outer.is_valid}")
print(f"inner {inner.volume/1000:.1f} cm3 valid={inner.is_valid}")

big = Box(400, 400, 400, align=(Align.CENTER, Align.CENTER, Align.MAX))
lower = largest(largest(outer & big) - inner)
big2 = Box(400, 400, 400, align=(Align.CENTER, Align.CENTER, Align.MIN))
upper = largest(largest(outer & big2) - inner)
print(f"halves: lower {lower.volume/1000:.1f} upper {upper.volume/1000:.1f} cm3")

FLOOR_Z = offset_profile(RINGS, WALL)[0][1]          # inner floor z
DECK_BOT = P["DECK_TOP"] - P["DECK_T"]

# ------------------------------------------------------------------- LOWER
print("== lower ==")
# corbel land ring (45 deg underside) + tongue + lugs
# corbel: 50deg diagonal underside runs straight into the wall INNER surface
# (wall curves inward below z0 — no flat bottom, no poke-through)
prof = Polygon((64.4, 0), (64.4, -2.0), (72.4, -11.6), (72.4, 0), align=None)
corbel = revolve(Plane.XZ * prof, Axis.Z)
lower = largest(lower + corbel)
tongue = Pos(0, 0, 0) * extrude(Circle(P["TONGUE_RO"]) - Circle(P["TONGUE_RI"]), P["TONGUE_H"])
lower = largest(lower + tongue)

def inward_frame(r, az, z):
    """Plane on a cylinder at (r, az, z): z_dir points INWARD, local y = world UP."""
    a = math.radians(az)
    return Plane(origin=Vector(r * math.cos(a), r * math.sin(a), z),
                 x_dir=Vector(math.sin(a), -math.cos(a), 0),
                 z_dir=Vector(-math.cos(a), -math.sin(a), 0))

lr = P["LUG_R"]
tearlug = Circle(lr) + Polygon((-lr * 0.71, -lr * 0.71), (lr * 0.71, -lr * 0.71),
                               (0, -lr * 1.75), align=None)   # solid teardrop, V down
for i in range(P["LUG_N"]):
    az = i * 90.0 + 45.0
    pl = inward_frame(P["TONGUE_RI"] + 0.05, az, P["LUG_Z"])
    lower = largest(lower + pl * extrude(tearlug, P["LUG_T"] + 0.05))

# floor bosses + upstanding registration pins (gabled tops, tray drops over)
pinp = Polygon((-2, 0), (2, 0), (2, 5), (0, 7.4), (-2, 5), align=None)
for az, rr in P["BOSSES"]:
    x = rr * math.cos(math.radians(az))
    y = rr * math.sin(math.radians(az))
    boss = Pos(x, y, FLOOR_Z - 0.5) * extrude(
        Rectangle(P["BOSS_W"], P["BOSS_W"], rotation=az), (DECK_BOT - FLOOR_Z) + 0.5)
    pin = Rot(0, 0, az) * Pos(rr, 0, DECK_BOT) * (
        Plane.XZ * extrude(pinp, 5, both=True))
    lower = largest(lower + boss + pin)

# PM intake: triangular opening + mesh rebate (accent facet) az252
pl_in, tp_in = facet_frame(P["AZ_PM_IN"], -37.0)
p2d = tri_local_2d(pl_in, tp_in)
lower = largest(lower - tri_prism(pl_in, inset_tri_2d(p2d, P["TRI_INSET_OPEN"]), WALL + 8, 6))
lower = largest(lower - (pl_in * Pos(0, 0, -P["MESH_T"])) *
                extrude(Polygon(*inset_tri_2d(p2d, P["TRI_INSET_REB"]), align=None), P["MESH_T"] + 6))

# PM exhaust: louvred gill slots CARVED across the two facets straddling the
# tunnel mouth (az324 apex-down + az342 apex-up). Angled cuts only -> no unions.
def slot_facet(az, inset, zmin=-20.5, zmax=-11.5):
    pl_s, tp_s = facet_frame(az, -11.0)
    tri = inset_tri_2d(tri_local_2d(pl_s, tp_s), inset)
    pts = sorted(tri, key=lambda p: p[1])
    def width_at(yv):
        xs = []
        for a, b in ((pts[0], pts[1]), (pts[0], pts[2]), (pts[1], pts[2])):
            if (a[1] - yv) * (b[1] - yv) < 0:
                t = (yv - a[1]) / (b[1] - a[1])
                xs.append(a[0] + t * (b[0] - a[0]))
        return (max(xs) - min(xs), (max(xs) + min(xs)) / 2) if len(xs) >= 2 else (0, 0)
    n = 0
    y0s, y1s = pts[0][1] + 3.0, pts[2][1] - 3.0
    yy = y0s
    while yy <= y1s:
        zw = pl_s.origin.Z + yy * pl_s.y_dir.Z
        if zmin <= zw <= zmax:
            w, xc = width_at(yy)
            if w - 4.0 >= 5.0:
                wp = pl_s.origin + pl_s.x_dir * xc + pl_s.y_dir * yy
                # world-vertical frame, axis 50deg below horizontal — the channel
                # CEILING slopes at the axis angle, so 50deg = printable. Long
                # inner reach pierces wall + corbel, stays z<0 at r>64.4.
                cutter = (vert_frame(wp)) * (Rot(50, 0, 0) * Pos(0, 0, -4.5) *
                          Box(w - 4.0, 3.6, 21,
                              align=(Align.CENTER, Align.CENTER, Align.CENTER)))
                yield_cut.append(cutter)
                n += 1
        yy += P["LOUVRE_PITCH"]
    return n

yield_cut = []
n1 = slot_facet(P["AZ_PM_EX"], 3.5)
n2 = slot_facet(P["AZ_PM_EX"] + 18.0, 3.5)   # neighbour facet across the mouth
for c in yield_cut:
    lower = largest(lower - c)
print(f"  exhaust slots: {n1}+{n2}")

# BME + convection diamond grids
for az in (P["AZ_BME"], P["AZ_CONV"]):
    pl_g, tp_g = facet_frame(az, -37.0)
    cs = diamond_grid(pl_g, tp_g, P["GRID_HOLE"], P["GRID_PITCH"], P["GRID_INSET"])
    print(f"  grid az{az}: {len(cs)} holes")
    if cs:
        allc = cs[0]
        for cc in cs[1:]:
            allc = allc + cc
        lower = largest(lower - allc)

# USB-C teardrop bore az36, in vertical frame. No boss pad needed: the bore
# passes through wall + corbel ring = 8-10mm of native engagement for the
# grommet collet.
pl_u, tp_u = facet_frame(P["AZ_USB"], -8.0)
wp_u = pl_u.origin + pl_u.y_dir * -3.0
vf_u = vert_frame(wp_u)
br = P["USB_BORE"] / 2
tear = Circle(br) + Polygon((-br * 0.71, br * 0.71), (br * 0.71, br * 0.71), (0, br * 1.75), align=None)
lower = largest(lower - (vf_u * Pos(0, 0, -14)) * extrude(tear, 22))

# keyhole az0: teardrop head + gable-top slot, cut in vertical frame
pl_k, tp_k = facet_frame(P["AZ_WALL"], -8.0)
wp_k = pl_k.origin + pl_k.y_dir * -4.0
vf_k = vert_frame(wp_k)
kh = P["KEY_HOLE_D"] / 2
sw2 = P["KEY_SLOT_W"] / 2
sl = P["KEY_SLOT_L"]
khole = (Circle(kh) +
         Polygon((-sw2, 0), (sw2, 0), (sw2, sl), (0, sl + sw2 * 1.2), (-sw2, sl), align=None))
lower = largest(lower - (vf_k * Pos(0, 0, -WALL - 6)) * extrude(khole, WALL + 12))

# base weep (active when hung/wall-mounted; tabletop-in-rain not a use case)
lower = largest(lower - Pos(0, 0, FLOOR_Z - WALL - 1) * extrude(Circle(P["WEEP_D"] / 2), WALL + 2))
print(f"lower done {lower.volume/1000:.1f} cm3 valid={lower.is_valid}")

# ------------------------------------------------------------------- UPPER
print("== upper ==")
ring_in = extrude(Circle(P["CH_IN_RO"]) - Circle(P["CH_IN_RI"]), P["CH_H"])
ring_out = extrude(Circle(P["CH_OUT_RO"]) - Circle(P["CH_OUT_RI"]), P["CH_H"])
web = Pos(0, 0, P["WEB_Z0"]) * extrude(Circle(73.5) - Circle(P["CH_IN_RI"]), P["CH_H"] - P["WEB_Z0"])
upper = largest(upper + ring_in + ring_out + web)

# L-slot grooves in inner ring wall outer face: teardrop cross-section
# (matches teardrop lug + clearance; roofs 50deg everywhere)
def inward_frame_u(r, az, z):
    a = math.radians(az)
    return Plane(origin=Vector(r * math.cos(a), r * math.sin(a), z),
                 x_dir=Vector(math.sin(a), -math.cos(a), 0),
                 z_dir=Vector(-math.cos(a), -math.sin(a), 0))

gR = P["LUG_R"] + P["SLOT_CLEAR"]      # groove half-height (lug Ø3 + clearance)
gr = P["SLOT_DEPTH"]
GW = 2 * gR + 0.6                       # groove height
for i in range(P["LUG_N"]):
    az0 = i * 90.0 + 45.0
    # vertical entry channel from rim to lug height (roof = 1.3mm radial bridge)
    entry = (inward_frame_u(P["CH_IN_RO"] + 0.05, az0, 0) * Pos(0, -0.5, 0)) * extrude(
        Rectangle(GW, P["LUG_Z"] + gR + 1.6, align=(Align.CENTER, Align.MIN)), gr + 0.05)
    upper = largest(upper - entry)
    # arc leg with clamping ramp (drops 0.7 over the travel) + detent rise
    steps = 5
    leg = None
    for s in range(steps + 1):
        a = az0 + s * P["TURN_DEG"] / steps
        zp = P["LUG_Z"] - 0.7 * s / steps + (0.3 if s == steps else 0.0)
        seg_w = 2 * math.pi * P["CH_IN_RO"] * (P["TURN_DEG"] / steps + 2.5) / 360.0
        piece = inward_frame_u(P["CH_IN_RO"] + 0.05, a, zp) * extrude(
            Rectangle(seg_w, GW), gr + 0.05)
        leg = piece if leg is None else leg + piece
    upper = largest(upper - leg)

# (antenna guide fins deleted: the spire cone interior itself funnels and
# corrals the whip tip — flat fin undersides were unprintable)

# hang loop: blade with teardrop eye on top pad
top_z = RINGS[-1][1]
pad = Pos(0, 0, top_z - 2) * extrude(Circle(6.0), 2.0)   # flush with top cap, no rim
outline = Polygon((-6, 0), (6, 0), (6.5, 8), (0, 16), (-6.5, 8), align=None)
eye = Polygon((-3.5, 4), (3.5, 4), (3.5, 7.5), (0, 11.8), (-3.5, 7.5), align=None)
blade = Plane.XZ * Pos(0, top_z - 0.5, 0) * extrude(outline - eye, 2.5, both=True)
upper = largest(upper + pad + blade)
bb = upper.bounding_box()
print(f"upper done {upper.volume/1000:.1f} cm3 valid={upper.is_valid} top={bb.max.Z:.0f}")

# -------------------------------------------------------------------- TRAY
print("== tray ==")
deck = Pos(0, 0, DECK_BOT) * extrude(Circle(P["DECK_R"]), P["DECK_T"])
tray = deck
for az, rr in P["BOSSES"]:
    hole = Rot(0, 0, az) * Pos(rr, 0, DECK_BOT - 1) * extrude(
        Rectangle(10.9, 4.9), P["DECK_T"] + 2)   # drops over boss pin (0.45/side)
    tray = largest(tray - hole)

HM_AZ = P["AZ_PM_IN"] + 90.0
HMF = Rot(0, 0, HM_AZ) * Pos(0, -14, 0)     # board frame: local -Y -> az252

def bayprof(pts):
    return Plane.YZ * Polygon(*pts, align=None)

CAN_TOP = P["DECK_TOP"] + 1.8 + P["HM_PCB_T"] + P["HM_CAN_H"]     # -21.6
# ---- HM bay: one gabled tunnel, extruded along local X ----
# solid: walls + gable roof (outer up-facing, any slope; cavity ceilings >=45)
sol_pts = [(-24.3, DECK_BOT), (24.3, DECK_BOT), (24.3, -18.4), (0, 5.4), (-24.3, -18.4)]
bay = HMF * Pos(-46, 0, 0) * extrude(bayprof(sol_pts), 114)         # x -46..68
# slide void (board+can), open both ends
v_slide = [(-20.3, P["DECK_TOP"]), (20.3, P["DECK_TOP"]), (20.3, -21.28), (-20.3, -21.28)]
cav1 = HMF * Pos(-44, 0, 0) * extrude(bayprof(v_slide), 114)   # same start as tunnel
# exhaust gable tunnel above can, sealed -X, open +X (= mouth at az324 facet)
v_tun = [(-22.3, -21.28), (22.3, -21.28), (0, 2.5)]
cav2 = HMF * Pos(-44, 0, 0) * extrude(bayprof(v_tun), 114)
# intake corridor along can slot face (-Y), sealed both ends; corbel above it
v_cor = [(-22.3, -41.0), (-19.3, -41.0), (-19.3, -19.9), (-22.3, -25.9)]
cav3 = HMF * Pos(-42, 0, 0) * extrude(bayprof(v_cor), 92)           # x -42..50
tray = largest((tray + bay) - cav1 - cav2 - cav3)
# rails + end stop posts (straddle Grove connector) in slide void
for sgn in (-1, 1):
    rail = HMF * Pos(-44, sgn * 16.0, P["DECK_TOP"]) * extrude(
        Rectangle(86, 6, align=(Align.MIN, Align.CENTER)), 1.8)   # y 13..19: clears corridor
    tray = largest(tray + rail)
for sgn in (-1, 1):
    stop = HMF * Pos(-42.25, sgn * 12.0, P["DECK_TOP"]) * extrude(
        Rectangle(2.5, 4.0), 8.0)
    tray = largest(tray + stop)
# Grove cable notch through the bay -X end wall (>=50deg gable, sealed tunnel)
notch = HMF * Pos(-48, 0, 0) * extrude(bayprof(
    [(-4.5, P["DECK_TOP"]), (4.5, P["DECK_TOP"]), (4.5, -27.5), (0, -22.0), (-4.5, -27.5)]), 6)
tray = largest(tray - notch)

# ---- intake snorkel: cross-gabled prism from corridor to az252 facet ----
snk_sol = [(2, DECK_BOT), (30, DECK_BOT), (30, -33), (16, -18), (2, -33)]
snk_cav = [(4, -41), (28, -41), (28, -34.2), (16, -21.8), (4, -34.2)]
snk_s = HMF * Pos(0, -21, 0) * (Plane.XZ * extrude(Polygon(*snk_sol, align=None), 22))
# void stops at y=-21.5: connects into corridor (-22.3..-19.3) but never
# undercuts the -Y rail's floor slab
snk_v = HMF * Pos(0, -21.5, 0) * (Plane.XZ * extrude(Polygon(*snk_cav, align=None), 23.5))
tray = largest((tray + snk_s) - snk_v)

# ---- shield: tangential on +Y side of bay, az72 zone ----
sc = Vector(25 * math.cos(math.radians(72)), 25 * math.sin(math.radians(72)), 0)
SHF = Pos(sc.X, sc.Y, 0) * Rot(0, 0, 342)   # local x = long (tangential) axis
for sgn in (-1, 1):
    ledge = SHF * Pos(-16.5, sgn * 12.0, P["DECK_TOP"]) * extrude(
        Rectangle(33, 2.5, align=(Align.MIN, Align.CENTER)), 6.0)
    flank = SHF * Pos(-16.5, sgn * (P["SHIELD_W"]/2 + P["RAIL_CLEAR"] + 1.0), P["DECK_TOP"]) * extrude(
        Rectangle(33, 2.0, align=(Align.MIN, Align.CENTER)), 9.0)
    tray = largest(tray + ledge + flank)
endlip = SHF * Pos(-P["SHIELD_L"]/2 - 1.8 - P["RAIL_CLEAR"], 0, P["DECK_TOP"]) * extrude(
    Rectangle(1.8, 18, align=(Align.MIN, Align.CENTER)), 9.0)
tray = largest(tray + endlip)

# ---- BME680: tangential board in drop-in clip at r41, az138 (clears HM corner)
AZ_BCLIP = P["AZ_BME"] - 6.0
arm = Rot(0, 0, AZ_BCLIP) * Pos(P["DECK_R"] - 8, 0, DECK_BOT) * extrude(
    Rectangle(18, 26, align=(Align.MIN, Align.CENTER)), P["DECK_T"])
tray = largest(tray + arm)
clipF = Rot(0, 0, AZ_BCLIP) * Pos(41, 0, 0)
for sgn in (-1, 1):
    post = clipF * Pos(sgn * (P["BME_W"]/2 + P["RAIL_CLEAR"] + 1.2), 0, DECK_BOT) * extrude(
        Rectangle(2.4, 10), P["DECK_T"] + 4.5)
    # lip with 50deg wedge underside (no flat cantilever)
    lipprof = Polygon((0, 0), (0, -3.4), (sgn * 2.2, -0.8), (sgn * 2.2, 0), align=None)
    lip = clipF * Pos(sgn * (P["BME_W"]/2 + P["RAIL_CLEAR"] + 0.1), 0,
                      DECK_BOT + P["DECK_T"] + 4.5) * (Plane.XZ * extrude(lipprof, 5, both=True))
    tray = largest(tray + post + lip)

# ---- antenna mast cup near bay ridge; base shaved by tunnel cavity itself
antf = HMF * Pos(0, 6, -10) * extrude(Circle(7.5) - Circle(4.7), 23)
antf = largest(antf - cav2)                       # oblique 46.8deg base, no islands
antf = largest(antf - (HMF * Pos(7, 6, 6) * Box(12, 7, 16)))        # side C-slot
tray = largest(tray + antf)

# ---- cable hooks / finger holes / weeps (clear zones only) ----
# hooks only in verified-free spots; NO finger holes (lift by bay roof + mast)
for az, rr in ((15, 42), (108, 44)):
    tray = largest(tray + Rot(0, 0, az) * Pos(rr, 0, P["DECK_TOP"]) * extrude(Rectangle(3, 10), 8))
for az, rr in ((50, 28), (60, 30), (165, 40)):
    tray = largest(tray - Rot(0, 0, az) * Pos(rr, 0, DECK_BOT - 1) * extrude(Circle(2.2), P["DECK_T"] + 2))
# corridor floor weep
tray = largest(tray - (HMF * Pos(10, -21, DECK_BOT - 1) * extrude(Circle(1.4), P["DECK_T"] + 3.5)))

# clip to shell clearance envelope + closure-ring keep-out (tongue/corbel zone)
tray = largest(tray & clear_in)
keepout = Pos(0, 0, -12.5) * extrude(Circle(90) - Circle(62.5), 25)
tray = largest(tray - keepout)
print(f"tray done {tray.volume/1000:.1f} cm3 valid={tray.is_valid}")

# -------------------------------------------------- grommet + mesh retainer
g = extrude(Circle(P["USB_BORE"]/2 + 1.5) - Circle(P["GROMMET_GRIP"]/2), 9)
g = largest(g - Pos(0, 0, 3) * Box(1.4, 30, 14, align=(Align.CENTER, Align.CENTER, Align.MIN)))
grommet = largest(g + extrude(Circle(P["USB_BORE"]/2 + 3.0) - Circle(P["GROMMET_GRIP"]/2), 2.2))

reb2d = inset_tri_2d(tri_local_2d(pl_in, tp_in), P["TRI_INSET_REB"] + 0.25)
opn2d = inset_tri_2d(tri_local_2d(pl_in, tp_in), P["TRI_INSET_OPEN"] + 2.0)
meshring = extrude(Polygon(*reb2d, align=None) - Polygon(*opn2d, align=None), 1.0)

# ------------------------------------------------------------- verification
print("== checks ==")
hm_env = HMF * Pos(0, 0, P["DECK_TOP"] + 1.8) * extrude(
    Rectangle(P["HM_L"], P["HM_W"]), P["HM_PCB_T"] + P["HM_CAN_H"])
sh_env = SHF * Pos(0, 0, P["DECK_TOP"] + 6) * extrude(
    Rectangle(P["SHIELD_L"], P["SHIELD_W"]), 1.6 + P["STACK_H"])

def ivol(a, b):
    try:
        r = a & b
        v = sum(s.volume for s in r.solids()) if len(r.solids()) else 0.0
        if v > 0.5:
            bbx = r.bounding_box()
            print(f"    !! overlap bbox {bbx.min} .. {bbx.max}")
        return v
    except Exception:
        return 0.0

print(f"  upper&lower {ivol(upper, lower):.2f} mm3")
print(f"  tray&lower  {ivol(tray, lower):.2f} mm3")
print(f"  HM&tray     {ivol(hm_env, tray):.2f} mm3")
print(f"  HM&lower    {ivol(hm_env, lower):.2f} mm3")
print(f"  shield&tray {ivol(sh_env, tray):.2f} mm3")
print(f"  shield&lower{ivol(sh_env, lower):.2f} mm3")

# ------------------------------------------------------------------ export
print("== export ==")
lower_p = Pos(0, 0, -RINGS[0][1]) * lower
upper_p = upper
tray_p = Pos(0, 0, -DECK_BOT) * tray
for name, part in (("kit1_lower", lower_p), ("kit1_upper", upper_p),
                   ("kit1_tray", tray_p), ("kit1_grommet", grommet),
                   ("kit1_meshring", meshring)):
    export_stl(part, f"{name}.stl", tolerance=0.05, angular_tolerance=0.3)
    b = part.bounding_box()
    print(f"  {name}.stl vol {part.volume/1000:.1f} cm3 "
          f"bbox {b.size.X:.0f}x{b.size.Y:.0f}x{b.size.Z:.0f}")
export_step(Compound([lower, upper, tray]), "kit1_assembly.step")
print("DONE")
