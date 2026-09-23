#!/usr/bin/env python3
"""Render the v8 bodies with the gyroid panel SEATED in the breathing window, so the
complete object reads (Tomas has only seen empty windows + the panel alone). Indicative
placement for review; the exact seat clearance is COUPON_TBD."""
import os
import numpy as np
import trimesh

E = os.path.expanduser("~/Documents/Claude/Projects/MDG/smartcitizenbali/hardware/diy-node/enclosure")
REV = os.path.join(E, "v8", "review")


def load(p):
    return trimesh.load(os.path.join(E, p), force="mesh")


def seat_plus():
    body = load("v8/v8_plus_body.stl")
    panel = load("v8/v8_gyroid_panel.stl")
    # panel local (X=33.6 w, Y=31.5 h, Z=8 thick) -> world (thickness along X = -X wall
    # normal): localX->Y, localY->Z, localZ->X
    M = np.eye(4)
    M[:3, :3] = np.array([[0, 0, 1], [1, 0, 0], [0, 1, 0]], float)
    panel.apply_transform(M)
    panel.apply_translation([-20.0, 0.0, 33.0])      # -X side window
    out = os.path.join(REV, "v8_plus_seated.stl")
    trimesh.util.concatenate([body, panel]).export(out)
    return out


def seat_basic():
    body = load("v8/v8_basic_body.stl")
    panel = load("v8/v8_gyroid_panel.stl")
    R = trimesh.transformations.rotation_matrix(np.radians(90), [1, 0, 0])  # Y<->Z
    panel.apply_transform(R)
    panel.apply_translation([0.0, 20.0, 33.0])       # +Y front window
    out = os.path.join(REV, "v8_basic_seated.stl")
    trimesh.util.concatenate([body, panel]).export(out)
    return out


if __name__ == "__main__":
    print(seat_plus())
    print(seat_basic())
