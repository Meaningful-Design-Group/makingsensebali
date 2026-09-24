#!/usr/bin/env python3
"""Making Sense Bali DIY node — v10 BASE BREATHING PANEL (the big drop-in insert).

The bottom of the enclosure is now the breathing element (Tomas, 2026-06-10): a large
drop-in gyroid panel that seats in the base frame (enclosure_v10.py) and breathes the
whole base->top chimney. Generated per variant (Basic and Plus base depths differ):

  Basic  flange ~41x31, vent ~35x25
  Plus   flange ~41x43, vent ~35x37

Single watertight solid via one marching-cubes pass (solid border/rim + sheet-gyroid
lattice) — the proven v8/v9 method. The SEAT_MARGIN border rests on the base shoulder;
the gyroid fills the opening. NOT FOR PRINT until ICD 5.1 sets the seat clearance.
"""
import os
import numpy as np
import trimesh
from skimage import measure
from scipy import ndimage

OUT = os.path.join(os.path.dirname(__file__), "..", "v10")
os.makedirs(OUT, exist_ok=True)

# matches enclosure_v10: open = 2*HW_IN-8 x (back_inner+FRONT_IN)-10 ; flange = open + 2*SEAT_MARGIN
HW_IN, back_inner = 21.5, 13.5
SEAT_MARGIN = 3.0
DEPTH = 4.0
R_OUT, R_IN = 3.0, 2.0
RIM = 1.4
PERIOD = 9.0
TARGET_OPEN = 0.48
RES = 0.30

VARIANTS = {"basic": 21.5, "plus": 33.5}      # FRONT_IN per variant


def rrect(X, Y, w, h, r):
    qx = np.abs(X) - (w / 2 - r)
    qy = np.abs(Y) - (h / 2 - r)
    out = np.sqrt(np.maximum(qx, 0.0) ** 2 + np.maximum(qy, 0.0) ** 2)
    ins = np.minimum(np.maximum(qx, qy), 0.0)
    return out + ins - r


def build(name, FRONT_IN):
    open_w = 2 * HW_IN - 8.0
    open_d = (back_inner + FRONT_IN) - 10.0
    FL_W, FL_D = open_w + 2 * SEAT_MARGIN, open_d + 2 * SEAT_MARGIN
    VENT_W, VENT_H = open_w, open_d
    pad = 2.0
    xs = np.arange(-FL_W / 2 - pad, FL_W / 2 + pad, RES)
    ys = np.arange(-FL_D / 2 - pad, FL_D / 2 + pad, RES)
    zs = np.arange(-DEPTH / 2 - pad, DEPTH / 2 + pad, RES)
    X, Y, Z = np.meshgrid(xs, ys, zs, indexing="ij")
    k = 2 * np.pi / PERIOD
    g = (np.sin(k * X) * np.cos(k * Y) + np.sin(k * Y) * np.cos(k * Z) + np.sin(k * Z) * np.cos(k * X))
    in_z = np.abs(Z) <= DEPTH / 2
    in_out = rrect(X, Y, FL_W, FL_D, R_OUT) <= 0
    e_vent = rrect(X, Y, VENT_W, VENT_H, R_IN)
    in_vent = e_vent <= 0
    border = in_out & ~in_vent
    rim_band = in_vent & (e_vent > -RIM)
    vent_z_count = float((in_vent & in_z).sum())
    best = None
    for t in np.linspace(0.20, 1.10, 46):
        gyro = in_vent & (np.abs(g) <= t)
        solid_in_vent = (gyro | rim_band) & in_z
        openf = 1.0 - solid_in_vent.sum() / vent_z_count
        d = abs(openf - TARGET_OPEN)
        if best is None or d < best[0]:
            best = (d, float(t), float(openf))
    _, T, openf = best
    gyro = in_vent & (np.abs(g) <= T)
    solid = in_z & (border | rim_band | gyro)
    field = ndimage.gaussian_filter(solid.astype(np.float32), sigma=1.0)
    verts, faces, _, _ = measure.marching_cubes(field, level=0.5, spacing=(RES, RES, RES))
    m = trimesh.Trimesh(verts, faces)
    m.merge_vertices()
    m.fix_normals()
    m.apply_translation(-m.bounds.mean(axis=0))
    vent_col = in_vent.any(axis=2)
    through = 1.0 - solid.any(axis=2)[vent_col].sum() / vent_col.sum()
    stl = os.path.join(OUT, f"v10_{name}_panel.stl")
    m.export(stl)
    sz = (m.bounds[1] - m.bounds[0]).round(2)
    print(f"{name}: flange {FL_W:.0f}x{FL_D:.0f} vent {VENT_W:.0f}x{VENT_H:.0f} | t={T:.2f} open={openf:.2f} "
          f"through={through:.3f} watertight={m.is_watertight} size={sz} vol={m.volume/1000:.1f}cm3")
    return m


if __name__ == "__main__":
    for nm, fi in VARIANTS.items():
        build(nm, fi)
    print("NOT FOR PRINT — seat clearance is COUPON_TBD_PANELSEAT (base side); fill ICD 5.1 first.")
