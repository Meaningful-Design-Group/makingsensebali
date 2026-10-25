# SPDX-License-Identifier: MIT
# Copyright 2026 Meaningful Design Group / Fab Lab Bali
# Source: https://github.com/Meaningful-Design-Group/makingsensebali
# Run: python3 proposal.py proposal.svg
"""The proposal to Seeed: a 3V3 / 5 V solder jumper on the UART socket and one I2C socket of
the Grove Shield for XIAO and the Expansion Base for XIAO."""
import sys
from xml.sax.saxutils import escape as esc

out = sys.argv[1]
W, H = 1100, 900
INK, MUTED, PAPER, LINE = "#1d2433", "#5b6475", "#fbfaf6", "#c9c4b6"
BOARD = "#1f2b45"
FIVE, FIVE_BG = "#9a5b00", "#fbeed6"
FONT = "Helvetica, Arial, sans-serif"

s = []
def add(x): s.append(x)
def text(x, y, t, size=14, fill=INK, weight="normal", anchor="start"):
    add(f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" font-weight="{weight}" text-anchor="{anchor}">{esc(t)}</text>')
def socket(x, y, name, hot):
    add(f'<rect x="{x}" y="{y}" width="60" height="70" rx="5" fill="{FIVE_BG if hot else "#3a4766"}" stroke="{FIVE if hot else "#d7d3c6"}" stroke-width="{3 if hot else 1}"/>')
    text(x + 30, y + 30, name, 14, FIVE if hot else "#c7cede", weight="bold", anchor="middle")
    text(x + 30, y + 50, "3V3 / 5V" if hot else "3V3", 12, FIVE if hot else "#c7cede", weight="bold" if hot else "normal", anchor="middle")

add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{FONT}">')
add(f'<rect width="{W}" height="{H}" fill="{PAPER}"/>')
text(30, 44, "5 V on two Grove sockets of the XIAO boards Seeed already makes", 24, weight="bold")
text(30, 70, "One solder jumper per socket, set to 3V3 out of the box. Highlighted: the sockets that get it.", 14, MUTED)

# Grove Shield for XIAO
text(40, 120, "Grove Shield for XIAO", 17, weight="bold")
add(f'<rect x="40" y="135" width="300" height="200" rx="14" fill="{BOARD}"/>')
add(f'<rect x="350" y="135" width="150" height="200" rx="14" fill="{BOARD}"/>')
add(f'<rect x="60" y="175" width="120" height="120" rx="8" fill="#e9ecf2" stroke="#9aa3b5"/>')
text(120, 240, "XIAO", 14, weight="bold", anchor="middle")
socket(195, 150, "D0", False); socket(265, 150, "D1", False)
socket(195, 250, "I2C", True); socket(265, 250, "UART", True)
socket(360, 150, "D2", False); socket(430, 150, "I2C", False)
socket(360, 250, "D8", False); socket(430, 250, "D9", False)

# Expansion Base for XIAO
text(580, 120, "Expansion Base for XIAO", 17, weight="bold")
add(f'<rect x="580" y="135" width="480" height="260" rx="20" fill="{BOARD}"/>')
add(f'<rect x="605" y="185" width="150" height="150" rx="8" fill="#e9ecf2" stroke="#9aa3b5"/>')
text(680, 265, "XIAO", 14, weight="bold", anchor="middle")
add(f'<rect x="790" y="215" width="100" height="100" rx="4" fill="#0b1020" stroke="#4a5873"/>')
text(840, 270, "OLED", 13, "#c7cede", anchor="middle")
socket(790, 140, "I2C", True); socket(870, 140, "I2C", False)
socket(790, 320, "A0/D0", False); socket(870, 320, "UART", True)
for r in range(4):
    for c in range(2):
        add(f'<rect x="{960 + 26 * c}" y="{220 + 24 * r}" width="12" height="12" rx="2" fill="#d9b44a"/>')
text(980, 330, "5V header", 12, "#c7cede", anchor="middle")
text(980, 200, "RTC", 12, "#c7cede", anchor="middle")

# the jumper
text(40, 460, "The jumper, on the back of each highlighted socket", 17, weight="bold")
jx, jy = 60, 500
for i, (lab, col) in enumerate((("3V3", "#ef7d00"), ("socket VCC", INK), ("5V, USB", "#d0312d"))):
    add(f'<rect x="{jx + i * 90}" y="{jy}" width="70" height="44" rx="6" fill="#d9b44a" stroke="{INK}"/>')
    text(jx + i * 90 + 35, jy + 70, lab, 13, col, weight="bold", anchor="middle")
add(f'<rect x="{jx + 62}" y="{jy + 14}" width="36" height="16" fill="#8a6d3b"/>')
text(jx + 80, jy + 100, "bridged to 3V3 as shipped", 13, MUTED, anchor="middle")
rules = [
    "Only the supply pin changes. SDA, SCL, RX and TX stay at the XIAO's 3.3 V,",
    "and the I2C pull-ups stay on 3V3.",
    "With 5 V selected, a sensor's fan or laser runs from USB 5 V directly, with",
    "no converter on the sensor board and no load on the XIAO's 3.3 V regulator.",
    "Silkscreen next to the jumper: a module that pulls its I2C lines up to its own",
    "VCC must not go in a socket set to 5 V. The ESP32 pins are not 5 V tolerant.",
]
for i, r in enumerate(rules):
    text(380, jy + 6 + i * 22, r, 14)

# what it unlocks
text(40, 680, "What plugs in with it", 17, weight="bold")
rows = [("Sensirion SEN54 or SEN55, bare", "I2C socket set to 5 V, through its JST GH cable"),
        ("Plantower PMS5003 or PMS5003T", "UART socket set to 5 V, through a Grove to 1.25 mm 8-pin cable"),
        ("Every Grove module, as today", "any socket left on 3V3")]
for i, (a, b) in enumerate(rows):
    y = 712 + i * 30
    text(40, y, a, 14, weight="bold")
    text(380, y, b, 14)

base = H - 52
add(f'<g font-family="{FONT}" font-size="13"><rect x="0" y="{base}" width="{W}" height="52" fill="#ffffff"/>'
    f'<line x1="0" y1="{base}" x2="{W}" y2="{base}" stroke="{LINE}"/>'
    f'<text x="20" y="{base+22}" fill="{INK}" font-weight="bold">Proposal to Seeed · 5 V on two Grove sockets · rev 2026-10-25</text>'
    f'<text x="20" y="{base+41}" fill="{MUTED}">CERN-OHL-W-2.0 · Meaningful Design Group / Fab Lab Bali · github.com/Meaningful-Design-Group/makingsensebali</text></g>')
add('</svg>')
open(out, "w").write("\n".join(s))
print("wrote", out)
