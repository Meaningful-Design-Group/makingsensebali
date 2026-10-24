# SPDX-License-Identifier: MIT
# Copyright 2026 Meaningful Design Group / Fab Lab Bali
# Source: https://github.com/Meaningful-Design-Group/makingsensebali
# Run: python3 wiring.py wiring.svg
"""Bayu v3 on the Seeed Grove Shield for XIAO with three PM sensors: Grove HM3301, a bare
Sensirion SEN54 and a Plantower PMS5003, plus the Grove BME680. Net colours follow
../../circuits/CONVENTIONS.md."""
import sys
from xml.sax.saxutils import escape as esc

out = sys.argv[1]
W, H = 1100, 1124
INK, MUTED, PAPER, LINE = "#1d2433", "#5b6475", "#fbfaf6", "#c9c4b6"
BOARD = "#1f2b45"
FONT = "Helvetica, Arial, sans-serif"
NET = {"5V": "#d0312d", "3V3": "#ef7d00", "GND": "#1d2433", "SDA": "#1f5fbf", "SCL": "#e6b400",
       "TX": "#4cae4f", "RX": "#1b6b3a", "SET": "#7a3fb3"}
GROVE = "#9aa0aa"

s = []
def add(x): s.append(x)
def text(x, y, t, size=14, fill=INK, weight="normal", anchor="start"):
    add(f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" font-weight="{weight}" text-anchor="{anchor}">{esc(t)}</text>')
def wire(pts, net, w=3.5, dash=None):
    d = " ".join(f"{x},{y}" for x, y in pts)
    extra = f' stroke-dasharray="{dash}"' if dash else ""
    outline = ' stroke="#7a6400"' if net == "SCL" else ""
    if net == "SCL":
        add(f'<polyline points="{d}" fill="none" stroke="#8a7000" stroke-width="{w+1.6}" stroke-linejoin="round"/>')
    add(f'<polyline points="{d}" fill="none" stroke="{NET[net]}" stroke-width="{w}" stroke-linejoin="round"{extra}/>')
    for x, y in (pts[0], pts[-1]):
        add(f'<circle cx="{x}" cy="{y}" r="4" fill="{NET[net]}" stroke="#ffffff" stroke-width="1"/>')
def grove(pts):
    d = " ".join(f"{x},{y}" for x, y in pts)
    add(f'<polyline points="{d}" fill="none" stroke="#ffffff" stroke-width="12" stroke-linejoin="round"/>')
    add(f'<polyline points="{d}" fill="none" stroke="{GROVE}" stroke-width="8" stroke-linejoin="round"/>')
def box(x, y, w, h, title, sub=None, fill="#ffffff", dash=None):
    extra = f' stroke-dasharray="{dash}"' if dash else ""
    add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{fill}" stroke="{INK}" stroke-width="1.5"{extra}/>')
    text(x + 12, y + 24, title, 15, weight="bold")
    if sub:
        for i, line in enumerate(sub):
            text(x + 12, y + 44 + i * 18, line, 13, MUTED)

add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{FONT}">')
add(f'<rect width="{W}" height="{H}" fill="{PAPER}"/>')
text(30, 44, "Bayu v3 with three PM sensors · Wiring on the Grove Shield", 24, weight="bold")
text(30, 70, "XIAO ESP32-S3, Grove Shield for XIAO, Grove BME680, Grove HM3301, Sensirion SEN54, Plantower PMS5003", 14, MUTED)
text(30, 94, "Grey bands are Grove cables. Thin lines are jumper wires, one colour per net as on every Bayu sheet.", 14, INK)
text(30, 114, "5 V comes from the shield's 5V pin and a mini breadboard shares it between the SEN54 and the PMS5003.", 14, INK)

# ---------------- mini breadboard (power junction) ----------------
bx, by, bw, bh = 70, 180, 260, 110
add(f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="8" fill="#f4f1e8" stroke="{INK}" stroke-width="1.5"/>')
text(bx, by + bh + 20, "Mini breadboard, power rows", 14, weight="bold")
for ry, net, lab in ((220, "5V", "5V row"), (250, "GND", "GND row")):
    add(f'<line x1="{bx+15}" y1="{ry}" x2="{bx+bw-15}" y2="{ry}" stroke="{NET[net]}" stroke-width="2" stroke-dasharray="2 6"/>')
    text(bx + 150, ry - 6, lab, 13, NET[net] if net == "5V" else INK, weight="bold")

# ---------------- the shield ----------------
L0, L1, R0, R1, SY, SH = 330, 620, 630, 770, 380, 200
add(f'<rect x="{L0}" y="{SY}" width="{L1-L0}" height="{SH}" rx="14" fill="{BOARD}"/>')
add(f'<rect x="{R0}" y="{SY}" width="{R1-R0}" height="{SH}" rx="14" fill="{BOARD}"/>')

# XIAO
xx, xy, xw, xh = 345, 410, 140, 140
add(f'<rect x="{xx-14}" y="{xy+50}" width="20" height="40" rx="5" fill="#9aa3b5"/>')
add(f'<rect x="{xx}" y="{xy}" width="{xw}" height="{xh}" rx="8" fill="#e9ecf2" stroke="#9aa3b5"/>')
text(xx + xw / 2, xy + 66, "XIAO ESP32-S3", 14, weight="bold", anchor="middle")
text(xx + xw / 2, xy + 84, "Wio-SX1262 on top", 13, MUTED, anchor="middle")
text(xx + xw / 2, xy + 100, "optional", 13, MUTED, anchor="middle")
# breakout header rows, male pins soldered in
TOP = ["5V", "GND", "3V3", "D10", "D9", "D8", "D7"]
BOT = ["D0", "D1", "D2", "D3", "D4", "D5", "D6"]
px = lambda i: 357 + 20 * i
for i, lab in enumerate(TOP):
    add(f'<rect x="{px(i)-5}" y="{SY+6}" width="10" height="10" rx="2" fill="#d9b44a"/>')
for i, lab in enumerate(BOT):
    add(f'<rect x="{px(i)-5}" y="{SY+SH-16}" width="10" height="10" rx="2" fill="#d9b44a"/>')
text(px(0) - 7, SY - 4, "5V", 13, NET["5V"], weight="bold", anchor="end")
text(px(1) + 7, SY - 4, "GND", 13, INK, weight="bold")
text(px(4) - 7, SY + SH + 18, "D4", 13, NET["SDA"], weight="bold", anchor="end")
text(px(5) + 7, SY + SH + 18, "D5", 13, "#8a7000", weight="bold")

def socket(x, y, name, pins, used=True):
    w, h = 54, 80
    add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="5" fill="{"#f2f2ee" if used else "#3a4766"}" stroke="#d7d3c6"/>')
    col = INK if used else "#c7cede"
    text(x + w / 2, y + 22, name, 14, col, weight="bold", anchor="middle")
    for i, p in enumerate(pins):
        text(x + w / 2, y + 44 + i * 16, p, 12, col if used else "#c7cede", anchor="middle")
SKT = {"D0": (495, 395), "D1": (557, 395), "I2C_A": (495, 487), "UART": (557, 487),
       "D2": (640, 395), "I2C_B": (707, 395), "D8": (640, 487), "D9": (707, 487)}
socket(*SKT["D0"], "D0", ["", ""], used=False)
socket(*SKT["D1"], "D1", ["", ""], used=False)
socket(*SKT["I2C_A"], "I2C", ["SCL", "SDA"])
socket(*SKT["UART"], "UART", ["RX D7", "TX D6"])
socket(*SKT["D2"], "D2", ["SET", "optional"], used=False)
socket(*SKT["I2C_B"], "I2C", ["SCL", "SDA"])
socket(*SKT["D8"], "D8", ["", ""], used=False)
socket(*SKT["D9"], "D9", ["", ""], used=False)

# ---------------- sensors ----------------
# BME680 above the right-hand I2C socket
box(590, 190, 170, 110, "BME680", ["Grove module", "I2C 0x76 or 0x77", "3V3 from the socket"])
grove([(SKT["I2C_B"][0] + 27, SKT["I2C_B"][1]), (SKT["I2C_B"][0] + 27, 300)])
# PMS5003 top right, connector on its left edge
PX, PY = 840, 170
box(PX, PY, 230, 190, "", None)
text(PX + 70, PY + 26, "PMS5003", 15, weight="bold")
for line_i, line in enumerate(["8-pin 1.25 mm cable", "to a 2.54 mm adapter", "fan 5 V, logic 3.3 V", "~100 mA"]):
    text(PX + 70, PY + 48 + line_i * 18, line, 13, MUTED)
PINS = ["1 VCC", "2 GND", "3 SET", "4 RXD", "5 TXD", "6 RESET", "7 NC", "8 NC"]
pin_y = lambda i: 190 + 18 * i
for i, lab in enumerate(PINS):
    add(f'<rect x="{PX-4}" y="{pin_y(i)-4}" width="8" height="8" fill="#d9b44a"/>')
    text(PX + 10, pin_y(i) + 5, lab, 12, INK if i < 5 else MUTED)
# SEN54 bottom left, connector along its top
SX0, SY0 = 40, 660
box(SX0, SY0, 300, 130, "", None)
text(SX0 + 12, SY0 + 70, "SEN54, bare module", 15, weight="bold")
for i, line in enumerate(["JST GH 6-pin cable to 2.54 mm ends", "supply 5 V, I2C 0x69, logic 3.3 V", "SEL to GND selects I2C"]):
    text(SX0 + 12, SY0 + 90 + i * 17, line, 13, MUTED)
SPINS = [("1 VDD", 70), ("2 GND", 110), ("3 SDA", 150), ("4 SCL", 190), ("5 SEL", 230), ("6 NC", 270)]
for lab, x in SPINS:
    add(f'<rect x="{x-4}" y="{SY0-4}" width="8" height="8" fill="#d9b44a"/>')
    text(x, SY0 + 22, lab.split()[0], 12, INK, anchor="middle")
    text(x, SY0 + 38, lab.split()[1], 12, INK if lab != "6 NC" else MUTED, anchor="middle")
# SEL bridged to GND on the cable
add(f'<path d="M110,{SY0+44} v8 h120 v-8" fill="none" stroke="{NET["GND"]}" stroke-width="2.5"/>')
text(170, SY0 + 64, "", 12)
# HM3301 under the left-hand I2C socket
box(420, 660, 230, 110, "HM3301", ["Grove module", "I2C 0x40", "3V3 from the socket"])
grove([(SKT["I2C_A"][0] + 27, SKT["I2C_A"][1] + 80), (SKT["I2C_A"][0] + 27, 660)])

# ---------------- power ----------------
# shield 5V and GND pins up to the breadboard rows
wire([(px(0), SY + 6), (px(0), 340), (300, 340), (300, 220)], "5V")
wire([(px(1), SY + 6), (px(1), 320), (310, 320), (310, 250)], "GND")
# breadboard to the PMS5003 VCC and GND, over the top
wire([(120, 220), (120, 150), (825, 150), (825, pin_y(0)), (PX - 4, pin_y(0))], "5V")
wire([(135, 250), (135, 160), (815, 160), (815, pin_y(1)), (PX - 4, pin_y(1))], "GND")
# breadboard to the SEN54 VDD and GND, down the left edge
wire([(85, 220), (40, 220), (40, 625), (70, 625), (70, SY0 - 4)], "5V")
wire([(85, 250), (52, 250), (52, 615), (110, 615), (110, SY0 - 4)], "GND")

# ---------------- SEN54 I2C from the D4 and D5 header pins ----------------
wire([(px(4), SY + SH - 6), (px(4), 605), (150, 605), (150, SY0 - 4)], "SDA")
wire([(px(5), SY + SH - 6), (px(5), 615), (190, 615), (190, SY0 - 4)], "SCL")

# ---------------- PMS5003 data from the Grove UART socket ----------------
ux = SKT["UART"][0]
grove([(ux + 27, SKT["UART"][1] + 80), (ux + 27, 585)])
add(f'<rect x="{ux+5}" y="585" width="44" height="12" rx="3" fill="{GROVE}"/>')
text(ux + 60, 594, "", 12)
wire([(ux + 30, 597), (ux + 30, 600), (795, 600), (795, pin_y(3)), (PX - 4, pin_y(3))], "TX")
wire([(ux + 20, 597), (ux + 20, 610), (805, 610), (805, pin_y(4)), (PX - 4, pin_y(4))], "RX")
text(812, 452, "Grove UART to", 13, INK)
text(812, 470, "female jumpers:", 13, INK)
text(812, 490, "yellow D7 to TXD", 13, NET["RX"], weight="bold")
text(812, 508, "white D6 to RXD", 13, NET["TX"], weight="bold")
text(812, 526, "red 3V3 not used", 13, MUTED)
text(812, 544, "black GND not needed", 13, MUTED)

# ---------------- legend ----------------
lx, ly = 680, 660
add(f'<rect x="{lx}" y="{ly}" width="390" height="160" rx="10" fill="#ffffff" stroke="{LINE}"/>')
text(lx + 16, ly + 26, "Nets", 15, weight="bold")
items = [("5V", "5V, from USB through the shield"), ("GND", "GND"), ("SDA", "I2C SDA, D4"),
         ("SCL", "I2C SCL, D5"), ("TX", "UART TX, D6 to PMS RXD"), ("RX", "UART RX, D7 from PMS TXD")]
for i, (net, lab) in enumerate(items):
    yy = ly + 50 + i * 18
    if net == "SCL":
        add(f'<line x1="{lx+16}" y1="{yy-4}" x2="{lx+46}" y2="{yy-4}" stroke="#8a7000" stroke-width="5.5"/>')
    add(f'<line x1="{lx+16}" y1="{yy-4}" x2="{lx+46}" y2="{yy-4}" stroke="{NET[net]}" stroke-width="4"/>')
    text(lx + 56, yy, lab, 13)
add(f'<line x1="{lx+250}" y1="{ly+68}" x2="{lx+280}" y2="{ly+68}" stroke="{GROVE}" stroke-width="8"/>')
text(lx + 288, ly + 72, "Grove cable", 13)

# ---------------- notes ----------------
notes = [
    "Solder a 1×7 male header into each row of holes beside the XIAO: the top row gives 5V and GND, the bottom row D4 and D5.",
    "Keep the Grove Shield whole. The second I2C socket, for the BME680, is on the half that snaps off.",
    "Bayu firmware v5 finds all four sensors at boot and publishes each PM sensor on its own channels, so the three can be compared.",
    "The SEN54 has no Grove plug. Keep its I2C wires under 10 cm, as Sensirion asks, and bridge SEL (pin 5) to GND (pin 2) on the cable.",
    "Grove modules usually carry I2C pull-ups and the bare SEN54 has none. With the board unpowered, measure SDA to 3V3: about 10 kΩ",
    "or less means pull-ups are there. If not, add 4.7 kΩ from SDA and SCL to 3V3 on the breadboard.",
    "PMS5003 SET (pin 3) can stay unconnected: Bayu firmware v5 never drives it and the fan runs all the time. For the Meshtastic build,",
    "run SET to pin 1 of the D2 socket so the fan can sleep between readings. RESET, pins 7 and 8 stay open.",
    "5 V load: SEN54 up to 100 mA and PMS5003 about 100 mA. Use a 5 V / 2 A USB-C supply, not a laptop port.",
    "For a fair comparison put the three inlets at the same height, side by side, none of them in another sensor's exhaust.",
]
for i, n in enumerate(notes):
    text(30, 852 + i * 22, n, 13)

base = H - 52
add(f'<g font-family="{FONT}" font-size="13"><rect x="0" y="{base}" width="{W}" height="52" fill="#ffffff"/>'
    f'<line x1="0" y1="{base}" x2="{W}" y2="{base}" stroke="{LINE}"/>'
    f'<text x="20" y="{base+22}" fill="{INK}" font-weight="bold">Bayu v3 with three PM sensors · Wiring on the Grove Shield · rev 2026-10-24</text>'
    f'<text x="20" y="{base+41}" fill="{MUTED}">CERN-OHL-W-2.0 · Meaningful Design Group / Fab Lab Bali · github.com/Meaningful-Design-Group/makingsensebali</text></g>')
add('</svg>')
open(out, "w").write("\n".join(s))
print("wrote", out)
