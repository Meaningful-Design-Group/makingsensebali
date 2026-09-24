#!/usr/bin/env python3
"""Making Sense Bali DIY node — v10 DIMENSIONED LAYOUT MAPS.

To-scale engineering diagrams (front + side) of the enclosure with the sensors drawn
inside at their real footprints, fully dimensioned in mm, so the fit can be read off
the page rather than guessed from a gray render. Mirrors enclosure_v10.py constants.

Outputs v10/review/v10_{basic,plus}_layout.png. Pure matplotlib (no 3D), true scale.
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch

OUT = os.path.join(os.path.dirname(__file__), "..", "v11", "review")
os.makedirs(OUT, exist_ok=True)

# ---- constants mirrored from enclosure_v10.py ----
wall = 2.5
back_y, back_inner = 16.0, 13.5
HW, HW_IN = 24.0, 21.5
foot_h = 3.0
perf_w, perf_h, perf_t = 40.0, 60.0, 1.6
perf_z0 = 18.0
bme_w, bme_h = 16.0, 12.5
bme_z = 26.0
xiao_w, xiao_h = 21.0, 17.8
hm_w, hm_h, hm_t = 40.0, 80.0, 1.6            # HM3301 module 80x40x18 (Tomas measured 2026-06-11)
can_w, can_h, can_d = 38.0, 40.0, 16.4
hm_z0, hm_carrier_y = 14.0, 13.0
key_z = 60.0
BASE_T = 5.0

VAR = {
    "basic": dict(FRONT=24.0, FRONT_IN=21.5, body_top=84.0, hm=False, lean=9.0, open_w=35.0, open_d=25.0),
    "plus":  dict(FRONT=40.0, FRONT_IN=37.5, body_top=110.0, hm=True, lean=2.0, open_w=35.0, open_d=37.0),
}

INK = "#1b2a3a"
WALLC = "#9fb3c8"
CAV = "#eef3f8"
COMP = {"perfboard": "#c9a227", "XIAO ESP32-S3": "#2f6f4f", "BME680": "#b5651d",
        "HM3301": "#7a4fb5", "breathing panel": "#2f8fb5"}


def dim(ax, p0, p1, text, off=0.0, horizontal=True, color=INK, fs=8):
    """Dimension line with arrows + centered label. off shifts the line out."""
    if horizontal:
        y = p0[1] + off
        ax.add_patch(FancyArrowPatch((p0[0], y), (p1[0], y), arrowstyle="<|-|>",
                                     mutation_scale=7, lw=0.8, color=color))
        ax.plot([p0[0], p0[0]], [p0[1], y], lw=0.5, color=color)
        ax.plot([p1[0], p1[0]], [p1[1], y], lw=0.5, color=color)
        ax.text((p0[0] + p1[0]) / 2, y, text, ha="center", va="bottom" if off >= 0 else "top",
                fontsize=fs, color=color, bbox=dict(fc="white", ec="none", pad=0.5))
    else:
        x = p0[0] + off
        ax.add_patch(FancyArrowPatch((x, p0[1]), (x, p1[1]), arrowstyle="<|-|>",
                                     mutation_scale=7, lw=0.8, color=color))
        ax.plot([p0[0], x], [p0[1], p0[1]], lw=0.5, color=color)
        ax.plot([p1[0], x], [p1[1], p1[1]], lw=0.5, color=color)
        ax.text(x, (p0[1] + p1[1]) / 2, text, ha="left" if off >= 0 else "right", va="center",
                rotation=90, fontsize=fs, color=color, bbox=dict(fc="white", ec="none", pad=0.5))


def rect(ax, x, y, w, h, label, color, alpha=0.85):
    ax.add_patch(Rectangle((x, y), w, h, fc=color, ec=INK, lw=0.8, alpha=alpha, zorder=3))
    ax.text(x + w / 2, y + h / 2, label, ha="center", va="center", fontsize=7,
            color="white", weight="bold", zorder=4)


def draw(name, c):
    FRONT, FRONT_IN, body_top, hm = c["FRONT"], c["FRONT_IN"], c["body_top"], c["hm"]
    z_top = body_top + foot_h
    perf_z = perf_z0 + foot_h
    fig, (axf, axs) = plt.subplots(1, 2, figsize=(12, 8))

    # ===== FRONT view (X horizontal, Z vertical) =====
    axf.set_title(f"{name.upper()} — front  (X × Z)", fontsize=10, color=INK)
    # outer wall + cavity (width constant 2*HW; cavity 2*HW_IN)
    axf.add_patch(Rectangle((-HW, foot_h), 2 * HW, body_top, fc=WALLC, ec=INK, lw=1.2, zorder=1))
    axf.add_patch(Rectangle((-HW_IN, foot_h), 2 * HW_IN, body_top, fc=CAV, ec=INK, lw=0.6, zorder=2))
    # perfboard + sensors (front faces)
    rect(axf, -perf_w / 2, perf_z, perf_w, perf_h, "perfboard 40×60", COMP["perfboard"], 0.5)
    rect(axf, -xiao_w / 2, perf_z + perf_h - xiao_h - 3, xiao_w, xiao_h, "XIAO\n21×17.8", COMP["XIAO ESP32-S3"])
    rect(axf, -5 - bme_w / 2, bme_z + foot_h - bme_h / 2, bme_w, bme_h, "BME680\n16×12.5", COMP["BME680"])
    if hm:
        rect(axf, -hm_w / 2, hm_z0 + foot_h, hm_w, hm_h, "HM3301\n80×40 *", COMP["HM3301"])
    # base breathing opening
    rect(axf, -c["open_w"] / 2, foot_h - BASE_T, c["open_w"], BASE_T, f"breathe {c['open_w']:.0f}", COMP["breathing panel"])
    # keyholes
    for sx in (-1, 1):
        axf.add_patch(plt.Circle((sx * 14.0, key_z + foot_h), 2.2, fc="white", ec=INK, lw=0.8, zorder=5))
    # dims
    dim(axf, (-HW, z_top), (HW, z_top), f"{2*HW:.0f}", off=8)
    dim(axf, (-HW_IN, z_top), (HW_IN, z_top), f"cavity {2*HW_IN:.0f}", off=20)
    dim(axf, (HW, foot_h), (HW, z_top), f"{body_top:.0f}", off=10, horizontal=False)
    dim(axf, (-HW_IN, perf_z), (-perf_w / 2, perf_z), f"{(2*HW_IN-perf_w)/2:.1f}", off=-6)
    axf.text(0, foot_h - BASE_T - 6, "wall 2.5 mm   |   perfboard clearance each side", ha="center", fontsize=7, color=INK)

    # ===== SIDE view (Y horizontal, Z vertical) — front leans back with height =====
    axs.set_title(f"{name.upper()} — side  (Y × Z), flat back at left", fontsize=10, color=INK)
    # outer profile: back flat at y=-back_y; front leans FRONT (base) -> FRONT-lean (top)
    lean = c["lean"]
    yf1 = FRONT - lean
    outer_xy = [(-back_y, foot_h), (FRONT, foot_h), (FRONT + 2, foot_h + 0.3 * body_top),
                (FRONT - lean * 0.4, foot_h + 0.62 * body_top), (yf1, z_top), (-back_y, z_top)]
    axs.add_patch(plt.Polygon(outer_xy, closed=True, fc=WALLC, ec=INK, lw=1.2, zorder=1))
    yf1i = FRONT - lean - wall
    cav_xy = [(-back_inner, foot_h), (FRONT - wall, foot_h), (FRONT + 2 - wall, foot_h + 0.3 * body_top),
              (FRONT - lean * 0.4 - wall, foot_h + 0.62 * body_top), (yf1i, z_top), (-back_inner, z_top)]
    axs.add_patch(plt.Polygon(cav_xy, closed=True, fc=CAV, ec=INK, lw=0.6, zorder=2))
    # perfboard against the back wall (thin), components projecting forward
    perf_y = -back_inner + 4.0
    axs.add_patch(Rectangle((perf_y, perf_z), perf_t, perf_h, fc=COMP["perfboard"], ec=INK, lw=0.8, alpha=0.6, zorder=3))
    axs.add_patch(Rectangle((perf_y + perf_t, perf_z + perf_h - xiao_h - 3), 17.8, xiao_h, fc=COMP["XIAO ESP32-S3"], ec=INK, lw=0.8, zorder=3))
    axs.text(perf_y + perf_t + 9, perf_z + perf_h - 12, "XIAO", ha="center", va="center", fontsize=7, color="white", weight="bold", zorder=4)
    axs.add_patch(Rectangle((perf_y + perf_t, bme_z + foot_h - bme_h / 2), bme_h, bme_h, fc=COMP["BME680"], ec=INK, lw=0.8, zorder=3))
    axs.text(perf_y + perf_t + 6, bme_z + foot_h, "BME", ha="center", va="center", fontsize=6.5, color="white", weight="bold", zorder=4)
    if hm:
        axs.add_patch(Rectangle((hm_carrier_y, hm_z0 + foot_h), hm_t, hm_h, fc=COMP["HM3301"], ec=INK, lw=0.8, zorder=3))
        axs.add_patch(Rectangle((hm_carrier_y + hm_t, hm_z0 + foot_h + (hm_h - can_h) / 2), can_d, can_h, fc=COMP["HM3301"], ec=INK, lw=0.8, alpha=0.7, zorder=3))
        axs.text(hm_carrier_y + 9, hm_z0 + foot_h + hm_h / 2, "HM3301\ncan", ha="center", va="center", fontsize=6, color="white", weight="bold", zorder=4)
    # base breathing panel
    axs.add_patch(Rectangle((-c["open_d"] / 2 + (FRONT_IN - back_inner) / 2, foot_h - BASE_T), c["open_d"], BASE_T, fc=COMP["breathing panel"], ec=INK, lw=0.8, zorder=3))
    # dims
    dim(axs, (-back_y, foot_h - 12), (FRONT, foot_h - 12), f"base depth {back_y + FRONT:.0f}", off=-4)
    dim(axs, (-back_y, z_top), (yf1, z_top), f"top depth {back_y + yf1:.0f}", off=8)
    dim(axs, (FRONT + 6, foot_h), (FRONT + 6, z_top), f"{body_top:.0f}", off=6, horizontal=False)
    axs.annotate("front leans back\n(organic)", (FRONT - 4, foot_h + 0.75 * body_top),
                 (FRONT + 8, foot_h + 0.78 * body_top), fontsize=7, color=INK,
                 arrowprops=dict(arrowstyle="->", color=INK, lw=0.7))
    axs.annotate("airflow ↑", (0, foot_h + body_top * 0.5), fontsize=9, color="#2f8fb5", ha="center", weight="bold")
    axs.annotate("intake (base)", ((FRONT_IN - back_inner) / 2, foot_h - BASE_T - 4), fontsize=7, color="#2f8fb5", ha="center")

    for ax in (axf, axs):
        ax.set_aspect("equal")
        ax.autoscale_view()
        ax.margins(0.18)
        ax.axis("off")
    fig.suptitle(f"DIY node v11 — {name.upper()} layout (to scale, mm)   "
                 f"*HM3301 80×40×18 (measured); can-port mapping = caliper-confirm   |   STAGING, NOT FOR PRINT",
                 fontsize=9.5, color="#a02020")
    p = os.path.join(OUT, f"v11_{name}_layout.png")
    fig.savefig(p, dpi=130, bbox_inches="tight")
    plt.close(fig)
    print(f"  {name}: {p}")


if __name__ == "__main__":
    for nm, c in VAR.items():
        draw(nm, c)
    print("dimensioned layout maps done")
