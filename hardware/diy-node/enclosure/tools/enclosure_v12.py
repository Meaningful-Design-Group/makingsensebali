#!/usr/bin/env python3
"""Making Sense Bali DIY node — v12 MODULAR STACKING SYSTEM.

A tower of interchangeable tier-modules on one standard interface (Tomas, 2026-06-11):

  * Common footprint MW x MD, flat back + keyholes (the stack lies flush on a wall at
    any height).
  * STANDARD PRESS-FIT KEYED RIM: each stacking module has a bottom SPIGOT that press-fits
    into the open-cavity SOCKET of the module below (COUPON_TBD_STACK). The cavity is open
    top-to-bottom, so air rises and the I2C+power cable runs up the centre. Rectangular
    section + flat back key the orientation.
  * Modules are clean GYROID-window boxes; only the CROWN carries the meru eaves/finial.

Parts:
  - BASIC  : XIAO + BME680 (BME low / XIAO high). Bottom = base intake grille. Indoor core.
  - PLUS   : HM3301 module (Eagle-resolved geometry, ICD 1.12) + SIDEWAYS PM apertures at
             the can vent zone. Retention = bottom pocket + back ribs + top skewer bar
             (v12_hm_bar.stl) — the board has NO mounting holes (Eagle file 2026-06-11).
  - CROWN  : faceted 3-tier meru, generous eaves, bottom spigot. Outdoor top.
  - CAP    : low gyroid-vented top, bottom spigot. Indoor top.

Variants: indoor Basic (Basic+cap), outdoor Basic (Basic+crown),
          indoor Plus (Basic+Plus+cap), outdoor Plus (Basic+Plus+crown).

*** STAGING — NOT FOR PRINT until the press-fit rim SECTION PRINT validates §5.1. ***
ICD §5.1 is INFERRED (1.12-DRAFT, Tomas waived coupons, ±0.1): the section print
(tools/fit_section_v12.py) is the de-facto coupon and gates full modules.
"""
import os
import math
import numpy as np
from build123d import *  # noqa: F403
import trimesh as _tm
from skimage import measure
from scipy import ndimage

OUT = os.path.join(os.path.dirname(__file__), "..", "v12")
os.makedirs(OUT, exist_ok=True)
REVIEW = os.path.join(OUT, "review")
os.makedirs(REVIEW, exist_ok=True)

COUPON_TBD_STACK = 0.15       # spigot/socket press fit — INFERRED (ICD §5.1, 2026-06-11); validate via rim section print
COUPON_TBD_PILOT_M2 = 1.75    # M2 self-tap pilot — INFERRED, standard value
COUPON_TBD_SLIDE = 0.30       # HM rail slide — INFERRED

# ---- common module frame ----
wall = 2.5
MW, MD = 46.0, 26.0
HW_IN = MW / 2 - wall          # 20.5
yin0, yin1 = wall, MD - wall   # 2.5 .. 23.5
fillet_r = 3.0
IFACE_H = 7.0                  # spigot engagement depth
IFACE_WALL = 2.0
GRILLE_T = 2.5
key_x = 14.0
WIN_INSET = 5.0               # gyroid window frame margin
SEAT_D = 1.8                  # window panel seat depth
# cap gyroid top (drop-in panel, breathing-plate method)
CAP_TOP_T = 4.0
CAP_OPEN_W, CAP_OPEN_D = 33.0, 13.0
CAP_SEAT_MARGIN = 3.0
CAP_SEAT_D = 2.5

# heights
BH = 58.0                      # Basic
PH = 96.0                      # Plus (board 80 to z 88 + 1 clearance + 7 socket zone; was 92:
                               # the board top poked into the crown-spigot zone)
CAP_H = 22.0

# components (ICD 1.12; HM3301 module resolved from Seeed Eagle .brd + datasheet V2.1)
xiao_w, xiao_h, xiao_t = 21.0, 17.8, 13.0
bme_w, bme_h, bme_t = 16.0, 12.5, 3.0
hm_w, hm_h, hm_t = 40.0, 80.0, 1.6   # carrier board exactly 80x40 (Eagle outline)
can_w, can_d, can_h = 38.0, 15.0, 40.0   # can 40(L)x38(W)x15(H); board-z 14.6..54.6, Grove end down
# NO Ø3.2 mounting holes exist on the carrier (Eagle file 2026-06-11) — no pegs anywhere.


def largest_solid(x):
    try:
        solids = list(x.solids())
    except (AttributeError, TypeError):
        solids = [s for item in x for s in item.solids()]
    if not solids:
        raise ValueError("no solids")
    return max(solids, key=lambda s: s.volume)


def box_lh(xl, xh, yl, yh, zl, zh):
    return Pos((xl + xh) / 2, (yl + yh) / 2, (zl + zh) / 2) * Box(xh - xl, yh - yl, zh - zl)


def gyroid_mesh(open_w, open_d, flange_w, flange_d, depth, period=8.0, target_open=0.48, res=0.28):
    """Sheet-gyroid lattice + solid border, as a watertight trimesh centred at the origin.
    The solid border overlaps the host frame so a boolean union fuses them into ONE part."""
    pad = 2.0
    xs = np.arange(-flange_w / 2 - pad, flange_w / 2 + pad, res)
    ys = np.arange(-flange_d / 2 - pad, flange_d / 2 + pad, res)
    zs = np.arange(-depth / 2 - pad, depth / 2 + pad, res)
    X, Y, Z = np.meshgrid(xs, ys, zs, indexing="ij")
    k = 2 * np.pi / period
    g = np.sin(k * X) * np.cos(k * Y) + np.sin(k * Y) * np.cos(k * Z) + np.sin(k * Z) * np.cos(k * X)

    def rr(w, h, r):
        qx = np.abs(X) - (w / 2 - r); qy = np.abs(Y) - (h / 2 - r)
        return np.sqrt(np.maximum(qx, 0) ** 2 + np.maximum(qy, 0) ** 2) + np.minimum(np.maximum(qx, qy), 0) - r

    in_z = np.abs(Z) <= depth / 2
    in_out = rr(flange_w, flange_d, 3.0) <= 0
    e = rr(open_w, open_d, 1.5)
    in_v = e <= 0
    border = in_out & ~in_v
    rim = in_v & (e > -1.4)
    vcount = float((in_v & in_z).sum())
    best = None
    for t in np.linspace(0.2, 1.1, 40):
        openf = 1.0 - ((in_v & (np.abs(g) <= t) | rim) & in_z).sum() / vcount
        d = abs(openf - target_open)
        if best is None or d < best[0]:
            best = (d, float(t), float(openf))
    T, openf = best[1], best[2]
    solid = in_z & (border | rim | (in_v & (np.abs(g) <= T)))
    field = ndimage.gaussian_filter(solid.astype(np.float32), sigma=1.0)
    v, f, _, _ = measure.marching_cubes(field, level=0.5, spacing=(res, res, res))
    m = _tm.Trimesh(v, f); m.merge_vertices(); m.fix_normals()
    m.apply_translation(-m.bounds.mean(axis=0))
    return m, openf


def base_tube(H):
    """Outer box (flat back at y=0) minus open-through cavity. Filleted front/side edges."""
    body = Pos(0, 0, 0) * Box(MW, MD, H, align=(Align.CENTER, Align.MIN, Align.MIN))
    body = fillet(body.edges().filter_by(Axis.Z), fillet_r)
    cavity = Pos(0, yin0, -2) * Box(2 * HW_IN, yin1 - yin0, H + 4, align=(Align.CENTER, Align.MIN, Align.MIN))
    cavity = fillet(cavity.edges().filter_by(Axis.Z), fillet_r - 1.0)
    return largest_solid(body - cavity)


def add_keyholes(body, H):
    kz = H / 2
    for sx in (-1, 1):
        kh = Pos(sx * key_x, 0, kz) * Rot(-90, 0, 0) * Cylinder(4.0, 30, align=(Align.CENTER, Align.CENTER, Align.CENTER))
        ks = Pos(sx * key_x, -2, kz) * Box(4.0, 6.3, 8, align=(Align.CENTER, Align.MIN, Align.MIN))  # head pocket stops short of the Plus board plane (y 4.5)
        body = largest_solid(largest_solid(body - kh) - ks)
    return body


def cut_window(body, face, zc, zh, wmax):
    """Cut a gyroid-window opening + inner seat on a face ('front','left','right')."""
    ww = min(wmax, 2 * HW_IN - 2 * WIN_INSET)
    hh = zh
    if face == "front":
        body = largest_solid(body - box_lh(-ww / 2, ww / 2, MD - wall - 1, MD + 1, zc - hh / 2, zc + hh / 2))
        body = largest_solid(body - box_lh(-(ww / 2 + 2), (ww / 2 + 2), MD - wall - SEAT_D, MD - wall + 0.1, zc - hh / 2 - 2, zc + hh / 2 + 2))
    elif face in ("left", "right"):
        dd = min(wmax, (yin1 - yin0) - 2 * WIN_INSET)
        yc = (yin0 + yin1) / 2
        x_in, x_out = MW / 2 - wall - 1, MW / 2 + 1
        xl, xh = (-x_out, -x_in) if face == "left" else (x_in, x_out)
        body = largest_solid(body - box_lh(xl, xh, yc - dd / 2, yc + dd / 2, zc - hh / 2, zc + hh / 2))
    return body


def bottom_spigot(body):
    clr = COUPON_TBD_STACK
    so = box_lh(-(HW_IN - clr), HW_IN - clr, yin0 + clr, yin1 - clr, -IFACE_H, 0.1)
    si = box_lh(-(HW_IN - clr - IFACE_WALL), HW_IN - clr - IFACE_WALL, yin0 + clr + IFACE_WALL, yin1 - clr - IFACE_WALL, -IFACE_H - 1, 1)
    return largest_solid(body + largest_solid(so - si))


# ---------------- modules ----------------
def build_basic():
    body = base_tube(BH)
    # base intake grille floor at the bottom
    floor = box_lh(-HW_IN, HW_IN, yin0, yin1, 0, GRILLE_T)
    body = largest_solid(body + floor)
    for i in range(-3, 4):
        body = largest_solid(body - box_lh(i * 5 - 1.4, i * 5 + 1.4, yin0 + 1, yin1 - 1, -1, GRILLE_T + 1))
    # gyroid windows: front + both sides (upper zone, above the board-free lower intake)
    body = cut_window(body, "front", BH * 0.55, BH * 0.6, 30)
    body = cut_window(body, "left", BH * 0.55, BH * 0.55, 30)
    body = cut_window(body, "right", BH * 0.55, BH * 0.55, 30)
    # perfboard standoffs (board vertical on the back wall)
    bz0, bz1 = 8.0, 50.0
    for sx in (-1, 1):
        for bz in (bz0 + 6, bz1 - 6):
            post = Pos(sx * 16, yin0, bz) * Rot(-90, 0, 0) * Cylinder(3.0, 4.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
            pilot = Pos(sx * 16, yin0 - 0.1, bz) * Rot(-90, 0, 0) * Cylinder(COUPON_TBD_PILOT_M2 / 2, 8, align=(Align.CENTER, Align.CENTER, Align.MIN))
            body = largest_solid(body + post - pilot)
    body = add_keyholes(body, BH)
    # dummies
    board = box_lh(-20, 20, yin0 + 4, yin0 + 5.6, bz0, bz1)
    xiao = box_lh(-xiao_w / 2, xiao_w / 2, yin0 + 5.6, yin0 + 5.6 + xiao_t, bz1 - 4 - xiao_h, bz1 - 4)
    bme = box_lh(-bme_w / 2, bme_w / 2, yin0 + 5.6, yin0 + 5.6 + bme_t + 3, bz0 + 4, bz0 + 4 + bme_h)
    return dict(body=body, H=BH, dummies=[board, xiao, bme], top_socket=True)


def build_plus():
    """HM3301 module vertical against the back zone. Geometry from Seeed Eagle .brd +
    datasheet V2.1 (ICD 1.12-DRAFT):
      * board exactly 80x40; the can (40x38x15) occupies board-z 14.6..54.6 with the
        GROVE END DOWN — the 4P cable drops through the centre floor gap to the Basic;
      * both air ports sit on the can's one 40x15 narrow face, flush with one LONG
        board edge -> the ports face SIDEWAYS, not front. PM apertures are therefore
        side-wall slots at the can vent zone, low + high pair per side, MIRROR-SYMMETRIC
        (datasheet doesn't label in vs out; works either way; confirm by feel at power-up);
      * NO mounting holes exist on the board (no pegs): retention = bottom pocket
        (tilt-in) + back ribs + a top SKEWER BAR through side-wall mortises.
    The chimney air from the Basic rises in the slot BEHIND the board (board = baffle,
    F-04); the Plus has no gyroid windows — crown/cap exhausts the column."""
    body = base_tube(PH)
    body = bottom_spigot(body)
    hm_y = yin0 + 2.0                  # board back face plane (2mm solder/rib space)
    hz0 = (PH - hm_h) / 2              # board bottom edge (8.0); board top 88, socket 89..96
    can_z0 = hz0 + 14.6                # can zone (Grove end down)
    can_z1 = can_z0 + can_h
    # back ribs: board rear-face locators (behind the board only, centre stays open)
    for sx in (-1, 1):
        body = largest_solid(body + box_lh(sx * 13 - 2, sx * 13 + 2, yin0 - 0.1, hm_y, hz0 - 3, hz0 + hm_h - 2))  # ±13: keyhole cyl (±14 r4) cuts transversally, no tangent face
    # bottom pocket: split floor + short front lip (tilt-in); centre gap = Grove cable drop
    for xl, xh in ((-18.0, -8.0), (8.0, 18.0)):
        body = largest_solid(body + box_lh(xl, xh, hm_y - 1.0, hm_y + hm_t + 1.8, hz0 - 3, hz0))
        body = largest_solid(body + box_lh(xl, xh, hm_y + hm_t + 0.3, hm_y + hm_t + 1.8, hz0 - 0.5, hz0 + 5))  # overlaps floor 0.5 (manifold union)
    # top skewer-bar mortises through BOTH side walls (bar holds the board's clear top strip)
    bar_y0, bar_y1 = hm_y + hm_t + 0.4, hm_y + hm_t + 3.4
    bar_z0, bar_z1 = hz0 + 66.0, hz0 + 74.0
    body = largest_solid(body - box_lh(-(MW / 2 + 1), MW / 2 + 1,
                                       bar_y0 - COUPON_TBD_SLIDE, bar_y1 + COUPON_TBD_SLIDE,
                                       bar_z0 - COUPON_TBD_SLIDE, bar_z1 + COUPON_TBD_SLIDE))
    # PM apertures: SIDEWAYS at the can vent zone (crown rain-shadow), in front of the
    # board plane so they serve only the PM bay
    ay0, ay1 = hm_y + hm_t + 2.0, yin1 - 1.5
    for sx in (-1, 1):
        xl, xh = (HW_IN - 1.0, MW / 2 + 1.0) if sx > 0 else (-(MW / 2 + 1.0), -(HW_IN - 1.0))
        for zl, zh in ((can_z0 + 2.0, can_z0 + 12.0), (can_z1 - 12.0, can_z1 - 2.0)):
            body = largest_solid(body - box_lh(xl, xh, ay0, ay1, zl, zh))
        # plenum baffle between the two apertures (anti short-circuit), 0.4 off the can
        bx0, bx1 = (19.6, 21.0) if sx > 0 else (-21.0, -19.6)  # 0.5 into the wall (manifold union)
        body = largest_solid(body + box_lh(bx0, bx1, ay0, ay1, can_z0 + 19.0, can_z0 + 21.0))
    body = add_keyholes(body, PH)
    hm_board = box_lh(-hm_w / 2, hm_w / 2, hm_y, hm_y + hm_t, hz0, hz0 + hm_h)
    hm_can = box_lh(-can_w / 2, can_w / 2, hm_y + hm_t, hm_y + hm_t + can_d, can_z0, can_z1)
    bar = box_lh(-(MW / 2 - 0.5), MW / 2 - 0.5, bar_y0, bar_y1, bar_z0, bar_z1)
    return dict(body=body, H=PH, dummies=[hm_board, hm_can], bar=bar, top_socket=True)


def _csec(XW, FRONT, z):
    """Faceted D section in the module frame: flat back at y=0, faceted front to y=FRONT."""
    K = 10
    pts = [(-XW, 0.0), (XW, 0.0)]
    for i in range(1, K):
        a = math.pi * i / K
        pts.append((XW * math.cos(a), FRONT * math.sin(a)))   # right -> front -> left
    pts.append((-XW, 0.0))
    with BuildSketch(Plane.XY.offset(z)) as sk:
        with BuildLine():
            Polyline(*pts)
        make_face()
    return sk.sketch


def build_crown():
    # faceted 3-tier meru, generous eaves; flat back at y=0 aligns with the module stack
    lv = [(0, 24, 28), (3, 33, 50), (12, 18, 32), (14, 28, 46), (22, 14, 26),
          (24, 23, 40), (32, 9, 18), (40, 3, 10)]
    crown = loft([_csec(XW, FRONT, z) for (z, XW, FRONT) in lv], ruled=True)
    crown = largest_solid(crown)
    crown = bottom_spigot(crown)
    return dict(body=crown, H=40, dummies=[], top_socket=False)


def build_cap():
    body = base_tube(CAP_H)
    body = bottom_spigot(body)
    # top frame with a central opening + inside seat for a DROP-IN GYROID panel
    # (the breathing-plate design, tools/breathing_panel_v12.py -> v12_cap_panel.stl)
    # top ring with a central opening; the gyroid lattice is FUSED into this opening
    # (boolean union, below) so the cap prints as ONE part — not a separate panel.
    top = box_lh(-HW_IN, HW_IN, yin0, yin1, CAP_H - CAP_TOP_T, CAP_H)
    body = largest_solid(body + top)
    oy = (yin0 + yin1) / 2
    ow, od = CAP_OPEN_W, CAP_OPEN_D
    body = largest_solid(body - box_lh(-ow / 2, ow / 2, oy - od / 2, oy + od / 2, CAP_H - CAP_TOP_T - 1, CAP_H + 1))
    body = cut_window(body, "front", CAP_H * 0.5, CAP_H * 0.55, 30)
    return dict(body=body, H=CAP_H, dummies=[], top_socket=False, oy=oy)


def integrate_cap(cap):
    """Fuse the gyroid lattice into the cap top opening -> one watertight part."""
    frame_p = os.path.join(OUT, "_cap_frame.stl")
    export_stl(cap["body"], frame_p)
    frame = _tm.load(frame_p, force="mesh")
    gy, openf = gyroid_mesh(CAP_OPEN_W, CAP_OPEN_D, CAP_OPEN_W + 2 * CAP_SEAT_MARGIN, CAP_OPEN_D + 2 * CAP_SEAT_MARGIN, CAP_TOP_T)
    gy.apply_translation([0.0, cap["oy"], CAP_H - CAP_TOP_T / 2.0])   # span the top ring, border overlaps it
    fused = _tm.boolean.union([frame, gy])
    parts = fused.split(only_watertight=False)
    if len(parts) > 1:
        fused = max(parts, key=lambda c: c.volume)
    os.remove(frame_p)
    return fused, openf


def chk(nm, a, b, lim=0.02):
    v = 0.0
    try:
        v = sum(s.volume for s in (a & b).solids()) / 1000.0
    except Exception:
        pass
    ok = v <= lim
    print(f"  [{'OK ' if ok else 'FAIL'}] {nm}: {v:.3f} cm3")
    return ok


if __name__ == "__main__":
    basic = build_basic()
    plus = build_plus()
    cap = build_cap()
    crown = build_crown()

    ok = True
    print("--- parts ---")
    for nm, part in [("basic", basic), ("plus", plus), ("crown", crown)]:
        b = part["body"]
        p = os.path.join(OUT, f"v12_{nm}.stl")
        export_stl(b, p)
        mesh = _tm.load(p, force="mesh")
        cs = mesh.split(only_watertight=False)
        wt = mesh.is_watertight
        if len(cs) > 1:
            keep = max(cs, key=lambda c: c.area); keep.fix_normals(); keep.export(p); wt = keep.is_watertight
        bb = b.bounding_box()
        print(f"  {nm}: {bb.size.X:.0f} x {bb.size.Y:.0f} x {bb.size.Z:.0f} mm  watertight={wt}")
        for d in part["dummies"]:
            ok &= chk(f"{nm} dummy vs body", d, b)

    # HM skewer bar (separate printed part; retains the board's top strip)
    bar = plus["bar"]
    export_stl(bar, os.path.join(OUT, "v12_hm_bar.stl"))
    ok &= chk("hm bar vs plus body", bar, plus["body"])
    for d in plus["dummies"]:
        ok &= chk("hm bar vs plus dummies", bar, d)

    # INTEGRATED cap: the gyroid lattice is fused into the cap (one printable part)
    cap_mesh, openf = integrate_cap(cap)
    cap_mesh.export(os.path.join(OUT, "v12_cap.stl"))
    czh = cap_mesh.bounds[1][2] - cap_mesh.bounds[0][2]
    print(f"  cap (gyroid INTEGRATED): watertight={cap_mesh.is_watertight} open~{openf:.2f} "
          f"bodies={len(cap_mesh.split(only_watertight=False))} z={czh:.0f} mm")

    # outdoor Plus stack (BREP): Basic + Plus + Crown
    parts = [basic["body"], Pos(0, 0, BH) * plus["body"], Pos(0, 0, BH + PH) * crown["body"]]
    parts += basic["dummies"] + [Pos(0, 0, BH) * d for d in plus["dummies"]]
    export_stl(Compound(parts), os.path.join(REVIEW, "v12_outdoor_plus_stack.stl"))
    # indoor Basic stack (mesh): Basic + integrated gyroid cap
    basic_mesh = _tm.load(os.path.join(OUT, "v12_basic.stl"), force="mesh")
    capm = cap_mesh.copy(); capm.apply_translation([0, 0, BH])
    _tm.util.concatenate([basic_mesh, capm]).export(os.path.join(REVIEW, "v12_indoor_basic_stack.stl"))
    print(f"\n=== v12 modular | parts OK={ok} | cap gyroid integrated | stacks exported ===")
    print("§5.1 INFERRED — print the rim fit sections FIRST (tools/fit_section_v12.py); they gate full modules.")
