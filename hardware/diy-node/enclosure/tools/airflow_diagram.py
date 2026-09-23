#!/usr/bin/env python3
"""Making Sense Bali DIY node — v10 AIRFLOW REVIEW diagram (current vs corrected).

Two side-view (Y x Z) schematics of the Plus node showing why the v10 air circulation
is wrong and how to fix it. Pure matplotlib, schematic (not to exact scale). Outputs
v10/review/v10_airflow_review.png.
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch, Polygon

OUT = os.path.join(os.path.dirname(__file__), "..", "v10", "review")
os.makedirs(OUT, exist_ok=True)

INK = "#1b2a3a"
COOL = "#2f8fb5"
HOT = "#c0392b"
PM = "#7a4fb5"
WALLC = "#c7d3df"
CAV = "#eef3f8"


def shell(ax):
    outer = [(-16, 3), (36, 3), (38, 32), (27, 62), (27 - 9, 97), (-16, 97)]
    ax.add_patch(Polygon(outer, closed=True, fc=WALLC, ec=INK, lw=1.4, zorder=1))
    inner = [(-13.5, 3), (33.5, 3), (35.5, 32), (24, 62), (24 - 9, 94), (-13.5, 94)]
    ax.add_patch(Polygon(inner, closed=True, fc=CAV, ec=INK, lw=0.5, zorder=2))


def comp(ax):
    ax.add_patch(Rectangle((-9.5, 21), 1.6, 60, fc="#c9a227", ec=INK, lw=0.6, alpha=0.5, zorder=3))
    ax.add_patch(Rectangle((-8, 60), 17.8, 17.8, fc="#2f6f4f", ec=INK, lw=0.6, zorder=3))
    ax.text(0.8, 69, "XIAO", color="white", fontsize=6.5, ha="center", va="center", weight="bold", zorder=4)
    ax.add_patch(Rectangle((-8, 23), 12.5, 12.5, fc="#b5651d", ec=INK, lw=0.6, zorder=3))
    ax.text(-1.7, 29, "BME", color="white", fontsize=6, ha="center", va="center", weight="bold", zorder=4)
    ax.add_patch(Rectangle((13, 18), 1.6, 40, fc=PM, ec=INK, lw=0.6, zorder=3))
    ax.add_patch(Rectangle((14.6, 26), 13, 24, fc=PM, ec=INK, lw=0.6, alpha=0.75, zorder=3))
    ax.text(21, 38, "HM3301\ncan", color="white", fontsize=6, ha="center", va="center", weight="bold", zorder=4)


def arrow(ax, p0, p1, color, lw=2.2, style="-|>"):
    ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle=style, mutation_scale=12, lw=lw, color=color, zorder=5))


fig, (axL, axR) = plt.subplots(1, 2, figsize=(13, 8.5))

# ---------- LEFT: v10 current (problems) ----------
axL.set_title("v10 NOW — what's wrong", fontsize=12, color=HOT, weight="bold")
shell(axL); comp(axL)
# big base intake (whole bottom), tiny high exhaust
axL.add_patch(Rectangle((-3, -2), 24, 5, fc=COOL, ec=INK, lw=0.8, zorder=3))
axL.text(9, -6, "huge base intake", color=COOL, fontsize=8, ha="center")
axL.add_patch(Rectangle((33, 80), 5, 9, fc=HOT, ec=INK, lw=0.8, zorder=3))
axL.text(45, 84, "tiny, low-ish\nexhaust", color=HOT, fontsize=8, ha="center")
# weak/stagnant flow
arrow(axL, (9, 0), (9, 22), COOL, 1.6, "-|>")
arrow(axL, (4, 40), (6, 30), "#888", 1.2, "<|-|>")   # recirculation eddy
axL.text(2, 48, "weak draw →\nnear-stagnant\ncolumn", color="#888", fontsize=8, ha="center")
# PM contamination
arrow(axL, (28, 40), (34, 44), PM, 1.8)
arrow(axL, (34, 36), (28, 33), PM, 1.8)
axL.text(40, 38, "HM in/out\nshort-circuit\n(no separation)", color=PM, fontsize=7.5, ha="center")
arrow(axL, (5, 70), (12, 45), HOT, 1.6)
axL.text(16, 60, "XIAO heat +\nHM heat mix\ninto BME air", color=HOT, fontsize=7.5, ha="left")
probs = ("1  big intake + small exhaust = throttled, mostly diffusion\n"
         "2  PM air merged with climate/MCU air (F-04 lost)\n"
         "3  HM3301 inlet/outlet not separated → recirculates\n"
         "4  XIAO + HM heat bias the BME680 T/RH")
axL.text(-17, -16, probs, fontsize=8, color=INK, va="top", family="monospace")

# ---------- RIGHT: corrected ----------
axR.set_title("Corrected — two separate air systems", fontsize=12, color="#1e7a3a", weight="bold")
shell(axR); comp(axR)
# baffle separating PM bay from climate column
axR.plot([10, 10], [3, 58], color=INK, lw=2.0, ls=(0, (4, 2)), zorder=4)
axR.text(10, 60, "baffle", color=INK, fontsize=7, ha="center")
# climate chimney: low intake by BME (left), HIGH balanced exhaust top
axR.add_patch(Rectangle((-13.5, -2), 12, 5, fc=COOL, ec=INK, lw=0.8, zorder=3))
axR.text(-7, -6, "low intake\n(by BME)", color=COOL, fontsize=8, ha="center")
axR.add_patch(Rectangle((-15, 86), 12, 7, fc=HOT, ec=INK, lw=0.8, zorder=3))
axR.text(-9, 96, "HIGH exhaust\n(area ≥ intake)", color=HOT, fontsize=8, ha="center")
arrow(axR, (-7, 0), (-6, 22), COOL, 2.2)
arrow(axR, (-3, 36), (-4, 60), COOL, 2.0)
arrow(axR, (-4, 64), (-8, 86), HOT, 2.2)
axR.text(-12, 50, "buoyancy\nchimney", color=INK, fontsize=8, ha="center", rotation=90)
# PM dedicated isolated duct: fresh in low-front, exhaust out separately
axR.add_patch(Rectangle((30, 14), 8, 4, fc=COOL, ec=INK, lw=0.8, zorder=3))
axR.text(46, 15, "PM fresh\nintake (down)", color=COOL, fontsize=7.5, ha="center")
axR.add_patch(Rectangle((30, 48), 8, 4, fc=PM, ec=INK, lw=0.8, zorder=3))
axR.text(46, 50, "PM exhaust\n(separate)", color=PM, fontsize=7.5, ha="center")
arrow(axR, (33, 16), (24, 30), COOL, 1.8)
arrow(axR, (24, 46), (33, 50), PM, 1.8)
axR.text(20, 8, "HM fan: fresh→can→out,\nisolated from the chimney", color=PM, fontsize=7.5, ha="center")
fixes = ("1  size exhaust ≥ intake, push it to the very top → real draw\n"
         "2  re-separate PM bay from climate column with a baffle\n"
         "3  HM3301 gets its own down intake + separate exhaust\n"
         "4  BME low in fresh intake, XIAO heat leaves high & away")
axR.text(-17, -16, fixes, fontsize=8, color=INK, va="top", family="monospace")

for ax in (axL, axR):
    ax.set_aspect("equal"); ax.axis("off"); ax.set_xlim(-22, 58); ax.set_ylim(-40, 105)

fig.suptitle("DIY node v10 — AIR CIRCULATION REVIEW (Plus, side view).  Schematic, not to scale.",
             fontsize=11, color=INK)
p = os.path.join(OUT, "v10_airflow_review.png")
fig.savefig(p, dpi=130, bbox_inches="tight")
plt.close(fig)
print(f"airflow diagram -> {p}")
