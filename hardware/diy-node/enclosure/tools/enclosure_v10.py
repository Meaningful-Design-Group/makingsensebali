#!/usr/bin/env python3
"""Making Sense Bali DIY node — v10 ORGANIC SHELL + BASE BREATHING (Basic + Plus).

Built on v9's verified function, with the changes Tomas called on 2026-06-10:

  1. BREATHING MOVES TO THE BASE. The side slide-in window is gone. The whole
     bottom is now a large drop-in GYROID breathing panel (tools/breathing_panel_v10.py),
     much bigger than the old 30x30 side plate. Air enters low through the base,
     flows up past the BME680 (low, fresh air) and the XIAO (high, sheds heat),
     and leaves through the high exhaust louvers — a clean base->top chimney.

  2. HM3301 BAY CORRECTED to the real ~40x40x16 envelope. The v8/v9 ICD claimed an
     80x40 carrier sourced only from the schematic (no mechanical drawing); the Grove
     HM3301 is a ~40x40 board. CONFIRM by caliper on a physical unit before print.

  3. ORGANIC SHELL over the KEPT chassis. The body is a softly-lofted, front-leaning
     pod (flat back retained for wall-mount keyholes, soft corners, gentle bulge),
     wrapping the validated internals VERBATIM: perfboard standoffs, keyholes, HM
     rails/pegs, exhaust louvers, ePTFE boss, separate hood (2x M3), press-fit base.

Sensor set (Tomas, current build): XIAO ESP32-S3 + BME680 (+ HM3301 on Plus). No SEN54.

*** STAGING BUILD — NOT FOR PRINT. *** Every fit is COUPON_TBD_*; ICD 5.1 still TBD.
HM3301 envelope is caliper-confirm. Organic form = first pass, to react to.
"""
import os
from build123d import *  # noqa: F403
import trimesh as _tm

OUT = os.path.join(os.path.dirname(__file__), "..", "v10")
os.makedirs(OUT, exist_ok=True)
REVIEW = os.path.join(OUT, "review")
os.makedirs(REVIEW, exist_ok=True)

# ---- COUPON_TBD_* : placeholder fits, replace from ICD 5.1 before any print ----
COUPON_TBD_SLIDE = 0.30
COUPON_TBD_PRESS = -0.05
COUPON_TBD_PILOT_M2 = 1.75
COUPON_TBD_PRESSFIT = 0.15
COUPON_TBD_M3_PILOT = 2.5
COUPON_TBD_PANELSEAT = 0.30        # drop-in base panel seat clearance
M3_CLR = 3.4

# ---- component dims (ICD 2, HM3301 CORRECTED to ~40x40, caliper-confirm) ----
perf_w, perf_h, perf_t = 40.0, 60.0, 1.6
bme_w, bme_h, bme_t = 16.0, 12.5, 3.0
xiao_w, xiao_h, xiao_t = 21.0, 17.8, 13.0     # on female headers
hm_w, hm_h, hm_t = 40.0, 40.0, 1.6            # CORRECTED: ~40x40 Grove board (was 80x40)
can_w, can_d, can_h = 30.0, 13.0, 24.0        # metal can on the board (envelope; confirm)
hm_hole_d = 3.2

# ---- common frame ----
wall = 2.5
back_y = 16.0
back_inner = back_y - wall
HW, HW_IN = 24.0, 21.5
fillet_r = 3.0
foot_h = 3.0
perf_back_gap = 4.0
perf_z0 = 18.0
key_x, key_z = 14.0, 60.0
bme_z = 26.0                                   # BME680 LOW (in the base intake stream)
hm_z0, hm_carrier_y = 14.0, 13.0

# ---- v10 base breathing panel (the bottom IS the breathing element, big) ----
BASE_T = 5.0                                   # base-frame thickness
SEAT_D = 2.5                                   # panel-seat pocket depth (shoulder = BASE_T-SEAT_D)
SEAT_MARGIN = 3.0                              # flange shoulder around the breathing opening
SPIGOT_H = 6.0
SPIGOT_WALL = 2.0

# ---- hood screw bosses ----
BOSS_R, BOSS_H, BOSS_X, HOOD_EAR_T = 4.0, 6.0, 16.0, 3.0

# ---- organic shell profile (front y leans back with height; flat back kept) ----
BACK_OVER = 6.0                                # section back overhang, sliced flat at -back_y
R_OUT, R_IN = 9.0, 7.0                         # soft corner radii (organic)

VARIANTS = {
    "basic": dict(FRONT=24.0, FRONT_IN=21.5, body_top=84.0, hm=False),
    "plus":  dict(FRONT=36.0, FRONT_IN=33.5, body_top=94.0, hm=True),
}


def largest_solid(x):
    try:
        solids = list(x.solids())
    except (AttributeError, TypeError):
        solids = [s for item in x for s in item.solids()]
    if not solids:
        raise ValueError("boolean produced no solids")
    return max(solids, key=lambda s: s.volume)


def box_lh(xl, xh, yl, yh, zl, zh):
    return Pos((xl + xh) / 2, (yl + yh) / 2, (zl + zh) / 2) * Box(xh - xl, yh - yl, zh - zl)


def sect(z, yf, hw, yb, r):
    """A rounded-rect loft section: width 2*hw, from yb (back, overhung) to yf (front)."""
    w, d = 2 * hw, yf - yb
    return Pos(0, (yb + yf) / 2, z) * RectangleRounded(w, d, r)


def build(name, cfg):
    FRONT, FRONT_IN, body_top = cfg["FRONT"], cfg["FRONT_IN"], cfg["body_top"]
    hm = cfg["hm"]
    H = body_top
    cap_cy = (FRONT_IN - back_inner) / 2

    # ---- dummy components (verified dims) ----
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
    # ORGANIC BODY — lofted pod, front leans back with height, flat back kept.
    # Width (x) is constant so the perfboard always fits; the organic read comes
    # from the front lean, a low bulge, and soft corners. Open top + bottom.
    # =====================================================================
    yb_o = -back_y - BACK_OVER
    outer = loft([
        sect(foot_h,           FRONT,      HW, yb_o, R_OUT),
        sect(foot_h + 0.30 * H, FRONT + 2.0, HW, yb_o, R_OUT),
        sect(foot_h + 0.62 * H, FRONT - 3.0, HW, yb_o, R_OUT),
        sect(foot_h + H,        FRONT - 9.0, HW, yb_o, R_OUT),
    ])
    outer = largest_solid(outer - Pos(0, -back_y, foot_h + H / 2) * Box(400, 400, H + 200, align=(Align.CENTER, Align.MAX, Align.CENTER)))

    yb_i = -back_inner - BACK_OVER
    cavity = loft([
        sect(foot_h - 3,        FRONT - wall,          HW_IN, yb_i, R_IN),
        sect(foot_h + 0.30 * H, FRONT + 2.0 - wall,    HW_IN, yb_i, R_IN),
        sect(foot_h + 0.62 * H, FRONT - 3.0 - wall,    HW_IN, yb_i, R_IN),
        sect(foot_h + H + 3,    FRONT - 9.0 - wall,    HW_IN, yb_i, R_IN),
    ])
    cavity = largest_solid(cavity - Pos(0, -back_inner, foot_h + H / 2) * Box(400, 400, H + 220, align=(Align.CENTER, Align.MAX, Align.CENTER)))
    body = largest_solid(outer - cavity)

    # perfboard standoffs (verbatim) — cantilevered off the flat back wall
    so_dx, so_dz = 16.2, 26.2
    perf_cz = perf_z0 + perf_h / 2 + foot_h
    for sx in (-1, 1):
        for sz in (-1, 1):
            post = Pos(sx * so_dx, -back_inner, perf_cz + sz * so_dz) * Rot(-90, 0, 0) * Cylinder(3.0, perf_back_gap, align=(Align.CENTER, Align.CENTER, Align.MIN))
            pilot = Pos(sx * so_dx, -back_inner - 0.1, perf_cz + sz * so_dz) * Rot(-90, 0, 0) * Cylinder(COUPON_TBD_PILOT_M2 / 2, perf_back_gap + 4, align=(Align.CENTER, Align.CENTER, Align.MIN))
            body = largest_solid(body + post - pilot)

    # keyholes on the flat back
    for sx in (-1, 1):
        kh = Pos(sx * key_x, 0, key_z + foot_h) * Rot(-90, 0, 0) * Cylinder(4.0, 50, align=(Align.CENTER, Align.CENTER, Align.CENTER))
        ks = Pos(sx * key_x, -back_y - 2, key_z + foot_h) * Box(4.0, 10, 10, align=(Align.CENTER, Align.MIN, Align.MIN))
        body = largest_solid(largest_solid(body - kh) - ks)

    # ---- Plus PM: HM3301 (40x40) vertical in front rails + pegs + can grille + down duct ----
    if hm:
        rail_gap = hm_t + COUPON_TBD_SLIDE
        for sx in (-1, 1):
            post = Pos(sx * (hm_w / 2 + 2.0), hm_carrier_y + rail_gap / 2, hm_z0 - 1 + foot_h) * Box(4.0, rail_gap + 5.0, hm_h + 2.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
            slot = Pos(sx * (hm_w / 2 - 1.0), hm_carrier_y - 0.05, hm_z0 - 1.5 + foot_h) * Box(6.0, rail_gap, hm_h + 4.0, align=(Align.CENTER, Align.MIN, Align.MIN))
            body = largest_solid(body + post - slot)
        for sx in (-1, 1):
            peg = Pos(sx * 16.0, hm_carrier_y - 0.02, hm_z0 + 4.0 + foot_h) * Rot(-90, 0, 0) * Cylinder((hm_hole_d + COUPON_TBD_PRESS) / 2, hm_t + 1.2, align=(Align.CENTER, Align.CENTER, Align.MIN))
            body = body + peg
        for gz in (can_face_z0 + 6, can_face_z0 + 16):
            grille = Pos(0, FRONT - 1.0, gz) * Box(22.0, wall + 6.0, 2.4, align=(Align.CENTER, Align.MAX, Align.CENTER))
            body = largest_solid(body - grille)

    # ---- high exhaust louvers (down-facing, side walls) ----
    ex_signs = (1,) if hm else (-1, 1)
    for sgn in ex_signs:
        for lz in (body_top - 14 + foot_h, body_top - 7 + foot_h):
            lv = Pos(sgn * (HW - 1.0), 4.0, lz) * Rot(0, sgn * 40, 0) * Box(wall + 9.0, 16.0, 2.6, align=(Align.CENTER, Align.CENTER, Align.CENTER))
            body = largest_solid(body - lv)

    # ePTFE membrane vent boss, upper +X side (leeward)
    boss = Pos(HW - 1.0, -2.0, body_top - 20 + foot_h) * Rot(0, 90, 0) * Cylinder(6.0, 2.5, align=(Align.CENTER, Align.CENTER, Align.MIN))
    body = body + boss
    vent = Pos(HW - 0.5, -2.0, body_top - 20 + foot_h) * Rot(0, 90, 0) * Cylinder(3.2, wall + 4, align=(Align.CENTER, Align.CENTER, Align.MIN))
    body = largest_solid(body - vent)

    # ---- 2x M3 hood bosses on the back of the top rim (above the perfboard) ----
    zb = body_top + foot_h
    boss_y = -back_inner + 2.0
    for sx in (-1, 1):
        body = body + Pos(sx * BOSS_X, boss_y, zb - BOSS_H) * Cylinder(BOSS_R, BOSS_H, align=(Align.CENTER, Align.CENTER, Align.MIN))
    body = largest_solid(body)
    for sx in (-1, 1):
        body = largest_solid(body - Pos(sx * BOSS_X, boss_y, zb - BOSS_H) * Cylinder(COUPON_TBD_M3_PILOT / 2, BOSS_H + 0.3, align=(Align.CENTER, Align.CENTER, Align.MIN)))

    # =====================================================================
    # HOOD — organic dome matching the top rim outline, separate (2x M3).
    # =====================================================================
    yf_top = FRONT - 9.0
    hood = loft([
        sect(zb,            yf_top,       HW, -back_y - BACK_OVER, R_OUT),
        sect(zb + 4,        yf_top + 2,   HW + 2, -back_y - BACK_OVER, R_OUT),
        Pos(0, (yf_top - back_y) / 2, zb + 15) * RectangleRounded(16, 12, 5),
    ])
    hood = largest_solid(hood - Pos(0, -back_y, zb + 8) * Box(400, 400, 60, align=(Align.CENTER, Align.MAX, Align.CENTER)))
    hood_in = loft([
        sect(zb - 0.1,      yf_top - wall,   HW_IN, -back_inner - BACK_OVER, R_IN),
        sect(zb + 4,        yf_top + 2 - wall, HW_IN, -back_inner - BACK_OVER, R_IN),
        Pos(0, (yf_top - back_y) / 2, zb + 15 - wall) * RectangleRounded(9, 6, 2),
    ])
    hood_in = largest_solid(hood_in - Pos(0, -back_inner, zb + 8) * Box(400, 400, 60, align=(Align.CENTER, Align.MAX, Align.CENTER)))
    hood = largest_solid(hood - hood_in)
    for sx in (-1, 1):
        ear = Pos(sx * BOSS_X, -back_inner + 2.0, zb) * Box(2 * BOSS_R, 8.0, HOOD_EAR_T, align=(Align.CENTER, Align.CENTER, Align.MIN))
        hood = hood + ear
    hood = largest_solid(hood)
    for sx in (-1, 1):
        hood = largest_solid(hood - Pos(sx * BOSS_X, boss_y, zb - 0.2) * Cylinder(M3_CLR / 2, HOOD_EAR_T + 0.6, align=(Align.CENTER, Align.CENTER, Align.MIN)))

    # =====================================================================
    # BASE FRAME — the bottom; prints flat, no feet. A big central breathing
    # opening with a seat pocket for the drop-in gyroid panel, a press-fit spigot
    # up into the cavity, the USB-C chase and the weep. Air: base panel -> cavity.
    # =====================================================================
    base_bottom = foot_h - BASE_T
    # footprint matches the body's base outline
    base = sect(0, FRONT, HW, yb_o, R_OUT)
    base = extrude(base, amount=BASE_T)               # z 0..BASE_T
    base = largest_solid(base - Pos(0, -back_y, BASE_T / 2) * Box(400, 400, BASE_T + 4, align=(Align.CENTER, Align.MAX, Align.CENTER)))
    base = Pos(0, 0, base_bottom) * base               # shift so top sits at foot_h
    base = largest_solid(base)
    # press-fit spigot up into the cavity
    sp_hw = HW_IN - COUPON_TBD_PRESSFIT
    sp_y0, sp_y1 = -back_inner + COUPON_TBD_PRESSFIT, FRONT_IN - COUPON_TBD_PRESSFIT
    spig_out = Pos(0, (sp_y0 + sp_y1) / 2, foot_h) * Box(2 * sp_hw, sp_y1 - sp_y0, SPIGOT_H, align=(Align.CENTER, Align.CENTER, Align.MIN))
    spig_out = fillet(spig_out.edges().filter_by(Axis.Z), fillet_r - 1.0)
    spig_in = Pos(0, (sp_y0 + sp_y1) / 2, foot_h - 0.1) * Box(2 * (sp_hw - SPIGOT_WALL), (sp_y1 - sp_y0) - 2 * SPIGOT_WALL, SPIGOT_H + 0.2, align=(Align.CENTER, Align.CENTER, Align.MIN))
    spigot = largest_solid(spig_out - spig_in)
    base = largest_solid(base + spigot)
    # big breathing opening + seat pocket (panel drops in from the cavity side)
    open_w = 2 * HW_IN - 8.0
    open_d = (back_inner + FRONT_IN) - 10.0
    open_cy = cap_cy
    base = largest_solid(base - box_lh(-open_w / 2, open_w / 2, open_cy - open_d / 2, open_cy + open_d / 2, base_bottom - 1, foot_h + 1))
    fl_w, fl_d = open_w + 2 * SEAT_MARGIN, open_d + 2 * SEAT_MARGIN
    base = largest_solid(base - box_lh(-fl_w / 2, fl_w / 2, open_cy - fl_d / 2, open_cy + fl_d / 2, foot_h - SEAT_D, foot_h + 1))
    panel_box = (-fl_w / 2, fl_w / 2, open_cy - fl_d / 2, open_cy + fl_d / 2, foot_h - SEAT_D, foot_h)
    # USB-C chase + weep in the solid border (off the opening)
    usb = Pos(-(open_w / 2 + 6), open_cy, foot_h + 0.5) * Rot(35, 0, 0) * Cylinder(4.25, BASE_T + 16, align=(Align.CENTER, Align.CENTER, Align.MAX))
    base = largest_solid(base - usb)
    weep = Pos(HW - 5, FRONT - 6, foot_h + 0.3) * Rot(0, -45, 0) * Cylinder(1.25, 12, align=(Align.CENTER, Align.CENTER, Align.MAX))
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
    # base breathing panel proxy (real lattice = tools/breathing_panel_v10.py)
    pb = panel_box
    panel_proxy = box_lh(pb[0], pb[1], pb[2], pb[3], pb[4], pb[5])
    ok &= chk("base panel vs base (seat fit)", panel_proxy, base)

    parts = [body, hood, base, panel_proxy, perfboard, bme] + ([hm_module] if hm else [])
    assembly = Compound(parts)
    hh = Pos(0, -back_y, 0) * Box(300, 300, 400, align=(Align.MAX, Align.CENTER, Align.MIN))
    cut_parts = [largest_solid(body - hh), largest_solid(hood - hh), largest_solid(base - hh), perfboard, bme] + ([hm_module] if hm else [])
    cutaway = Compound(cut_parts)

    exports = [
        (f"v10_{name}_body", body, OUT, True, True),
        (f"v10_{name}_hood", hood, OUT, True, True),
        (f"v10_{name}_base", base, OUT, True, True),
        (f"v10_{name}_assembly", assembly, REVIEW, False, False),
        (f"v10_{name}_cutaway", cutaway, REVIEW, False, False),
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
    print(f"  {name} breathing opening: {open_w:.0f} x {open_d:.0f} mm | interference {'OK' if ok else 'FAIL'}")
    return dict(ok=ok, open_w=open_w, open_d=open_d)


if __name__ == "__main__":
    allok = True
    for nm, cfg in VARIANTS.items():
        allok &= build(nm, cfg)["ok"]
    print(f"\n=== v10 STAGING build complete | interference {'OK' if allok else 'FAIL'} ===")
    print("NOT FOR PRINT — fill ICD 5.1; confirm HM3301 envelope by caliper; organic form is a first pass.")
