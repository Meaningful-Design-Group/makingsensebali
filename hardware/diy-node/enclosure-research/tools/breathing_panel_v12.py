#!/usr/bin/env python3
"""v12 drop-in GYROID panels (breathing-plate method) for the modular system.

Same single-watertight-solid marching-cubes approach as the v8-v11 breathing plate:
solid border/rim + sheet-gyroid lattice, one pass over a scalar field. Sizes mirror the
openings cut in enclosure_v12.py. Panels are centred at the origin for clean seating.

  cap : flange 39 x 19, vent 33 x 13  (the indoor Basic cap top)

NOT FOR PRINT until ICD 5.1 sets the seat clearance.
"""
import os
import numpy as np
import trimesh
from skimage import measure
from scipy import ndimage

OUT = os.path.join(os.path.dirname(__file__), "..", "v12")
os.makedirs(OUT, exist_ok=True)
SEAT_MARGIN, DEPTH, R_OUT, R_IN, RIM, PERIOD, TARGET_OPEN, RES = 3.0, 4.0, 3.0, 1.5, 1.4, 8.0, 0.48, 0.28
PANELS = {"cap": (33.0, 13.0)}     # (open_w, open_d)


def rrect(X, Y, w, h, r):
    qx = np.abs(X) - (w / 2 - r); qy = np.abs(Y) - (h / 2 - r)
    return np.sqrt(np.maximum(qx, 0) ** 2 + np.maximum(qy, 0) ** 2) + np.minimum(np.maximum(qx, qy), 0) - r


def build(name, open_w, open_d):
    FW, FD = open_w + 2 * SEAT_MARGIN, open_d + 2 * SEAT_MARGIN
    pad = 2.0
    xs = np.arange(-FW / 2 - pad, FW / 2 + pad, RES)
    ys = np.arange(-FD / 2 - pad, FD / 2 + pad, RES)
    zs = np.arange(-DEPTH / 2 - pad, DEPTH / 2 + pad, RES)
    X, Y, Z = np.meshgrid(xs, ys, zs, indexing="ij")
    k = 2 * np.pi / PERIOD
    g = np.sin(k * X) * np.cos(k * Y) + np.sin(k * Y) * np.cos(k * Z) + np.sin(k * Z) * np.cos(k * X)
    in_z = np.abs(Z) <= DEPTH / 2
    in_out = rrect(X, Y, FW, FD, R_OUT) <= 0
    e_vent = rrect(X, Y, open_w, open_d, R_IN)
    in_vent = e_vent <= 0
    border = in_out & ~in_vent
    rim_band = in_vent & (e_vent > -RIM)
    vcount = float((in_vent & in_z).sum())
    best = None
    for t in np.linspace(0.20, 1.10, 46):
        openf = 1.0 - ((in_vent & (np.abs(g) <= t) | rim_band) & in_z).sum() / vcount
        d = abs(openf - TARGET_OPEN)
        if best is None or d < best[0]:
            best = (d, float(t), float(openf))
    _, T, openf = best
    solid = in_z & (border | rim_band | (in_vent & (np.abs(g) <= T)))
    field = ndimage.gaussian_filter(solid.astype(np.float32), sigma=1.0)
    v, f, _, _ = measure.marching_cubes(field, level=0.5, spacing=(RES, RES, RES))
    m = trimesh.Trimesh(v, f); m.merge_vertices(); m.fix_normals(); m.apply_translation(-m.bounds.mean(axis=0))
    stl = os.path.join(OUT, f"v12_{name}_panel.stl")
    m.export(stl)
    sz = (m.bounds[1] - m.bounds[0]).round(2)
    print(f"{name}: flange {FW:.0f}x{FD:.0f} vent {open_w:.0f}x{open_d:.0f} open={openf:.2f} watertight={m.is_watertight} size={sz}")


if __name__ == "__main__":
    for nm, (w, d) in PANELS.items():
        build(nm, w, d)
    print("NOT FOR PRINT — seat clearance is COUPON_TBD; fill ICD 5.1 first.")
