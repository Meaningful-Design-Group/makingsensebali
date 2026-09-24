#!/usr/bin/env python3
"""Making Sense Bali DIY node — v9 BREATHING PLATE (the slide-in friction insert).

The flat plate that slides into the body's breathing-window RAIL and grips by
friction (enclosure_v9.py, the slide-in rail on the BME680 wall). Tomas's spec
(2026-06-10): 35 x 35 face, 7 mm thick — almost double the old ~20x20x6.5 panel,
sized so its solid border rides in the rail and the plate covers the window.

Single watertight solid via one marching-cubes pass over a scalar occupancy field
(solid border/rim + sheet-gyroid breathing lattice), same proven method as the v8
gyroid panel — no fragile mesh<->BREP booleans. PETG.

Sheet gyroid:  g = sin x cos y + sin y cos z + sin z cos x ;  solid where |g| <= t.

PLATE NOMINAL = 35 x 35 x 7. All fit clearance lives on the BODY rail side
(COUPON_TBD_RAIL in enclosure_v9.py), so this plate stays at Tomas's clean numbers
until ICD 5.1 is measured. NOT FOR PRINT until 5.1 is filled.
"""
import os
import numpy as np
import trimesh
from skimage import measure
from scipy import ndimage

OUT = os.path.join(os.path.dirname(__file__), "..", "v9")
os.makedirs(OUT, exist_ok=True)

# --- geometry (matches the enclosure_v9 rail: PLATE_W/H/T, VENT_W/H) ---
PLATE_W, PLATE_H = 35.0, 35.0      # outer face (Tomas's spec) — the rail grips this footprint
DEPTH = 7.0                        # plate thickness (Tomas's spec)
VENT_W, VENT_H = 30.0, 30.0        # breathing zone; the (35-30)/2 = 2.5 mm border is the rail-ride edge
R_OUT, R_IN = 2.5, 1.5             # corner fillets (ICD: min visible R1.5)
RIM = 1.4                          # continuous solid border just inside the vent (seals the lattice edge)
PERIOD = 10.0                      # gyroid cell size (mm); isotropic wall scale
TARGET_OPEN = 0.48                 # target open-VOLUME fraction inside the vent
RES = 0.30                         # voxel size (mm)


def rrect(X, Y, w, h, r):
    """Signed distance to a rounded rectangle; < 0 inside."""
    qx = np.abs(X) - (w / 2 - r)
    qy = np.abs(Y) - (h / 2 - r)
    out = np.sqrt(np.maximum(qx, 0.0) ** 2 + np.maximum(qy, 0.0) ** 2)
    ins = np.minimum(np.maximum(qx, qy), 0.0)
    return out + ins - r


def build():
    pad = 2.0
    xs = np.arange(-PLATE_W / 2 - pad, PLATE_W / 2 + pad, RES)
    ys = np.arange(-PLATE_H / 2 - pad, PLATE_H / 2 + pad, RES)
    zs = np.arange(-DEPTH / 2 - pad, DEPTH / 2 + pad, RES)
    X, Y, Z = np.meshgrid(xs, ys, zs, indexing="ij")
    k = 2 * np.pi / PERIOD
    g = (np.sin(k * X) * np.cos(k * Y)
         + np.sin(k * Y) * np.cos(k * Z)
         + np.sin(k * Z) * np.cos(k * X))

    in_z = np.abs(Z) <= DEPTH / 2
    in_out = rrect(X, Y, PLATE_W, PLATE_H, R_OUT) <= 0
    e_vent = rrect(X, Y, VENT_W, VENT_H, R_IN)
    in_vent = e_vent <= 0
    border = in_out & ~in_vent                     # solid 2.5 mm border -> rides in the rail
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
    m.apply_translation(-m.bounds.mean(axis=0))    # centre at origin

    # straight sightline through the thickness — want ~0 so rain/light never reach the
    # sensor; airflow still passes because the gyroid void is bicontinuous (no straight hole).
    vent_col = in_vent.any(axis=2)
    blocked_col = solid.any(axis=2)
    through = 1.0 - blocked_col[vent_col].sum() / vent_col.sum()

    stl = os.path.join(OUT, "v9_breathing_panel.stl")
    m.export(stl)
    sz = (m.bounds[1] - m.bounds[0]).round(2)
    print(f"chosen t={T:.3f}  open_vol_frac={openf:.2f}  straight_sightline_thru_thickness={through:.3f}")
    print(f"panel: watertight={m.is_watertight} comps={len(m.split(only_watertight=False))} "
          f"vol_cm3={m.volume / 1000:.2f} faces={len(m.faces)}")
    print(f"size_mm={sz}  ->  {stl}")
    print("NOT FOR PRINT — rail fit clearance is COUPON_TBD_RAIL (body side); fill ICD 5.1 first.")
    return m


if __name__ == "__main__":
    build()
