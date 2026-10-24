# SPDX-License-Identifier: MIT
# Copyright 2026 Meaningful Design Group / Fab Lab Bali
# Source: https://github.com/Meaningful-Design-Group/makingsensebali
# Run: python3 draw_circuits.py
"""Draw the twelve circuit sheets of the Bayu node, three for each variant (anchor, dense,
indoor, relay): wiring-breadboard.svg, wiring-core.svg and schematic.svg.

Designators, net names, colours and positions all come from CONVENTIONS.md, and every sheet
is drawn by the same functions, so the four variants come out as one system. Change
CONVENTIONS.md first, then this file, then run it. Stdlib only."""
import os
from xml.sax.saxutils import escape as esc

HERE = os.path.dirname(os.path.abspath(__file__))
REV = "2026-10-24"
W = 1100
FONT = "Helvetica, Arial, sans-serif"
INK, MUTED, PAPER, LINE = "#1d2433", "#5b6475", "#fbfaf6", "#c9c4b6"
GREY, GREY_TXT = "#b4b8c1", "#8d929c"
RADIO = "#4a5873"        # U2 outline and its B2B / SPI lines; not a net colour
PART, PART_EDGE = "#f4efe2", "#8a8371"

# one colour per net, CONVENTIONS.md "Wire colours"
NET = {
    "+5V_USB": "#d0312d", "+5V_F": "#d0312d", "+5V_IN": "#d0312d",
    "3V3": "#ef7d00", "GND": "#1d2433",
    "I2C_SDA": "#1f5fbf", "I2C_SCL": "#e6b400",
    "UART_TX": "#4cae4f", "UART_RX": "#1b6b3a",
    "PMS_SET": "#7a3fb3", "BTN": "#8a8f99", "LED_DIN": "#d63384",
    "COAX": "#8a5a2b", "LORA_SPI": RADIO, "VBAT_SENSE": "#2a9d8f",
}
SCL_EDGE = "#7a6000"
DARK_TEXT_ON = {"3V3", "I2C_SCL", "UART_TX", "BTN", "VBAT_SENSE"}   # ink text on these tags

# CONVENTIONS.md "Per variant". None = not fitted.
VARIANTS = {
    "anchor": dict(name="Anchor", u2="fitted", J1="SEN54", J2="PMS5003", J3="SHT40", J4=None, jp1=True),
    "dense": dict(name="Dense", u2="optional", J1=None, J2="PMS5003T", J3=None, J4=None, jp1=False),
    "indoor": dict(name="Indoor", u2=None, J1=None, J2="PMS5003", J3="SCD40", J4="SHT40", jp1=False),
    "relay": dict(name="Relay", u2="fitted", J1=None, J2=None, J3="SHT40", J4=None, jp1=False),
}

# XIAO edges with USB-C to the left: top edge, then bottom edge, left to right
XIAO_TOP = [("5V", ""), ("GND", ""), ("3V3", ""), ("D10", "GPIO9"), ("D9", "GPIO8"), ("D8", "GPIO7"), ("D7", "GPIO44")]
XIAO_BOT = [("D0", "GPIO1"), ("D1", "GPIO2"), ("D2", "GPIO3"), ("D3", "GPIO4"), ("D4", "GPIO5"), ("D5", "GPIO6"), ("D6", "GPIO43")]
XPIN = {"BTN": "D0 · GPIO1", "LED_DIN": "D1 · GPIO2", "PMS_SET": "D2 · GPIO3", "I2C_SDA": "D4 · GPIO5",
        "I2C_SCL": "D5 · GPIO6", "UART_TX": "D6 · GPIO43", "UART_RX": "D7 · GPIO44"}

# Helvetica advance widths per 1000 em, for layout and for the overlap check
_CW = {c: w for s, w in [(" ,./:;'!|", 278), ("()-[]r²", 333), ("\"", 355), ("*", 389), ("°", 400),
                         ("Jcksvxyz", 500), ("0123456789#$_?abdeghnopqu–µ", 556),
                         ("+=<>×−", 584), ("FTZ", 611), ("ABEKPSVXY&", 667), ("CDHNRUw", 722),
                         ("GOQ", 778), ("Ω", 768), ("Mm", 833), ("%", 889), ("W", 944),
                         ("→—", 1000), ("ijl", 222), ("ft·I", 278), ("L", 556)] for c in s}


def tw(s, size, bold=False):
    return sum(_CW.get(c, 556) for c in s) * size / 1000 * (1.07 if bold else 1.0)


def n(x):
    return f"{x:.1f}".rstrip("0").rstrip(".")


class Sheet:
    def __init__(self, key, kind):
        self.v, self.key, self.kind = VARIANTS[key], key, kind
        self.el, self.texts, self.segs = [], [], []
        self.wid = 0

    def add(self, s):
        self.el.append(s)

    def text(self, x, y, t, size=14, fill=INK, bold=False, anchor="start"):
        assert size >= 13, t
        w = tw(t, size, bold)
        x0 = {"start": x, "middle": x - w / 2, "end": x - w}[anchor]
        self.texts.append((x0, y - 0.72 * size, x0 + w, y + 0.2 * size, t))
        self.add(f'<text x="{n(x)}" y="{n(y)}" font-size="{size}" fill="{fill}"'
                 + (' font-weight="bold"' if bold else "")
                 + (f' text-anchor="{anchor}"' if anchor != "start" else "") + f">{esc(t)}</text>")
        return w

    def para(self, x, y, s, width, size=14, lead=19, fill=INK, bold=False):
        """Wrap s into lines of at most width px; returns the y below the last line."""
        line = ""
        for word in s.split(" "):
            if line and tw(line + " " + word, size, bold) > width:
                self.text(x, y, line, size, fill, bold)
                y, line = y + lead, word
            else:
                line = (line + " " + word).strip()
        if line:
            self.text(x, y, line, size, fill, bold)
            y += lead
        return y

    def rect(self, x, y, w, h, fill="none", stroke=None, sw=1.5, rx=0, dash=None, op=None):
        self.add(f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}"'
                 + (f' rx="{n(rx)}"' if rx else "") + f' fill="{fill}"'
                 + (f' fill-opacity="{op}"' if op else "")
                 + (f' stroke="{stroke}" stroke-width="{sw}"' if stroke else "")
                 + (f' stroke-dasharray="{dash}"' if dash else "") + "/>")

    def line(self, x1, y1, x2, y2, stroke=MUTED, sw=1.2, dash=None):
        self.add(f'<line x1="{n(x1)}" y1="{n(y1)}" x2="{n(x2)}" y2="{n(y2)}" stroke="{stroke}" stroke-width="{sw}"'
                 + (f' stroke-dasharray="{dash}"' if dash else "") + "/>")

    def circle(self, x, y, r, fill, stroke=None, sw=1.2):
        self.add(f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(r)}" fill="{fill}"'
                 + (f' stroke="{stroke}" stroke-width="{sw}"' if stroke else "") + "/>")

    def wire(self, pts, net, dash=False, w=4.0, grey=False):
        """A wire or trace in its net colour; SCL (yellow) gets a dark outline."""
        col = GREY if grey else NET[net]
        d = " ".join(f"{n(x)},{n(y)}" for x, y in pts)
        da = ' stroke-dasharray="9 6"' if dash else ""
        if net == "I2C_SCL" and not grey:
            self.add(f'<polyline points="{d}" fill="none" stroke="{SCL_EDGE}" stroke-width="{n(w + 2)}" '
                     f'stroke-linejoin="round" stroke-linecap="round"{da}/>')
        self.add(f'<polyline points="{d}" fill="none" stroke="{col}" stroke-width="{n(w)}" '
                 f'stroke-linejoin="round" stroke-linecap="round"{da}/>')
        self.wid += 1
        self.segs += [(a, b, net, self.wid) for a, b in zip(pts, pts[1:])]

    def tag(self, x, y, net, anchor="start", grey=False, label=None):
        """Net label: a pill in the net colour. y is the text baseline."""
        t = label or net
        w = tw(t, 13, True) + 10
        x0 = x if anchor == "start" else x - w
        fill = PAPER if grey else NET[net]
        self.rect(x0, y - 13.5, w, 18, fill=fill, stroke=GREY if grey else (SCL_EDGE if net == "I2C_SCL" else None),
                  sw=1, rx=4)
        txt = GREY_TXT if grey else (INK if net in DARK_TEXT_ON else "#ffffff")
        self.text(x0 + 5, y, t, 13, txt, bold=True)
        return w

    # ---- frame shared by every sheet ----
    def header(self, subtitle):
        self.text(30, 46, f"Bayu {self.v['name']} · {self.kind}", 26, bold=True)
        assert tw(subtitle, 15) < 695, subtitle
        self.text(30, 72, subtitle, 15, MUTED)
        legend(self)

    def svg(self, H):
        foot = H - 52
        head = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
                f'font-family="{FONT}">\n<rect width="{W}" height="{H}" fill="{PAPER}"/>')
        tail = (f'<g font-family="{FONT}" font-size="13"><rect x="0" y="{foot}" width="{W}" height="52" fill="#ffffff"/>'
                f'<line x1="0" y1="{foot}" x2="{W}" y2="{foot}" stroke="{LINE}"/>'
                f'<text x="20" y="{foot + 22}" fill="{INK}" font-weight="bold">Bayu {self.v["name"]} · {esc(self.kind)} · rev {REV}</text>'
                f'<text x="20" y="{foot + 41}" fill="{MUTED}">CERN-OHL-W-2.0 · Meaningful Design Group / Fab Lab Bali · '
                f'github.com/Meaningful-Design-Group/makingsensebali</text></g>\n</svg>\n')
        return head + "\n" + "\n".join(self.el) + "\n" + tail


def legend(sh):
    x, y = 735, 18
    sh.rect(x, y, 345, 182, fill="#ffffff", stroke=LINE, rx=10)
    sh.text(x + 16, y + 28, "Nets, the same colour on every sheet", 14, bold=True)
    col1 = [("+5V_USB", "+5V_USB, +5V_F, +5V_IN"), ("3V3", "3V3"), ("GND", "GND"), ("I2C_SDA", "I2C_SDA"),
            ("I2C_SCL", "I2C_SCL"), ("UART_TX", "UART_TX"), ("UART_RX", "UART_RX")]
    col2 = [("PMS_SET", "PMS_SET"), ("BTN", "BTN"), ("LED_DIN", "LED_DIN"), ("VBAT_SENSE", "VBAT_SENSE"), ("COAX", "antenna coax"),
            ("LORA_SPI", "U2 radio lines"), ("opt", "optional"), ("nf", "not fitted")]
    for cx, items in ((x + 16, col1), (x + 206, col2)):
        for i, (key, label) in enumerate(items):
            yy = y + 50 + i * 17
            if key == "opt":
                sh.rect(cx, yy - 9, 24, 12, fill=PART, stroke=INK, sw=1.4, dash="4 3", rx=2)
            elif key == "nf":
                sh.rect(cx, yy - 9, 24, 12, fill="none", stroke=GREY, sw=1.6, rx=2)
            else:
                if key == "I2C_SCL":
                    sh.line(cx, yy - 3, cx + 24, yy - 3, SCL_EDGE, 7)
                sh.line(cx, yy - 3, cx + 24, yy - 3, NET[key], 5, dash="5 3" if key == "COAX" else None)
            sh.text(cx + 32, yy + 2, label, 13)


def xiao(sh, x1, yt, yb, p, u2, show_absent):
    """XIAO ESP32-S3 seen from the top, USB-C to the left. x1 is the x of the first pin
    (5V on the top edge, D0 on the bottom edge), yt and yb are the two pin rows.
    The same drawing serves the breadboard and the Core."""
    left, right = x1 - 1.35 * p, x1 + 6.95 * p
    top, bot, mid = yt - 10, yb + 10, (yt + yb) / 2
    sh.rect(left - 18, mid - 21, 24, 42, fill="#b9bfcc", stroke="#7f889b", rx=5)
    sh.rect(left, top, right - left, bot - top, fill="#e9ecf2", stroke="#7f889b", sw=1.6, rx=10)
    taken = u2 is not None
    for edge, pins, y in (("t", XIAO_TOP, yt), ("b", XIAO_BOT, yb)):
        for i, (d, g) in enumerate(pins):
            x = x1 + i * p
            lv = i % 2
            lines = [d] + ([g] if g else [])
            if edge == "t":
                ys = [yt + 24 + lv * 32 + k * 15 for k in range(len(lines))]
                if lv:
                    sh.line(x, y + 6, x, ys[0] - 12, "#9aa3b5", 1)
            else:
                last = yb - 14 - lv * 32
                ys = [last - 15 * (len(lines) - 1 - k) for k in range(len(lines))]
                if lv:
                    sh.line(x, y - 6, x, ys[-1] + 4, "#9aa3b5", 1)
            dim = taken and d in ("D8", "D9", "D10")
            sh.text(x, ys[0], d, 13, MUTED if dim else INK, bold=not dim, anchor="middle")
            if g:
                sh.text(x, ys[1], g, 13, MUTED, anchor="middle")
            sh.rect(x - 6, y - 6, 12, 12, fill="#d9b44a", stroke="#a8841f", sw=1, rx=2)
    cx = (left + right) / 2
    sh.text(cx, mid - 10, "U1 XIAO ESP32-S3", 14, bold=True, anchor="middle")
    if u2:
        dash = None if u2 == "fitted" else "7 5"
        sh.rect(left + 5, top + 5, right - left - 10, bot - top - 10, stroke=RADIO, sw=2.4, rx=8, dash=dash)
        sh.text(cx, mid + 8, "U2 Wio-SX1262 on top" if u2 == "fitted" else "U2 Wio-SX1262, optional",
                13, RADIO, anchor="middle")
        sh.text(cx, mid + 24, "D8 to D10: radio SPI", 13, MUTED, anchor="middle")
        sh.circle(right - 16, mid, 6, "#d9b44a", RADIO, 1.5)
    elif not show_absent:
        sh.text(cx, mid + 8, "WiFi only, no U2", 13, MUTED, anchor="middle")
    else:
        sh.rect(left + 5, top + 5, right - left - 10, bot - top - 10, stroke=GREY, sw=2, rx=8, dash="7 5")
        sh.text(cx, mid + 8, "U2 Wio-SX1262 not fitted", 13, GREY_TXT, anchor="middle")
    return dict(left=left, right=right, mid=mid, ufl=(right - 16, mid))


# ====================================================================================
# Breadboard, phase 0
# ====================================================================================
P, C1, Y0 = 30, 62, 222


def cx(c):
    return C1 + (c - 1) * P


ROW = {r: Y0 + 130 + i * P for i, r in enumerate("abcde")}
ROW.update({r: Y0 + 340 + i * P for i, r in enumerate("fghij")})
T1, T2, B1, B2 = Y0 + 40, Y0 + 70, Y0 + 505, Y0 + 535      # rails: GND, +5V_USB, 3V3, GND
LANE0, SY = Y0 + 582, Y0 + 735                               # first wire lane, top of the parts


def bb_part(sh, x0, x1, cols, pins, title, lines, state="fitted"):
    """A part below the breadboard: box, connector along its top edge, pin labels staggered."""
    dash = "6 4" if state == "optional" else None
    sh.rect(x0, SY, x1 - x0, 132, fill="#ffffff", stroke=INK, sw=1.4, rx=8, dash=dash)
    for i, (c, (label, net)) in enumerate(zip(cols, pins)):
        x = cx(c)
        y = SY + 22 + (i % 2) * 18
        if i % 2:
            sh.line(x, SY + 6, x, y - 12, "#9aa3b5", 1)
        sh.text(x, y, label, 13, INK if net else MUTED, anchor="middle")
        sh.rect(x - 5, SY - 5, 10, 10, fill="#d9b44a" if net else "#d6d2c6", stroke="#8a8371", sw=1, rx=1)
    sh.text(x0 + 10, SY + 68, title, 14, bold=True)
    y = SY + 86
    for t in lines:
        sh.text(x0 + 10, y, t, 13, MUTED)
        y += 16


def breadboard(key):
    v = VARIANTS[key]
    sh = Sheet(key, "Breadboard wiring, phase 0")
    sense = [s for s in (v["J1"], v["J2"], v["J3"], v["J4"]) if s]
    sub = "XIAO ESP32-S3" + (" + Wio-SX1262" if v["u2"] == "fitted" else "") + ", " + ", ".join(sense)
    sub += (", Wio-SX1262 optional" if v["u2"] == "optional" else "") + " · 5 V USB wall supply · top view"
    sh.header(sub)
    pms, sen, sht = v["J2"], v["J1"], "SHT40" in (v["J3"], v["J4"])
    scd = "SCD40" in (v["J3"], v["J4"])
    y = 98
    for t in TOP_NOTES_BB[key]:
        y = sh.para(30, y, t, 690)

    # ---- the board ----
    sh.rect(40, Y0, 1022, 560, fill="#f3f1ea", stroke=LINE, sw=1.5, rx=12)
    sh.rect(40, ROW["e"] + 16, 1022, ROW["f"] - ROW["e"] - 32, fill="#e7e3d7")
    for c in (1, 5, 10, 15, 20, 25, 30):
        sh.text(cx(c), Y0 + 18, str(c), 13, MUTED, anchor="middle")
    for yy, net in ((T1 - 12, "GND"), (T2 + 12, "+5V_USB"), (B1 + 15, "3V3"), (B2 + 13, "GND")):
        sh.line(50, yy, cx(30) + 12, yy, NET[net], 2.5)
    for c in range(1, 31):
        for yy in [T1, T2, B1, B2] + list(ROW.values()):
            sh.rect(cx(c) - 3.5, yy - 3.5, 7, 7, fill="#a9a497", rx=1)
    for r, yy in ROW.items():
        sh.text(954, yy + 5, r, 13, MUTED)
    for yy, t, net in ((T1, "GND", "GND"), (T2, "+5V_USB", "+5V_USB"), (B1, "3V3", "3V3"), (B2, "GND", "GND")):
        sh.text(978, yy + 5, t, 13, NET[net], bold=True)

    xi = xiao(sh, cx(2), ROW["b"], ROW["g"], P, v["u2"], show_absent=False)
    if v["u2"]:
        ux, uy = xi["ufl"]
        sh.wire([(ux, uy), (350, uy)], "COAX", dash=True, w=3)
        sh.text(358, uy - 3, "U2 LoRa U.FL, pigtail", 13, NET["COAX"], bold=True)
        sh.text(358, uy + 14, "to SMA bulkhead, whip", 13, NET["COAX"])

    def dot(x, y, net, grey=False):
        sh.circle(x, y, 4.5, GREY if grey else NET[net], "#ffffff", 1.2)

    # ---- top edge: power, 3V3 to the bottom rail, D7 to the PMS ----
    sh.wire([(cx(2), ROW["a"]), (cx(2), T2)], "+5V_USB")
    sh.wire([(cx(3), ROW["a"]), (cx(3), T1)], "GND")
    sh.wire([(cx(4), ROW["a"]), (cx(4), Y0 + 110), (cx(10), Y0 + 110), (cx(10), B1)], "3V3")
    sh.wire([(cx(30), T1), (cx(30), B2)], "GND")
    for x, y, net in ((cx(2), ROW["a"], "+5V_USB"), (cx(2), T2, "+5V_USB"), (cx(3), ROW["a"], "GND"),
                      (cx(3), T1, "GND"), (cx(4), ROW["a"], "3V3"), (cx(10), B1, "3V3"),
                      (cx(30), T1, "GND"), (cx(30), B2, "GND")):
        dot(x, y, net)
    if pms:
        sh.wire([(cx(8), ROW["a"]), (cx(8), Y0 + 96), (cx(20), Y0 + 96), (cx(20), SY)], "UART_RX")
        dot(cx(8), ROW["a"], "UART_RX")

    # ---- the parts, each in its fixed slot ----
    parts = []   # (cols, pins, box, title, lines, state)
    parts.append(([1, 2], [("1", "BTN"), ("2", "GND")], (24, 116), "SW1 button",
                  ["optional", "D0 to GND"], "optional"))
    parts.append(([4, 5, 6], [("DIN", "LED_DIN"), ("VCC", "3V3"), ("GND", "GND")], (128, 236), "U7 WS2812B",
                  ["optional", "on 3V3"], "optional"))
    sock = {s: j for j in ("J3", "J4") for s in [v[j]] if s}
    if sht:
        parts.append(([11, 12, 13, 14], [("1 SCL", "I2C_SCL"), ("2 SDA", "I2C_SDA"), ("3 VCC", "3V3"), ("4 GND", "GND")],
                      (336, 478), "U5 SHT40", ["Grove, I2C 0x44", f"Core: {sock['SHT40']}"], "fitted"))
    if pms:
        parts.append((list(range(16, 24)), [("1 VCC", "+5V_USB"), ("2 GND", "GND"), ("3 SET", "PMS_SET"),
                                            ("4 RXD", "UART_TX"), ("5 TXD", "UART_RX"), ("6 RESET", None),
                                            ("7 NC", None), ("8 NC", None)],
                      (486, 748), f"U4 {pms}", ["PicoBlade 1.25 mm, 8-pin, Core: J2",
                                                "5 V fan and laser, 3.3 V logic", "6 RESET, 7 and 8 stay open"],
                      "fitted"))
    if sen:
        parts.append((list(range(25, 31)), [("1 VDD", "+5V_USB"), ("2 GND", "GND"), ("3 SDA", "I2C_SDA"),
                                            ("4 SCL", "I2C_SCL"), ("5 SEL", "GND"), ("6 NC", None)],
                      (756, 958), "U3 SEN54", ["JST GH 1.25 mm, 6-pin", "Core: J1 · I2C 0x69",
                                               "SEL to GND selects I2C"], "fitted"))
    if scd:
        parts.append(([25, 26, 27, 28], [("1 SCL", "I2C_SCL"), ("2 SDA", "I2C_SDA"), ("3 VCC", "3V3"), ("4 GND", "GND")],
                      (756, 898), "U6 SCD40", ["Grove, I2C 0x62", f"Core: {sock['SCD40']}"], "fitted"))

    # signal wires from the XIAO's bottom holes: (net, XIAO column, hole, target column)
    sig = [("BTN", 2, "h", 1), ("LED_DIN", 3, "i", 4)]
    if pms:
        sig += [("PMS_SET", 4, "i", 18), ("UART_TX", 8, "i", 19)]
    if sht:
        sig += [("I2C_SDA", 6, "h", 12), ("I2C_SCL", 7, "h", 11)]
    if sen:
        sig += [("I2C_SDA", 6, "i", 27), ("I2C_SCL", 7, "i", 28)]
    if scd:
        sig += [("I2C_SDA", 6, "i", 26), ("I2C_SCL", 7, "i", 25)]
    jog = {"h": -10, "i": 10}
    # lanes: a wire whose source is further left runs deeper, so staggered wires never cross
    right = sorted([s for s in sig if s[3] > s[1]], key=lambda s: cx(s[1]) + jog[s[2]])
    lane = {id(s): len(right) - k for k, s in enumerate(right)}
    for s in sig:
        lane.setdefault(id(s), 0)
    for s in sig:
        net, col, hole, tc = s
        x, y = cx(col), ROW[hole]
        xj = x + jog[hole]
        ly = LANE0 + 12 * lane[id(s)]
        opt = net in ("BTN", "LED_DIN")
        sh.wire([(x, y), (xj, y), (xj, ly), (cx(tc), ly), (cx(tc), SY)], net, dash=opt)
        dot(x, y, net)
        if net == "LED_DIN":     # R3 in series, just above U7
            rx = cx(tc)
            sh.rect(rx - 5, SY - 48, 10, 28, fill="#e8d5b5", stroke="#8a6d3b", sw=1.2, rx=3)
            sh.text(rx - 12, SY - 37, "R3", 13, INK, bold=True, anchor="end")
            sh.text(rx - 12, SY - 22, "330 Ω", 13, MUTED, anchor="end")
    # power wires from the rails, straight down to the pin underneath
    src = {"+5V_USB": T2, "GND": B2, "3V3": B1}
    for cols, pins, box, title, lines, state in parts:
        for c, (label, net) in zip(cols, pins):
            if net in src:
                sh.wire([(cx(c), src[net]), (cx(c), SY)], net, dash=state == "optional")
                dot(cx(c), src[net], net)
    if sen:   # R1, R2: the SEN54's pull-ups, from SDA and SCL straight to the 3V3 rail
        for c, r in ((6, "R1"), (7, "R2")):
            sh.line(cx(c), ROW["j"], cx(c), B1, "#8a8371", 2)
            sh.rect(cx(c) - 4, ROW["j"] + 10, 8, 26, fill="#e8d5b5", stroke="#8a6d3b", sw=1.2, rx=3)
            dot(cx(c), ROW["j"], "I2C_SDA" if r == "R1" else "I2C_SCL")
            dot(cx(c), B1, "3V3")
        sh.line(cx(7) + 6, ROW["j"] + 23, 344, ROW["j"] + 23, MUTED, 1, dash="3 3")
        sh.text(350, ROW["j"] + 10, "R1, R2 4.7 kΩ", 13, INK, bold=True)
        sh.text(350, ROW["j"] + 27, "SDA, SCL to 3V3", 13, MUTED)
    for cols, pins, box, title, lines, state in parts:
        bb_part(sh, box[0], box[1], cols, pins, title, lines, state)

    y = SY + 170
    for t in BOTTOM_NOTES_BB[key]:
        y = sh.para(30, y, t, 1040) + 4
    return sh, y + 40


# ====================================================================================
# Bayu Core, phase 1: one board, the same geometry on every variant
# ====================================================================================
S, CBX, CBY = 12, 60, 330


def X(mm):
    return CBX + mm * S


def Y(mm):
    return CBY + mm * S


def state_of(v, ref):
    if ref == "J5":
        return "optional"
    if ref in ("J6", "CR1"):
        return None
    if ref == "U2":
        return v["u2"]
    return "fitted" if v[ref] else None


def socket(sh, ref, box, pins, entry, nets, state):
    """Draw a socket at its fixed place on the Core. box and pins in mm. entry: the side the
    cable comes in from. nets: one per pin, None for open pins."""
    x, y, w, h = box
    fill, stroke, dash = (PART, INK, None) if state == "fitted" else \
        (PART, INK, "5 3") if state == "optional" else ("none", GREY, None)
    sh.rect(X(x), Y(y), w * S, h * S, fill=fill, stroke=stroke, sw=1.5, rx=3, dash=dash)
    for i, ((px, py), net) in enumerate(zip(pins, nets)):
        sh.rect(X(px) - 4, Y(py) - 4, 8, 8, fill="#d9b44a" if state else "none",
                stroke="#8a6d3b" if state else GREY, sw=1, rx=1)
        num = str(i + 1)
        if entry == "top":
            sh.text(X(px), Y(y + h) - 8, num, 13, INK if state else GREY_TXT, anchor="middle")
            stub = [(X(px), Y(y + h)), (X(px), Y(y + h) + 22)]
        elif entry == "bottom":
            sh.text(X(px), Y(y) + 17, num, 13, INK if state else GREY_TXT, anchor="middle")
            stub = [(X(px), Y(y)), (X(px), Y(y) - 22)]
        else:
            sh.text(X(x) + 40, Y(py) + 5, num, 13, INK if state else GREY_TXT)
            stub = [(X(x), Y(py)), (X(x) - 22, Y(py))]
        if net and state:
            sh.wire(stub, net, w=3, dash=state == "optional")


def callout(sh, x, y, title, sub, rows, plug, state, w=270):
    """Box beside the board: what each pin of a socket carries and what plugs into it."""
    absent = state is None
    h = 52 + 21 * len(rows) + 30
    sh.rect(x, y, w, h, fill=PAPER if absent else "#ffffff", stroke=GREY if absent else INK,
            sw=1.3, rx=8, dash="5 3" if state == "optional" else None)
    sh.text(x + 12, y + 22, title, 14, GREY_TXT if absent else INK, bold=True)
    sh.text(x + 12, y + 40, sub, 13, GREY_TXT if absent else MUTED)
    yy = y + 63
    for num, net, txt in rows:
        sh.text(x + 14, yy, num, 13, GREY_TXT if absent else INK, bold=True)
        tx = x + 34
        if net:
            tx += sh.tag(tx, yy, net, grey=absent) + 8
        if txt:
            sh.text(tx, yy, txt, 13, GREY_TXT if absent else MUTED)
        yy += 21
    sh.text(x + 12, yy + 8, plug, 13, GREY_TXT if absent else INK, bold=not absent)
    return y + h


def core(key):
    v = VARIANTS[key]
    sh = Sheet(key, "Bayu Core connector map, phase 1")
    sh.header(f"One Core board for every variant, 60 × 40 mm at 12 px per mm. Grey parts are not fitted on {v['name']}.")
    y = 98
    for t in TOP_NOTES_CORE[key]:
        y = sh.para(30, y, t, 690)

    # the board
    sh.rect(X(0), Y(0), 60 * S, 40 * S, fill="#e6eee1", stroke="#7f9a7a", sw=2, rx=14)
    sh.text(X(34), Y(23.6), "Bayu Core · 60 × 40 mm", 14, "#6f8a6a", bold=True, anchor="middle")

    # U1 and U2, USB-C at the left edge
    xi = xiao(sh, X(4.43), Y(20 - 8.89), Y(20 + 8.89), 2.54 * S, v["u2"], show_absent=True)
    if v["u2"]:
        ux, uy = xi["ufl"]
        sh.wire([(ux, uy), (X(23.6), uy), (X(23.6), Y(-6.0))], "COAX", dash=True, w=3)
        sh.text(X(24.4), Y(-4.6), "U2 LoRa pigtail, U.FL to the SMA bulkhead", 13, NET["COAX"], bold=True)
        sh.text(X(24.4), Y(-3.2), "never power the radio without its antenna", 13, NET["COAX"])

    # J6, CR1, F1 along the top-left edge
    socket(sh, "J6", (1.5, 0.6, 6.0, 4.6), [(3.5, 2.0), (5.5, 2.0)], "top", ["+5V_IN", "GND"], None)
    sh.text(X(6.2), Y(7.0), "J6", 14, GREY_TXT, bold=True)
    sh.rect(X(9.0), Y(1.8), 3.6 * S, 1.8 * S, fill="none", stroke=GREY, sw=1.5, rx=2)
    sh.line(X(11.9), Y(1.8), X(11.9), Y(3.6), GREY, 3)
    sh.text(X(10.8), Y(5.7), "CR1", 14, GREY_TXT, bold=True, anchor="middle")
    sh.rect(X(14.0), Y(1.2), 4.4 * S, 3.0 * S, fill=PART, stroke=INK, sw=1.5, rx=3)
    sh.text(X(16.2), Y(6.3), "F1", 14, INK, bold=True, anchor="middle")
    sh.wire([(X(12.6), Y(2.7)), (X(14.0), Y(2.7))], "+5V_USB", w=3)
    sh.wire([(X(18.4), Y(2.7)), (X(19.8), Y(2.7))], "+5V_F", w=3)

    # sockets
    st = {r: state_of(v, r) for r in ("J1", "J2", "J3", "J4", "J5")}
    socket(sh, "J1", (38.0, 0.6, 11.0, 4.6), [(40.375 + 1.25 * i, 2.0) for i in range(6)], "top",
           ["+5V_F", "GND", "I2C_SDA", "I2C_SCL", "GND", None], st["J1"])
    sh.text(X(37.4), Y(3.4), "J1", 14, INK if st["J1"] else GREY_TXT, bold=True, anchor="end")
    socket(sh, "J2", (37.0, 34.8, 13.0, 4.6), [(39.125 + 1.25 * i, 38.0) for i in range(8)], "bottom",
           ["+5V_F", "GND", "PMS_SET", "UART_TX", "UART_RX", None, None, None], st["J2"])
    sh.text(X(36.4), Y(37.6), "J2", 14, INK if st["J2"] else GREY_TXT, bold=True, anchor="end")
    grove = ["I2C_SCL", "I2C_SDA", "3V3", "GND"]
    socket(sh, "J3", (53.4, 8.5, 6.0, 10.0), [(55.4, 10.5 + 2 * i) for i in range(4)], "right", grove, st["J3"])
    sh.text(X(56.4), Y(8.0), "J3", 14, INK if st["J3"] else GREY_TXT, bold=True, anchor="middle")
    socket(sh, "J4", (53.4, 21.5, 6.0, 10.0), [(55.4, 23.5 + 2 * i) for i in range(4)], "right", grove, st["J4"])
    sh.text(X(56.4), Y(21.0), "J4", 14, INK if st["J4"] else GREY_TXT, bold=True, anchor="middle")
    socket(sh, "J5", (3.0, 34.8, 10.0, 4.6), [(5.0 + 2 * i, 38.0) for i in range(4)], "bottom",
           ["LED_DIN", "BTN", "3V3", "GND"], st["J5"])
    sh.text(X(2.6), Y(37.6), "J5", 14, INK, bold=True, anchor="end")
    # R3 beside J5, R1 R2 JP1 next to J3
    sh.rect(X(15.0), Y(36.2), 2.6 * S, 1.4 * S, fill="#e8d5b5", stroke="#8a6d3b", sw=1.2, rx=2)
    sh.text(X(18.2), Y(37.4), "R3 330 Ω", 13, INK, bold=True)
    for yy, t in ((10.2, "R1 4.7 kΩ"), (13.0, "R2 4.7 kΩ")):
        sh.rect(X(47.0), Y(yy), 2.6 * S, 1.4 * S, fill="#e8d5b5", stroke="#8a6d3b", sw=1.2, rx=2)
        sh.text(X(46.4), Y(yy + 1.2), t, 13, INK, bold=True, anchor="end")
    for k in (0, 1):
        sh.rect(X(47.0 + 1.5 * k), Y(15.8), 1.1 * S, 1.6 * S, fill="#d9b44a", stroke="#8a6d3b", sw=1, rx=2)
    if v["jp1"]:
        sh.rect(X(47.8), Y(16.2), 1.0 * S, 0.8 * S, fill="#b8b2a4")
    sh.text(X(46.4), Y(17.0), "JP1 closed" if v["jp1"] else "JP1 open", 13, INK, bold=True, anchor="end")

    # callouts: right column J1 J3 J4 J2, above-left J6, below-left J5
    def plug(ref, txt):
        return txt if st.get(ref) else f"not fitted on {v['name']}"

    pms = v["J2"]
    xr = 810
    yb = callout(sh, xr, 210, "J1 · SEN54 socket", "JST GH 1.25 mm, 6-pin",
                 [("1", "+5V_F", ""), ("2", "GND", ""), ("3", "I2C_SDA", XPIN["I2C_SDA"]),
                  ("4", "I2C_SCL", XPIN["I2C_SCL"]), ("5", "GND", "SEL, I2C mode"), ("6", None, "not connected")],
                 plug("J1", "SEN54, on its 6-pin cable"), st["J1"])
    sh.line(X(49.0), Y(3.0), xr, Y(3.0))
    j3 = v["J3"] and f"Grove {v['J3']}, I2C " + ("0x44" if v["J3"] == "SHT40" else "0x62")
    j4 = v["J4"] and f"Grove {v['J4']}, I2C 0x44"
    grove_rows = [("1", "I2C_SCL", XPIN["I2C_SCL"]), ("2", "I2C_SDA", XPIN["I2C_SDA"]), ("3", "3V3", ""), ("4", "GND", "")]
    y3 = yb + 12
    yb = callout(sh, xr, y3, "J3 · Grove I2C socket A", "4-pin, VCC is 3V3", grove_rows, plug("J3", j3), st["J3"])
    sh.line(X(59.4), Y(13.5), xr, Y(13.5))
    y4 = yb + 12
    yb = callout(sh, xr, y4, "J4 · Grove I2C socket B", "4-pin, VCC is 3V3", grove_rows, plug("J4", j4), st["J4"])
    sh.line(X(59.4), Y(26.5), xr, Y(26.5))
    y2 = yb + 12
    yb = callout(sh, xr, y2, "J2 · Plantower socket", "Molex PicoBlade 1.25 mm, 8-pin",
                 [("1", "+5V_F", ""), ("2", "GND", ""), ("3", "PMS_SET", XPIN["PMS_SET"]),
                  ("4", "UART_TX", "D6, to PMS RXD"), ("5", "UART_RX", "D7, from PMS TXD"),
                  ("6", None, "RESET, left open"), ("7", None, "not connected"), ("8", None, "not connected")],
                 plug("J2", f"{pms}, on its own 8-pin cable"), st["J2"])
    sh.line(X(50.0), Y(37.2), 790, Y(37.2))
    sh.line(790, Y(37.2), 790, y2 + 30)
    sh.line(790, y2 + 30, xr, y2 + 30)
    callout(sh, CBX, 200 - 0, "J6 · 5 V in, JST PH 2-pin", "from the Bayu Power board",
            [("1", "+5V_IN", "through CR1 to +5V_USB"), ("2", "GND", "")],
            f"J6 and CR1 not fitted on {v['name']}", None, w=262)
    sh.line(X(4.5), 200 + 52 + 42 + 30, X(4.5), Y(0.6))
    yj5 = Y(40) + 24
    yb5 = callout(sh, CBX, yj5, "J5 · Grove GPIO socket", "optional on every variant",
                  [("1", "LED_DIN", "D1, after R3"), ("2", "BTN", "D0, button to GND"), ("3", "3V3", ""), ("4", "GND", "")],
                  "Grove RGB LED, button on a split cable", "optional", w=262)
    sh.line(X(8.0), Y(40), X(8.0), yj5)

    y = yj5 + 6
    for t in CORE_NOTES:
        y = sh.para(352, y + 14, t, 430, size=13, lead=17, fill=INK)
    return sh, max(y, yb, yb5) + 40


# ====================================================================================
# Schematic: the same blocks in the same places on every variant
# ====================================================================================
def block(sh, x, y, w, h, title, sub, state):
    absent = state is None
    sh.rect(x, y, w, h, fill=PAPER if absent else "#ffffff", stroke=GREY if absent else INK, sw=1.5, rx=6,
            dash="6 4" if state == "optional" else None)
    sh.text(x + 10, y + 21, title, 14, GREY_TXT if absent else INK, bold=True)
    if sub:
        sh.text(x + 10, y + 38, sub, 13, GREY_TXT if absent else MUTED)


def sensor(sh, y, title, sub, pins, state):
    """Sensor block in the right column, pins on its left with stubs and net tags."""
    x, w = 900, 170
    h = 52 + 22 * len(pins)
    block(sh, x, y, w, h, title, sub, state)
    for i, (label, net, note) in enumerate(pins):
        yy = y + 64 + 22 * i
        sh.text(x + 10, yy + 5, label, 13, GREY_TXT if not state else INK)
        if note:
            sh.text(x + 10 + tw(label, 13) + 8, yy + 5, note, 13, GREY_TXT if not state else MUTED)
        if net:
            sh.wire([(x, yy), (x - 34, yy)], net, w=2.5, grey=not state, dash=state == "optional")
            sh.tag(x - 38, yy + 5, net, anchor="end", grey=not state)
        else:
            sh.line(x, yy, x - 14, yy, GREY, 2)
    return y + h


def schematic(key):
    v = VARIANTS[key]
    sh = Sheet(key, "Schematic")
    sh.header(f"Same references and net names on every variant. Grey parts are not fitted on {v['name']}.")
    y = 98
    for t in TOP_NOTES_SCH[key]:
        y = sh.para(30, y, t, 690)

    # ---- U1 ----
    ux0, ux1, uy0 = 440, 640, 220
    block(sh, ux0, uy0, ux1 - ux0, 290, "U1 XIAO ESP32-S3", None, "fitted")
    left_nets = ["+5V_USB", "GND", "3V3", "LORA_SPI", "LORA_SPI", "LORA_SPI", "UART_RX"]
    right_nets = ["BTN", "LED_DIN", "PMS_SET", "VBAT_SENSE", "I2C_SDA", "I2C_SCL", "UART_TX"]
    for i, ((d, g), net) in enumerate(zip(XIAO_TOP, left_nets)):
        yy = uy0 + 58 + 30 * i
        sh.text(ux0 + 10, yy + 5, f"{d} · {g}" if g else d, 13, INK)
        if net == "LORA_SPI":
            continue
        sh.wire([(ux0, yy), (ux0 - 34, yy)], net, w=2.5)
        sh.tag(ux0 - 38, yy + 5, net, anchor="end")
    for i, ((d, g), net) in enumerate(zip(XIAO_BOT, right_nets)):
        yy = uy0 + 58 + 30 * i
        sh.text(ux1 - 10, yy + 5, f"{d} · {g}", 13, INK, anchor="end")
        sh.wire([(ux1, yy), (ux1 + 24, yy)], net, w=2.5)
        sh.tag(ux1 + 28, yy + 5, net)
    sh.text(ux0 + 10, uy0 + 270, "USB-C: the 5V pin is VBUS", 13, MUTED)

    # ---- power: F1, J6 and CR1 ----
    yp = 232
    w1 = sh.tag(40, yp + 5, "+5V_USB")
    sh.wire([(40 + w1, yp), (110 + 34, yp)], "+5V_USB", w=2.5)
    sh.rect(144, yp - 10, 48, 20, fill="#ffffff", stroke=INK, sw=1.5, rx=3)
    sh.text(168, yp - 16, "F1 1 A", 13, INK, bold=True, anchor="middle")
    sh.wire([(192, yp), (226, yp)], "+5V_F", w=2.5)
    sh.tag(230, yp + 5, "+5V_F")
    sh.text(40, yp + 28, "resettable fuse, feeds J1 and J2", 13, MUTED)
    yj, yc = 274, 309
    block(sh, 40, yj, 90, 62, "J6", None, None)
    sh.text(50, yj + 40, "1 +5V_IN", 13, GREY_TXT)
    sh.text(50, yj + 56, "2 GND", 13, GREY_TXT)
    sh.line(130, yc, 170, yc, GREY, 2.5)
    sh.add(f'<path d="M170 {yc - 10} L170 {yc + 10} L190 {yc} Z" fill="none" stroke="{GREY}" stroke-width="1.5"/>')
    sh.line(190, yc - 10, 190, yc + 10, GREY, 2.5)
    sh.line(190, yc, 226, yc, GREY, 2.5)
    sh.tag(230, yc + 5, "+5V_USB", grey=True)
    sh.text(166, yj + 18, "CR1", 13, GREY_TXT, bold=True)
    sh.text(140, yj + 60, "J6, CR1 not fitted", 13, GREY_TXT)

    # ---- U2 ----
    u2 = v["u2"]
    block(sh, 40, 352, 230, 210, "U2 Wio-SX1262", "on U1's B2B connector", u2)
    tcol = GREY_TXT if not u2 else INK
    for i, (pin, d) in enumerate((("MOSI", "D10 · GPIO9"), ("MISO", "D9 · GPIO8"), ("SCK", "D8 · GPIO7"))):
        yy = uy0 + 58 + 30 * (3 + i)
        sh.text(260, yy + 5, pin, 13, tcol, anchor="end")
        if u2:
            sh.wire([(270, yy), (ux0, yy)], "LORA_SPI", w=2, dash=u2 == "optional")
        else:
            sh.line(270, yy, 300, yy, GREY, 2)
    sh.text(282, uy0 + 58 + 90 + 21, "LORA_SPI, D8 to D10", 13, RADIO if u2 else GREY_TXT, bold=True)
    yy = 352 + 150
    for t in ("NSS GPIO41, RESET GPIO42", "BUSY GPIO40, DIO1 GPIO39", "RF switch GPIO38, B2B only"):
        sh.text(50, yy, t, 13, MUTED if u2 else GREY_TXT)
        yy += 17
    if u2:
        sh.wire([(270, 540), (470, 540), (470, uy0 + 290)], "LORA_SPI", w=2, dash=u2 == "optional")
        sh.text(280, 533, "B2B: GPIO38 to 42", 13, RADIO, bold=True)
        sh.wire([(80, 562), (80, 612)], "COAX", dash=True, w=3)
        sh.text(92, 596, "ANT: U.FL, pigtail, SMA bulkhead, whip", 13, NET["COAX"], bold=True)
        sh.text(92, 613, "never power the radio without it", 13, NET["COAX"])

    # ---- J5: R3 and U7 on pin 1, SW1 on pin 2 (split cable), CONVENTIONS.md ----
    jx, jy, g = 520, 560, 26
    block(sh, jx, jy, 70, 152, "J5", None, "optional")
    nets = ["LED_DIN", "BTN", "3V3", "GND"]
    for i, net in enumerate(nets):
        yy = jy + 50 + g * i
        sh.text(jx + 10, yy + 5, str(i + 1), 13, INK)
        if i == 0:       # board side: LED_DIN through R3
            sh.wire([(jx, yy), (jx - 24, yy)], net, w=2.5, dash=True)
            sh.rect(jx - 64, yy - 8, 40, 16, fill="#e8d5b5", stroke="#8a6d3b", sw=1.2, rx=3)
            sh.wire([(jx - 64, yy), (jx - 84, yy)], net, w=2.5, dash=True)
            sh.tag(jx - 88, yy + 5, net, anchor="end")
        else:
            sh.wire([(jx, yy), (jx - 30, yy)], net, w=2.5, dash=True)
            sh.tag(jx - 34, yy + 5, net, anchor="end")
    sh.text(jx - 44, jy + 30, "R3 330 Ω", 13, INK, bold=True, anchor="middle")
    # cable side: pins 1, 3, 4 run straight to U7; pin 2 stops at SW1, whose other side is GND
    u7 = jx + 160
    for i in (0, 2, 3):
        yy = jy + 50 + g * i
        sh.wire([(jx + 70, yy), (u7, yy)], nets[i], w=2.5, dash=True)
    yy = jy + 50 + g
    sh.wire([(jx + 70, yy), (jx + 82, yy)], "BTN", w=2.5, dash=True)
    sh.circle(jx + 85, yy, 3, "#ffffff", INK, 1.5)
    sh.line(jx + 87, yy - 1, jx + 104, yy - 7, INK, 2)
    sh.circle(jx + 106, yy, 3, "#ffffff", INK, 1.5)
    sh.wire([(jx + 109, yy), (jx + 116, yy)], "GND", w=2.5, dash=True)
    sh.tag(jx + 118, yy + 5, "GND")
    sh.text(jx + 74, yy - 10, "SW1", 13, INK, bold=True)
    sh.rect(u7, jy + 36, 100, 124, fill="#ffffff", stroke=INK, sw=1.5, rx=6, dash="6 4")
    for i, t in ((0, "DIN"), (2, "VDD"), (3, "GND")):
        sh.text(u7 + 10, jy + 55 + g * i, t, 13, INK)
    sh.text(u7 + 10, jy + 152, "U7 WS2812B", 14, INK, bold=True)

    # ---- R1, R2, JP1 ----
    rx, ry = 470, 776
    for i, (net, r) in enumerate((("I2C_SDA", "R1"), ("I2C_SCL", "R2"))):
        yy = ry + 40 * i
        tw_ = sh.tag(rx - 4, yy + 5, net, anchor="end")
        sh.wire([(rx, yy), (rx + 20, yy)], net, w=2.5)
        sh.rect(rx + 20, yy - 8, 44, 16, fill="#e8d5b5", stroke="#8a6d3b", sw=1.2, rx=3)
        sh.text(rx + 42, yy - 13 if i == 0 else yy + 25, f"{r} 4.7 kΩ", 13, INK, bold=True, anchor="middle")
        sh.line(rx + 64, yy, rx + 90, yy, INK, 2)
    sh.line(rx + 90, ry, rx + 90, ry + 40, INK, 2)
    sh.line(rx + 90, ry + 20, rx + 110, ry + 20, INK, 2)
    sh.rect(rx + 110, ry + 12, 14, 16, fill="#d9b44a", stroke="#8a6d3b", sw=1, rx=2)
    sh.rect(rx + 130, ry + 12, 14, 16, fill="#d9b44a", stroke="#8a6d3b", sw=1, rx=2)
    if v["jp1"]:
        sh.rect(rx + 122, ry + 15, 10, 10, fill="#8a8371")
    sh.wire([(rx + 144, ry + 20), (rx + 170, ry + 20)], "3V3", w=2.5)
    sh.tag(rx + 174, ry + 25, "3V3")
    sh.text(rx + 127, ry + 2, "JP1 closed" if v["jp1"] else "JP1 open", 13, INK, bold=True, anchor="middle")
    sh.text(rx - 100, ry + 76, "close JP1 only for a bare SEN54", 13, MUTED)

    # ---- sensors, right column ----
    def on(ref):
        return ref if v[ref] else None
    y = 214
    y = sensor(sh, y, "U3 SEN54 · J1" if v["J1"] else "U3 SEN54", "JST GH 6-pin, I2C 0x69" if v["J1"] else "not fitted",
               [("1 VDD", "+5V_F", ""), ("2 GND", "GND", ""), ("3 SDA", "I2C_SDA", ""), ("4 SCL", "I2C_SCL", ""),
                ("5 SEL", "GND", "I2C mode"), ("6 NC", None, "")], "fitted" if v["J1"] else None) + 12
    pms = v["J2"]
    y = sensor(sh, y, f"U4 {pms or 'PMS5003'} · J2" if pms else "U4 PMS5003", "PicoBlade 8-pin, 9600 8N1" if pms else "not fitted",
               [("1 VCC", "+5V_F", ""), ("2 GND", "GND", ""), ("3 SET", "PMS_SET", ""), ("4 RXD", "UART_TX", ""),
                ("5 TXD", "UART_RX", ""), ("6 RESET", None, "open"), ("7 NC", None, ""), ("8 NC", None, "")],
               "fitted" if pms else None) + 12
    sht = "J3" if v["J3"] == "SHT40" else "J4" if v["J4"] == "SHT40" else None
    grove = [("1 SCL", "I2C_SCL", ""), ("2 SDA", "I2C_SDA", ""), ("3 VCC", "3V3", ""), ("4 GND", "GND", "")]
    y = sensor(sh, y, f"U5 SHT40 · {sht}" if sht else "U5 SHT40", "Grove, I2C 0x44" if sht else "not fitted",
               grove, "fitted" if sht else None) + 12
    scd = "J3" if v["J3"] == "SCD40" else None
    y = sensor(sh, y, f"U6 SCD40 · {scd}" if scd else "U6 SCD40", "Grove, I2C 0x62" if scd else "not fitted",
               grove, "fitted" if scd else None)

    yn = 666
    for t in BOTTOM_NOTES_SCH[key]:
        yn = sh.para(40, yn, t, 330, size=13, lead=17) + 6
    return sh, max(y, yn, 900) + 40


# ====================================================================================
# Words on the sheets
# ====================================================================================
HEADER_ONLY = ("Solder the header into the XIAO only and trim the stubs flush. The Wio's edge pads over "
               "D0 to D4 carry radio lines, a pin through both boards ties them to the button, LED, SET and SDA.")
FIRMWARE = ("Firmware: Meshtastic (Bayu variant) listens on D7, drives D6 to the PMS RXD and D2 to SET, so it can "
            "sleep the fan. Smart Citizen v5 only listens on D7 and never drives the PMS, SET then floats high "
            "and the fan keeps running. Wire all three and the same node runs either.")
PMS_OPEN = ("PMS pins 6 (RESET), 7 and 8 stay open. The sensor pulls SET and RESET up inside, so there is no "
            "resistor on them. Logic is 3.3 V on every line, no level shifter.")
OPTIONAL = ("SW1 and U7 are optional and only the Meshtastic build uses them, v5 reads the XIAO's own BOOT "
            "button. R3, 330 Ω, sits in series on the LED data line on every variant. U7 runs on 3V3. The "
            "WS2812B asks for 3.5 V, but one pixel lights fine on 3.3 V and then reads the GPIO cleanly.")
POWER = ("Power: a 5 V / 2 A USB-C wall supply. The XIAO's 5V pin is USB VBUS, the top rail carries it as "
         "+5V_USB. On the Core it goes through F1 first and becomes +5V_F.")

TOP_NOTES_BB = {
    "anchor": [HEADER_ONLY, "Never power the radio without its antenna. D8, D9 and D10 are the radio's SPI bus, "
               "leave them empty.", "R1 and R2 are the 4.7 kΩ pull-ups the bare SEN54 needs. The Grove SHT40 "
               "brings its own 10 kΩ."],
    "dense": ["The Wio-SX1262 is optional. If you fit it: " + HEADER_ONLY[0].lower() + HEADER_ONLY[1:],
              "Never power the radio without its antenna, and leave D8 to D10 empty for its SPI bus.",
              "Plug in the WiFi antenna that comes with the XIAO, the plain XIAO has none on the board."],
    "indoor": ["WiFi only, no Wio-SX1262. Plug in the WiFi antenna that comes with the XIAO.",
               "Most SCD40 and SHT40 breakouts carry 10 kΩ pull-ups. Two of them make 5 kΩ, fine at 100 kHz, "
               "so add none. A bare sensor without a breakout needs 4.7 kΩ to 3V3.",
               "3V3 budget: the regulator gives 700 mA. WiFi transmit takes up to about 340 mA and the SCD40 "
               "205 mA at its peak, about 550 mA together."],
    "relay": [HEADER_ONLY, "Never power the radio without its antenna. D8, D9 and D10 are the radio's SPI bus, "
              "leave them empty.", "No PM sensor on a Relay, so D2, D3, D6 and D7 stay free."],
}
BOTTOM_NOTES_BB = {
    "anchor": [FIRMWARE, PMS_OPEN + " SEN54 pin 6 is not connected.",
               "Keep the I2C wires under 10 cm, Sensirion asks for it. Both sensor cases are tied to their GND pin, "
               "keep them off other metal.", OPTIONAL, POWER],
    "dense": [FIRMWARE, PMS_OPEN + " Check pin 1 on your own cable before the first power-up.",
              "The PMS5003T reads T and RH inside its own case, in the fan's air. Publish them as indicative, never "
              "as air temperature.", OPTIONAL, POWER],
    "indoor": [FIRMWARE, PMS_OPEN + " The PMS cable needs a PicoBlade to 2.54 mm adapter, or dupont ends "
               "crimped on.", "In the shell the SHT40 and SCD40 sit upstream of the PMS exhaust, away from the "
               "XIAO, see placement.svg.", OPTIONAL, POWER],
    "relay": ["The SHT40 is drawn as the Grove board that goes on J3. On the breadboard an Adafruit 4885 works "
              "too: VIN to 3V3, its 3V pin left open. Clone boards order their pins differently, read the "
              "silkscreen.", "The LoRa whip goes out through the SMA bulkhead, the XIAO's WiFi antenna stays "
              "inside the box.", OPTIONAL, POWER],
}
TOP_NOTES_CORE = {
    "anchor": ["On the Anchor: U2, J1 SEN54, J2 PMS5003, J3 SHT40, JP1 closed for the bare SEN54. J4 stays "
               "empty, J5 is optional.", HEADER_ONLY],
    "dense": ["On Dense: J2 takes the PMS5003T's own cable. U2 is optional. J1, J3 and J4 stay empty, JP1 open, "
              "J5 optional.", "Plug the cable's pin 1 into pin 1 here. With U2: " + HEADER_ONLY[0].lower()
              + HEADER_ONLY[1:]],
    "indoor": ["On Indoor: J2 PMS5003, J3 SCD40, J4 SHT40. No U2, J1 stays empty, JP1 open because the Grove "
               "boards bring their own pull-ups. J5 optional.",
               "Before the first power-up, beep J2 pin 1 through to the sensor's pin 1. A PicoBlade cable can be "
               "crimped 1-to-1 or flipped, and a flipped one leaves the PMS unpowered with D6 on its TXD pin."],
    "relay": ["On the Relay: U2 and J3 SHT40. J1, J2 and J4 stay empty, JP1 open because the Grove SHT40 brings "
              "its own pull-ups. J5 optional.", HEADER_ONLY],
}
CORE_NOTES = [
    "F1, 1 A resettable fuse from +5V_USB to +5V_F, which feeds J1 and J2. A shorted cable trips F1 and "
    "leaves the USB supply alone.",
    "CR1, Schottky from +5V_IN to +5V_USB, so USB power never flows back into the Power board. Seeed asks for "
    "a diode on any external 5 V into the XIAO's 5V pin.",
    "R1, R2, 4.7 kΩ I2C pull-ups to 3V3 through JP1. Close JP1 only for a bare SEN54.",
    "J2 pin 6 RESET stays open, the PMS pulls SET and RESET up inside. There is no resistor on it.",
    "Grove VCC on J3, J4 and J5 is 3V3. D8 to D10 carry U2's SPI, no connector uses them. Keep 25 mm clear "
    "above U1 for the stack and the pigtail.",
]
TOP_NOTES_SCH = {
    "anchor": ["Anchor: U2 fitted, U3 SEN54 on J1, U4 PMS5003 on J2, U5 SHT40 on J3, JP1 closed.",
               "Net names follow the XIAO: UART_TX leaves D6 for the PMS RXD, UART_RX comes back from the PMS TXD "
               "into D7.", "Never power the radio without its antenna."],
    "dense": ["Dense: U4 PMS5003T on J2, U2 optional (dashed), JP1 open.",
              "Net names follow the XIAO: UART_TX leaves D6 for the PMS RXD, UART_RX comes back from the PMS TXD "
              "into D7.", "The PMS5003T's T and RH come from inside the sensor, in the fan's air. Treat them as indicative."],
    "indoor": ["Indoor: U4 PMS5003 on J2, U6 SCD40 on J3, U5 SHT40 on J4, no U2, JP1 open.",
               "Net names follow the XIAO: UART_TX leaves D6 for the PMS RXD, UART_RX comes back from the PMS TXD "
               "into D7.", "The SCD40 and SHT40 breakouts bring their own 10 kΩ pull-ups."],
    "relay": ["Relay: U2 fitted, U5 SHT40 on J3, JP1 open. No PM sensor.",
              "D2, D3, D6 and D7 are free on a Relay. The radio takes D8 to D10 and GPIO38 to 42.",
              "Never power the radio without its antenna."],
}
_SCH_COMMON = ["SW1 needs no resistor, the firmware turns on GPIO1's internal pull-up.",
               "D3 · GPIO4 is VBAT_SENSE, used only with the Bayu Power board.",
               "U2's edge pads over D0 to D4 carry its radio lines, so the header goes into the XIAO only."]
BOTTOM_NOTES_SCH = {k: _SCH_COMMON if v["u2"] else _SCH_COMMON[:2] for k, v in VARIANTS.items()}


# ====================================================================================
# Check: what the review asked for, so it fails loudly instead of in a render
# ====================================================================================
def problems(sh, H):
    out = []
    T = sh.texts
    for i, a in enumerate(T):
        if a[0] < 4 or a[2] > W - 4 or a[3] > H - 52:
            out.append(f"off the sheet: {a[4]!r}")
        for b in T[i + 1:]:
            if a[0] < b[2] - 1 and b[0] < a[2] - 1 and a[1] < b[3] - 1 and b[1] < a[3] - 1:
                out.append(f"text on text: {a[4]!r} / {b[4]!r}")
    for (p, q, net, wid) in sh.segs:
        L = max(abs(q[0] - p[0]), abs(q[1] - p[1]))
        steps = max(1, int(L / 2))
        for t in T:
            for k in range(steps + 1):
                x = p[0] + (q[0] - p[0]) * k / steps
                y = p[1] + (q[1] - p[1]) * k / steps
                if t[0] - 2 < x < t[2] + 2 and t[1] - 2 < y < t[3] + 2:
                    out.append(f"{net} wire through {t[4]!r}")
                    break
    segs = sh.segs
    for i, (p, q, n1, w1) in enumerate(segs):
        for (r, s, n2, w2) in segs[i + 1:]:
            if w1 == w2:
                continue
            if p[0] == q[0] and r[0] == s[0] and abs(p[0] - r[0]) < 6:
                lo, hi = max(min(p[1], q[1]), min(r[1], s[1])), min(max(p[1], q[1]), max(r[1], s[1]))
                if hi - lo > 3:
                    out.append(f"{n1} and {n2} run on top of each other at x={p[0]:.0f}")
            if p[1] == q[1] and r[1] == s[1] and abs(p[1] - r[1]) < 6:
                lo, hi = max(min(p[0], q[0]), min(r[0], s[0])), min(max(p[0], q[0]), max(r[0], s[0]))
                if hi - lo > 3:
                    out.append(f"{n1} and {n2} run on top of each other at y={p[1]:.0f}")
    return sorted(set(out))


if __name__ == "__main__":
    bad = 0
    for key in VARIANTS:
        for fname, fn in (("wiring-breadboard.svg", breadboard), ("wiring-core.svg", core), ("schematic.svg", schematic)):
            sh, H = fn(key)
            H = int(H + 52)
            path = os.path.join(HERE, key, fname)
            with open(path, "w", encoding="utf-8") as f:
                f.write(sh.svg(H))
            found = problems(sh, H)
            bad += len(found)
            print(f"wrote {key}/{fname} ({H} px)" + "".join(f"\n  ! {p}" for p in found))
    raise SystemExit(1 if bad else 0)
