#!/usr/bin/env python3
"""Making Sense Bali DIY node — v8 GYROID breathing panel (the snap-in insert).

Rebuilds the breathing panel that enclosure_v7.py *promised* (tools/gyroid_panel.py)
but never delivered. The three orphan gyroid STLs in v7/ are non-watertight,
negative-volume open sheets with no source script — unprintable. THIS is the source
script, and it produces a SINGLE WATERTIGHT SOLID (frame + solid rim + sheet-gyroid
lattice) in one marching-cubes pass over a scalar occupancy field. No fragile
mesh<->BREP booleans, no boolean-engine dependency. Filleted outer corners via a
rounded-rectangle SDF.

Sheet gyroid:  g = sin x cos y + sin y cos z + sin z cos x ;  solid where |g| <= t.
`t` is auto-tuned to hit a target open-VOLUME fraction; PERIOD sets the wall scale.

Seats into the body's front window (WIN_W x WIN_H) on its inside rebate; the snap
clearance stays COUPON_TBD_SNAP until ICD 5.1 is measured. PETG. Print orientation
+ support-free status are decided by the slicer-in-loop, not assumed.
"""
import os
import numpy as np
import trimesh
from skimage import measure
from scipy import ndimage

OUT = os.path.join(os.path.dirname(__file__), "..", "v8")
os.makedirs(OUT, exist_ok=True)

# --- geometry (matches enclosure_v7 window; flange = v7 "panel target ~33.6 x 31.6") ---
WIN_W, WIN_H = 30.0, 28.0          # breathing window (gyroid zone)
FLANGE_W, FLANGE_H = 33.6, 31.6    # outer flange, seats in the body rebate (+3.6)
DEPTH = 8.0
R_OUT, R_IN = 2.5, 1.5             # corner fillets (ICD: min visible R1.5)
RIM = 1.4                          # continuous solid border just inside the window
PERIOD = 10.0                      # gyroid cell size (mm) -> wall scale. Isotropic.
                                   # ~3% projected straight-porosity is inherent at
                                   # 48% open; handled in the assembly by the foil
                                   # liner + air gap behind the panel (the real IR /
                                   # light barrier), with the panel in the hood's
                                   # rain-shadow. Don't chase it in the lattice.
TARGET_OPEN = 0.48                 # target open-VOLUME fraction inside the window
RES = 0.30                         # voxel size (mm)
COUPON_TBD_SNAP = 0.30             # placeholder seat clearance (applied body-side)


def rrect(X, Y, w, h, r):
    """Signed distance to a rounded rectangle; < 0 inside."""
    qx = np.abs(X) - (w / 2 - r)
    qy = np.abs(Y) - (h / 2 - r)
    out = np.sqrt(np.maximum(qx, 0.0) ** 2 + np.maximum(qy, 0.0) ** 2)
    ins = np.minimum(np.maximum(qx, qy), 0.0)
    return out + ins - r


def build():
    pad = 2.0
    xs = np.arange(-FLANGE_W / 2 - pad, FLANGE_W / 2 + pad, RES)
    ys = np.arange(-FLANGE_H / 2 - pad, FLANGE_H / 2 + pad, RES)
    zs = np.arange(-DEPTH / 2 - pad, DEPTH / 2 + pad, RES)
    X, Y, Z = np.meshgrid(xs, ys, zs, indexing="ij")
    k = 2 * np.pi / PERIOD
    g = (np.sin(k * X) * np.cos(k * Y)
         + np.sin(k * Y) * np.cos(k * Z)
         + np.sin(k * Z) * np.cos(k * X))

    in_z = np.abs(Z) <= DEPTH / 2
    in_out = rrect(X, Y, FLANGE_W, FLANGE_H, R_OUT) <= 0
    e_win = rrect(X, Y, WIN_W, WIN_H, R_IN)
    in_win = e_win <= 0
    flange = in_out & ~in_win
    rim_band = in_win & (e_win > -RIM)
    win_z_count = float((in_win & in_z).sum())

    # auto-tune t to TARGET_OPEN (open = empty fraction of the window volume)
    best = None
    for t in np.linspace(0.20, 1.10, 46):
        gyro = in_win & (np.abs(g) <= t)
        solid_in_win = (gyro | rim_band) & in_z
        openf = 1.0 - solid_in_win.sum() / win_z_count
        d = abs(openf - TARGET_OPEN)
        if best is None or d < best[0]:
            best = (d, float(t), float(openf))
    _, T, openf = best

    gyro = in_win & (np.abs(g) <= T)
    solid = in_z & (flange | rim_band | gyro)
    field = ndimage.gaussian_filter(solid.astype(np.float32), sigma=1.0)
    verts, faces, _, _ = measure.marching_cubes(field, level=0.5, spacing=(RES, RES, RES))
    m = trimesh.Trimesh(verts, faces)
    m.merge_vertices()
    m.fix_normals()
    m.apply_translation(-m.bounds.mean(axis=0))   # centre at origin for clean assembly

    # straight sightline THROUGH the thickness (panel Z = the wall-normal once the
    # panel is seated in the front window): frac of window (x,y) columns with a
    # fully-open front-to-back path. Want ~0 so rain/light never reach the sensor;
    # airflow still gets through because the gyroid void is bicontinuous (it winds
    # around the solid, no straight hole). This is the axis that matters, not the
    # in-plane one.
    win_col = in_win.any(axis=2)
    blocked_col = solid.any(axis=2)
    through = 1.0 - blocked_col[win_col].sum() / win_col.sum()

    stl = os.path.join(OUT, "v8_gyroid_panel.stl")
    m.export(stl)
    sz = (m.bounds[1] - m.bounds[0]).round(2)
    print(f"chosen t={T:.3f}  open_vol_frac={openf:.2f}  straight_sightline_thru_thickness={through:.3f}")
    print(f"panel: watertight={m.is_watertight} comps={len(m.split(only_watertight=False))} "
          f"vol_cm3={m.volume / 1000:.2f} faces={len(m.faces)}")
    print(f"size_mm={sz}  ->  {stl}")
    return m


if __name__ == "__main__":
    build()
