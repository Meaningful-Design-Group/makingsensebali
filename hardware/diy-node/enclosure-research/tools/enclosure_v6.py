#!/usr/bin/env python3
"""Making Sense Bali DIY node — v6 SHARED PLATFORM (Basic + Plus, one generator).

Research-grounded (../DESIGN_RESEARCH.md) and built to the outdoor-sensor-enclosure
skill. ONE parametric body, two variants that share the brain mount, the BME680
radiation-shield bay, the hood (drip-lip), the venting strategy and the bottom
bayonet cap:

  Basic = XIAO ESP32-S3 + BME680 on a 40×60 perfboard. Shallow body.
  Plus  = Basic + Grove HM3301. The body grows a FRONT bay for the vertical
          HM3301 with its own DOWN-facing duct; the BME680 shield moves to a
          SIDE bay so the particulate air path never crosses the T/RH air.

(The HM3301 sits alongside the perfboard, not stacked below it — stacking would
exceed the 140 mm height limit. Same height class for both, ~102–112 mm.)

Four fundamentals, both variants:
  • Self-heat/radiation — BME680 LOW in a down-louvered, foil-lined bay (front on
    Basic, side on Plus), XIAO HIGH so the chimney carries MCU heat up and away;
    firmware T-offset. (Research §3/§6.)
  • Airflow — chimney: cool in low past the BME680, warm out the high side louvers
    under the hood eave.
  • Water — no upward opening; down-facing louvers; hood + drip-lip curl; 2.5 mm
    weep; ePTFE membrane boss; not sealed airtight. (Research §9–14.)
  • Particulate (Plus) — HM3301 on a dedicated down-duct, intake at the front-
    bottom wall, can grille front, separated from the BME680 bay. (Research §7.)

Validated internals reused verbatim: perfboard standoffs, keyholes, HM3301 rails
+ 2 pegs, bottom bayonet cap (centred on the cavity). ALL FITS COUPON_TBD_*.
"""
import os
from build123d import *  # noqa: F403

OUT = os.path.join(os.path.dirname(__file__), "..", "v6")
os.makedirs(OUT, exist_ok=True)
REVIEW = os.path.join(OUT, "review")
os.makedirs(REVIEW, exist_ok=True)

COUPON_TBD_SLIDE = 0.30
COUPON_TBD_PRESS = -0.05
COUPON_TBD_PILOT_M2 = 1.75

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
HW = 24.0
HW_IN = 21.5
fillet_r = 3.0
floor_z = 12.0
perf_back_gap = 4.0
perf_z0, perf_cx = 18.0, 0.0
key_x, key_z = 16.0, 60.0
bme_z = 26.0
eave = 4.0
drip = 3.0
roof_h = 16.0
n_lugs = 3
hm_z0, hm_carrier_y = 13.0, 13.0

VARIANTS = {
    "basic": dict(FRONT=24.0, FRONT_IN=21.5, body_top=86.0, hm=False, cap_r=18.0),
    "plus":  dict(FRONT=34.5, FRONT_IN=32.0, body_top=96.0, hm=True,  cap_r=20.0),
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


def build(name, cfg):
    FRONT, FRONT_IN, body_top = cfg["FRONT"], cfg["FRONT_IN"], cfg["body_top"]
    hm, cap_r = cfg["hm"], cfg["cap_r"]
    cap_window_r = cap_r - 7.0
    cap_cy = (FRONT_IN - back_inner) / 2

    # dummies
    perf_y0 = -back_inner + perf_back_gap
    perfboard = Pos(perf_cx, perf_y0, perf_z0) * Box(perf_w, perf_t, perf_h, align=(Align.CENTER, Align.MIN, Align.MIN))
    perf_env = Pos(perf_cx, perf_y0 + perf_t, perf_z0) * Box(perf_w, 11.0, perf_h, align=(Align.CENTER, Align.MIN, Align.MIN))
    dummies = perfboard + perf_env
    if hm:
        # BME680 on the perfboard low-LEFT; HM3301 takes the front
        bme = Pos(-12.0, perf_y0 + perf_t, bme_z) * Box(bme_w, bme_t + 4, bme_h, align=(Align.CENTER, Align.MIN, Align.CENTER))
        hm_carrier = Pos(0, hm_carrier_y, hm_z0) * Box(hm_w, hm_t, hm_h, align=(Align.CENTER, Align.MIN, Align.MIN))
        hm_can = Pos(0, hm_carrier_y + hm_t, hm_z0 + (hm_h - can_h) / 2) * Box(can_w, can_d, can_h, align=(Align.CENTER, Align.MIN, Align.MIN))
        hm_module = hm_carrier + hm_can
        can_face_z0 = hm_z0 + (hm_h - can_h) / 2
    else:
        bme = Pos(0, perf_y0 + perf_t, bme_z) * Box(bme_w, bme_t + 4, bme_h, align=(Align.CENTER, Align.MIN, Align.CENTER))
        hm_module = None

    # body box
    body = Pos(0, -back_y, 0) * Box(2 * HW, back_y + FRONT, body_top, align=(Align.CENTER, Align.MIN, Align.MIN))
    body = fillet(body.edges().filter_by(Axis.Z), fillet_r)
    cavity = Pos(0, -back_inner, floor_z - wall) * Box(2 * HW_IN, back_inner + FRONT_IN, body_top + 10, align=(Align.CENTER, Align.MIN, Align.MIN))
    cavity = fillet(cavity.edges().filter_by(Axis.Z), fillet_r - 1.0)
    body = largest_solid(body - cavity)

    # floor + cap opening
    floor_plate = Pos(0, -back_y, floor_z - wall) * Box(2 * HW, back_y + FRONT, wall, align=(Align.CENTER, Align.MIN, Align.MIN))
    floor_plate = fillet(floor_plate.edges().filter_by(Axis.Z), fillet_r)
    floor_plate = largest_solid(floor_plate - Pos(0, cap_cy, 0) * Cylinder(cap_r - 3.0, 100, align=(Align.CENTER, Align.CENTER, Align.CENTER)))
    body = body + floor_plate

    # bayonet cap seat
    cap_seat = Pos(0, cap_cy, floor_z - wall - 6.0) * Cylinder(cap_r + wall + COUPON_TBD_SLIDE, 6.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
    cap_seat = largest_solid(cap_seat - Pos(0, cap_cy, floor_z - wall - 6.1) * Cylinder(cap_r + COUPON_TBD_SLIDE, 6.2, align=(Align.CENTER, Align.CENTER, Align.MIN)))
    body = body + cap_seat

    # perfboard standoffs
    so_dx, so_dz = 16.2, 26.2
    perf_cz = perf_z0 + perf_h / 2
    for sx in (-1, 1):
        for sz in (-1, 1):
            sx_, sz_ = sx * so_dx, perf_cz + sz * so_dz
            post = Pos(sx_, -back_inner, sz_) * Rot(-90, 0, 0) * Cylinder(3.0, perf_back_gap, align=(Align.CENTER, Align.CENTER, Align.MIN))
            pilot = Pos(sx_, -back_inner - 0.1, sz_) * Rot(-90, 0, 0) * Cylinder(COUPON_TBD_PILOT_M2 / 2, perf_back_gap + 4, align=(Align.CENTER, Align.CENTER, Align.MIN))
            body = largest_solid(body + post - pilot)

    # keyholes
    for sx in (-1, 1):
        kh = Pos(sx * key_x, 0, key_z) * Rot(-90, 0, 0) * Cylinder(4.0, 50, align=(Align.CENTER, Align.CENTER, Align.CENTER))
        ks = Pos(sx * key_x, -back_y - 2, key_z) * Box(4.0, 10, 10, align=(Align.CENTER, Align.MIN, Align.MIN))
        body = largest_solid(largest_solid(body - kh) - ks)

    if hm:
        # HM3301 rails + pegs
        rail_gap = hm_t + COUPON_TBD_SLIDE
        for sx in (-1, 1):
            post = Pos(sx * (hm_w / 2 + 2.0), hm_carrier_y + rail_gap / 2, hm_z0 - 1) * Box(4.0, rail_gap + 5.0, hm_h + 2.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
            slot = Pos(sx * (hm_w / 2 - 1.0), hm_carrier_y - 0.05, hm_z0 - 1.5) * Box(6.0, rail_gap, hm_h + 4.0, align=(Align.CENTER, Align.MIN, Align.MIN))
            body = largest_solid(body + post - slot)
        for sx in (-1, 1):
            peg = Pos(sx * 16.0, hm_carrier_y - 0.02, hm_z0 + 4.0) * Rot(-90, 0, 0) * Cylinder((hm_hole_d + COUPON_TBD_PRESS) / 2, hm_t + 1.2, align=(Align.CENTER, Align.CENTER, Align.MIN))
            body = body + peg
        # HM3301 can grille on the front, at the can face
        for gz in (can_face_z0 + 10, can_face_z0 + 24):
            grille = Pos(0, FRONT - 1.0, gz) * Box(24.0, wall + 6.0, 2.4, align=(Align.CENTER, Align.MAX, Align.CENTER))
            body = largest_solid(body - grille)
        # dedicated DOWN-facing PM intake duct at the front-bottom
        for lz in (16.0, 22.0):
            duct = Pos(0, FRONT - 1.0, lz) * Rot(40, 0, 0) * Box(26.0, wall + 9.0, 2.8, align=(Align.CENTER, Align.CENTER, Align.CENTER))
            body = largest_solid(body - duct)
        # BME680 shield bay: down-louvers on the lower-LEFT side wall (away from HM3301)
        for lz in (20.0, 27.0, 34.0):
            lv = Pos(-(HW - 1.0), -2.0, lz) * Rot(0, -40, 0) * Box(wall + 9.0, 16.0, 2.6, align=(Align.CENTER, Align.CENTER, Align.CENTER))
            body = largest_solid(body - lv)
    else:
        # BME680 shield bay: down-louvers in the lower FRONT wall
        for lz in (20.0, 27.0, 34.0):
            lv = Pos(0, FRONT - 1.0, lz) * Rot(40, 0, 0) * Box(28.0, wall + 9.0, 2.6, align=(Align.CENTER, Align.CENTER, Align.CENTER))
            body = largest_solid(body - lv)

    # brain exhaust louvers high on the side walls (down-facing) under the hood
    ex_side = 1 if hm else -1   # use the side opposite the BME680 bay on Plus
    for sgn in ((1,) if hm else (-1, 1)):
        for lz in (body_top - 14, body_top - 7):
            lv = Pos(sgn * (HW - 1.0), 6.0, lz) * Rot(0, sgn * 40, 0) * Box(wall + 9.0, 16.0, 2.6, align=(Align.CENTER, Align.CENTER, Align.CENTER))
            body = largest_solid(body - lv)

    # USB-C gland chase, bottom, angled down
    usb = Pos(-10.0, cap_cy, floor_z - wall + 1.0) * Rot(35, 0, 0) * Cylinder(4.25, wall + 16, align=(Align.CENTER, Align.CENTER, Align.MIN))
    body = largest_solid(body - usb)

    # weep hole 2.5 mm at the low point, angled down-out
    weep = Pos(0, FRONT_IN - 2.0, floor_z + 0.5) * Rot(55, 0, 0) * Cylinder(1.25, 14, align=(Align.CENTER, Align.CENTER, Align.MIN))
    body = largest_solid(body - weep)

    # ePTFE membrane vent boss on the upper +X side wall (leeward)
    boss = Pos(HW - 1.0, -2.0, body_top - 20) * Rot(0, 90, 0) * Cylinder(6.0, 2.5, align=(Align.CENTER, Align.CENTER, Align.MIN))
    body = body + boss
    vent = Pos(HW - 0.5, -2.0, body_top - 20) * Rot(0, 90, 0) * Cylinder(3.2, wall + 4, align=(Align.CENTER, Align.CENTER, Align.MIN))
    body = largest_solid(body - vent)

    # hood with drip-lip curl
    zb = body_top
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
    hcut = Pos(0, -back_y, 0) * Box(500, 400, 500, align=(Align.CENTER, Align.MAX, Align.CENTER))
    roof = largest_solid(roof - hcut)
    body = body + roof

    # cap (bayonet, down mesh intake)
    cap = Cylinder(cap_r, 3.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
    cap = cap + Cylinder(cap_r + 4.0, 1.6, align=(Align.CENTER, Align.CENTER, Align.MIN))
    stem = Pos(0, 0, 3.0) * Cylinder(cap_r, 7.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
    stem = largest_solid(stem - Pos(0, 0, 2.9) * Cylinder(cap_r - wall, 7.2, align=(Align.CENTER, Align.CENTER, Align.MIN)))
    cap = cap + stem
    for k in range(n_lugs):
        lug = Pos(0, 0, 7.6) * Rot(0, 0, k * 120) * (Pos(cap_r + 1.2, 0, 0) * Box(2.4, 8.0, 2.4, align=(Align.CENTER, Align.CENTER, Align.MIN)))
        cap = cap + lug
    cap = largest_solid(cap - Cylinder(cap_window_r, 30, align=(Align.CENTER, Align.CENTER, Align.CENTER)))
    seat = Pos(0, 0, 3.0) * Cylinder(cap_window_r + 3.0, 1.2, align=(Align.CENTER, Align.CENTER, Align.MIN))
    seat = largest_solid(seat - Cylinder(cap_window_r - 1.5, 30, align=(Align.CENTER, Align.CENTER, Align.CENTER)))
    cap = cap + seat
    for k in range(n_lugs):
        entry = Pos(0, cap_cy, 0) * Rot(0, 0, k * 120) * (Pos(cap_r + 1.2, 0, floor_z - wall - 6.2) * Box(3.4, 9.0, 6.5, align=(Align.CENTER, Align.CENTER, Align.MIN)))
        turn = Pos(0, cap_cy, 0) * Rot(0, 0, k * 120) * (Pos(cap_r + 1.2, 0, floor_z - wall - 3.4) * Box(3.4, 22.0, 3.2, align=(Align.CENTER, Align.MIN, Align.MIN)))
        body = largest_solid(largest_solid(body - entry) - turn)

    # interference
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

    # exports
    cap_placed = Pos(0, cap_cy, floor_z - wall - 6.0 - 1.6) * cap
    parts = [body, cap_placed, perfboard, bme] + ([hm_module] if hm else [])
    assembly = Compound(parts)
    hh = Pos(0, -back_y, 0) * Box(300, 300, 400, align=(Align.MAX, Align.CENTER, Align.MIN))
    cut_parts = [largest_solid(body - hh), perfboard, bme] + ([hm_module] if hm else [])
    cutaway = Compound(cut_parts)
    for nm, part, outdir, step in [
            (f"v6_{name}_body", body, OUT, True), (f"v6_{name}_cap", cap, OUT, True),
            (f"v6_{name}_assembly", assembly, REVIEW, False), (f"v6_{name}_cutaway", cutaway, REVIEW, False)]:
        export_stl(part, os.path.join(outdir, f"{nm}.stl"))
        if step:
            export_step(part, os.path.join(outdir, f"{nm}.step"))
    bb = body.bounding_box()
    print(f"  {name} body: {bb.size.X:.0f} x {bb.size.Y:.0f} x {bb.size.Z:.0f} mm")


for nm, cfg in VARIANTS.items():
    build(nm, cfg)
