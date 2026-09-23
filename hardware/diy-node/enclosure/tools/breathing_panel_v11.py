#!/usr/bin/env python3
"""v11 climate-intake breathing panels (drop-in gyroid), per variant.

v11 separates PM air from climate air, so the base breathing panel now covers only the
CLIMATE opening (back zone). Plus's climate opening is smaller than Basic's (the front
zone is the isolated PM bay with its own grille). Vent sizes mirror enclosure_v11.py:
  Basic  open 35 x 25   ->  flange 41 x 31
  Plus   open 35 x 16.5 ->  flange 41 x 22.5
Single watertight solid via marching cubes. NOT FOR PRINT until ICD 5.1.
"""
import os
import numpy as np
import trimesh
from skimage import measure
from scipy import ndimage

OUT = os.path.join(os.path.dirname(__file__), "..", "v11")
os.makedirs(OUT, exist_ok=True)
SEAT_MARGIN, DEPTH, R_OUT, R_IN, RIM, PERIOD, TARGET_OPEN, RES = 3.0, 4.0, 3.0, 2.0, 1.4, 9.0, 0.48, 0.30
# (open_w, open_d) per variant — climate opening only
VARIANTS = {"basic": (35.0, 25.0), "plus": (35.0, 16.5)}


def rrect(X, Y, w, h, r):
    qx = np.abs(X) - (w / 2 - r); qy = np.abs(Y) - (h / 2 - r)
    return np.sqrt(np.maximum(qx, 0) ** 2 + np.maximum(qy, 0) ** 2) + np.minimum(np.maximum(qx, qy), 0) - r


def build(name, open_w, open_d):
    FL_W, FL_D = open_w + 2 * SEAT_MARGIN, open_d + 2 * SEAT_MARGIN
    pad = 2.0
    xs = np.arange(-FL_W / 2 - pad, FL_W / 2 + pad, RES)
    ys = np.arange(-FL_D / 2 - pad, FL_D / 2 + pad, RES)
    zs = np.arange(-DEPTH / 2 - pad, DEPTH / 2 + pad, RES)
    X, Y, Z = np.meshgrid(xs, ys, zs, indexing="ij")
    k = 2 * np.pi / PERIOD
    g = np.sin(k * X) * np.cos(k * Y) + np.sin(k * Y) * np.cos(k * Z) + np.sin(k * Z) * np.cos(k * X)
    in_z = np.abs(Z) <= DEPTH / 2
    in_out = rrect(X, Y, FL_W, FL_D, R_OUT) <= 0
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
    through = 1.0 - solid.any(axis=2)[in_vent.any(axis=2)].sum() / in_vent.any(axis=2).sum()
    stl = os.path.join(OUT, f"v11_{name}_panel.stl")
    m.export(stl)
    print(f"{name}: flange {FL_W:.0f}x{FL_D:.0f} vent {open_w:.0f}x{open_d:.0f} open={openf:.2f} "
          f"through={through:.3f} watertight={m.is_watertight} vol={m.volume/1000:.1f}cm3")


if __name__ == "__main__":
    for nm, (w, d) in VARIANTS.items():
        build(nm, w, d)
    print("NOT FOR PRINT — seat clearance COUPON_TBD_PANELSEAT; fill ICD 5.1 first.")
