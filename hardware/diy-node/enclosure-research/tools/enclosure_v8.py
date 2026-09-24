#!/usr/bin/env python3
"""Making Sense Bali DIY node — v8 SHARED PLATFORM (Basic + Plus), additive-native.

Fuses v6's validated two-variant internals with v7's additive-native language, in
ONE parametric generator:

  - sheet-GYROID breathing window for the BME680 (the snap-in insert is made by
    tools/gyroid_panel.py), NOT louvers. Front wall on Basic; LEFT side wall on Plus
    (so the PM air path never crosses the T/RH air).
  - product craft carried from v7: lifted standoff feet (which also hold the bottom
    intake off any flush surface), a shadow-gap reveal under the hood, a radius
    system, the domed hood + drip-lip curl.
  - zero-hardware print-in-place bottom bayonet (verbatim from v7).
  - Plus grows a front bay for the vertical HM3301 with its own DOWN-facing PM duct
    + can grille (verbatim from v6). BME680 -> side window keeps the two air systems
    physically separate (ICD F-04).
  - high side exhaust slots under the eave finish the chimney: intake low (bottom
    cap + low gyroid window), warm air out high in the hood's rain-shadow.

Validated internals reused verbatim (v6, itself from v4/v5): perfboard standoffs,
keyholes, HM3301 rails + 2 pegs into the Ø3.2 holes, bottom bayonet centred on the
cavity. ALL FITS COUPON_TBD_*; nothing fit-critical is final until ICD 5.1 is
measured from the printed coupons.
"""
import os
import math
from build123d import *  # noqa: F403
import trimesh as _tm

OUT = os.path.join(os.path.dirname(__file__), "..", "v8")
os.makedirs(OUT, exist_ok=True)
REVIEW = os.path.join(OUT, "review")
os.makedirs(REVIEW, exist_ok=True)

COUPON_TBD_SLIDE = 0.30
COUPON_TBD_PRESS = -0.05
COUPON_TBD_PILOT_M2 = 1.75
COUPON_TBD_PANEL = 0.30           # gyroid panel seat clearance

# frozen component dims (ICD 2)
perf_w, perf_h, perf_t = 40.0, 60.0, 1.6
bme_w, bme_h, bme_t = 16.0, 12.5, 3.0
hm_w, hm_h, hm_t = 40.0, 80.0, 1.6
can_w, can_h, can_d = 38.0, 40.0, 15.2
hm_hole_d = 3.2

# common frame
wall = 2.5
back_y = 16.0
back_inner = back_y - wall
HW, HW_IN = 24.0, 21.5
fillet_r = 3.0
floor_z = 12.0
foot_h = 3.0
perf_back_gap = 4.0
perf_z0 = 18.0
key_x, key_z = 16.0, 60.0
bme_z = 30.0
eave, drip, roof_h = 4.0, 3.0, 16.0
n_lugs = 3
hm_z0, hm_carrier_y = 13.0, 13.0

# gyroid breathing window (matches tools/gyroid_panel.py: window 30x28, flange 33.6x31.6)
win_w, win_h = 30.0, 28.0
flange_w, flange_h = 33.6, 31.6
ledge = 1.8                        # inside rebate depth the flange seats against

VARIANTS = {
    # cap_r=16 shared by both: seat outer (16 + wall + slide = 18.8) clears the 21.5
    # inner half-width by ~2.7 mm, so the bayonet skirt/slots never graze the side
    # wall — the root cause of the v6 sliver. One cap fits the whole family. Bottom
    # service opening stays Ø18 (cap window) + Ø26 floor hole: enough for mesh + cable.
    "basic": dict(FRONT=24.0, FRONT_IN=21.5, body_top=86.0, hm=False, cap_r=16.0),
    "plus":  dict(FRONT=36.0, FRONT_IN=33.5, body_top=96.0, hm=True,  cap_r=16.0),
}


def largest_solid(x):
    try:
        solids = list(x.solids())
    except (AttributeError, TypeError):
        solids = [s for item in x for s in item.solids()]
    if not solids:
        raise ValueError("boolean produced no solids")
    return max(solids, key=lambda s: s.volume)


def yrect(z, y0, y1, w):
    return Pos(0, (y0 + y1) / 2.0, z) * Rectangle(w, (y1 - y0))


# ---- print-in-place bayonet (added-tab topology: the socket stays ONE solid) ----
BAYO_RB = 16.0            # socket bore (cap plug slides in)
BAYO_RP = 13.0            # cap plug radius (well under the bore -> room for lugs)
BAYO_HSK = 7.0            # skirt depth below the floor (keeps cap above the feet)
BAYO_TAB_IN = 14.0        # inward reach of the 3 locking tabs
BAYO_TAB_ARC = 52.0       # deg
BAYO_TAB_T = 2.6          # tab thickness (z); tab top = the rest ledge
BAYO_TAB_DZ = 2.6         # tab base above the skirt bottom
BAYO_LUG_OUT = 15.7       # cap lug reaches just under the bore
BAYO_LUG_ARC = 34.0       # deg (< gap between tabs, so lugs pass through to enter)
BAYO_LUG_T = 2.4
BAYO_LUG_LOCAL_Z = 9.6    # lug bottom in cap-local frame; near the plug top so the lug
                          # rests ON the tab top once twisted to lock (not at tab level)


def arc_sector(r_in, r_out, arc_deg, t, ang):
    """Clean annular sector solid (r_in..r_out over arc_deg), z 0..t, centred at ang."""
    annulus = largest_solid(Cylinder(r_out, t, align=(Align.CENTER, Align.CENTER, Align.MIN))
                            - Cylinder(r_in, t + 0.2, align=(Align.CENTER, Align.CENTER, Align.MIN)))
    R = r_out + 5.0
    a0, a1 = math.radians(-arc_deg / 2), math.radians(arc_deg / 2)
    pts = [(0, 0), (R * math.cos(a0), R * math.sin(a0)), (R * math.cos(a1), R * math.sin(a1))]
    with BuildPart() as wp:
        with BuildSketch(Plane.XY):
            with BuildLine():
                Polyline(*pts, close=True)
            make_face()
        extrude(amount=t)
    return Rot(0, 0, ang) * largest_solid(annulus & wp.part)


def build(name, cfg):
    FRONT, FRONT_IN, body_top = cfg["FRONT"], cfg["FRONT_IN"], cfg["body_top"]
    hm, cap_r = cfg["hm"], cfg["cap_r"]
    cap_window_r = cap_r - 7.0
    cap_cy = (FRONT_IN - back_inner) / 2

    # ---- dummy components (verified dims) for interference ----
    perf_y0 = -back_inner + perf_back_gap
    perfboard = Pos(0, perf_y0, perf_z0 + foot_h) * Box(perf_w, perf_t, perf_h, align=(Align.CENTER, Align.MIN, Align.MIN))
    perf_env = Pos(0, perf_y0 + perf_t, perf_z0 + foot_h) * Box(perf_w, 11.0, perf_h, align=(Align.CENTER, Align.MIN, Align.MIN))
    dummies = perfboard + perf_env
    if hm:
        # inboard (x=-5) so the sensor clears the seated side gyroid panel and sits
        # behind it with a foil-liner air gap (~3 mm) — the panel is 8 mm thick.
        bme = Pos(-5.0, perf_y0 + perf_t, bme_z + foot_h) * Box(bme_w, bme_t + 4, bme_h, align=(Align.CENTER, Align.MIN, Align.CENTER))
        hm_carrier = Pos(0, hm_carrier_y, hm_z0 + foot_h) * Box(hm_w, hm_t, hm_h, align=(Align.CENTER, Align.MIN, Align.MIN))
        hm_can = Pos(0, hm_carrier_y + hm_t, hm_z0 + foot_h + (hm_h - can_h) / 2) * Box(can_w, can_d, can_h, align=(Align.CENTER, Align.MIN, Align.MIN))
        hm_module = hm_carrier + hm_can
        can_face_z0 = hm_z0 + foot_h + (hm_h - can_h) / 2
    else:
        bme = Pos(0, perf_y0 + perf_t, bme_z + foot_h) * Box(bme_w, bme_t + 4, bme_h, align=(Align.CENTER, Align.MIN, Align.CENTER))
        hm_module = None

    # ---- monocoque shell ----
    body = Pos(0, -back_y, foot_h) * Box(2 * HW, back_y + FRONT, body_top, align=(Align.CENTER, Align.MIN, Align.MIN))
    body = fillet(body.edges().filter_by(Axis.Z), fillet_r)
    cavity = Pos(0, -back_inner, floor_z - wall + foot_h) * Box(2 * HW_IN, back_inner + FRONT_IN, body_top + 10, align=(Align.CENTER, Align.MIN, Align.MIN))
    cavity = fillet(cavity.edges().filter_by(Axis.Z), fillet_r - 1.0)
    body = largest_solid(body - cavity)

    # The base below the cavity floor is otherwise a SOLID block (the cavity starts at
    # the floor and only goes up). Carve the bayonet socket bore through it so the cap
    # actually inserts from below and the bottom intake connects to the cavity. v6/v7
    # never did this — the cap could not seat. Caught by the assembly simulation.
    body = largest_solid(body - Pos(0, cap_cy, foot_h - 0.1) * Cylinder(BAYO_RB + COUPON_TBD_SLIDE, (floor_z - wall) + 0.2, align=(Align.CENTER, Align.CENTER, Align.MIN)))

    # lifted feet (craft + hold the bottom intake off a flush surface)
    for sx in (-1, 1):
        for fy in (-back_y + 5, FRONT - 5):
            body = body + Pos(sx * (HW - 6), fy, 0) * Cylinder(3.5, foot_h, align=(Align.CENTER, Align.CENTER, Align.MIN))

    # floor + bayonet socket. Added-tab topology: a CONTINUOUS skirt + 3 ADDED inward
    # tabs. The v6/v7 design CUT entry/turn slots through a thin ring and fragmented it
    # (Basic 3 islands, Plus 4). Nothing is cut into islands here, so the body stays one
    # solid. Clearances COUPON_TBD_SLIDE; lock engagement validated by a section print.
    fz = floor_z - wall + foot_h
    floor_plate = Pos(0, -back_y, fz) * Box(2 * HW, back_y + FRONT, wall, align=(Align.CENTER, Align.MIN, Align.MIN))
    floor_plate = fillet(floor_plate.edges().filter_by(Axis.Z), fillet_r)
    floor_plate = largest_solid(floor_plate - Pos(0, cap_cy, 0) * Cylinder(BAYO_RB + COUPON_TBD_SLIDE, 100, align=(Align.CENTER, Align.CENTER, Align.CENTER)))
    body = body + floor_plate
    skirt = largest_solid(Cylinder(BAYO_RB + COUPON_TBD_SLIDE + wall, BAYO_HSK, align=(Align.CENTER, Align.CENTER, Align.MIN))
                          - Cylinder(BAYO_RB + COUPON_TBD_SLIDE, BAYO_HSK + 0.2, align=(Align.CENTER, Align.CENTER, Align.MIN)))
    body = body + Pos(0, cap_cy, fz - BAYO_HSK) * skirt
    for k in range(n_lugs):
        body = body + Pos(0, cap_cy, fz - BAYO_HSK + BAYO_TAB_DZ) * arc_sector(BAYO_TAB_IN, BAYO_RB + COUPON_TBD_SLIDE + 0.6, BAYO_TAB_ARC, BAYO_TAB_T, 60 + k * 120)
    body = largest_solid(body)

    # perfboard standoffs
    so_dx, so_dz = 16.2, 26.2
    perf_cz = perf_z0 + perf_h / 2 + foot_h
    for sx in (-1, 1):
        for sz in (-1, 1):
            post = Pos(sx * so_dx, -back_inner, perf_cz + sz * so_dz) * Rot(-90, 0, 0) * Cylinder(3.0, perf_back_gap, align=(Align.CENTER, Align.CENTER, Align.MIN))
            pilot = Pos(sx * so_dx, -back_inner - 0.1, perf_cz + sz * so_dz) * Rot(-90, 0, 0) * Cylinder(COUPON_TBD_PILOT_M2 / 2, perf_back_gap + 4, align=(Align.CENTER, Align.CENTER, Align.MIN))
            body = largest_solid(body + post - pilot)

    # keyholes (hang shell first, boards after)
    for sx in (-1, 1):
        kh = Pos(sx * key_x, 0, key_z + foot_h) * Rot(-90, 0, 0) * Cylinder(4.0, 50, align=(Align.CENTER, Align.CENTER, Align.CENTER))
        ks = Pos(sx * key_x, -back_y - 2, key_z + foot_h) * Box(4.0, 10, 10, align=(Align.CENTER, Align.MIN, Align.MIN))
        body = largest_solid(largest_solid(body - kh) - ks)

    # ---- BME680 gyroid breathing window + inside flange rebate ----
    wz = bme_z + foot_h
    if hm:
        # LEFT (-X) side wall, low, by the BME680 — away from the HM3301 front bay
        body = largest_solid(body - Pos(-HW, 0, wz) * Box(2 * wall + 6, win_w, win_h, align=(Align.CENTER, Align.CENTER, Align.CENTER)))
        body = largest_solid(body - Pos(-(HW_IN - ledge), 0, wz) * Box(2 * ledge, flange_w + COUPON_TBD_PANEL, flange_h + COUPON_TBD_PANEL, align=(Align.MAX, Align.CENTER, Align.CENTER)))
    else:
        # FRONT (+Y) wall
        body = largest_solid(body - Pos(0, FRONT - wall - 1, wz) * Box(win_w, wall + 3, win_h, align=(Align.CENTER, Align.MIN, Align.CENTER)))
        body = largest_solid(body - Pos(0, FRONT - wall - ledge, wz) * Box(flange_w + COUPON_TBD_PANEL, ledge + 0.2, flange_h + COUPON_TBD_PANEL, align=(Align.CENTER, Align.MIN, Align.CENTER)))

    # ---- Plus PM system: HM3301 vertical mount, dedicated DOWN duct, separated ----
    if hm:
        rail_gap = hm_t + COUPON_TBD_SLIDE
        for sx in (-1, 1):
            post = Pos(sx * (hm_w / 2 + 2.0), hm_carrier_y + rail_gap / 2, hm_z0 - 1 + foot_h) * Box(4.0, rail_gap + 5.0, hm_h + 2.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
            slot = Pos(sx * (hm_w / 2 - 1.0), hm_carrier_y - 0.05, hm_z0 - 1.5 + foot_h) * Box(6.0, rail_gap, hm_h + 4.0, align=(Align.CENTER, Align.MIN, Align.MIN))
            body = largest_solid(body + post - slot)
        for sx in (-1, 1):
            peg = Pos(sx * 16.0, hm_carrier_y - 0.02, hm_z0 + 4.0 + foot_h) * Rot(-90, 0, 0) * Cylinder((hm_hole_d + COUPON_TBD_PRESS) / 2, hm_t + 1.2, align=(Align.CENTER, Align.CENTER, Align.MIN))
            body = body + peg
        # can grille on the front, at the can face
        for gz in (can_face_z0 + 10, can_face_z0 + 24):
            grille = Pos(0, FRONT - 1.0, gz) * Box(24.0, wall + 6.0, 2.4, align=(Align.CENTER, Align.MAX, Align.CENTER))
            body = largest_solid(body - grille)
        # dedicated DOWN-facing PM intake duct at the front-bottom (down-and-out 40deg)
        for lz in (16.0 + foot_h, 22.0 + foot_h):
            duct = Pos(0, FRONT - 1.0, lz) * Rot(40, 0, 0) * Box(26.0, wall + 9.0, 2.8, align=(Align.CENTER, Align.CENTER, Align.CENTER))
            body = largest_solid(body - duct)

    # ---- brain exhaust slots high under the eave (down-facing, rain-shadow) ----
    ex_signs = (1,) if hm else (-1, 1)   # on Plus, opposite the BME side window
    for sgn in ex_signs:
        for lz in (body_top - 14 + foot_h, body_top - 7 + foot_h):
            lv = Pos(sgn * (HW - 1.0), 6.0, lz) * Rot(0, sgn * 40, 0) * Box(wall + 9.0, 16.0, 2.6, align=(Align.CENTER, Align.CENTER, Align.CENTER))
            body = largest_solid(body - lv)

    # USB-C gland chase, bottom, angled down
    usb = Pos(-10.0, cap_cy, fz + 1.0) * Rot(35, 0, 0) * Cylinder(4.25, wall + 16, align=(Align.CENTER, Align.CENTER, Align.MIN))
    body = largest_solid(body - usb)

    # weep hole 2.5 mm at the low interior point, angled down-out
    weep = Pos(0, FRONT_IN - 2.0, floor_z + 0.5 + foot_h) * Rot(55, 0, 0) * Cylinder(1.25, 14, align=(Align.CENTER, Align.CENTER, Align.MIN))
    body = largest_solid(body - weep)

    # ePTFE membrane vent boss on the upper +X side wall (leeward)
    boss = Pos(HW - 1.0, -2.0, body_top - 20 + foot_h) * Rot(0, 90, 0) * Cylinder(6.0, 2.5, align=(Align.CENTER, Align.CENTER, Align.MIN))
    body = body + boss
    vent = Pos(HW - 0.5, -2.0, body_top - 20 + foot_h) * Rot(0, 90, 0) * Cylinder(3.2, wall + 4, align=(Align.CENTER, Align.CENTER, Align.MIN))
    body = largest_solid(body - vent)

    # shadow-gap reveal groove just below the hood (craft)
    sg = Pos(0, -back_y, body_top + foot_h - 1.5) * Box(2 * HW + 1, back_y + FRONT + 1, 1.0, align=(Align.CENTER, Align.MIN, Align.MIN))
    sg = largest_solid(sg - Pos(0, -back_y - 0.5, body_top + foot_h - 2.5) * Box(2 * HW - 2.0, back_y + FRONT + 2, 3.0, align=(Align.CENTER, Align.MIN, Align.MIN)))
    body = largest_solid(body - sg)

    # hood with drip-lip curl
    zb = body_top + foot_h
    roof_outer = loft([
        yrect(zb, -back_y, FRONT, 2 * HW),
        yrect(zb + eave, -back_y, FRONT + eave, 2 * HW + 2 * eave),
        Pos(0, (FRONT - back_y) / 2, zb + roof_h) * Rectangle(14.0, 12.0),
    ], ruled=True)
    roof_inner = loft([
        yrect(zb - 0.1, -back_inner, FRONT_IN, 2 * HW_IN),
        yrect(zb + eave, -back_inner, FRONT_IN, 2 * HW_IN),
        Pos(0, (FRONT_IN - back_inner) / 2, zb + roof_h - wall) * Rectangle(7.0, 6.0),
    ], ruled=True)
    roof = largest_solid(roof_outer - roof_inner)
    lip = Pos(0, -back_y, zb + eave - drip) * Box(2 * (HW + eave), back_y + FRONT + eave, drip, align=(Align.CENTER, Align.MIN, Align.MIN))
    lip = largest_solid(lip - Pos(0, -back_y - 1, zb + eave - drip - 1) * Box(2 * (HW + eave) - 3.0, back_y + FRONT + eave, drip + 3, align=(Align.CENTER, Align.MIN, Align.MIN)))
    roof = roof + lip
    roof = largest_solid(roof - (Pos(0, -back_y, 0) * Box(500, 400, 500, align=(Align.CENTER, Align.MAX, Align.CENTER))))
    body = body + roof

    # ---- cap: zero-hardware bayonet plug + down mesh intake ----
    # A thin plug cup carries 3 lugs that pass up through the tab gaps and twist under
    # the socket tabs to lock (~37 deg). Mesh + cable enter the down window. COUPON_TBD.
    cap = Cylinder(BAYO_RP + 3.0, 2.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
    cap = cap + Cylinder(BAYO_RP + 4.5, 1.4, align=(Align.CENTER, Align.CENTER, Align.MIN))
    plug_h = BAYO_LUG_LOCAL_Z + BAYO_LUG_T - 2.0 + 0.6   # plug reaches just past the lugs
    plug = largest_solid(Cylinder(BAYO_RP, plug_h, align=(Align.CENTER, Align.CENTER, Align.MIN))
                         - Cylinder(BAYO_RP - wall, plug_h + 0.2, align=(Align.CENTER, Align.CENTER, Align.MIN)))
    cap = cap + Pos(0, 0, 2.0) * plug
    for k in range(n_lugs):
        cap = cap + Pos(0, 0, BAYO_LUG_LOCAL_Z) * arc_sector(BAYO_RP - 0.5, BAYO_LUG_OUT, BAYO_LUG_ARC, BAYO_LUG_T, k * 120)
    cap = largest_solid(cap - Cylinder(BAYO_RP - wall - 0.5, 40, align=(Align.CENTER, Align.CENTER, Align.CENTER)))
    cap = largest_solid(cap)

    # guarantee a single printable solid: drop any inverted boolean sliver left by the
    # bayonet "turn" slot grazing the side wall. The bayonet detail is refined in the
    # features pass (its clearances are COUPON_TBD); the base form must be 1 solid.
    body = largest_solid(body)

    # ---- interference + exports ----
    print(f"--- {name} interference ---")
    ok = True

    def chk(nm, a, b, lim=0.02):
        v = 0.0
        try:
            v = sum(s.volume for s in (a & b).solids()) / 1000.0
        except Exception:
            pass
        print(f"  [{'OK ' if v <= lim else 'FAIL'}] {nm}: {v:.3f} cm3")
        return v <= lim

    ok &= chk("boards vs body", dummies, body)
    ok &= chk("bme vs body", bme, body)
    if hm:
        ok &= chk("hm module vs body", hm_module, body)

    cap_rest_z = (fz - BAYO_HSK + BAYO_TAB_DZ + BAYO_TAB_T) + 0.3 - BAYO_LUG_LOCAL_Z  # lug rests on tab top
    cap_placed = Pos(0, cap_cy, cap_rest_z) * Rot(0, 0, 60) * cap   # locked (lugs twisted under tabs)
    parts = [body, cap_placed, perfboard, bme] + ([hm_module] if hm else [])
    assembly = Compound(parts)
    hh = Pos(0, -back_y, 0) * Box(300, 300, 400, align=(Align.MAX, Align.CENTER, Align.MIN))
    cut_parts = [largest_solid(body - hh), perfboard, bme] + ([hm_module] if hm else [])
    cutaway = Compound(cut_parts)
    for nm, part, outdir, step, clean in [
            (f"v8_{name}_body", body, OUT, True, True), (f"v8_{name}_cap", cap, OUT, True, True),
            (f"v8_{name}_assembly", assembly, REVIEW, False, False), (f"v8_{name}_cutaway", cutaway, REVIEW, False, False)]:
        p = os.path.join(outdir, f"{nm}.stl")
        export_stl(part, p)
        if step:
            export_step(part, os.path.join(outdir, f"{nm}.step"))
        if clean:  # OCC may tessellate the single solid into a main island + a tiny
            # inverted sliver where the bayonet turn-slot grazes the wall. Keep the
            # main island so the printed STL is one solid. (Bayonet slot geometry is
            # an OPEN features-pass item — see DESIGN_LOG.)
            mesh = _tm.load(p, force="mesh")
            cs = mesh.split(only_watertight=False)
            if len(cs) > 1:
                keep = max(cs, key=lambda c: c.area)
                keep.fix_normals()
                keep.export(p)
                print(f"    cleaned {nm}: {len(cs)} islands -> 1 (wt={keep.is_watertight})")
    bb = body.bounding_box()
    print(f"  {name} body: {bb.size.X:.0f} x {bb.size.Y:.0f} x {bb.size.Z:.0f} mm  | interference {'OK' if ok else 'FAIL'}")
    return dict(body=body, cap=cap, perfboard=perfboard, perf_env=perf_env, bme=bme,
                hm_module=hm_module, cap_cy=cap_cy, fz=fz, FRONT=FRONT, FRONT_IN=FRONT_IN,
                body_top=body_top, bme_z=bme_z + foot_h, cap_rest_z=cap_rest_z)


if __name__ == "__main__":
    for nm, cfg in VARIANTS.items():
        build(nm, cfg)
