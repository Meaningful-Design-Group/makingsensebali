# SPDX-License-Identifier: MIT
# Copyright 2026 Meaningful Design Group / Fab Lab Bali
# Source: https://github.com/Meaningful-Design-Group/makingsensebali
# Run: python3 adapter_leads.py adapter-leads.svg
"""Bayu v3 with three PM sensors, plug-in version: a Grove I2C hub and two Grove adapter
leads with a 5 V step-up module, so the bare SEN54 and the PMS5003 plug into Grove sockets.
Net colours follow ../../circuits/CONVENTIONS.md."""
import sys
from xml.sax.saxutils import escape as esc

out = sys.argv[1]
W, H = 1100, 1440
INK, MUTED, PAPER, LINE = "#1d2433", "#5b6475", "#fbfaf6", "#c9c4b6"
BOARD = "#1f2b45"
FONT = "Helvetica, Arial, sans-serif"
NET = {"5V": "#d0312d", "3V3": "#ef7d00", "GND": "#1d2433", "SDA": "#1f5fbf", "SCL": "#e6b400",
       "TX": "#4cae4f", "RX": "#1b6b3a"}
GROVE = "#9aa0aa"
MOD = "#2f6f5e"

s = []
def add(x): s.append(x)
def text(x, y, t, size=14, fill=INK, weight="normal", anchor="start"):
    add(f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" font-weight="{weight}" text-anchor="{anchor}">{esc(t)}</text>')
def wire(pts, net, w=3.5):
    d = " ".join(f"{x},{y}" for x, y in pts)
    if net == "SCL":
        add(f'<polyline points="{d}" fill="none" stroke="#8a7000" stroke-width="{w+1.6}" stroke-linejoin="round"/>')
    add(f'<polyline points="{d}" fill="none" stroke="{NET[net]}" stroke-width="{w}" stroke-linejoin="round"/>')
    for x, y in (pts[0], pts[-1]):
        add(f'<circle cx="{x}" cy="{y}" r="4" fill="{NET[net]}" stroke="#ffffff" stroke-width="1"/>')
def grove(pts):
    d = " ".join(f"{x},{y}" for x, y in pts)
    add(f'<polyline points="{d}" fill="none" stroke="#ffffff" stroke-width="12" stroke-linejoin="round"/>')
    add(f'<polyline points="{d}" fill="none" stroke="{GROVE}" stroke-width="8" stroke-linejoin="round"/>')
def box(x, y, w, h, title, sub=(), fill="#ffffff", stroke=INK, tcol=INK, dash=None):
    extra = f' stroke-dasharray="{dash}"' if dash else ""
    add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{fill}" stroke="{stroke}" stroke-width="1.5"{extra}/>')
    text(x + 12, y + 22, title, 14, tcol, weight="bold")
    for i, line in enumerate(sub):
        text(x + 12, y + 40 + i * 17, line, 13, MUTED if tcol == INK else "#e3efe9")
def heading(y, label, t):
    add(f'<circle cx="44" cy="{y-5}" r="13" fill="{INK}"/>')
    text(44, y, label, 14, "#ffffff", weight="bold", anchor="middle")
    text(66, y, t, 17, weight="bold")

add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{FONT}">')
add(f'<rect width="{W}" height="{H}" fill="{PAPER}"/>')
text(30, 44, "Bayu v3 with three PM sensors · Plug-in version with adapter leads", 24, weight="bold")
text(30, 70, "Every sensor goes into a Grove socket. A small module on each lead turns the socket's 3V3 into 5 V.", 14, MUTED)
text(30, 94, "Grey bands are Grove cables. On the leads, every wire is drawn in its net colour, with the Grove wire colour named.", 14, INK)

# ================= A: plug-in layout =================
heading(140, "A", "What plugs in where")
# shield, left half only
add(f'<rect x="40" y="170" width="330" height="220" rx="14" fill="{BOARD}"/>')
add(f'<rect x="52" y="225" width="20" height="40" rx="5" fill="#9aa3b5"/>')
add(f'<rect x="66" y="195" width="150" height="170" rx="8" fill="#e9ecf2" stroke="#9aa3b5"/>')
text(141, 270, "XIAO ESP32-S3", 14, weight="bold", anchor="middle")
text(141, 290, "Wio-SX1262 on top", 13, MUTED, anchor="middle")
text(141, 307, "optional", 13, MUTED, anchor="middle")
def socket(x, y, name, used):
    add(f'<rect x="{x}" y="{y}" width="62" height="80" rx="5" fill="{"#f2f2ee" if used else "#3a4766"}" stroke="#d7d3c6"/>')
    text(x + 31, y + 46, name, 14, INK if used else "#c7cede", weight="bold", anchor="middle")
socket(230, 190, "D0", False)
socket(298, 190, "D1", False)
socket(230, 290, "I2C", True)
socket(298, 290, "UART", True)
text(40, 163, "Grove Shield, the small half is enough", 13, MUTED)

# I2C hub
box(450, 160, 170, 160, "Grove I2C hub", ["4 ports, all the", "same bus and 3V3"])
for i in range(4):
    add(f'<rect x="606" y="{232 + i * 20}" width="14" height="12" rx="2" fill="#d7d3c6"/>')
grove([(261, 370), (261, 430), (420, 430), (420, 280), (450, 280)])
# hub to HM3301, BME680, lead A
box(720, 140, 150, 64, "HM3301", ["Grove module"])
box(720, 220, 150, 64, "BME680", ["Grove module"])
grove([(620, 238), (680, 238), (680, 172), (720, 172)])
grove([(620, 258), (700, 258), (700, 252), (720, 252)])
box(720, 300, 120, 56, "Lead A", ["5 V module"], fill=MOD, stroke=MOD, tcol="#ffffff")
grove([(620, 278), (660, 278), (660, 328), (720, 328)])
box(920, 300, 150, 56, "SEN54", ["bare module"])
add(f'<line x1="840" y1="328" x2="920" y2="328" stroke="{INK}" stroke-width="5"/>')
text(880, 320, "JST GH", 12, MUTED, anchor="middle")
# UART to lead B to PMS
box(720, 400, 120, 56, "Lead B", ["5 V module"], fill=MOD, stroke=MOD, tcol="#ffffff")
grove([(329, 370), (329, 455), (680, 455), (680, 428), (720, 428)])
box(920, 400, 150, 56, "PMS5003", ["fan 5 V"])
add(f'<line x1="840" y1="428" x2="920" y2="428" stroke="{INK}" stroke-width="5"/>')
text(880, 420, "8-pin", 12, MUTED, anchor="middle")

# ================= B and C: the leads, as wire lists =================
def lead(y0, label, title, rows, conn_title, conn_pins, extra):
    """rows: (wire colour name, net, conn pin index). Rows 0 and 1 run through the module."""
    heading(y0, label, title)
    GX, GY = 60, y0 + 40
    ry = lambda i: GY + 34 + 34 * i
    add(f'<rect x="{GX}" y="{GY}" width="130" height="{40 + 34 * len(rows)}" rx="6" fill="#ffffff" stroke="{INK}" stroke-width="1.5"/>')
    text(GX + 65, GY - 10, "Grove plug, wires", 13, weight="bold", anchor="middle")
    CX, CY = 880, y0 + 40
    cy = lambda i: CY + 34 + 26 * i
    ch = 40 + 26 * len(conn_pins)
    add(f'<rect x="{CX}" y="{CY}" width="190" height="{ch}" rx="6" fill="#ffffff" stroke="{INK}" stroke-width="1.5"/>')
    text(CX + 95, CY - 10, conn_title, 13, weight="bold", anchor="middle")
    for i, (lab, used) in enumerate(conn_pins):
        add(f'<rect x="{CX-5}" y="{cy(i)-5}" width="10" height="10" fill="#d9b44a"/>')
        text(CX + 14, cy(i) + 5, lab, 13, INK if used else MUTED)
    MX, MW = 380, 200
    add(f'<rect x="{MX}" y="{ry(0)-26}" width="{MW}" height="{ry(1)-ry(0)+52}" rx="8" fill="{MOD}"/>')
    text(MX + MW / 2, ry(0) - 32, "5 V module: MT3608, or a fixed 5 V buck-boost", 13, MOD, weight="bold", anchor="middle")
    for side, xx, labs in (("in", MX, ("IN+", "IN−")), ("out", MX + MW, ("OUT+", "OUT−"))):
        for k in range(2):
            add(f'<rect x="{xx-5}" y="{ry(k)-5}" width="10" height="10" fill="#d9b44a"/>')
            text(xx + (14 if side == "in" else -14), ry(k) + 5, labs[k], 13, "#ffffff", weight="bold",
                 anchor="start" if side == "in" else "end")
    for i, (wcol, net, pin) in enumerate(rows):
        text(GX + 12, ry(i) + 5, wcol, 13)
        tx = CX - 5
        if i < 2:
            out_net = "5V" if net == "3V3" else net
            wire([(GX + 130, ry(i)), (MX - 5, ry(i))], net)
            mid = 820
            wire([(MX + MW + 5, ry(i)), (mid, ry(i)), (mid + (10 if i else 0), cy(pin)), (tx, cy(pin))] if ry(i) != cy(pin) else [(MX + MW + 5, ry(i)), (tx, cy(pin))], out_net)
        else:
            mid = 760 + 20 * (i - 2)
            wire([(GX + 130, ry(i)), (mid, ry(i)), (mid, cy(pin)), (tx, cy(pin))], net)
    extra(CX, cy, ry, rows)

def sen_extra(CX, cy, ry, rows):
    add(f'<path d="M{CX+120},{cy(1)} h18 v{cy(4)-cy(1)} h-18" fill="none" stroke="{NET["GND"]}" stroke-width="3"/>')
    text(CX + 95, cy(5) + 62, "pins 2 and 5 joined in the plug,", 12, MUTED, anchor="middle")
    text(CX + 95, cy(5) + 78, "SEL to GND selects I2C", 12, MUTED, anchor="middle")
    text(560, ry(3) + 34, "SDA and SCL pass straight through. Keep plug to SEN54 under 10 cm, Sensirion's limit.", 13, MUTED, anchor="middle")
lead(560, "B", "Lead A · Grove I2C to SEN54",
     [("red, 3V3", "3V3", 0), ("black, GND", "GND", 1), ("white, SDA", "SDA", 2), ("yellow, SCL", "SCL", 3)],
     "SEN54, JST GH 6-pin", [("1 VDD", 1), ("2 GND", 1), ("3 SDA", 1), ("4 SCL", 1), ("5 SEL", 1), ("6 NC", 0)], sen_extra)

def pms_extra(CX, cy, ry, rows):
    text(CX + 95, cy(7) + 62, "SET, RESET, 7 and 8 stay open", 12, MUTED, anchor="middle")
    text(560, ry(3) + 34, "White D6 goes to RXD and yellow D7 to TXD, 3.3 V logic both ways.", 13, MUTED, anchor="middle")
lead(880, "C", "Lead B · Grove UART to PMS5003",
     [("red, 3V3", "3V3", 0), ("black, GND", "GND", 1), ("white, D6 TX", "TX", 3), ("yellow, D7 RX", "RX", 4)],
     "PMS5003, 8-pin 1.25 mm", [("1 VCC", 1), ("2 GND", 1), ("3 SET", 0), ("4 RXD", 1), ("5 TXD", 1), ("6 RESET", 0), ("7 NC", 0), ("8 NC", 0)], pms_extra)

# ================= notes =================
notes = [
    "Set and check the module before a sensor goes on it. Power the lead from a Grove socket with nothing on the output and measure",
    "OUT+ to OUT−. A fixed buck-boost should read 5.0 V. An MT3608 comes set to anything: turn its trimmer to 5.0 V, then seal it with a drop of glue.",
    "On most of these modules IN− and OUT− are the same ground. Check it with a multimeter before relying on it.",
    "Heat-shrink the module inside the lead. The Grove side stays a plain Grove plug, so the lead goes into any Grove socket or hub port.",
    "Everything now runs from the XIAO's 3V3 regulator. See the current budget on the build page before deploying three PM sensors this way.",
]
for i, n in enumerate(notes):
    text(30, 1250 + i * 24, n, 13)

base = H - 52
add(f'<g font-family="{FONT}" font-size="13"><rect x="0" y="{base}" width="{W}" height="52" fill="#ffffff"/>'
    f'<line x1="0" y1="{base}" x2="{W}" y2="{base}" stroke="{LINE}"/>'
    f'<text x="20" y="{base+22}" fill="{INK}" font-weight="bold">Bayu v3 with three PM sensors · Grove adapter leads · rev 2026-10-24</text>'
    f'<text x="20" y="{base+41}" fill="{MUTED}">CERN-OHL-W-2.0 · Meaningful Design Group / Fab Lab Bali · github.com/Meaningful-Design-Group/makingsensebali</text></g>')
add('</svg>')
open(out, "w").write("\n".join(s))
print("wrote", out)
