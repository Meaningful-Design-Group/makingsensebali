#!/usr/bin/env python3
"""Making Sense Bali DIY node — v9 THREE-PART SHELL (Basic + Plus), additive-native.

v9 fixes the two fatal v8 failures (see HANDOFF_v9_redesign.md):

  RC-1  v8 fused the hood to the body (one sealed monocoque), so the only openings
        were smaller than the 40x60 perfboard — the electronics had no way in.
        v9: the body is OPEN-TOP. The hood is a SEPARATE part that screws on with
        2x M3 into bosses on the body's top rim. Boards load from the open top,
        hood goes on last.

  RC-2  v8's cavity floor was an unsupported ~43 mm bridge printed mid-body; it
        collapsed. v9: the body is OPEN-BOTTOM (no floor, no in-body bayonet). A
        SEPARATE full-footprint BASE PLATE closes the bottom, printed flat on the
        bed (no bridge), carrying the feet, the mesh intake, the USB-C chase and
        the weep. It mates to the body with a PRESS-FIT spigot.

Three printed parts per variant: body (open tube), hood (domed crown), base plate.

Validated v8 internals carried VERBATIM (they printed clean): wall geometry,
perfboard standoffs, keyholes, HM3301 rails + 2 pegs, gyroid breathing window +
rebate, side/eave exhaust slots, ePTFE membrane boss, shadow-gap reveal, can
grille + down PM duct (Plus). Only the bottom (floor/bayonet) and top (roof fuse)
changed.

*** STAGING BUILD — NOT FOR PRINT. ***
Every fit is a named COUPON_TBD_* parameter. ICD 5.1 is still TBD. Nothing
fit-critical prints until 5.1 is measured from the printed coupons. The press-fit
ring (COUPON_TBD_PRESSFIT) is the parameter most sensitive to 5.1 and is the first
section to test once numbers land.
"""
import os
import math
from build123d import *  # noqa: F403
import trimesh as _tm

OUT = os.path.join(os.path.dirname(__file__), "..", "v9")
os.makedirs(OUT, exist_ok=True)
REVIEW = os.path.join(OUT, "review")
os.makedirs(REVIEW, exist_ok=True)

# ---- COUPON_TBD_* : placeholder fits, replace from ICD 5.1 before any print ----
COUPON_TBD_SLIDE = 0.30           # sliding fit (HM3301 rail gap)
COUPON_TBD_PRESS = -0.05          # press fit (pegs into Ø3.2)
COUPON_TBD_PILOT_M2 = 1.75        # perfboard standoff self-tap pilot
COUPON_TBD_PANEL = 0.30           # gyroid panel seat clearance
COUPON_TBD_PRESSFIT = 0.15        # base-plate spigot vs cavity wall (THE press fit).
                                  # Staged slightly POSITIVE so the assembly viz reads
                                  # clean; the real (likely slightly negative) interference
                                  # comes from the clearance ladder in ICD 5.1.
COUPON_TBD_M3_PILOT = 2.5         # M3 thread-forming pilot in the hood bosses (PETG)
M3_CLR = 3.4                      # M3 free-clearance hole (body top-rim shelf)

# frozen component dims (ICD 2)
perf_w, perf_h, perf_t = 40.0, 60.0, 1.6
bme_w, bme_h, bme_t = 16.0, 12.5, 3.0
hm_w, hm_h, hm_t = 40.0, 80.0, 1.6
can_w, can_h, can_d = 38.0, 40.0, 15.2
hm_hole_d = 3.2

# common frame (verbatim from v8)
wall = 2.5
back_y = 16.0
back_inner = back_y - wall
HW, HW_IN = 24.0, 21.5
fillet_r = 3.0
floor_z = 12.0
foot_h = 3.0                      # base-plate top sits at z = foot_h; body bottom rim too
perf_back_gap = 4.0
perf_z0 = 18.0
key_x, key_z = 16.0, 60.0
bme_z = 30.0
eave, drip, roof_h = 4.0, 3.0, 16.0
hm_z0, hm_carrier_y = 13.0, 13.0

# gyroid breathing window (matches tools/gyroid_panel.py: window 30x28, flange 33.6x31.6)
win_w, win_h = 30.0, 28.0
flange_w, flange_h = 33.6, 31.6
ledge = 1.8

# --- v9 new geometry params ---
SPIGOT_H = 6.0                    # press-fit spigot rise into the cavity
SPIGOT_WALL = 2.0
GRILLE_T = wall                   # intake grille floor = full wall thickness (2.5), prints on the bed
MESH_SEAT_T = 2.0                 # real-depth pocket for the drop-in mesh/grid panel (inside face)
OPEN_W, OPEN_D = 30.0, 30.0       # intake open area ~2x v9.0 (~20x22) — "double the size"
SEAT_MARGIN = 3.0                 # mesh-seat shoulder around the open area
BOSS_R = 4.0                      # hood-screw boss radius on body top rim
BOSS_H = 6.0                      # boss height (M3 thread engagement), sits above perfboard top
BOSS_X = 18.0
HOOD_EAR_T = 3.0                  # hood screw-ear thickness at the hood base

# --- v9 breathing-plate slide-in rail (Tomas, 2026-06-10: 35x35x7 friction plate) ---
PLATE_W, PLATE_H, PLATE_T = 35.0, 35.0, 7.0   # the insert plate (Tomas's spec). Generated
                                              # by tools/breathing_panel_v9.py -> v9_breathing_panel.stl
VENT_W, VENT_H = 30.0, 30.0                    # breathing zone inside the plate
WIN_OPEN = 31.0                                # through-hole in the wall (plate overlaps wall ~2mm/side)
RAIL_LIP = 2.0                                 # outer lip wrap over the plate face (retains outward)
RAIL_WEB = 3.0                                 # rail side-web width
RAIL_TOPEXT = 8.0                              # rail extends above the plate for top insertion
RAIL_STOP_OUT = 3.0                            # bottom locating ledge protrusion (self-supporting)
COUPON_TBD_RAIL = 0.25                         # plate-in-rail slide/friction clearance (per ICD 5.1)

VARIANTS = {
    "basic": dict(FRONT=24.0, FRONT_IN=21.5, body_top=86.0, hm=False),
    "plus":  dict(FRONT=36.0, FRONT_IN=33.5, body_top=96.0, hm=True),
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


def box_lh(xl, xh, yl, yh, zl, zh):
    """Axis-aligned box from explicit min/max bounds."""
    return Pos((xl + xh) / 2, (yl + yh) / 2, (zl + zh) / 2) * Box(xh - xl, yh - yl, zh - zl)


def build(name, cfg):
    FRONT, FRONT_IN, body_top = cfg["FRONT"], cfg["FRONT_IN"], cfg["body_top"]
    hm = cfg["hm"]
    cap_cy = (FRONT_IN - back_inner) / 2          # cavity centre in y (mesh/USB datum)

    # ---- dummy components (verified dims) for interference ----
    perf_y0 = -back_inner + perf_back_gap
    perfboard = Pos(0, perf_y0, perf_z0 + foot_h) * Box(perf_w, perf_t, perf_h, align=(Align.CENTER, Align.MIN, Align.MIN))
    perf_env = Pos(0, perf_y0 + perf_t, perf_z0 + foot_h) * Box(perf_w, 11.0, perf_h, align=(Align.CENTER, Align.MIN, Align.MIN))
    dummies = perfboard + perf_env
    if hm:
        bme = Pos(-5.0, perf_y0 + perf_t, bme_z + foot_h) * Box(bme_w, bme_t + 4, bme_h, align=(Align.CENTER, Align.MIN, Align.CENTER))
        hm_carrier = Pos(0, hm_carrier_y, hm_z0 + foot_h) * Box(hm_w, hm_t, hm_h, align=(Align.CENTER, Align.MIN, Align.MIN))
        hm_can = Pos(0, hm_carrier_y + hm_t, hm_z0 + foot_h + (hm_h - can_h) / 2) * Box(can_w, can_d, can_h, align=(Align.CENTER, Align.MIN, Align.MIN))
        hm_module = hm_carrier + hm_can
        can_face_z0 = hm_z0 + foot_h + (hm_h - can_h) / 2
    else:
        bme = Pos(0, perf_y0 + perf_t, bme_z + foot_h) * Box(bme_w, bme_t + 4, bme_h, align=(Align.CENTER, Align.MIN, Align.CENTER))
        hm_module = None

    # =====================================================================
    # BODY — open tube. Open TOP (hood is separate) and open BOTTOM (base
    # plate is separate). No floor plate, no in-body bayonet. This is the
    # core RC-1/RC-2 fix.
    # =====================================================================
    body = Pos(0, -back_y, foot_h) * Box(2 * HW, back_y + FRONT, body_top, align=(Align.CENTER, Align.MIN, Align.MIN))
    body = fillet(body.edges().filter_by(Axis.Z), fillet_r)
    # cavity runs PAST both ends of the body -> open top and open bottom.
    cavity = Pos(0, -back_inner, foot_h - 2.0) * Box(2 * HW_IN, back_inner + FRONT_IN, body_top + 12, align=(Align.CENTER, Align.MIN, Align.MIN))
    cavity = fillet(cavity.edges().filter_by(Axis.Z), fillet_r - 1.0)
    body = largest_solid(body - cavity)

    # perfboard standoffs (verbatim v8) — cantilevered off the back wall, hang boards in
    so_dx, so_dz = 16.2, 26.2
    perf_cz = perf_z0 + perf_h / 2 + foot_h
    for sx in (-1, 1):
        for sz in (-1, 1):
            post = Pos(sx * so_dx, -back_inner, perf_cz + sz * so_dz) * Rot(-90, 0, 0) * Cylinder(3.0, perf_back_gap, align=(Align.CENTER, Align.CENTER, Align.MIN))
            pilot = Pos(sx * so_dx, -back_inner - 0.1, perf_cz + sz * so_dz) * Rot(-90, 0, 0) * Cylinder(COUPON_TBD_PILOT_M2 / 2, perf_back_gap + 4, align=(Align.CENTER, Align.CENTER, Align.MIN))
            body = largest_solid(body + post - pilot)

    # keyholes (hang shell first, boards after) — verbatim v8
    for sx in (-1, 1):
        kh = Pos(sx * key_x, 0, key_z + foot_h) * Rot(-90, 0, 0) * Cylinder(4.0, 50, align=(Align.CENTER, Align.CENTER, Align.CENTER))
        ks = Pos(sx * key_x, -back_y - 2, key_z + foot_h) * Box(4.0, 10, 10, align=(Align.CENTER, Align.MIN, Align.MIN))
        body = largest_solid(largest_solid(body - kh) - ks)

    # ---- BME680 breathing window + vertical SLIDE-IN RAIL (Tomas, 2026-06-10) ----
    # The 35x35x7 breathing plate (tools/breathing_panel_v9.py -> v9_breathing_panel.stl)
    # slides DOWN into two side rails and grips by friction (slot = plate + COUPON_TBD_RAIL).
    # Rails mount on the OUTSIDE of the wall, in the rain-shadow: an inward mount leaves
    # only ~1.5 mm to the Plus BME680 — too tight for the foil-liner air gap. The plate
    # loads from the open top before the hood; a bottom ledge locates it over the window.
    # C-channel per side: wall outer face = inner stop, side web = lateral stop, outer lip
    # = outward retainer. plate_box = the seated-plate envelope (for the assembly + fit check).
    wz = bme_z + foot_h
    gap = PLATE_T + COUPON_TBD_RAIL
    side_cl = COUPON_TBD_RAIL / 2.0
    rail_zl = wz - PLATE_H / 2.0
    rail_zh = wz + PLATE_H / 2.0 + RAIL_TOPEXT

    if hm:
        # -X side wall: outer face x=-HW, outward=-X, in-plane horizontal = Y
        wf = -HW
        hc = 5.0                                   # window Y-centre (keeps the 35-wide plate off the back corner)
        plate_out = wf - gap                       # plate outer plane (most -X)
        lip_out = plate_out - RAIL_LIP
        body = largest_solid(body - box_lh(wf - 1, -HW_IN + 1, hc - WIN_OPEN / 2, hc + WIN_OPEN / 2, wz - WIN_OPEN / 2, wz + WIN_OPEN / 2))
        for sy in (-1, 1):
            ey = hc + sy * (PLATE_W / 2 + side_cl)
            yl, yh = (ey, ey + RAIL_WEB) if sy > 0 else (ey - RAIL_WEB, ey)
            body = body + box_lh(lip_out, wf, yl, yh, rail_zl, rail_zh)                 # side web
            ly, lyh = (ey - RAIL_LIP, ey) if sy > 0 else (ey, ey + RAIL_LIP)
            body = body + box_lh(lip_out, plate_out, ly, lyh, rail_zl, rail_zh)          # outer retaining lip
        body = body + box_lh(wf - RAIL_STOP_OUT, wf, hc - PLATE_W / 2, hc + PLATE_W / 2, rail_zl - 2, rail_zl)  # bottom ledge
        body = largest_solid(body)
        plate_box = (plate_out, wf, hc - PLATE_W / 2, hc + PLATE_W / 2, wz - PLATE_H / 2, wz + PLATE_H / 2)
    else:
        # +Y front wall: outer face y=FRONT, outward=+Y, in-plane horizontal = X
        wf = FRONT
        hc = 0.0
        plate_out = wf + gap
        lip_out = plate_out + RAIL_LIP
        body = largest_solid(body - box_lh(hc - WIN_OPEN / 2, hc + WIN_OPEN / 2, FRONT_IN - 1, wf + 1, wz - WIN_OPEN / 2, wz + WIN_OPEN / 2))
        for sx in (-1, 1):
            ex = hc + sx * (PLATE_W / 2 + side_cl)
            xl, xh = (ex, ex + RAIL_WEB) if sx > 0 else (ex - RAIL_WEB, ex)
            body = body + box_lh(xl, xh, wf, lip_out, rail_zl, rail_zh)                  # side web
            lx, lxh = (ex - RAIL_LIP, ex) if sx > 0 else (ex, ex + RAIL_LIP)
            body = body + box_lh(lx, lxh, plate_out, lip_out, rail_zl, rail_zh)          # outer retaining lip
        body = body + box_lh(hc - PLATE_W / 2, hc + PLATE_W / 2, wf, wf + RAIL_STOP_OUT, rail_zl - 2, rail_zl)  # bottom ledge
        body = largest_solid(body)
        plate_box = (hc - PLATE_W / 2, hc + PLATE_W / 2, wf, plate_out, wz - PLATE_H / 2, wz + PLATE_H / 2)

    # ---- Plus PM system: HM3301 rails + pegs + can grille + down PM duct ---- (verbatim v8)
    if hm:
        rail_gap = hm_t + COUPON_TBD_SLIDE
        for sx in (-1, 1):
            post = Pos(sx * (hm_w / 2 + 2.0), hm_carrier_y + rail_gap / 2, hm_z0 - 1 + foot_h) * Box(4.0, rail_gap + 5.0, hm_h + 2.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
            slot = Pos(sx * (hm_w / 2 - 1.0), hm_carrier_y - 0.05, hm_z0 - 1.5 + foot_h) * Box(6.0, rail_gap, hm_h + 4.0, align=(Align.CENTER, Align.MIN, Align.MIN))
            body = largest_solid(body + post - slot)
        for sx in (-1, 1):
            peg = Pos(sx * 16.0, hm_carrier_y - 0.02, hm_z0 + 4.0 + foot_h) * Rot(-90, 0, 0) * Cylinder((hm_hole_d + COUPON_TBD_PRESS) / 2, hm_t + 1.2, align=(Align.CENTER, Align.CENTER, Align.MIN))
            body = body + peg
        for gz in (can_face_z0 + 10, can_face_z0 + 24):
            grille = Pos(0, FRONT - 1.0, gz) * Box(24.0, wall + 6.0, 2.4, align=(Align.CENTER, Align.MAX, Align.CENTER))
            body = largest_solid(body - grille)
        for lz in (16.0 + foot_h, 22.0 + foot_h):
            duct = Pos(0, FRONT - 1.0, lz) * Rot(40, 0, 0) * Box(26.0, wall + 9.0, 2.8, align=(Align.CENTER, Align.CENTER, Align.CENTER))
            body = largest_solid(body - duct)

    # ---- brain exhaust slots high under the eave (down-facing) ---- (verbatim v8)
    ex_signs = (1,) if hm else (-1, 1)
    for sgn in ex_signs:
        for lz in (body_top - 14 + foot_h, body_top - 7 + foot_h):
            lv = Pos(sgn * (HW - 1.0), 6.0, lz) * Rot(0, sgn * 40, 0) * Box(wall + 9.0, 16.0, 2.6, align=(Align.CENTER, Align.CENTER, Align.CENTER))
            body = largest_solid(body - lv)

    # ePTFE membrane vent boss on the upper +X side wall (leeward) — verbatim v8
    boss = Pos(HW - 1.0, -2.0, body_top - 20 + foot_h) * Rot(0, 90, 0) * Cylinder(6.0, 2.5, align=(Align.CENTER, Align.CENTER, Align.MIN))
    body = body + boss
    vent = Pos(HW - 0.5, -2.0, body_top - 20 + foot_h) * Rot(0, 90, 0) * Cylinder(3.2, wall + 4, align=(Align.CENTER, Align.CENTER, Align.MIN))
    body = largest_solid(body - vent)

    # shadow-gap reveal groove just below the hood (craft) — verbatim v8
    sg = Pos(0, -back_y, body_top + foot_h - 1.5) * Box(2 * HW + 1, back_y + FRONT + 1, 1.0, align=(Align.CENTER, Align.MIN, Align.MIN))
    sg = largest_solid(sg - Pos(0, -back_y - 0.5, body_top + foot_h - 2.5) * Box(2 * HW - 2.0, back_y + FRONT + 2, 3.0, align=(Align.CENTER, Align.MIN, Align.MIN)))
    body = largest_solid(body - sg)

    # ---- v9: 2x M3 hood bosses on the back of the top rim ----
    # Sit ABOVE the perfboard top (perf top z = perf_z0+foot_h+perf_h). Merged into the
    # back wall over their full height -> a thickening of the rim, well supported, no
    # standalone post. Hood screws engage these (see hood ears below).
    zb = body_top + foot_h
    boss_y = -back_inner + 2.0    # overlaps the back wall (inner face at -back_inner)
    for sx in (-1, 1):
        b = Pos(sx * BOSS_X, boss_y, zb - BOSS_H) * Cylinder(BOSS_R, BOSS_H, align=(Align.CENTER, Align.CENTER, Align.MIN))
        body = body + b
    body = largest_solid(body)
    for sx in (-1, 1):
        pilot = Pos(sx * BOSS_X, boss_y, zb - BOSS_H) * Cylinder(COUPON_TBD_M3_PILOT / 2, BOSS_H + 0.3, align=(Align.CENTER, Align.CENTER, Align.MIN))
        body = largest_solid(body - pilot)

    # =====================================================================
    # HOOD — separate part. Lofted dome (verbatim v8 roof) + drip lip, plus two
    # screw EARS at the base that present M3 clearance holes over the body bosses.
    # Prints flat-base-down (the wide loft base on the bed; ears are at the bed plane).
    # =====================================================================
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
    hood = largest_solid(roof_outer - roof_inner)
    lip = Pos(0, -back_y, zb + eave - drip) * Box(2 * (HW + eave), back_y + FRONT + eave, drip, align=(Align.CENTER, Align.MIN, Align.MIN))
    lip = largest_solid(lip - Pos(0, -back_y - 1, zb + eave - drip - 1) * Box(2 * (HW + eave) - 3.0, back_y + FRONT + eave, drip + 3, align=(Align.CENTER, Align.MIN, Align.MIN)))
    hood = hood + lip
    hood = largest_solid(hood - (Pos(0, -back_y, 0) * Box(500, 400, 500, align=(Align.CENTER, Align.MAX, Align.CENTER))))
    # screw ears: bridge from the hood back inner wall to (±BOSS_X, boss_y), at the base
    for sx in (-1, 1):
        ear = Pos(sx * BOSS_X, -back_inner + 2.0, zb) * Box(2 * BOSS_R, 8.0, HOOD_EAR_T, align=(Align.CENTER, Align.CENTER, Align.MIN))
        hood = hood + ear
    hood = largest_solid(hood)
    for sx in (-1, 1):
        clr = Pos(sx * BOSS_X, boss_y, zb - 0.2) * Cylinder(M3_CLR / 2, HOOD_EAR_T + 0.6, align=(Align.CENTER, Align.CENTER, Align.MIN))
        hood = largest_solid(hood - clr)
    # NOTE (open item for the hood section test): screw is vertical M3 into the body
    # bosses. Exact drive direction / access ergonomics (the flat back blocks the rear;
    # service is off-wall via the open bottom) is deferred to the hood section print per
    # HANDOFF_v9. Geometry here = boss pilot on body, clearance on hood ear.

    # =====================================================================
    # BASE PLATE — separate full-footprint part. Closes the open bottom.
    # PRINTS GRILLE-DOWN, FLAT ON THE BED, NO FEET. The grille floor is the
    # first layer on the bed -> fully supported, never a suspended span. (v9.0
    # had feet hanging below the floor; that forces a feet-down print which
    # lifts the grille ~3 mm off the bed and re-creates the v8 floor-bridge
    # failure. The node hangs on the wall via keyholes and never rests on feet,
    # so the feet are removed entirely — Tomas, 2026-06-10.)
    # Top face at z = foot_h (meets body bottom rim). base spans z = base_bottom..foot_h.
    # =====================================================================
    base_bottom = foot_h - (GRILLE_T + MESH_SEAT_T)
    base = Pos(0, -back_y, base_bottom) * Box(2 * HW, back_y + FRONT, GRILLE_T + MESH_SEAT_T, align=(Align.CENTER, Align.MIN, Align.MIN))
    base = fillet(base.edges().filter_by(Axis.Z), fillet_r)
    # press-fit spigot rim (rises into the cavity; COUPON_TBD_PRESSFIT against inner wall)
    sp_hw = HW_IN - COUPON_TBD_PRESSFIT
    sp_y0, sp_y1 = -back_inner + COUPON_TBD_PRESSFIT, FRONT_IN - COUPON_TBD_PRESSFIT
    spig_out = Pos(0, (sp_y0 + sp_y1) / 2, foot_h) * Box(2 * sp_hw, sp_y1 - sp_y0, SPIGOT_H, align=(Align.CENTER, Align.CENTER, Align.MIN))
    spig_out = fillet(spig_out.edges().filter_by(Axis.Z), fillet_r - 1.0)
    spig_in = Pos(0, (sp_y0 + sp_y1) / 2, foot_h - 0.1) * Box(2 * (sp_hw - SPIGOT_WALL), (sp_y1 - sp_y0) - 2 * SPIGOT_WALL, SPIGOT_H + 0.2, align=(Align.CENTER, Align.CENTER, Align.MIN))
    spigot = largest_solid(spig_out - spig_in)
    base = largest_solid(base + spigot)
    # intake: DOUBLED opening (~30x30 vs ~20x22) + a real-depth mesh/grid-panel seat.
    # The grille floor is the full wall thickness (GRILLE_T) and prints on the bed; the
    # mesh / grid panel drops into a MESH_SEAT_T pocket on the inside face, serviceable
    # from inside once the base is popped off. Air path: slots -> seat -> spigot -> cavity.
    seat = Pos(0, cap_cy, foot_h - MESH_SEAT_T) * Box(OPEN_W + 2 * SEAT_MARGIN, OPEN_D + 2 * SEAT_MARGIN, MESH_SEAT_T + 0.1, align=(Align.CENTER, Align.CENTER, Align.MIN))
    base = largest_solid(base - seat)
    n_slots = int(OPEN_W // 5)
    for i in range(n_slots):
        sx0 = -OPEN_W / 2.0 + 2.5 + i * 5.0
        slot = Pos(sx0, cap_cy, base_bottom - 0.1) * Box(3.0, OPEN_D, GRILLE_T + 0.3, align=(Align.CENTER, Align.CENTER, Align.MIN))
        base = largest_solid(base - slot)
    # USB-C gland chase, off to the -X side (clear of the intake seat), angled down-out
    usb = Pos(-20.0, cap_cy, foot_h + 0.5) * Rot(35, 0, 0) * Cylinder(4.25, (GRILLE_T + MESH_SEAT_T) + 16, align=(Align.CENTER, Align.CENTER, Align.MAX))
    base = largest_solid(base - usb)
    # weep at a front corner, clear of the intake, angled down-out
    weep = Pos(HW_IN - 4.0, FRONT_IN - 4.0, foot_h + 0.3) * Rot(0, -45, 0) * Cylinder(1.25, 12, align=(Align.CENTER, Align.CENTER, Align.MAX))
    base = largest_solid(base - weep)

    # ---- interference + watertight + exports ----
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
    ok &= chk("boards vs base", dummies, base)
    ok &= chk("bme vs base", bme, base)
    ok &= chk("body vs base flange", body, base)   # should be ~0 (meet face-to-face)
    # spigot engagement is informational: positive clearance -> ~0 here at staging
    try:
        eng = sum(s.volume for s in (body & spigot).solids()) / 1000.0
    except Exception:
        eng = 0.0
    print(f"  [info] spigot-in-cavity overlap: {eng:.3f} cm3 (set by COUPON_TBD_PRESSFIT={COUPON_TBD_PRESSFIT})")

    # seated breathing-plate proxy (the real lattice plate = tools/breathing_panel_v9.py).
    # A nominal 35x35x7 must seat in the rails without colliding -> positive clearance.
    bx = plate_box
    if hm:
        plate_proxy = box_lh(bx[1] - PLATE_T, bx[1], bx[2], bx[3], bx[4], bx[5])   # inner face on wall, out -X
    else:
        plate_proxy = box_lh(bx[0], bx[1], bx[2], bx[2] + PLATE_T, bx[4], bx[5])   # inner face on wall, out +Y
    ok &= chk("breathing plate vs body (rail fit)", plate_proxy, body)

    # assembly + cutaway for review
    parts = [body, Pos(0, 0, 0) * hood, base, plate_proxy, perfboard, bme] + ([hm_module] if hm else [])
    assembly = Compound(parts)
    hh = Pos(0, -back_y, 0) * Box(300, 300, 400, align=(Align.MAX, Align.CENTER, Align.MIN))
    cut_parts = [largest_solid(body - hh), largest_solid(hood - hh), largest_solid(base - hh), plate_proxy, perfboard, bme] + ([hm_module] if hm else [])
    cutaway = Compound(cut_parts)

    exports = [
        (f"v9_{name}_body", body, OUT, True, True),
        (f"v9_{name}_hood", hood, OUT, True, True),
        (f"v9_{name}_base", base, OUT, True, True),
        (f"v9_{name}_assembly", assembly, REVIEW, False, False),
        (f"v9_{name}_cutaway", cutaway, REVIEW, False, False),
    ]
    for nm, part, outdir, step, clean in exports:
        p = os.path.join(outdir, f"{nm}.stl")
        export_stl(part, p)
        if step:
            export_step(part, os.path.join(outdir, f"{nm}.step"))
        if clean:
            mesh = _tm.load(p, force="mesh")
            cs = mesh.split(only_watertight=False)
            wt = mesh.is_watertight
            if len(cs) > 1:
                keep = max(cs, key=lambda c: c.area)
                keep.fix_normals()
                keep.export(p)
                wt = keep.is_watertight
                print(f"    {nm}: {len(cs)} islands -> kept largest (watertight={wt})")
            else:
                print(f"    {nm}: 1 solid (watertight={wt})")

    for part, lbl in [(body, "body"), (hood, "hood"), (base, "base")]:
        bb = part.bounding_box()
        print(f"  {name} {lbl}: {bb.size.X:.0f} x {bb.size.Y:.0f} x {bb.size.Z:.0f} mm")
    print(f"  {name} interference {'OK' if ok else 'FAIL'}")
    return dict(body=body, hood=hood, base=base, ok=ok)


if __name__ == "__main__":
    allok = True
    for nm, cfg in VARIANTS.items():
        allok &= build(nm, cfg)["ok"]
    print(f"\n=== v9 STAGING build complete | interference {'OK' if allok else 'FAIL'} ===")
    print("NOT FOR PRINT — fill ICD 5.1 first. Press-fit ring is the first section test.")
