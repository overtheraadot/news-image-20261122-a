#!/usr/bin/env python3
"""THE WORLD TODAY - one-page broadsheet front page for Sunday 22 November 2026.

Draws a 1024x1024 PNG with pure Python standard library only: a masthead
with the date, one big hero story (Iran strikes US bases across the Gulf)
with a drawn scene of the Gulf at dawn, a dense grid of 30 story tiles each
with a tiny drawn pictogram, a short headline and a one-line caption, and a
bottom ticker strip. No PIL, no third-party imports: hand-rolled pixel
buffer, drawing primitives, a hand-drawn 5x7 bitmap font (all-caps
broadsheet style) and a struct+zlib PNG encoder. Deterministic: every
story is baked into this file, no randomness, no network, no clock reads.

Run:  python3 main.py
Writes entry.png to $MAKEFUN_OUTPUT_DIR (default /output/entry.png).
"""

import os
import struct
import zlib

W = H = 1024

PAPER = (247, 242, 230)
PAPER2 = (252, 249, 240)
INK = (18, 18, 18)
NAVY = (13, 32, 58)
NAVY2 = (24, 52, 86)
RED = (172, 28, 32)
RED2 = (198, 52, 44)
GREY = (96, 94, 88)
DARKGREY = (64, 62, 58)
RULE = (186, 176, 152)
LIGHTRULE = (214, 207, 188)
WHITE = (255, 255, 255)
GOLD = (212, 160, 44)
CREAM = (250, 246, 236)
SKY = (146, 190, 214)
SKY2 = (214, 176, 120)
SEA = (38, 84, 118)
SEA2 = (24, 60, 92)
SAND = (214, 196, 150)
ORANGE = (224, 110, 30)
YELLOW = (244, 196, 66)
GREEN = (46, 120, 66)
TEAL = (24, 128, 118)
PURPLE = (104, 72, 150)
BROWN = (122, 84, 52)
PINK = (196, 96, 120)

# ---------------------------------------------------------------- font
# 5x7 bitmap font, all caps. Each glyph is 7 rows of 5 bits ('#' = on).
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("01110", "10000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00001", "01110"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00010", "00100", "00000", "00100"),
    "-": ("00000", "00000", "00000", "11111", "00000", "00000", "00000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    ">": ("10000", "01000", "00100", "00010", "00100", "01000", "10000"),
    "<": ("00001", "00010", "00100", "01000", "00100", "00010", "00001"),
    "*": ("00000", "10101", "01110", "11111", "01110", "10101", "00000"),
    "#": ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    "@": ("01110", "10001", "10111", "10101", "10110", "10000", "01110"),
}


# ---------------------------------------------------------------- canvas
class Canvas:
    """RGB pixel buffer with small drawing primitives."""

    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.buf = bytearray(w * h * 3)
        r, g, b = bg
        for i in range(0, len(self.buf), 3):
            self.buf[i] = r
            self.buf[i + 1] = g
            self.buf[i + 2] = b

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.buf[i] = c[0]
            self.buf[i + 1] = c[1]
            self.buf[i + 2] = c[2]

    def rect(self, x, y, w, h, c):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.buf[i] = c[0]
                self.buf[i + 1] = c[1]
                self.buf[i + 2] = c[2]

    def hline(self, x, y, w, c):
        self.rect(x, y, w, 1, c)

    def vline(self, x, y, h, c):
        self.rect(x, y, 1, h, c)

    def line(self, x0, y0, x1, y1, c):
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        x, y = x0, y0
        while True:
            self.set(x, y, c)
            if x == x1 and y == y1:
                return
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy

    def circle(self, cx, cy, r, c):
        x = 0
        y = r
        d = 3 - 2 * r
        while x <= y:
            for px, py in ((cx + x, cy + y), (cx - x, cy + y), (cx + x, cy - y),
                           (cx - x, cy - y), (cx + y, cy + x), (cx - y, cy + x),
                           (cx + y, cy - x), (cx - y, cy - x)):
                self.set(px, py, c)
            if d < 0:
                d += 4 * x + 6
            else:
                d += 4 * (x - y) + 10
                y -= 1
            x += 1

    def fcircle(self, cx, cy, r, c):
        for yy in range(cy - r, cy + r + 1):
            dx = int((r * r - (yy - cy) * (yy - cy)) ** 0.5) if abs(yy - cy) <= r else 0
            self.rect(cx - dx, yy, 2 * dx + 1, 1, c)

    def triangle(self, x0, y0, x1, y1, x2, y2, c):
        # Filled triangle via scanline interpolation.
        pts = sorted(((x0, y0), (x1, y1), (x2, y2)), key=lambda p: p[1])
        (ax, ay), (bx, by), (cx, cy) = pts
        if ay == cy:
            return
        def interp(y, p, q):
            if q[1] == p[1]:
                return p[0]
            return p[0] + (q[0] - p[0]) * (y - p[1]) / (q[1] - p[1])
        for y in range(ay, cy + 1):
            if y < by:
                xa = interp(y, (ax, ay), (bx, by))
                xb = interp(y, (ax, ay), (cx, cy))
            else:
                xa = interp(y, (bx, by), (cx, cy))
                xb = interp(y, (ax, ay), (cx, cy))
            lo, hi = (int(min(xa, xb)), int(max(xa, xb)))
            self.rect(lo, y, hi - lo + 1, 1, c)

    def ellipse(self, cx, cy, rx, ry, c):
        for yy in range(cy - ry, cy + ry + 1):
            t = (yy - cy) / ry if ry else 0
            if abs(t) > 1:
                continue
            dx = int(rx * (1 - t * t) ** 0.5)
            self.rect(cx - dx, yy, 2 * dx + 1, 1, c)

    def starburst(self, cx, cy, r0, r1, n, c):
        import math
        for k in range(n):
            a = 2 * math.pi * k / n
            x1 = int(cx + r1 * math.cos(a))
            y1 = int(cy + r1 * math.sin(a))
            self.line(cx, cy, x1, y1, c)
            a2 = a + math.pi / n
            x2 = int(cx + r0 * math.cos(a2))
            y2 = int(cy + r0 * math.sin(a2))
            self.line(cx, cy, x2, y2, c)

    # ------------------------------------------------------------ text
    def text(self, x, y, s, scale, c, align="left"):
        s = s.upper()
        cw = 6 * scale
        if align == "center":
            x -= (len(s) * cw - scale) // 2
        elif align == "right":
            x -= len(s) * cw - scale
        for ch_i, ch in enumerate(s):
            glyph = FONT.get(ch, FONT[" "])
            gx = x + ch_i * cw
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits[col] == "1":
                        self.rect(gx + col * scale, y + row * scale, scale, scale, c)
        return len(s) * cw - scale

    def text_width(self, s, scale):
        return len(s.upper()) * 6 * scale - scale

    def wrap(self, s, scale, max_w):
        """Greedy word wrap; returns list of lines, each <= max_w px wide."""
        words = s.upper().split(" ")
        lines = []
        cur = ""
        for w in words:
            trial = (cur + " " + w).strip()
            if self.text_width(trial, scale) <= max_w:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
        return lines


# ---------------------------------------------------------------- icons
# Each icon draws inside a 22x22 box at (x, y). Keep them bold and simple:
# at tile size they must read at a glance.
def icon(c, kind, x, y, col):
    if kind == "blast":  # explosion starburst
        c.starburst(x + 11, y + 11, 4, 10, 8, col)
        c.fcircle(x + 11, y + 11, 3, YELLOW)
    elif kind == "missile":  # missile on a diagonal trail
        c.line(x + 3, y + 19, x + 15, y + 7, GREY)
        c.triangle(x + 15, y + 3, x + 20, y + 8, x + 14, y + 9, col)
        c.fcircle(x + 4, y + 18, 2, ORANGE)
        c.fcircle(x + 7, y + 15, 2, YELLOW)
    elif kind == "ship":  # cargo ship on waves
        c.rect(x + 2, y + 9, 18, 6, col)
        c.rect(x + 4, y + 4, 6, 5, col)
        c.rect(x + 12, y + 6, 5, 3, col)
        c.line(x + 1, y + 18, x + 21, y + 18, SEA)
        c.line(x + 3, y + 20, x + 19, y + 20, SEA)
    elif kind == "flag":  # flag on a pole
        c.vline(x + 4, y + 2, 18, INK)
        c.triangle(x + 4, y + 2, x + 19, y + 6, x + 4, y + 10, col)
    elif kind == "shield":  # shield
        c.triangle(x + 3, y + 3, x + 19, y + 3, x + 11, y + 7, col)
        c.rect(x + 3, y + 3, 16, 9, col)
        c.triangle(x + 3, y + 11, x + 19, y + 11, x + 11, y + 20, col)
        c.text(x + 8, y + 6, "!", 1, WHITE)
    elif kind == "target":  # concentric target
        c.circle(x + 11, y + 11, 9, col)
        c.circle(x + 11, y + 11, 5, col)
        c.fcircle(x + 11, y + 11, 2, RED)
    elif kind == "warn":  # warning triangle
        c.triangle(x + 11, y + 2, x + 20, y + 19, x + 2, y + 19, col)
        c.text(x + 9, y + 9, "!", 1, WHITE)
    elif kind == "globe":  # globe with meridians
        c.circle(x + 11, y + 11, 9, col)
        c.line(x + 11, y + 2, x + 11, y + 20, col)
        c.line(x + 2, y + 11, x + 20, y + 11, col)
        c.ellipse(x + 11, y + 11, 5, 9, col)
    elif kind == "trade":  # two-way arrows
        c.line(x + 2, y + 7, x + 18, y + 7, col)
        c.triangle(x + 18, y + 7, x + 13, y + 4, x + 13, y + 10, col)
        c.line(x + 20, y + 15, x + 4, y + 15, col)
        c.triangle(x + 4, y + 15, x + 9, y + 12, x + 9, y + 18, col)
    elif kind == "ballot":  # ballot box with tick
        c.rect(x + 3, y + 8, 16, 11, col)
        c.rect(x + 7, y + 3, 8, 5, WHITE)
        c.line(x + 6, y + 14, x + 10, y + 17, WHITE)
        c.line(x + 10, y + 17, x + 17, y + 9, WHITE)
    elif kind == "summit":  # two flags (a summit)
        c.vline(x + 5, y + 3, 16, INK)
        c.triangle(x + 5, y + 3, x + 13, y + 6, x + 5, y + 9, col)
        c.vline(x + 15, y + 5, 14, INK)
        c.triangle(x + 15, y + 5, x + 21, y + 8, x + 15, y + 11, RED)
    elif kind == "chat":  # speech bubble
        c.rect(x + 3, y + 3, 16, 11, col)
        c.triangle(x + 7, y + 14, x + 11, y + 14, x + 7, y + 19, col)
        c.hline(x + 6, y + 7, 10, WHITE)
        c.hline(x + 6, y + 10, 7, WHITE)
    elif kind == "robot":  # robot head
        c.rect(x + 5, y + 6, 12, 11, col)
        c.vline(x + 11, y + 2, 4, col)
        c.fcircle(x + 11, y + 2, 2, RED)
        c.fcircle(x + 8, y + 11, 2, WHITE)
        c.fcircle(x + 14, y + 11, 2, WHITE)
        c.hline(x + 8, y + 15, 6, WHITE)
    elif kind == "pin":  # map pin
        c.fcircle(x + 11, y + 8, 7, col)
        c.triangle(x + 5, y + 11, x + 17, y + 11, x + 11, y + 21, col)
        c.fcircle(x + 11, y + 8, 3, WHITE)
    elif kind == "star":  # five-point star (approx)
        c.starburst(x + 11, y + 11, 5, 10, 5, col)
        c.fcircle(x + 11, y + 11, 4, col)
    elif kind == "quake":  # cracked ground
        c.line(x + 2, y + 4, x + 8, y + 10, col)
        c.line(x + 8, y + 10, x + 5, y + 15, col)
        c.line(x + 5, y + 15, x + 11, y + 19, col)
        c.line(x + 20, y + 3, x + 14, y + 9, col)
        c.line(x + 14, y + 9, x + 18, y + 14, col)
        c.line(x + 18, y + 14, x + 12, y + 20, col)
    elif kind == "health":  # medical cross
        c.rect(x + 8, y + 2, 6, 18, col)
        c.rect(x + 2, y + 8, 18, 6, col)
    elif kind == "cloud":  # storm cloud with rain
        c.ellipse(x + 11, y + 9, 9, 5, col)
        c.fcircle(x + 6, y + 9, 4, col)
        c.fcircle(x + 16, y + 9, 4, col)
        c.vline(x + 6, y + 16, 4, SEA)
        c.vline(x + 11, y + 16, 4, SEA)
        c.vline(x + 16, y + 16, 4, SEA)
    elif kind == "bridge":  # suspension bridge
        c.vline(x + 3, y + 5, 13, col)
        c.vline(x + 18, y + 5, 13, col)
        c.hline(x + 1, y + 17, 20, col)
        c.line(x + 3, y + 5, x + 11, y + 12, col)
        c.line(x + 18, y + 5, x + 11, y + 12, col)
    elif kind == "atom":  # atom with orbits
        c.fcircle(x + 11, y + 11, 3, col)
        c.ellipse(x + 11, y + 11, 9, 4, col)
        c.ellipse(x + 11, y + 11, 4, 9, col)
    elif kind == "ball":  # football
        c.circle(x + 11, y + 11, 9, INK)
        c.fcircle(x + 11, y + 11, 3, INK)
        c.line(x + 11, y + 2, x + 11, y + 8, INK)
        c.line(x + 11, y + 14, x + 11, y + 20, INK)
        c.line(x + 3, y + 7, x + 8, y + 10, INK)
        c.line(x + 19, y + 7, x + 14, y + 10, INK)
    elif kind == "coin":  # coin with $
        c.fcircle(x + 11, y + 11, 9, col)
        c.circle(x + 11, y + 11, 9, INK)
        c.text(x + 8, y + 8, "$", 1, INK)
    elif kind == "dove":  # olive branch (peace)
        c.line(x + 4, y + 19, x + 18, y + 5, GREEN)
        c.ellipse(x + 8, y + 12, 4, 2, GREEN)
        c.ellipse(x + 14, y + 8, 4, 2, GREEN)
        c.fcircle(x + 18, y + 5, 2, GREEN)
    elif kind == "rocket":  # rocket
        c.triangle(x + 11, y + 1, x + 16, y + 11, x + 6, y + 11, col)
        c.rect(x + 8, y + 11, 6, 5, col)
        c.triangle(x + 8, y + 11, x + 4, y + 17, x + 8, y + 16, RED)
        c.triangle(x + 14, y + 11, x + 18, y + 17, x + 14, y + 16, RED)
        c.triangle(x + 11, y + 16, x + 13, y + 21, x + 9, y + 21, ORANGE)


# ---------------------------------------------------------------- hero scene
def draw_hero_scene(c, x, y, w, h):
    """The Gulf at dawn: sky, low sun, sea, a tanker and a warship with a
    radar dome, missile arcs overhead and bursts over the water."""
    # Sky bands, pale dawn to deeper blue.
    bands = [(SKY2, 0.0), ((196, 172, 128), 0.25), (SKY, 0.5), ((120, 168, 198), 0.75)]
    for yy in range(h):
        t = yy / max(1, h - 1)
        col = bands[0][0]
        for i in range(len(bands) - 1):
            c0, t0 = bands[i]
            c1, t1 = bands[i + 1]
            if t0 <= t <= t1:
                f = (t - t0) / max(0.001, t1 - t0)
                col = tuple(int(c0[k] + (c1[k] - c0[k]) * f) for k in range(3))
                break
        c.rect(x, y + yy, w, 1, col)
    # Low sun.
    sx, sy = x + int(w * 0.78), y + int(h * 0.30)
    c.fcircle(sx, sy, 26, (244, 200, 110))
    c.fcircle(sx, sy, 18, (250, 220, 150))
    # Distant coastline.
    c.rect(x, y + int(h * 0.52), w, 4, SAND)
    c.rect(x, y + int(h * 0.52) + 4, w, 8, (196, 178, 132))
    # Sea.
    c.rect(x, y + int(h * 0.58), w, h - int(h * 0.58), SEA)
    c.rect(x, y + int(h * 0.58), w, 2, SEA2)
    for k in range(14):
        wx = x + 30 + k * 72
        wy = y + int(h * 0.62) + (k % 4) * 16
        c.hline(wx, wy, 34, (120, 170, 200))
    # Tanker, left.
    tx, ty = x + 60, y + int(h * 0.60)
    c.rect(tx, ty + 18, 210, 22, (96, 96, 100))
    c.rect(tx + 8, ty, 60, 18, (96, 96, 100))
    c.rect(tx + 90, ty + 4, 44, 14, (140, 40, 36))
    c.rect(tx + 150, ty + 8, 40, 10, (200, 200, 200))
    c.vline(tx + 200, ty - 6, 24, (96, 96, 100))
    # Warship with radar dome, right.
    wx0, wy0 = x + int(w * 0.62), y + int(h * 0.58)
    c.rect(wx0, wy0 + 22, 190, 18, (112, 118, 124))
    c.triangle(wx0 + 190, wy0 + 22, wx0 + 214, wy0 + 40, wx0 + 190, wy0 + 40, (112, 118, 124))
    c.rect(wx0 + 30, wy0 + 4, 70, 18, (128, 134, 140))
    c.fcircle(wx0 + 130, wy0 + 6, 12, WHITE)
    c.fcircle(wx0 + 130, wy0 + 6, 12, (210, 210, 210))
    c.vline(wx0 + 60, wy0 - 10, 14, (112, 118, 124))
    # Missile arcs: quadratic curves sampled point by point.
    def arc(x0, y0, cx, cy, x1, y1, col, n=60):
        px, py = None, None
        for i in range(n + 1):
            t = i / n
            mx = (1 - t) * (1 - t) * x0 + 2 * (1 - t) * t * cx + t * t * x1
            my = (1 - t) * (1 - t) * y0 + 2 * (1 - t) * t * cy + t * t * y1
            if px is not None:
                c.line(int(px), int(py), int(mx), int(my), col)
            px, py = mx, my
    arc(x + 120, y + 40, x + 320, y - 30, x + 560, y + 96, (90, 90, 90))
    arc(x + 700, y + 30, x + 820, y - 20, x + 920, y + 84, (90, 90, 90))
    # Missile heads.
    c.triangle(x + 556, y + 88, x + 566, y + 98, x + 552, y + 100, INK)
    c.triangle(x + 916, y + 76, x + 926, y + 86, x + 912, y + 88, INK)
    # Explosions over the water.
    ex, ey = x + 560, y + int(h * 0.66)
    c.starburst(ex, ey, 8, 34, 10, ORANGE)
    c.starburst(ex, ey, 4, 20, 10, YELLOW)
    c.fcircle(ex, ey, 9, YELLOW)
    ex2, ey2 = x + 920, y + int(h * 0.62)
    c.starburst(ex2, ey2, 6, 24, 8, ORANGE)
    c.fcircle(ex2, ey2, 7, YELLOW)
    # Smoke columns, hugging the bursts.
    for sx0, sy0, sh in ((ex - 4, ey - 8, 30), (ex2 - 3, ey2 - 6, 24)):
        c.fcircle(sx0, sy0 - sh // 2, 7, (120, 118, 112))
        c.fcircle(sx0 + 5, sy0 - sh, 5, (140, 138, 130))


# ---------------------------------------------------------------- stories
# (tag, tag colour, icon, headline, caption) - all first reported on
# Sunday 22 November 2026, verified against the morning news wires.
STORIES = [
    ("WAR", RED, "blast", "LVIV STRIKE",
     "Russian missile hits Lviv; 2 killed, 10 hurt in blast"),
    ("WAR", RED, "missile", "400-DRONE BARRAGE",
     "Russia fires 400 drones and 110 missiles at Ukraine"),
    ("WAR", RED, "ship", "BALTIC SHIP HIT",
     "Drones set Russian cargo ship ablaze; Finland on alert"),
    ("WAR", RED, "flag", "POLAND PROBE",
     "Warsaw investigates Russian missile fall on its soil"),
    ("WAR", RED, "flag", "ESTONIA SHUTS BORDER",
     "Tallinn to close frontier with Russia, Moscow fumes"),
    ("WAR", RED, "shield", "NATO PLEDGE",
     "Zelenskyy: NATO is the clearest security guarantee"),
    ("WAR", RED, "target", "ISKANDER FUEL HIT",
     "Kyiv strikes plant making fuel for Iskander missiles"),
    ("WAR", RED, "warn", "KINDERGARTEN HIT",
     "Russian strike wounds children in Zaporizhzhya region"),
    ("CLIMATE", GREEN, "globe", "COP31 DEADLOCK",
     "Climate talks in overtime; fossil fuels cut from draft"),
    ("TRADE", TEAL, "trade", "EU-INDONESIA DEAL",
     "Ten-year talks end; 98.5% of tariffs to be scrapped"),
    ("POLITICS", NAVY2, "ballot", "HONG KONG VOTES",
     "5,700 voters pick powerful Election Committee"),
    ("POLITICS", NAVY2, "summit", "TRUMP-XI FALLOUT",
     "Shenzhen summit reverberates; Japan under pressure"),
    ("POLITICS", NAVY2, "chat", "TRUMP ON IRAN",
     "Trump: Iran deal could last 20 years, eyes change"),
    ("POLITICS", NAVY2, "dove", "CEASEFIRE CALL",
     "Melania Trump seeks more truces before Christmas"),
    ("TECH", PURPLE, "robot", "ROBOT WEAPONS",
     "UN talks fail to set rules for killer robots"),
    ("WAR", RED, "pin", "SUDAN OFFENSIVE",
     "Tasis alliance seizes Bau in the Blue Nile region"),
    ("WORLD", BROWN, "star", "EL CHAPO ISIDRO",
     "Mexico captures FBI most-wanted cartel boss"),
    ("WORLD", BROWN, "quake", "PERU QUAKE",
     "M6.7 quake shakes Andes; no casualties reported"),
    ("WORLD", BROWN, "quake", "MYANMAR TREMOR",
     "M4.1 quake strikes Myanmar in the early hours"),
    ("HEALTH", PINK, "health", "MANIPUR POISON",
     "Toxic alcohol kills 11 and sickens 180 in India"),
    ("WEATHER", SEA, "cloud", "CYCLONE AKVAN",
     "Storm forces 14 flights cancelled at Ranchi airport"),
    ("WORLD", BROWN, "bridge", "NITISH SETU OPENS",
     "Modi opens Bihar bridge linking Patna and Vaishali"),
    ("WORLD", BROWN, "flag", "JAPAN-INDIA DRILLS",
     "Japanese troops to train live-fire in India, a first"),
    ("WORLD", BROWN, "health", "BOLSONARO IN ICU",
     "Brazil ex-president in ICU with bowel obstruction"),
    ("POLITICS", NAVY2, "warn", "DENMARK EXPULSION",
     "Copenhagen expels Russian aide over rapper plot"),
    ("WORLD", BROWN, "chat", "ZAGREB PROTEST",
     "Croats rally over psychiatric hospital death"),
    ("POLITICS", NAVY2, "ballot", "ISRAEL COALITION",
     "Eisenkot invites Likud to coalition talks"),
    ("WAR", RED, "shield", "HOUTHI MISSILE",
     "Saudi coalition deflects Houthi missile in west"),
    ("POLITICS", NAVY2, "chat", "HAMAS TALKS",
     "Turkish intel chief meets Hamas team in Istanbul"),
    ("SCIENCE", PURPLE, "atom", "RIEMANN CLAIM",
     "Mathematician claims AI-aided proof of Riemann"),
]

TICKER = ("US AIRLINES WARNED OF AL-QAEDA THREAT BEFORE THANKSGIVING"
          "  *  AUSTRALIA ENDS ENGLAND'S T20 STREAK"
          "  *  BYU OUTLASTS KANSAS 31-29 IN 3OT"
          "  *  HEARTS ROUT DUNDEE 8-0"
          "  *  BOCA WIN COPA SUDAMERICANA 2-0"
          "  *  PRINCE WILLIAM INSURES 10,000 FOREST WORKERS")


# ---------------------------------------------------------------- layout
def build():
    c = Canvas(W, H, PAPER)
    # Outer frame.
    c.rect(0, 0, W, 4, INK)
    c.rect(0, H - 4, W, 4, INK)
    c.rect(0, 0, 4, H, INK)
    c.rect(W - 4, 0, 4, H, INK)

    # ---- Masthead ------------------------------------------------
    c.text(14, 14, "NO. 326", 1, GREY)
    c.text(1010, 14, "SUNDAY EDITION", 1, GREY, align="right")
    c.text(W // 2, 30, "THE WORLD TODAY", 9, INK, align="center")
    c.hline(14, 102, 996, INK)
    c.hline(14, 105, 996, INK)
    c.text(14, 112, "ONE DAY - ONE PAGE", 1, GREY)
    c.text(W // 2, 108, "SUNDAY, 22 NOVEMBER 2026", 2, RED, align="center")
    c.text(1010, 112, "ALL THE WORLD'S NEWS", 1, GREY, align="right")

    # ---- Hero ----------------------------------------------------
    c.text(W // 2, 128, "IRAN STRIKES US BASES", 5, INK, align="center")
    c.text(W // 2, 165, "IN THE GULF", 5, RED, align="center")
    draw_hero_scene(c, 10, 204, 1004, 154)
    c.rect(10, 204, 1004, 2, INK)
    c.rect(10, 356, 1004, 2, INK)
    deck = ("MISSILES AND DRONES HIT PATRIOT RADARS IN BAHRAIN AND KUWAIT; "
            "TANKERS ATTACKED OFF OMAN AS THE REGION BRACES FOR MORE.")
    lines = c.wrap(deck, 1, 980)
    yy = 364
    for ln in lines:
        c.text(W // 2, yy, ln, 1, DARKGREY, align="center")
        yy += 9

    # ---- Section header ------------------------------------------
    c.hline(14, 398, 996, INK)
    c.text(14, 404, "THE DAY IN 30 STORIES", 2, NAVY)
    c.text(1010, 406, "WORLD - POLITICS - SPORT - SCIENCE", 1, GREY, align="right")
    c.hline(14, 424, 996, RULE)

    # ---- Story grid ----------------------------------------------
    for i, (tag, tagcol, ic, head, cap) in enumerate(STORIES):
        row, col = divmod(i, 5)
        tx = 10 + col * 202
        ty = 430 + row * 82
        c.rect(tx, ty, 196, 76, PAPER2)
        c.rect(tx, ty, 196, 1, RULE)
        c.rect(tx, ty + 75, 196, 1, RULE)
        c.rect(tx, ty, 1, 76, RULE)
        c.rect(tx + 195, ty, 1, 76, RULE)
        icon(c, ic, tx + 6, ty + 4, tagcol)
        c.text(tx + 32, ty + 9, tag, 1, tagcol)
        hlines = c.wrap(head, 2, 184)
        hy = ty + 29
        for ln in hlines[:2]:
            c.text(tx + 6, hy, ln, 2, INK)
            hy += 14
        clines = c.wrap(cap, 1, 184)
        cy = hy + 2
        for ln in clines[:2]:
            c.text(tx + 6, cy, ln, 1, DARKGREY)
            cy += 8

    # ---- Ticker ---------------------------------------------------
    c.rect(10, 924, 1004, 72, NAVY)
    c.text(22, 934, "LATEST >", 2, GOLD)
    tlines = c.wrap(TICKER, 1, 1004 - 130)
    ty = 934
    for ln in tlines[:3]:
        c.text(130, ty, ln, 1, WHITE)
        ty += 10
    c.text(W // 2, 1002, "ALL STORIES FIRST REPORTED SUNDAY 22 NOVEMBER 2026",
           1, GREY, align="center")
    return c


# ---------------------------------------------------------------- PNG
def chunk(typ, data):
    out = struct.pack(">I", len(data)) + typ + data
    out += struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)
    return out


def encode_png(c):
    raw = bytearray()
    for yy in range(c.h):
        raw.append(0)
        raw += c.buf[yy * c.w * 3:(yy + 1) * c.w * 3]
    ihdr = struct.pack(">IIBBBBB", c.w, c.h, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 6))
    png += chunk(b"IEND", b"")
    return png


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    data = encode_png(build())
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(data)
    print("wrote", path, len(data), "bytes")


if __name__ == "__main__":
    main()
