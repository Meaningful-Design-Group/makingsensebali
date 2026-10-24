# SPDX-License-Identifier: MIT
# Copyright 2026 Meaningful Design Group / Fab Lab Bali
# Source: https://github.com/Meaningful-Design-Group/makingsensebali
# Run: python3 concept.py concept.svg
"""Generate hardware/bayu-node/grove-shield-mini/concept.svg: the proposed Grove Shield Mini
for XIAO, top and bottom views at 12 px per mm, plus its pin plan."""
import sys
from xml.sax.saxutils import escape as esc

out = sys.argv[1]
W, H = 1160, 1072
INK, MUTED, PAPER, LINE = "#1d2433", "#5b6475", "#fbfaf6", "#c9c4b6"
BOARD = "#1f2b45"
NEW, NEW_BG = "#1f7a4d", "#e3f2e9"
FIVE, FIVE_BG = "#9a5b00", "#fbeed6"
FONT = "Helvetica, Arial, sans-serif"
MM = 12  # px per mm

s = []
def add(x): s.append(x)
def text(x, y, t, size=14, fill=INK, weight="normal", anchor="start"):
    add(f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" font-weight="{weight}" text-anchor="{anchor}">{esc(t)}</text>')

add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{FONT}">')
add(f'<rect width="{W}" height="{H}" fill="{PAPER}"/>')
text(40, 48, "Grove Shield Mini for XIAO, a proposal", 26, weight="bold")
text(40, 74, "Four Grove sockets, a real-time clock and a microSD slot, on the 39 × 25 mm the snapped Grove Shield already has.", 15, MUTED)

BW, BH = 39*MM, 25*MM  # 468 x 300

def board(x, y, title):
    text(x, y-14, title, 16, weight="bold")
    add(f'<rect x="{x}" y="{y}" width="{BW}" height="{BH}" rx="16" fill="{BOARD}"/>')
    for hx, hy in ((x+14, y+14), (x+BW-14, y+BH-14)):
        add(f'<circle cx="{hx}" cy="{hy}" r="7" fill="{PAPER}" stroke="#9aa3b5"/>')
    # dimension lines
    add(f'<line x1="{x}" y1="{y+BH+22}" x2="{x+BW}" y2="{y+BH+22}" stroke="{MUTED}"/>')
    text(x+BW/2, y+BH+40, "39 mm", 12, MUTED, anchor="middle")
    add(f'<line x1="{x+BW+18}" y1="{y}" x2="{x+BW+18}" y2="{y+BH}" stroke="{MUTED}"/>')
    text(x+BW+26, y+BH/2+4, "25", 12, MUTED)

# ---------- top view ----------
tx, ty = 40, 130
board(tx, ty, "Top")
# XIAO footprint 21 x 17.5 mm, USB-C at the left edge
xw, xh = 21*MM, int(17.5*MM)
xx, xy = tx+10, ty+(BH-xh)//2
add(f'<rect x="{xx-14}" y="{xy+xh/2-24}" width="30" height="48" rx="6" fill="#9aa3b5"/>')
add(f'<rect x="{xx+8}" y="{xy}" width="{xw-8}" height="{xh}" rx="10" fill="#e9ecf2" stroke="#9aa3b5"/>')
for i in range(7):
    px = xx + 22 + i*32
    add(f'<rect x="{px}" y="{xy-10}" width="14" height="12" rx="3" fill="#d9b44a"/>')
    add(f'<rect x="{px}" y="{xy+xh-2}" width="14" height="12" rx="3" fill="#d9b44a"/>')
text(xx+xw/2+4, xy+90, "XIAO ESP32-S3", 16, weight="bold", anchor="middle")
text(xx+xw/2+4, xy+112, "Wio-SX1262 on top,", 12, MUTED, anchor="middle")
text(xx+xw/2+4, xy+128, "25 mm clear above", 12, MUTED, anchor="middle")
# sockets 2 x 2
def sock(x, y, name, sub, five=False):
    w, h = 92, 128
    add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="#f2f2ee" stroke="#d7d3c6"/>')
    for i in range(4):
        add(f'<rect x="{x+8}" y="{y+10+i*13}" width="16" height="7" rx="2" fill="#b9b3a2"/>')
    text(x+30, y+22, name[:2], 15, weight="bold")
    text(x+30, y+40, name[3:], 13, INK, weight="bold")
    for i, part in enumerate(sub.split(" · ")):
        text(x+8, y+70+i*15, part, 12, INK)
    if five:
        add(f'<rect x="{x+6}" y="{y+94}" width="{w-12}" height="26" rx="5" fill="{FIVE_BG}"/>')
        text(x+w/2, y+112, "3V3 / 5V", 12, FIVE, weight="bold", anchor="middle")
    else:
        text(x+w/2, y+112, "3V3", 12, MUTED, anchor="middle")
sx = tx + 262
sock(sx,      ty+14,  "G1 I2C",  "SCL D5 · SDA D4", five=True)
sock(sx+100,  ty+14,  "G2 I2C",  "SCL D5 · SDA D4")
sock(sx,      ty+156, "G3 UART", "RX D7 · TX D6", five=True)
sock(sx+100,  ty+156, "G4 A/D",  "A2/D2 · A3/D3")
# button
add(f'<rect x="{tx+16}" y="{ty+BH-30}" width="22" height="18" rx="3" fill="#cfd5e2"/>')
text(tx+44, ty+BH-16, "button D0", 11, "#c7cede")

# ---------- bottom view ----------
bx, by = 620, 130
board(bx, by, "Bottom (seen from below)")
# microSD 15 x 14.5 mm
add(f'<rect x="{bx+24}" y="{by+40}" width="{15*MM}" height="{int(14.5*MM)}" rx="6" fill="#c7cede" stroke="#9aa3b5"/>')
text(bx+24+15*MM/2, by+110, "microSD", 16, weight="bold", anchor="middle")
text(bx+24+15*MM/2, by+130, "SPI D8–D10", 12, INK, anchor="middle")
text(bx+24+15*MM/2, by+146, "CS on D1", 12, INK, anchor="middle")
# CR1220 holder, 13 mm
cx, cy = bx+330, by+118
add(f'<circle cx="{cx}" cy="{cy}" r="{6.5*MM}" fill="#c7cede" stroke="#9aa3b5"/>')
text(cx, cy-6, "CR1220", 15, weight="bold", anchor="middle")
text(cx, cy+14, "RTC backup", 12, INK, anchor="middle")
# RTC chip and jumpers
add(f'<rect x="{bx+250}" y="{by+222}" width="40" height="40" rx="4" fill="#3b4a6a" stroke="#9aa3b5"/>')
text(bx+300, by+240, "PCF8563 RTC", 12, "#e9ecf2", weight="bold")
text(bx+300, by+256, "I2C 0x51", 12, "#c7cede")
add(f'<rect x="{bx+24}" y="{by+232}" width="34" height="16" rx="3" fill="{FIVE_BG}"/>')
add(f'<rect x="{bx+64}" y="{by+232}" width="34" height="16" rx="3" fill="{FIVE_BG}"/>')
text(bx+106, by+245, "JP1 JP2, 3V3/5V", 12, "#e9ecf2")
text(bx+24, by+276, "4.7 kΩ pull-ups to 3V3 on SDA, SCL", 12, "#c7cede")

# ---------- pin plan ----------
px, py = 40, 520
text(px, py, "Pin plan", 18, weight="bold")
rows = [
    ("D0", "GPIO1", "user button", ""),
    ("D1", "GPIO2", "microSD chip select", "new"),
    ("D2", "GPIO3", "G4 pin 1, PMS5003 SET", ""),
    ("D3", "GPIO4", "G4 pin 2, analog in (battery, any analog Grove)", ""),
    ("D4, D5", "GPIO5, 6", "I2C: G1, G2 and the RTC", ""),
    ("D6, D7", "GPIO43, 44", "UART: G3", ""),
    ("D8 to D10", "GPIO7, 8, 9", "SPI: microSD and the Wio-SX1262, each on its own CS", "new"),
    ("—", "GPIO38 to 42", "LoRa control, board-to-board connector only", ""),
]
cw = (110, 130, 470)
y = py + 18
add(f'<rect x="{px}" y="{y}" width="{sum(cw)}" height="34" rx="6" fill="{INK}"/>')
for i, h in enumerate(("XIAO pin", "GPIO", "Job on the Mini")):
    text(px + 12 + sum(cw[:i]), y+23, h, 13, "#ffffff", weight="bold")
for r, (a, b, c, tag) in enumerate(rows):
    yy = y + 34 + r*34
    add(f'<rect x="{px}" y="{yy}" width="{sum(cw)}" height="34" fill="{"#ffffff" if r%2==0 else "#f4f2ec"}"/>')
    text(px+12, yy+22, a, 13, weight="bold")
    text(px+12+cw[0], yy+22, b, 13, MUTED)
    text(px+12+cw[0]+cw[1], yy+22, c, 13, NEW if tag else INK)
add(f'<rect x="{px}" y="{y}" width="{sum(cw)}" height="{34+len(rows)*34}" rx="6" fill="none" stroke="{LINE}"/>')

# ---------- what changes ----------
cx0, cy0 = 790, 520
text(cx0, cy0, "Compared with the Grove Shield", 18, weight="bold")
changes = [
    ("Same", "XIAO footprint, 3V3 Grove pinout, all 14 pins"),
    ("", "broken out, the snapped size of 39 × 25 mm."),
    ("New", "Second I2C and an A/D socket where the"),
    ("", "shield's left half has D0 and D1 sockets."),
    ("New", "PCF8563 clock with a coin cell, so a node"),
    ("", "with no WiFi still timestamps its data."),
    ("New", "microSD on the back, to buffer readings"),
    ("", "when the uplink is down."),
    ("New", "G1 and G3 switch to 5 V for PM sensor fans."),
    ("", "Logic stays 3.3 V, pull-ups go to 3V3."),
    ("Gone", "Battery charger and the D8, D9 sockets that"),
    ("", "the LoRa radio takes anyway."),
]
for i, (tag, line) in enumerate(changes):
    yy = cy0 + 34 + i*22
    if tag:
        col = NEW if tag == "New" else (MUTED if tag == "Same" else FIVE)
        text(cx0, yy, tag, 13, col, weight="bold")
    text(cx0+50, yy, line, 13)

ny = 880
note = [
    "Every Bayu variant becomes plug and play on this board, including the PMS5003 nodes, once there is a Grove to",
    "1.25 mm 8-pin cable for the Plantower. The microSD and the LoRa radio share one SPI bus with separate chip selects,",
    "which the firmware has to handle. The 5 V jumpers only switch the supply pin, so a 5 V module that pulls its own",
    "I2C lines up to 5 V would still be unsafe for the ESP32-S3 and must not go in G1 set to 5 V.",
    "",
    "Concept drawing, not a layout. Sizes at 12 px per mm for the board, the XIAO, the microSD socket and the coin cell.",
]
for i, n in enumerate(note):
    text(40, ny + i*22, n, 13, MUTED if i == len(note)-1 else INK)
# footer stamp: what this is, revision, licence, source
add(f'<g font-family="{FONT}" font-size="13"><rect x="0" y="1020" width="{W}" height="52" fill="#ffffff"/>'
    f'<line x1="0" y1="1020" x2="{W}" y2="1020" stroke="{LINE}"/>'
    f'<text x="20" y="1042" fill="{INK}" font-weight="bold">Grove Shield Mini for XIAO · concept · rev 2026-10-24</text>'
    f'<text x="20" y="1061" fill="{MUTED}">CERN-OHL-W-2.0 · Meaningful Design Group / Fab Lab Bali · github.com/Meaningful-Design-Group/makingsensebali</text></g>')
add('</svg>')
open(out, "w").write("\n".join(s))
print("wrote", out)
