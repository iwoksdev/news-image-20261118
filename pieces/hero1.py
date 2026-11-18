#!/usr/bin/env python3
"""Piece 3 — Hero 1: "Xi greets Trump on the tarmac as APEC opens in Shenzhen".

Slot on the final 1024x1024 page: 323 x 228 (x 16-339, y 145-373).
Art area 323 x 102 at the top of the slot; kicker, headline and dek below.
Rendered at 8x and Lanczos-downscaled to 2x the slot (646 x 456) -> hero1.png.

Text comes from ../stories.json (heroes[0]); fonts from ../fonts. Deterministic.
"""
import json
import math
import os
import random

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FONT_DIR = os.path.join(ROOT, "fonts")
OUT = os.path.join(HERE, "hero1.png")

SLOT_W, SLOT_H = 323, 228
ART_H = 102
K = 8                     # internal supersample (slot units -> px)
OUT_SCALE = 2             # delivered at 2x the slot

PAPER = (247, 242, 227)
INK = (18, 18, 20)
GREY = (96, 96, 100)
PURPLE = (112, 48, 150)

SERIF = "NotoSerif-Regular.ttf"
SERIF_XB = "NotoSerif-ExtraBold.ttf"
SANS = "NotoSans-Regular.ttf"
SANS_B = "NotoSans-Bold.ttf"

_F = {}


def F(name, size):
    key = (name, round(size * K))
    if key not in _F:
        _F[key] = ImageFont.truetype(os.path.join(FONT_DIR, name), max(1, round(size * K)))
    return _F[key]


class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.img = Image.new("RGB", (round(w * K), round(h * K)), bg)
        self.d = ImageDraw.Draw(self.img)

    def rect(self, x, y, w, h, fill=None, outline=None, width=1):
        self.d.rectangle([x * K, y * K, (x + w) * K, (y + h) * K], fill=fill, outline=outline,
                         width=max(1, round(width * K)))

    def rrect(self, x, y, w, h, r, fill=None, outline=None, width=1):
        self.d.rounded_rectangle([x * K, y * K, (x + w) * K, (y + h) * K], radius=r * K, fill=fill,
                                 outline=outline, width=max(1, round(width * K)))

    def ell(self, cx, cy, rx, ry=None, fill=None, outline=None, width=1):
        ry = rx if ry is None else ry
        self.d.ellipse([(cx - rx) * K, (cy - ry) * K, (cx + rx) * K, (cy + ry) * K], fill=fill,
                       outline=outline, width=max(1, round(width * K)))

    def poly(self, pts, fill=None, outline=None, width=1):
        p = [(a * K, b * K) for a, b in pts]
        if fill is not None:
            self.d.polygon(p, fill=fill)
        if outline is not None:
            self.d.line(p + [p[0]], fill=outline, width=max(1, round(width * K)), joint="curve")

    def line(self, pts, fill, width=1):
        self.d.line([(a * K, b * K) for a, b in pts], fill=fill, width=max(1, round(width * K)), joint="curve")

    def vgrad(self, x, y, w, h, c1, c2):
        n = round(h * K)
        for i in range(n):
            t = i / max(1, n - 1)
            c = tuple(round(c1[j] + (c2[j] - c1[j]) * t) for j in range(3))
            yy = y * K + i
            self.d.line([(x * K, yy), ((x + w) * K, yy)], fill=c, width=1)

    def tw(self, s, font, size):
        return self.d.textlength(s, font=F(font, size)) / K

    def text(self, x, y, s, font, size, fill=INK, anchor="la"):
        self.d.text((x * K, y * K), s, font=F(font, size), fill=fill, anchor=anchor)

    def wrap(self, text, font, size, maxw):
        words, lines, cur = text.split(), [], ""
        for w in words:
            t = (cur + " " + w).strip()
            if self.tw(t, font, size) <= maxw:
                cur = t
            else:
                if cur:
                    lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
        return lines


def chip(cv, x, y, s, size, fg=INK, bg=(255, 255, 255), pad=4, right=False, top=False):
    w = cv.tw(s, SANS_B, size) + pad * 2
    h = size * 1.5
    xx = x - w if right else x
    yy = y - h if top else y
    cv.rect(xx, yy, w, h, fill=bg)
    cv.text(xx + pad, yy + h * 0.16, s, SANS_B, size, fg)


# --------------------------------------------------------------------------- art
def flag(cv, x, y, w, h, kind):
    if kind == "cn":
        cv.rect(x, y, w, h, fill=(222, 41, 16))
        star(cv, x + w * 0.2, y + h * 0.3, h * 0.2, h * 0.085, (255, 222, 0))
        for i, (dx, dy) in enumerate(((0.40, 0.12), (0.48, 0.27), (0.48, 0.47), (0.40, 0.62))):
            star(cv, x + w * dx, y + h * dy, h * 0.07, h * 0.03, (255, 222, 0))
    elif kind == "us":
        for s in range(13):
            cv.rect(x, y + s * h / 13, w, h / 13 + 0.02, fill=(178, 34, 52) if s % 2 == 0 else (255, 255, 255))
        cv.rect(x, y, w * 0.42, h * 7 / 13, fill=(60, 59, 110))
    else:  # ru
        cv.rect(x, y, w, h / 3, fill=(255, 255, 255))
        cv.rect(x, y + h / 3, w, h / 3, fill=(0, 57, 166))
        cv.rect(x, y + 2 * h / 3, w, h / 3, fill=(213, 43, 30))


def star(cv, cx, cy, ro, ri, fill, rot=-90):
    pts = []
    for i in range(10):
        r = ro if i % 2 == 0 else ri
        a = math.radians(rot + i * 36)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    cv.poly(pts, fill=fill)


def person(cv, x, base, h, suit, hair, tie=None, lean=0.0):
    """Simple standing figure, feet at (x, base), height h. lean>0 tips the torso right."""
    hw = h * 0.16                        # half shoulder width
    head_r = h * 0.085
    torso_top = base - h * 0.78
    torso_bot = base - h * 0.42
    dx = lean * h * 0.12
    # legs
    cv.poly([(x - hw * 0.8, torso_bot), (x + hw * 0.8, torso_bot), (x + hw * 0.55, base), (x - hw * 0.55, base)], fill=suit)
    cv.line([(x, torso_bot), (x, base - h * 0.05)], (12, 12, 16), h * 0.012)
    # torso (jacket)
    cv.poly([(x - hw + dx * 0.4, torso_top), (x + hw + dx * 0.4, torso_top), (x + hw * 0.9, torso_bot), (x - hw * 0.9, torso_bot)], fill=suit)
    # shirt V + tie
    cv.poly([(x + dx * 0.4 - hw * 0.22, torso_top), (x + dx * 0.4 + hw * 0.22, torso_top), (x + dx * 0.2, torso_top + h * 0.14)], fill=(245, 245, 248))
    if tie:
        cv.poly([(x + dx * 0.4 - hw * 0.07, torso_top + h * 0.02), (x + dx * 0.4 + hw * 0.07, torso_top + h * 0.02), (x + dx * 0.2, torso_top + h * 0.19)], fill=tie)
    # neck + head
    hx, hy = x + dx, torso_top - head_r * 1.05
    cv.rect(hx - head_r * 0.35, torso_top - head_r * 0.5, head_r * 0.7, head_r * 0.6, fill=(226, 184, 150))
    cv.ell(hx, hy, head_r, head_r * 1.08, fill=(230, 190, 156))
    # hair cap
    cv.d.pieslice([(hx - head_r) * K, (hy - head_r * 1.08) * K, (hx + head_r) * K, (hy + head_r * 1.08) * K], 190, 350, fill=hair)


def draw_art(cv, w, h):
    # ---- sky
    cv.vgrad(0, 0, w, h * 0.64, (232, 110, 58), (254, 216, 164))
    # sun with soft glow
    sx, sy = w * 0.835, h * 0.20
    for r, a in ((16, 0.10), (12, 0.18), (9, 0.35)):
        glow = Image.new("RGB", cv.img.size, (0, 0, 0))
    cv.ell(sx, sy, 10, 10, fill=(255, 226, 170))
    cv.ell(sx, sy, 7.5, 7.5, fill=(255, 245, 212))
    # thin cloud bands
    for cy, cw in ((h * 0.30, 60), (h * 0.36, 38), (h * 0.26, 24)):
        cv.rrect(w * 0.62 - cw / 2, cy, cw, 1.6, 0.8, fill=(255, 200, 150))

    # ---- Shenzhen skyline, two depth layers
    horizon = h * 0.64
    rnd = random.Random(2026)
    far = (170, 118, 160)
    near = (104, 64, 118)
    x = -4
    while x < w:
        bw = rnd.uniform(6, 14)
        bh = rnd.uniform(10, 24)
        cv.rect(x, horizon - bh, bw, bh, fill=far)
        x += bw + rnd.uniform(0, 3)
    x = -2
    while x < w:
        bw = rnd.uniform(7, 16)
        bh = rnd.uniform(6, 18)
        cv.rect(x, horizon - bh, bw, bh, fill=near)
        # a few lit windows
        for _ in range(int(bw * bh / 30)):
            wx = x + rnd.uniform(1, max(1.2, bw - 2))
            wy = horizon - bh + rnd.uniform(1.5, max(2, bh - 2))
            cv.rect(wx, wy, 0.9, 0.9, fill=(255, 220, 150))
        x += bw + rnd.uniform(0.5, 4)
    # Ping An Finance Centre (tall tapering spire) + a second tower
    px = w * 0.665
    cv.poly([(px - 6, horizon), (px - 4.5, h * 0.16), (px - 1.2, h * 0.07), (px, h * 0.03), (px + 1.2, h * 0.07),
             (px + 4.5, h * 0.16), (px + 6, horizon)], fill=near)
    cv.line([(px, h * 0.03), (px, horizon)], (140, 96, 150), 0.6)
    qx = w * 0.745
    cv.poly([(qx - 4, horizon), (qx - 3, h * 0.25), (qx, h * 0.21), (qx + 3, h * 0.25), (qx + 4, horizon)], fill=near)
    cv.poly([(w * 0.60 - 3.5, horizon), (w * 0.60 - 3.5, h * 0.30), (w * 0.60 + 3.5, h * 0.30), (w * 0.60 + 3.5, horizon)], fill=near)

    # ---- apron
    cv.rect(0, horizon, w, h - horizon, fill=(82, 84, 92))
    cv.vgrad(0, horizon, w, 6, (60, 62, 70), (82, 84, 92))
    cv.line([(0, horizon), (w, horizon)], (150, 150, 158), 0.5)
    # taxiway centreline + edge markings
    for i in range(0, int(w) + 10, 20):
        cv.rect(i, h * 0.90, 11, 1.3, fill=(232, 200, 70))
    cv.line([(0, h * 0.72), (w, h * 0.72)], (120, 122, 130), 0.5)

    # ---- red carpet, perspective trapezoid from the air stair to the right
    c0x, c1x = w * 0.60, w * 0.985
    cv.poly([(c0x, h * 0.73), (c1x, h * 0.73), (c1x, h * 0.86), (c0x - 8, h * 0.86)], fill=(170, 28, 34))
    cv.poly([(c0x, h * 0.73), (c1x, h * 0.73), (c1x, h * 0.745), (c0x - 0.5, h * 0.745)], fill=(200, 60, 66))
    cv.poly([(c0x - 8, h * 0.86), (c1x, h * 0.86), (c1x, h * 0.845), (c0x - 7.2, h * 0.845)], fill=(120, 18, 24))

    # ---- honour-guard flag line along the back of the carpet: CN / US alternating
    for i in range(7):
        fx = w * 0.655 + i * 15.5
        cv.line([(fx, h * 0.73), (fx, h * 0.46)], (240, 240, 244), 0.8)
        cv.ell(fx, h * 0.455, 0.8, 0.8, fill=(250, 220, 120))
        flag(cv, fx + 0.6, h * 0.47, 8.5, 5.6, "cn" if i % 2 == 0 else "us")

    # ---- the aircraft (VC-25-style: white top, light-blue belly, dark cheatline)
    nose_x = w * 0.585
    tail_x = w * 0.045
    cy = h * 0.45
    fh = h * 0.085                     # fuselage half-height
    L = nose_x - tail_x
    white = (250, 251, 253)
    lblue = (150, 192, 232)
    dblue = (28, 62, 140)
    shade = (222, 226, 234)
    # fuselage outline
    body = [(tail_x + L * 0.11, cy - fh), (nose_x - L * 0.12, cy - fh), (nose_x - L * 0.04, cy - fh * 0.62),
            (nose_x, cy + fh * 0.05), (nose_x - L * 0.03, cy + fh * 0.62), (nose_x - L * 0.10, cy + fh),
            (tail_x + L * 0.16, cy + fh), (tail_x + L * 0.02, cy + fh * 0.15), (tail_x, cy - fh * 0.1)]
    cv.poly(body, fill=white)
    # light-blue belly
    cv.poly([(tail_x + L * 0.16, cy + fh * 0.25), (nose_x - L * 0.06, cy + fh * 0.25), (nose_x - L * 0.03, cy + fh * 0.62),
             (nose_x - L * 0.10, cy + fh), (tail_x + L * 0.16, cy + fh), (tail_x + L * 0.02, cy + fh * 0.15), (tail_x, cy - fh * 0.1),
             (tail_x + L * 0.10, cy + fh * 0.25)], fill=lblue)
    # dark cheatline sweeping up to the nose
    cheat = [(tail_x + L * 0.10, cy + fh * 0.16), (nose_x - L * 0.16, cy + fh * 0.16), (nose_x - L * 0.09, cy - fh * 0.05),
             (nose_x - L * 0.06, cy - fh * 0.2), (nose_x - L * 0.06, cy - fh * 0.02), (nose_x - L * 0.10, cy + fh * 0.30),
             (tail_x + L * 0.10, cy + fh * 0.30)]
    cv.poly(cheat, fill=dblue)
    # tail fin (light blue, dark stripe, flag)
    fin = [(tail_x + L * 0.12, cy - fh * 0.95), (tail_x + L * 0.17, cy - fh * 3.6), (tail_x + L * 0.27, cy - fh * 3.6),
           (tail_x + L * 0.30, cy - fh * 0.95)]
    cv.poly(fin, fill=lblue)
    cv.poly([(tail_x + L * 0.145, cy - fh * 3.1), (tail_x + L * 0.215, cy - fh * 3.1), (tail_x + L * 0.16, cy - fh * 1.25),
             (tail_x + L * 0.125, cy - fh * 1.25)], fill=white)
    flag(cv, tail_x + L * 0.225, cy - fh * 3.3, L * 0.045, fh * 0.9, "us")
    # horizontal stabiliser
    cv.poly([(tail_x + L * 0.03, cy - fh * 0.2), (tail_x - L * 0.02, cy - fh * 1.0), (tail_x + L * 0.11, cy - fh * 1.0),
             (tail_x + L * 0.19, cy - fh * 0.2)], fill=shade)
    # wing (near side, swept back and towards the viewer)
    root0, root1 = tail_x + L * 0.42, tail_x + L * 0.62
    cv.poly([(root0, cy + fh * 0.35), (root1, cy + fh * 0.35), (root1 - L * 0.26, cy + fh * 2.55),
             (root1 - L * 0.36, cy + fh * 2.55)], fill=shade)
    cv.line([(root0, cy + fh * 0.35), (root1 - L * 0.36, cy + fh * 2.55)], (190, 194, 204), 0.5)
    cv.line([(root1, cy + fh * 0.35), (root1 - L * 0.26, cy + fh * 2.55)], (200, 204, 214), 0.4)
    # engines under the wing
    for ex, ey, s in ((root0 - L * 0.10, cy + fh * 1.75, 1.0), (root0 + L * 0.04, cy + fh * 1.15, 0.92)):
        ew, eh = L * 0.13 * s, fh * 1.05 * s
        cv.rrect(ex, ey, ew, eh, eh * 0.45, fill=(206, 210, 220))
        cv.rrect(ex, ey, ew * 0.22, eh, eh * 0.45, fill=(70, 74, 84))
        cv.line([(ex + ew * 0.1, ey + eh * 0.5), (ex + ew * 0.95, ey + eh * 0.5)], (170, 174, 186), 0.5)
    # windows + doors + cockpit
    for i in range(26):
        wx = tail_x + L * (0.20 + i * 0.027)
        if abs(wx - (nose_x - L * 0.16)) < L * 0.02 or abs(wx - (tail_x + L * 0.30)) < L * 0.015:
            continue
        cv.rect(wx, cy - fh * 0.55, 0.95, 1.05, fill=(52, 70, 110))
    for doorx in (nose_x - L * 0.165, tail_x + L * 0.295):
        cv.rect(doorx, cy - fh * 0.78, 2.3, fh * 1.45, outline=(170, 178, 200), width=0.35)
    cv.poly([(nose_x - L * 0.085, cy - fh * 0.66), (nose_x - L * 0.03, cy - fh * 0.40), (nose_x - L * 0.07, cy - fh * 0.40),
             (nose_x - L * 0.10, cy - fh * 0.52)], fill=(40, 56, 96))
    cv.text(tail_x + L * 0.37, cy - fh * 0.98, "UNITED STATES OF AMERICA", SANS_B, 3.6, dblue)
    # landing gear
    for gx in (nose_x - L * 0.10, root1 - L * 0.02, root1 + L * 0.015):
        cv.line([(gx, cy + fh), (gx, cy + fh * 2.6)], (60, 60, 66), 0.9)
        cv.ell(gx, cy + fh * 2.75, 1.5, 1.5, fill=(28, 28, 32))
        cv.ell(gx, cy + fh * 2.75, 0.6, 0.6, fill=(150, 150, 156))
    # shadow under the aircraft
    cv.ell(tail_x + L * 0.52, cy + fh * 3.1, L * 0.45, fh * 0.5, fill=(66, 68, 76))
    cv.poly(body, outline=(190, 196, 206), width=0.3)

    # ---- air stair at the forward door, down to the carpet
    dx0 = nose_x - L * 0.155
    top = (dx0 + 2.4, cy - fh * 0.1)
    bot = (dx0 + 26, h * 0.73)
    cv.poly([(top[0], top[1] - fh * 0.6), (top[0] + 3.5, top[1] - fh * 0.6), (bot[0] + 3.5, bot[1]), (bot[0] - 3.5, bot[1])], fill=(196, 198, 206))
    cv.line([(top[0], top[1] - fh * 0.6), (bot[0] - 3.5, bot[1])], (120, 122, 130), 0.5)
    for i in range(1, 9):
        t = i / 9
        sx0 = top[0] + (bot[0] - 3.5 - top[0]) * t
        sy0 = top[1] - fh * 0.6 + (bot[1] - top[1] + fh * 0.6) * t
        cv.line([(sx0, sy0), (sx0 + 3.5, sy0)], (140, 142, 150), 0.4)
    cv.line([(top[0], top[1] - fh * 1.3), (bot[0] - 3.5, bot[1] - fh * 0.9)], (120, 122, 130), 0.6)
    cv.line([(top[0] + 3.5, top[1] - fh * 1.3), (bot[0] + 3.5, bot[1] - fh * 0.9)], (120, 122, 130), 0.6)

    # ---- Xi and Trump embracing at the foot of the stairs (feet on the carpet)
    base = h * 0.835
    ph = 15.5
    person(cv, w * 0.690, base, ph, suit=(26, 28, 44), hair=(32, 30, 34), tie=(160, 24, 30), lean=0.5)        # Xi
    person(cv, w * 0.716, base, ph, suit=(22, 26, 48), hair=(228, 200, 120), tie=(200, 30, 36), lean=-0.5)   # Trump
    # arms across each other
    cv.line([(w * 0.690 - 1.2, base - ph * 0.68), (w * 0.716 + 1.4, base - ph * 0.60)], (26, 28, 44), 1.3)
    cv.line([(w * 0.716 + 1.2, base - ph * 0.70), (w * 0.690 - 1.6, base - ph * 0.60)], (22, 26, 48), 1.3)
    # small welcoming party further down the carpet
    for i, fx in enumerate((0.80, 0.822, 0.844)):
        person(cv, w * fx, base - 0.5, 12.5, suit=(30, 32, 48), hair=(30, 28, 32))
    # photographers' flash points (tiny) — restraint: just two
    for fx, fy in ((w * 0.645, h * 0.80), (w * 0.94, h * 0.78)):
        cv.ell(fx, fy, 0.9, 0.9, fill=(255, 255, 240))

    # ---- labels: minimal, direct
    chip(cv, 5, h - 5, "SHENZHEN BAO'AN AIRPORT · WEDNESDAY MORNING", 7.5, top=True)
    chip(cv, w - 5, 5, "APEC 2026 · SHENZHEN", 7.5, fg=(255, 255, 255), bg=PURPLE, right=True)


# --------------------------------------------------------------------------- text block
def draw_text(cv, story, x, y, w):
    n, c = story["n"], PURPLE
    r = 7.5
    cv.ell(x + r, y + r, r, r, fill=c)
    cv.text(x + r, y + r - 4.6, str(n), SANS_B, 9.3, (255, 255, 255), anchor="ma")
    cv.text(x + 2 * r + 5, y + r - 7.1, story["cat"], SANS_B, 10.5, c)
    cv.text(x + w, y + r - 6.2, story["source"], SANS, 9, GREY, anchor="ra")
    yy = y + 20
    for size in (20.5, 20, 19.5, 19, 18.5, 18):
        lines = cv.wrap(story["headline"], SERIF_XB, size, w)
        if len(lines) <= 2:
            break
    for ln in lines:
        cv.text(x, yy, ln, SERIF_XB, size, INK)
        yy += size * 1.12
    yy += 4
    for size in (11.5, 11, 10.5):
        lines = cv.wrap(story["dek"], SERIF, size, w)
        if len(lines) <= 3:
            break
    for ln in lines:
        cv.text(x, yy, ln, SERIF, size, (36, 36, 40))
        yy += size * 1.3
    assert yy <= SLOT_H + 1, f"text overflows slot: {yy}"


def main():
    story = json.load(open(os.path.join(ROOT, "stories.json")))["heroes"][0]
    cv = Canvas(SLOT_W, SLOT_H, PAPER)
    art = Canvas(SLOT_W, ART_H, PAPER)
    draw_art(art, SLOT_W, ART_H)
    cv.img.paste(art.img, (0, 0))
    cv.rect(0.6, 0.6, SLOT_W - 1.2, ART_H - 1.2, outline=INK, width=1.3)
    draw_text(cv, story, 0, ART_H + 6, SLOT_W)
    out = cv.img.resize((SLOT_W * OUT_SCALE, SLOT_H * OUT_SCALE), Image.LANCZOS)
    out.save(OUT, optimize=True)
    print("saved", OUT, out.size, os.path.getsize(OUT), "bytes")


if __name__ == "__main__":
    main()
