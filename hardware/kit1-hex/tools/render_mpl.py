#!/usr/bin/env python3
"""Headless multi-view STL renderer (matplotlib, no GL)."""
import sys
import numpy as np
import trimesh
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection


def add_mesh(ax, m, color=(0.72, 0.78, 0.86), zshift=0.0):
    tris = m.triangles.copy()
    tris[:, :, 2] += zshift
    n = m.face_normals
    light = np.array([0.4, -0.5, 0.75])
    light = light / np.linalg.norm(light)
    lam = np.clip(n @ light, 0, 1) * 0.75 + 0.25
    cols = np.clip(np.outer(lam, color), 0, 1)
    pc = Poly3DCollection(tris, facecolors=cols, edgecolors="none")
    ax.add_collection3d(pc)


def frame(ax, pts):
    lo = pts.min(axis=0)
    hi = pts.max(axis=0)
    c = (lo + hi) / 2
    r = (hi - lo).max() / 2 * 1.05
    ax.set_xlim(c[0] - r, c[0] + r)
    ax.set_ylim(c[1] - r, c[1] + r)
    ax.set_zlim(c[2] - r, c[2] + r)
    ax.set_axis_off()
    ax.set_box_aspect((1, 1, 1))


def sheet(meshes, out, title, views=((25, -60), (8, 0), (8, 90), (55, -120))):
    fig = plt.figure(figsize=(14, 11), dpi=110)
    allpts = np.vstack([m.vertices + np.array([0, 0, zs]) for m, zs, _ in meshes])
    for i, (elev, azim) in enumerate(views):
        ax = fig.add_subplot(2, 2, i + 1, projection="3d")
        for m, zs, col in meshes:
            add_mesh(ax, m, color=col, zshift=zs)
        frame(ax, allpts)
        ax.view_init(elev=elev, azim=azim)
    fig.suptitle(title, fontsize=15)
    fig.tight_layout()
    fig.savefig(out, facecolor="white")
    print("wrote", out)


if __name__ == "__main__":
    body = (0.74, 0.79, 0.87)
    accent = (0.94, 0.42, 0.25)
    tray_c = (0.65, 0.82, 0.70)
    lo = trimesh.load("kit1_lower.stl")
    up = trimesh.load("kit1_upper.stl")
    tr = trimesh.load("kit1_tray.stl")
    sheet([(lo, 0, body)], "kit1_lower_views.png", "KIT 1 lower bowl (print orientation)")
    sheet([(up, 0, body)], "kit1_upper_views.png", "KIT 1 upper dome + spire (print orientation)")
    sheet([(tr, 0, tray_c)], "kit1_tray_views.png", "KIT 1 tray (print orientation)")
    # deployed assembly: lower at -66, upper at 0, tray deck_bot -43
    sheet([(lo, -66 - 0, body), (up, 0, accent), (tr, -43, tray_c)],
          "kit1_assembly_views.png", "KIT 1 deployed (upper tinted, tray green)",
          views=((12, -55), (2, 0), (30, -120), (78, -90)))
