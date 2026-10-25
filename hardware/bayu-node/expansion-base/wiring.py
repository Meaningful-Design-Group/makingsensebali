# SPDX-License-Identifier: MIT
# Copyright 2026 Meaningful Design Group / Fab Lab Bali
# Source: https://github.com/Meaningful-Design-Group/makingsensebali
# Run: python3 wiring.py wiring.svg
"""Bayu v3 with three PM sensors on the Seeed Expansion Base for XIAO, no soldering:
Grove HM3301 and BME680 in the two I2C sockets, a bare SEN54 and a PMS5003 on jumper wires,
5 V from the board's own 5V pins. Net colours follow ../circuits/CONVENTIONS.md."""
import sys
from xml.sax.saxutils import escape as esc

out = sys.argv[1]
W, H = 1100, 1060
INK, MUTED, PAPER, LINE = "#1d2433", "#5b6475", "#fbfaf6", "#c9c4b6"
BOARD = "#1f2b45"
FONT = "Helvetica, Arial, sans-serif"
NET = {"5V": "#d0312d", "3V3": "#ef7d00", "GND": "#1d2433", "SDA": "#1f5fbf", "SCL": "#e6b400",
       "TX": "#4cae4f", "RX": "#1b6b3a"}
GROVE = "#9aa0aa"

s = []
def add(x): s.append(x)
def text(x, y, t, size=14, fill=INK, weight="normal", anchor="start"):
    add(f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" font-weight="{weight}" text-anchor="{anchor}">{esc(t)}</text>')
def wire(pts, net, w=3.5):
    d = " ".join(f"{x},{y}" for x, y in pts)
    add(f'<polyline points="{d}" fill="none" stroke="{PAPER}" stroke-width="{w+5}" stroke-linejoin="round"/>')
    if net == "SCL":
        add(f'<polyline points="{d}" fill="none" stroke="#8a7000" stroke-width="{w+1.6}" stroke-linejoin="round"/>')
    add(f'<polyline points="{d}" fill="none" stroke="{NET[net]}" stroke-width="{w}" stroke-linejoin="round"/>')
    for x, y in (pts[0], pts[-1]):
        add(f'<circle cx="{x}" cy="{y}" r="4" fill="{NET[net]}" stroke="#ffffff" stroke-width="1"/>')
def grove(pts):
    d = " ".join(f"{x},{y}" for x, y in pts)
    add(f'<polyline points="{d}" fill="none" stroke="#ffffff" stroke-width="12" stroke-linejoin="round"/>')
    add(f'<polyline points="{d}" fill="none" stroke="{GROVE}" stroke-width="8" stroke-linejoin="round"/>')
def box(x, y, w, h, title, sub=()):
    add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="#ffffff" stroke="{INK}" stroke-width="1.5"/>')
    if title:
        text(x + 12, y + 24, title, 15, weight="bold")
    for i, line in enumerate(sub):
        text(x + 12, y + 44 + i * 18, line, 13, MUTED)

add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{FONT}">')
add(f'<rect width="{W}" height="{H}" fill="{PAPER}"/>')
text(30, 44, "Bayu v3 with three PM sensors · Wiring on the Expansion Base for XIAO", 24, weight="bold")
text(30, 70, "XIAO ESP32-S3, Seeed Expansion Base, Grove BME680, Grove HM3301, Sensirion SEN54, Plantower PMS5003", 14, MUTED)
text(30, 94, "No soldering: the board breaks out every XIAO pin on female headers and has two 5 V points of its own.", 14, INK)

# ---------------- the Expansion Base ----------------
BX0, BY0, BX1, BY1 = 300, 230, 780, 560
add(f'<rect x="{BX0}" y="{BY0}" width="{BX1-BX0}" height="{BY1-BY0}" rx="22" fill="{BOARD}"/>')
# XIAO between two 2x7 female header blocks; the outer rows are the breakout
px = lambda i: 345 + 25 * i
TOP = ["5V", "GND", "3V3", "D10", "D9", "D8", "D7"]
BOT = ["D0", "D1", "D2", "D3", "D4", "D5", "D6"]
for i in range(7):
    for yy in (256, 278):
        add(f'<rect x="{px(i)-8}" y="{yy-8}" width="16" height="16" rx="2" fill="#0f1729" stroke="#4a5873"/>')
    for yy in (488, 510):
        add(f'<rect x="{px(i)-8}" y="{yy-8}" width="16" height="16" rx="2" fill="#0f1729" stroke="#4a5873"/>')
add(f'<rect x="{px(0)-14}" y="300" width="{px(6)-px(0)+28}" height="166" rx="8" fill="#e9ecf2" stroke="#9aa3b5"/>')
add(f'<rect x="{px(0)-28}" y="360" width="16" height="44" rx="4" fill="#9aa3b5"/>')
text((px(0) + px(6)) / 2, 370, "XIAO ESP32-S3", 14, weight="bold", anchor="middle")
text((px(0) + px(6)) / 2, 390, "plugs into the inner rows", 13, MUTED, anchor="middle")
text((px(0) + px(6)) / 2, 408, "Wio-SX1262 on top, optional", 13, MUTED, anchor="middle")
text(px(0) - 12, 248, "5V", 13, NET["5V"], weight="bold", anchor="end")
text(px(1) + 12, 246, "GND", 13, "#ffffff", weight="bold")
text(px(4) - 12, 534, "D4", 13, "#9ec1ff", weight="bold", anchor="end")
text(px(5) + 12, 534, "D5", 13, "#f2d36b", weight="bold")
# OLED
add(f'<rect x="545" y="320" width="100" height="120" rx="4" fill="#0b1020" stroke="#4a5873"/>')
text(595, 376, "OLED", 13, "#c7cede", weight="bold", anchor="middle")
text(595, 394, "I2C 0x3C", 12, "#c7cede", anchor="middle")
text(735, 262, "RTC 0x51", 12, "#c7cede", anchor="middle")
# Grove sockets
def socket(x, y, name, pins, used=True):
    add(f'<rect x="{x}" y="{y}" width="62" height="70" rx="5" fill="{"#f2f2ee" if used else "#3a4766"}" stroke="#d7d3c6"/>')
    col = INK if used else "#c7cede"
    text(x + 31, y + 22, name, 14, col, weight="bold", anchor="middle")
    for i, p in enumerate(pins):
        text(x + 31, y + 42 + i * 15, p, 12, col, anchor="middle")
socket(520, 236, "I2C", ["SCL SDA", "3V3"])
socket(600, 236, "I2C", ["SCL SDA", "3V3"])
socket(520, 478, "A0/D0", ["not used"], used=False)
socket(600, 478, "UART", ["RX D7", "TX D6"])
# right-hand 2x4 male header
HX = (712, 742)
HY = lambda r: 330 + 24 * r
LEFTC = ["SWCLK", "SWDIO", "3V3", "GND"]
RIGHTC = ["RX D7", "TX D6", "5V", "GND"]
for r in range(4):
    for c in range(2):
        add(f'<rect x="{HX[c]-6}" y="{HY(r)-6}" width="12" height="12" rx="2" fill="#d9b44a"/>')
text(HX[0] - 12, HY(0) + 4, "SWD", 12, "#c7cede", anchor="end")
text(HX[1] + 0, HY(3) + 30, "5V header", 12, "#c7cede", anchor="middle")
text(HX[0] - 14, HY(2) + 4, "3V3 · 5V", 12, "#c7cede", anchor="end")
text(HX[0] - 14, HY(3) + 4, "GND · GND", 12, "#c7cede", anchor="end")

# ---------------- sensors ----------------
box(320, 110, 170, 80, "HM3301", ["Grove module, 3V3"])
grove([(551, 236), (551, 150), (490, 150)])
box(660, 110, 170, 80, "BME680", ["Grove module, 3V3"])
grove([(631, 236), (631, 150), (660, 150)])
# PMS5003, connector on its left edge
PX, PY = 850, 230
box(PX, PY, 220, 210, "", ())
text(PX + 76, PY + 26, "PMS5003", 15, weight="bold")
for i, line in enumerate(["8-pin 1.25 mm cable", "to a 2.54 mm adapter", "fan 5 V, logic 3.3 V"]):
    text(PX + 76, PY + 48 + i * 18, line, 13, MUTED)
PINS = ["1 VCC", "2 GND", "3 SET", "4 RXD", "5 TXD", "6 RESET", "7 NC", "8 NC"]
pin_y = lambda i: PY + 22 + 18 * i
for i, lab in enumerate(PINS):
    add(f'<rect x="{PX-4}" y="{pin_y(i)-4}" width="8" height="8" fill="#d9b44a"/>')
    text(PX + 10, pin_y(i) + 5, lab, 12, INK if i in (0, 1, 3, 4) else MUTED)
# SEN54, connector along its top
SX0, SY0 = 40, 660
box(SX0, SY0, 300, 150, "", ())
SPINS = [("1", "VDD", 70), ("2", "GND", 110), ("3", "SDA", 150), ("4", "SCL", 190), ("5", "SEL", 230), ("6", "NC", 270)]
for n, lab, x in SPINS:
    add(f'<rect x="{x-4}" y="{SY0-4}" width="8" height="8" fill="#d9b44a"/>')
    text(x, SY0 + 22, n, 12, INK, anchor="middle")
    text(x, SY0 + 38, lab, 12, INK if n != "6" else MUTED, anchor="middle")
add(f'<path d="M110,{SY0+46} v8 h120 v-8" fill="none" stroke="{NET["GND"]}" stroke-width="2.5"/>')
text(SX0 + 12, SY0 + 82, "SEN54, bare module", 15, weight="bold")
for i, line in enumerate(["JST GH cable to 2.54 mm ends", "pins 2 and 5 joined: SEL to GND", "supply 5 V, I2C 0x69, logic 3.3 V"]):
    text(SX0 + 12, SY0 + 102 + i * 17, line, 13, MUTED)

# ---------------- wires ----------------
# SEN54 power from the left header's 5V and GND
wire([(px(1), 256), (px(1), 205), (52, 205), (52, 615), (110, 615), (110, SY0 - 4)], "GND")
wire([(px(0), 256), (px(0), 218), (40, 218), (40, 627), (70, 627), (70, SY0 - 4)], "5V")
# SEN54 I2C from D4 and D5 on the bottom breakout row
wire([(px(4), 510), (px(4), 598), (150, 598), (150, SY0 - 4)], "SDA")
wire([(px(5), 510), (px(5), 608), (190, 608), (190, SY0 - 4)], "SCL")
# PMS5003 power from the right header's 5V and GND
wire([(HX[1], HY(2)), (800, HY(2)), (800, pin_y(0)), (PX - 4, pin_y(0))], "5V")
wire([(HX[1], HY(3)), (812, HY(3)), (812, pin_y(1)), (PX - 4, pin_y(1))], "GND")
# PMS5003 data from the Grove UART socket
grove([(631, 548), (631, 572)])
add(f'<rect x="609" y="572" width="44" height="12" rx="3" fill="{GROVE}"/>')
wire([(640, 584), (640, 590), (824, 590), (824, pin_y(3)), (PX - 4, pin_y(3))], "TX")
wire([(622, 584), (622, 602), (836, 602), (836, pin_y(4)), (PX - 4, pin_y(4))], "RX")
text(850, 470, "Grove UART to female jumpers:", 13, INK)
text(850, 490, "yellow D7 to TXD", 13, NET["RX"], weight="bold")
text(850, 508, "white D6 to RXD", 13, NET["TX"], weight="bold")
text(850, 526, "red 3V3 and black GND not used", 13, MUTED)

# ---------------- legend ----------------
lx, ly = 400, 660
add(f'<rect x="{lx}" y="{ly}" width="380" height="140" rx="10" fill="#ffffff" stroke="{LINE}"/>')
text(lx + 16, ly + 26, "Nets", 15, weight="bold")
items = [("5V", "5V from USB"), ("GND", "GND"), ("SDA", "I2C SDA, D4"), ("SCL", "I2C SCL, D5"),
         ("TX", "UART TX, D6 to PMS RXD"), ("RX", "UART RX, D7 from PMS TXD")]
for i, (net, lab) in enumerate(items):
    yy = ly + 50 + (i % 3) * 22
    xx = lx + 16 + (i // 3) * 180
    if net == "SCL":
        add(f'<line x1="{xx}" y1="{yy-4}" x2="{xx+26}" y2="{yy-4}" stroke="#8a7000" stroke-width="5.5"/>')
    add(f'<line x1="{xx}" y1="{yy-4}" x2="{xx+26}" y2="{yy-4}" stroke="{NET[net]}" stroke-width="4"/>')
    text(xx + 34, yy, lab, 12)
add(f'<line x1="{lx+16}" y1="{ly+120}" x2="{lx+42}" y2="{ly+120}" stroke="{GROVE}" stroke-width="8"/>')
text(lx + 50, ly + 124, "Grove cable", 12)

notes = [
    "Male to male jumpers go into the board's female header holes. Use the outer row of each block: the inner row holds the XIAO.",
    "Each bare sensor gets its own 5 V point: the SEN54 from 5V and GND on the left header, the PMS5003 from 5V and GND on the right.",
    "The Grove HM3301 carries 4.7 kΩ I2C pull-ups (Seeed's schematic), so the bare SEN54 needs none. Keep its I2C wires under 10 cm.",
    "PMS5003 SET stays unconnected here: D2 is the microSD chip select on this board. The Bayu firmware v5 never drives SET anyway.",
    "On board, also on the bus or on XIAO pins: the user button on D1, the buzzer on D3, the microSD on the back with its chip select on D2.",
    "Where a wire crosses another with a gap, they are not connected.",
]
for i, n in enumerate(notes):
    text(30, 852 + i * 22, n, 13)

base = H - 52
add(f'<g font-family="{FONT}" font-size="13"><rect x="0" y="{base}" width="{W}" height="52" fill="#ffffff"/>'
    f'<line x1="0" y1="{base}" x2="{W}" y2="{base}" stroke="{LINE}"/>'
    f'<text x="20" y="{base+22}" fill="{INK}" font-weight="bold">Bayu v3 with three PM sensors · Wiring on the Expansion Base · rev 2026-10-25</text>'
    f'<text x="20" y="{base+41}" fill="{MUTED}">CERN-OHL-W-2.0 · Meaningful Design Group / Fab Lab Bali · github.com/Meaningful-Design-Group/makingsensebali</text></g>')
add('</svg>')
open(out, "w").write("\n".join(s))
print("wrote", out)
