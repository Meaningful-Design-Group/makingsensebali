# SPDX-License-Identifier: MIT
# Copyright 2026 Meaningful Design Group / Fab Lab Bali
# Source: https://github.com/Meaningful-Design-Group/makingsensebali
# Run: python3 grove_shield_map.py grove-shield-map.svg
"""Generate hardware/bayu-node/grove/grove-shield-map.svg: the Seeed Grove Shield for XIAO
socket map, and which module goes in which socket for each Bayu variant."""
import sys
from xml.sax.saxutils import escape as esc

out = sys.argv[1]
W, H = 1200, 1112
INK, MUTED, PAPER, LINE = "#1d2433", "#5b6475", "#fbfaf6", "#c9c4b6"
BOARD, BOARD2 = "#1f2b45", "#2a3a5c"
GREEN, GREEN_BG = "#1f7a4d", "#e3f2e9"
AMBER, AMBER_BG = "#9a5b00", "#fbeed6"
LORA_BG = "#efe9f7"
FONT = "Helvetica, Arial, sans-serif"

s = []
def add(x): s.append(x)
def text(x, y, t, size=14, fill=INK, weight="normal", anchor="start", style=""):
    add(f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" font-weight="{weight}" '
        f'text-anchor="{anchor}" {style}>{esc(t)}</text>')

add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{FONT}">')
add(f'<rect width="{W}" height="{H}" fill="{PAPER}"/>')
text(40, 48, "Bayu on the Seeed Grove Shield for XIAO", 26, weight="bold")
text(40, 74, "Which module goes in which socket, for each variant. Every socket on this shield is powered at 3V3.", 15, MUTED)

# ---------- the shield ----------
ox, oy = 40, 100
# left half (keeps the XIAO) and right half (snaps off)
add(f'<rect x="{ox}" y="{oy}" width="470" height="300" rx="18" fill="{BOARD}"/>')
add(f'<rect x="{ox+482}" y="{oy}" width="250" height="300" rx="18" fill="{BOARD}"/>')
add(f'<line x1="{ox+476}" y1="{oy-8}" x2="{ox+476}" y2="{oy+308}" stroke="{MUTED}" stroke-dasharray="6 5" stroke-width="2"/>')
text(ox+476, oy+326, "snap line", 12, MUTED, anchor="middle")

# XIAO
xx, xy = ox+30, oy+60
add(f'<rect x="{xx-22}" y="{xy+70}" width="34" height="44" rx="6" fill="#9aa3b5"/>')  # USB-C
add(f'<rect x="{xx}" y="{xy}" width="190" height="184" rx="10" fill="#e9ecf2" stroke="#9aa3b5"/>')
for i in range(7):
    px = xx + 18 + i*26
    add(f'<rect x="{px}" y="{xy-14}" width="14" height="14" rx="3" fill="#d9b44a"/>')
    add(f'<rect x="{px}" y="{xy+184}" width="14" height="14" rx="3" fill="#d9b44a"/>')
text(xx+95, xy+80, "XIAO ESP32-S3", 17, weight="bold", anchor="middle")
text(xx+95, xy+102, "Wio-SX1262 clips on top", 13, MUTED, anchor="middle")
text(xx+95, xy+120, "header in the XIAO only", 13, MUTED, anchor="middle")
# 5V header callout
text(xx, oy+22, "5V · GND · 3V3 header pins along this edge", 12, "#c7cede")

def socket(x, y, name, pins, lora=False, accent="#f2f2ee"):
    w, h = 104, 118
    if lora:
        add(f'<rect x="{x-6}" y="{y-6}" width="{w+12}" height="{h+12}" rx="10" fill="none" stroke="#8a6cc2" stroke-width="3" stroke-dasharray="7 4"/>')
    add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{accent}" stroke="#d7d3c6"/>')
    for i in range(4):
        add(f'<rect x="{x+10}" y="{y+12+i*14}" width="18" height="8" rx="2" fill="#b9b3a2"/>')
    text(x+36, y+28, name, 17, weight="bold")
    text(x+36, y+46, "3V3", 12, MUTED)
    for i, p in enumerate(pins):
        text(x+10, y+84+i*16, p, 12, INK)

lx, ly = ox+240, oy+24
socket(lx,      ly,      "D0", ["pin 1  D0", "pin 2  D1"])
socket(lx+116,  ly,      "D1", ["pin 1  D1", "pin 2  D2"])
socket(lx,      ly+142,  "I2C", ["pin 1  SCL D5", "pin 2  SDA D4"])
socket(lx+116,  ly+142,  "UART", ["pin 1  RX D7", "pin 2  TX D6"])
rx, ry = ox+500, oy+24
socket(rx,      ry,      "D2", ["pin 1  D2", "pin 2  D3"])
socket(rx+116,  ry,      "I2C", ["pin 1  SCL D5", "pin 2  SDA D4"])
socket(rx,      ry+142,  "D8", ["pin 1  D8", "pin 2  D9"], lora=True)
socket(rx+116,  ry+142,  "D9", ["pin 1  D9", "pin 2  D10"], lora=True)

# legend for the shield
lgx, lgy = 800, 118
add(f'<rect x="{lgx}" y="{lgy}" width="360" height="300" rx="12" fill="#ffffff" stroke="{LINE}"/>')
text(lgx+18, lgy+32, "Reading the shield", 16, weight="bold")
notes = [
    "Pin 1 is the yellow wire of a Grove cable.",
    "The left half keeps the XIAO and four sockets:",
    "D0, D1, I2C and UART. The right half snaps off,",
    "and with it the second I2C and the D2 socket the",
    "Plantower SET line uses. Keep the shield whole.",
    "",
    "Dashed purple: lost when the Wio-SX1262 is",
    "fitted. D8 to D10 are the radio's SPI bus.",
    "",
    "Sockets give 3V3 only. Anything that needs",
    "5 V, like a PMS5003 fan, takes a wire from",
    "the 5V header pin.",
]
for i, n in enumerate(notes):
    text(lgx+18, lgy+60+i*20, n, 13, INK if n else INK)

# ---------- the matrix ----------
cols = [("Variant", 170), ("I2C socket", 180), ("I2C socket", 170), ("UART socket", 175),
        ("D2 socket", 150), ("5V header pin", 125), ("On today's shield", 150)]
mx, my = 40, 470
total = sum(w for _, w in cols)
add(f'<rect x="{mx}" y="{my}" width="{total}" height="44" rx="8" fill="{INK}"/>')
x = mx
for name, w in cols:
    text(x+12, my+28, name, 14, "#ffffff", weight="bold")
    x += w

rows = [
    ("Bayu v3", "deployed today", ["Grove BME680", "Grove HM3301", "—", "—", "—"], "yes"),
    ("Anchor", "", ["Grove SEN54 *", "Grove SHT40", "PMS5003 data", "PMS5003 SET", "PMS5003 fan"], "two"),
    ("Dense", "", ["—", "—", "PMS5003T data", "PMS5003T SET", "PMS5003T fan"], "no"),
    ("Indoor", "", ["Grove SCD41", "Grove SHT40", "PMS5003 data", "PMS5003 SET", "PMS5003 fan"], "no"),
    ("Relay", "", ["Grove SHT40", "—", "—", "—", "—"], "yes"),
]
rh = 74
for r, (name, sub, cells, ok) in enumerate(rows):
    y = my + 44 + r*rh
    bg = "#ffffff" if r % 2 == 0 else "#f4f2ec"
    add(f'<rect x="{mx}" y="{y}" width="{total}" height="{rh}" fill="{bg}"/>')
    text(mx+12, y+(32 if sub else 43), name, 17, weight="bold")
    if sub:
        text(mx+12, y+52, sub, 12, MUTED)
    x = mx + cols[0][1]
    for c, (cell, (_, w)) in enumerate(zip(cells, cols[1:6])):
        fill = MUTED if cell == "—" else INK
        if c == 4 and cell != "—":
            add(f'<rect x="{x+6}" y="{y+14}" width="{w-12}" height="{rh-28}" rx="6" fill="{AMBER_BG}"/>')
            fill = AMBER
        text(x+12, y+42, cell, 14, fill)
        x += w
    vw = cols[-1][1]
    if ok == "yes":
        add(f'<rect x="{x+8}" y="{y+16}" width="{vw-16}" height="{rh-32}" rx="8" fill="{GREEN_BG}"/>')
        text(x+vw/2, y+42, "plug and play", 14, GREEN, weight="bold", anchor="middle")
    else:
        add(f'<rect x="{x+8}" y="{y+16}" width="{vw-16}" height="{rh-32}" rx="8" fill="{AMBER_BG}"/>')
        text(x+vw/2, y+42, "one or two 5V wires *" if ok == "two" else "one 5V wire", 13 if ok == "two" else 14, AMBER, weight="bold", anchor="middle")
add(f'<rect x="{mx}" y="{my}" width="{total}" height="{44+len(rows)*rh}" rx="8" fill="none" stroke="{LINE}"/>')

fy = my + 44 + len(rows)*rh + 34
foot = [
    "The PMS5003 has no Grove version. Its data goes in the UART socket and SET in the D2 socket, through a Grove to",
    "1.25 mm 8-pin cable, and its fan takes 5 V from the header. Leave SET out and the fan simply runs all the time.",
    "* Seeed fitted the Grove SEN54 with a regulator for 3.3 V supply, according to one review. Not confirmed on our bench yet.",
    "  A bare Sensirion SEN54 needs 5 V, which makes a second wire from the 5V header.",
    "The Grove HM3301 makes its own 5 V from the socket's 3V3, with a step-down and a step-up converter (Seeed's schematic).",
    "The D0 and D1 sockets take the Grove button and LED. With LoRa fitted, the D8 and D9 sockets are not usable.",
]
for i, f in enumerate(foot):
    text(40, fy + i*22, f, 13, INK)
# footer stamp: what this is, revision, licence, source
add(f'<g font-family="{FONT}" font-size="13"><rect x="0" y="1060" width="{W}" height="52" fill="#ffffff"/>'
    f'<line x1="0" y1="1060" x2="{W}" y2="1060" stroke="{LINE}"/>'
    f'<text x="20" y="1082" fill="{INK}" font-weight="bold">Bayu on the Seeed Grove Shield for XIAO · socket map · rev 2026-10-24</text>'
    f'<text x="20" y="1101" fill="{MUTED}">CERN-OHL-W-2.0 · Meaningful Design Group / Fab Lab Bali · github.com/Meaningful-Design-Group/makingsensebali</text></g>')
add('</svg>')
open(out, "w").write("\n".join(s))
print("wrote", out)
