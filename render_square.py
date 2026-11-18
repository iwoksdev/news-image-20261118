#!/usr/bin/env python3
"""Render entry.png — 'The Day in World News · Wednesday 18 November 2026'.

1024x1024 newspaper front page, drawn with PIL at 3x and Lanczos-downscaled.
Text comes from stories.json; coastlines from world_110m.json / regions_50m.json
(Natural Earth, public domain); fonts from ./fonts (Noto + Playfair, OFL,
static instances subset to Latin). No network, no clock, deterministic.

    python3 render_square.py        # writes entry.png next to this file
"""
import json
import math
import os
import random

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
SS = 3                       # supersample factor
W, H = 1024, 1024
OUT = os.path.join(HERE, "entry.png")

PAPER = (248, 244, 232)
INK = (18, 18, 20)
GREY = (92, 92, 96)
RULE = (150, 148, 140)
RED = (176, 32, 28)
GOLD = (250, 206, 70)

FONT_DIR = os.path.join(HERE, "fonts")
SERIF = "NotoSerif-Regular.ttf"
SERIF_B = "NotoSerif-Bold.ttf"
SERIF_XB = "NotoSerif-ExtraBold.ttf"
SERIF_I = "NotoSerif-Italic.ttf"
SANS = "NotoSans-Regular.ttf"
SANS_B = "NotoSans-Bold.ttf"
DISPLAY = "PlayfairDisplay-Black.ttf"
DISPLAY2 = "NotoSerifDisplay-Black.ttf"

# region palette (keys used in stories.json colours -> mapped by hex)
REGION = {
    "#6a3fa0": (112, 48, 150),   # asia
    "#cf6f1f": (196, 86, 20),    # middle east
    "#1f4e9c": (28, 78, 170),    # europe
    "#2e7d46": (30, 120, 66),    # africa
    "#c0392b": (178, 40, 34),    # americas
    "#0e7c7b": (14, 124, 122),   # oceania
    "#555555": (92, 92, 96),     # global
    "#111111": (24, 24, 30),     # space
}


def col(hexstr):
    return REGION.get(hexstr, tuple(int(hexstr[i:i + 2], 16) for i in (1, 3, 5)))


DATA = json.load(open(os.path.join(HERE, "stories.json")))
WORLD = json.load(open(os.path.join(HERE, "world_110m.json")))
REGIONS = json.load(open(os.path.join(HERE, "regions_50m.json")))

_FONTS = {}


def F(name, size):
    key = (name, round(size * SS))
    if key not in _FONTS:
        _FONTS[key] = ImageFont.truetype(os.path.join(FONT_DIR, name), max(1, round(size * SS)))
    return _FONTS[key]


# --------------------------------------------------------------------------- canvas
class Canvas:
    """Thin wrapper: 1x coordinates in, SS-scaled drawing out."""

    def __init__(self, w, h, bg=None):
        self.w, self.h = w, h
        self.img = Image.new("RGB", (round(w * SS), round(h * SS)), bg or PAPER)
        self.d = ImageDraw.Draw(self.img)

    def S(self, v):
        return v * SS

    def rect(self, x, y, w, h, fill=None, outline=None, width=1):
        self.d.rectangle([x * SS, y * SS, (x + w) * SS, (y + h) * SS], fill=fill,
                         outline=outline, width=max(1, round(width * SS)))

    def rrect(self, x, y, w, h, r, fill=None, outline=None, width=1):
        self.d.rounded_rectangle([x * SS, y * SS, (x + w) * SS, (y + h) * SS], radius=r * SS,
                                 fill=fill, outline=outline, width=max(1, round(width * SS)))

    def ell(self, cx, cy, rx, ry=None, fill=None, outline=None, width=1):
        ry = rx if ry is None else ry
        self.d.ellipse([(cx - rx) * SS, (cy - ry) * SS, (cx + rx) * SS, (cy + ry) * SS],
                       fill=fill, outline=outline, width=max(1, round(width * SS)))

    def poly(self, pts, fill=None, outline=None, width=1):
        p = [(a * SS, b * SS) for a, b in pts]
        if fill is not None:
            self.d.polygon(p, fill=fill)
        if outline is not None:
            self.d.line(p + [p[0]], fill=outline, width=max(1, round(width * SS)), joint="curve")

    def line(self, pts, fill, width=1):
        self.d.line([(a * SS, b * SS) for a, b in pts], fill=fill,
                    width=max(1, round(width * SS)), joint="curve")

    def dashed(self, p0, p1, fill, width=1, dash=3, gap=2.5):
        x0, y0 = p0
        x1, y1 = p1
        L = math.hypot(x1 - x0, y1 - y0)
        if L == 0:
            return
        ux, uy = (x1 - x0) / L, (y1 - y0) / L
        t = 0
        while t < L:
            e = min(L, t + dash)
            self.line([(x0 + ux * t, y0 + uy * t), (x0 + ux * e, y0 + uy * e)], fill, width)
            t += dash + gap

    def arc(self, cx, cy, r, a0, a1, fill, width=1):
        self.d.arc([(cx - r) * SS, (cy - r) * SS, (cx + r) * SS, (cy + r) * SS], a0, a1,
                   fill=fill, width=max(1, round(width * SS)))

    def tw(self, text, font_name, size):
        return self.d.textlength(text, font=F(font_name, size)) / SS

    def text(self, x, y, s, font_name, size, fill=INK, anchor="la"):
        self.d.text((x * SS, y * SS), s, font=F(font_name, size), fill=fill, anchor=anchor)

    def ctext(self, cx, y, s, font_name, size, fill=INK):
        self.text(cx, y, s, font_name, size, fill, anchor="ma")

    def rtext(self, rx, y, s, font_name, size, fill=INK):
        self.text(rx, y, s, font_name, size, fill, anchor="ra")

    def wrap(self, text, font_name, size, maxw):
        words = text.split()
        lines, cur = [], ""
        for w in words:
            t = (cur + " " + w).strip()
            if self.tw(t, font_name, size) <= maxw:
                cur = t
            else:
                if cur:
                    lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
        return lines

    def fit(self, x, y, w, text, font_name, sizes, lh, max_lines, fill=INK, draw=True):
        """Largest size whose wrap fits in max_lines; draws; returns height used."""
        chosen = None
        for size in sizes:
            lines = self.wrap(text, font_name, size, w)
            if len(lines) <= max_lines:
                chosen = (size, lines)
                break
        if chosen is None:
            size = sizes[-1]
            lines = self.wrap(text, font_name, size, w)
            print(f"WARNING overflow ({len(lines)} > {max_lines} lines): {text[:60]}")
            chosen = (size, lines)
        size, lines = chosen
        if draw:
            yy = y
            for ln in lines:
                self.text(x, yy, ln, font_name, size, fill)
                yy += size * lh
        return len(lines) * size * lh

    def paste(self, other, x, y):
        self.img.paste(other.img, (round(x * SS), round(y * SS)))

    def star(self, cx, cy, ro, ri, fill, rot=-90, n=5):
        pts = []
        for i in range(2 * n):
            r = ro if i % 2 == 0 else ri
            a = math.radians(rot + i * 180 / n)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
        self.poly(pts, fill=fill)

    def vgrad(self, x, y, w, h, c1, c2):
        steps = max(2, round(h * SS))
        for i in range(steps):
            t = i / (steps - 1)
            c = tuple(round(c1[j] + (c2[j] - c1[j]) * t) for j in range(3))
            yy = y + h * i / steps
            self.d.line([(x * SS, yy * SS), ((x + w) * SS, yy * SS)], fill=c, width=2)


# --------------------------------------------------------------------------- geo helpers
def project(bbox, box):
    """Equirectangular, uniform scale, centred. bbox=(lon0,lat0,lon1,lat1), box=(x,y,w,h)."""
    lon0, lat0, lon1, lat1 = bbox
    x, y, w, h = box
    midlat = math.radians((lat0 + lat1) / 2)
    gw = (lon1 - lon0) * math.cos(midlat)
    gh = (lat1 - lat0)
    s = min(w / gw, h / gh)
    ox = x + (w - gw * s) / 2
    oy = y + (h - gh * s) / 2

    def fn(lon, lat):
        return (ox + (lon - lon0) * math.cos(midlat) * s, oy + (lat1 - lat) * s)
    return fn


def draw_polys(cv, polys, proj, fill, outline=None, width=0.6):
    for ring in polys:
        pts = [proj(lon, lat) for lon, lat in ring]
        if len(pts) >= 3:
            cv.poly(pts, fill=fill, outline=outline, width=width)


def burst(cv, cx, cy, r, fill, n=8):
    pts = []
    for i in range(2 * n):
        rr = r if i % 2 == 0 else r * 0.45
        a = math.radians(i * 180 / n)
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    cv.poly(pts, fill=fill)


def drone(cv, cx, cy, s, fill, flip=False):
    """Shahed-style delta silhouette, pointing left (or right if flip)."""
    k = -1 if flip else 1
    cv.poly([(cx - 1.0 * s * k, cy), (cx + 0.9 * s * k, cy - 0.55 * s), (cx + 1.0 * s * k, cy - 0.15 * s),
             (cx + 0.6 * s * k, cy), (cx + 1.0 * s * k, cy + 0.15 * s), (cx + 0.9 * s * k, cy + 0.55 * s)],
            fill=fill)


def chip(cv, x, y, s, font, size, fg=INK, bg=(255, 255, 255), pad=4, right=False, top=False):
    w = cv.tw(s, font, size) + pad * 2
    h = size * 1.45
    xx = x - w if right else x
    yy = y - h if top else y
    cv.rect(xx, yy, w, h, fill=bg)
    cv.text(xx + pad, yy + h * 0.14, s, font, size, fg)


# --------------------------------------------------------------------------- hero art
def art_apec(w, h):
    cv = Canvas(w, h)
    cv.vgrad(0, 0, w, h, (252, 150, 70), (254, 214, 150))
    cv.ell(w * 0.80, h * 0.26, 9, 9, fill=(255, 240, 200))
    # distant skyline (Shenzhen) in dusk purple
    rnd = random.Random(3)
    bx = 0
    sky = (96, 60, 110)
    while bx < w:
        bw = rnd.uniform(9, 20)
        bh = rnd.uniform(14, 40)
        cv.rect(bx, h * 0.62 - bh, bw, bh, fill=sky)
        bx += bw + rnd.uniform(1, 4)
    # Ping An tower spire
    cv.poly([(w * 0.60, h * 0.62), (w * 0.60, h * 0.12), (w * 0.615, h * 0.04), (w * 0.63, h * 0.12), (w * 0.63, h * 0.62)], fill=sky)
    # tarmac
    cv.rect(0, h * 0.62, w, h * 0.38, fill=(74, 76, 84))
    cv.line([(0, h * 0.62), (w, h * 0.62)], (120, 122, 130), 0.8)
    for i in range(0, int(w), 22):
        cv.rect(i, h * 0.86, 11, 1.4, fill=(220, 210, 90))
    # red carpet
    cv.poly([(w * 0.33, h * 0.66), (w * 0.47, h * 0.66), (w * 0.52, h * 1.0), (w * 0.26, h * 1.0)], fill=(176, 32, 36))
    # plane: side view, nose to the right, white with blue belly + tail stripe
    px, py = w * 0.08, h * 0.44           # left (tail) x, fuselage centreline y
    L = w * 0.62
    fh = h * 0.13
    body = [(px + L * 0.10, py - fh), (px + L * 0.86, py - fh), (px + L * 0.96, py - fh * 0.55), (px + L, py),
            (px + L * 0.96, py + fh * 0.55), (px + L * 0.86, py + fh), (px + L * 0.15, py + fh), (px + L * 0.02, py + fh * 0.3)]
    cv.poly(body, fill=(248, 249, 251))
    # blue belly
    cv.poly([(px + L * 0.15, py + fh * 0.25), (px + L * 0.92, py + fh * 0.25), (px + L * 0.86, py + fh), (px + L * 0.15, py + fh), (px + L * 0.02, py + fh * 0.3)], fill=(42, 90, 170))
    cv.line([(px + L * 0.15, py + fh * 0.2), (px + L * 0.92, py + fh * 0.2)], (120, 170, 230), 1.0)
    # tail fin
    cv.poly([(px + L * 0.10, py - fh), (px + L * 0.16, py - fh * 3.3), (px + L * 0.26, py - fh * 3.3), (px + L * 0.24, py - fh)], fill=(42, 90, 170))
    cv.poly([(px + L * 0.17, py - fh * 3.0), (px + L * 0.19, py - fh * 3.0), (px + L * 0.14, py - fh * 1.4), (px + L * 0.12, py - fh * 1.4)], fill=(255, 255, 255))
    # tailplane
    cv.poly([(px + L * 0.06, py - fh * 0.2), (px + L * 0.0, py - fh * 1.1), (px + L * 0.12, py - fh * 1.1), (px + L * 0.18, py - fh * 0.2)], fill=(230, 232, 236))
    # wing
    cv.poly([(px + L * 0.42, py + fh * 0.3), (px + L * 0.30, py + fh * 2.0), (px + L * 0.40, py + fh * 2.0), (px + L * 0.62, py + fh * 0.3)], fill=(226, 228, 232))
    # engines
    cv.rrect(px + L * 0.36, py + fh * 1.05, L * 0.14, fh * 0.85, 2, fill=(200, 204, 212))
    cv.rrect(px + L * 0.50, py + fh * 0.85, L * 0.12, fh * 0.75, 2, fill=(215, 218, 224))
    # windows + cockpit
    for i in range(12):
        cv.rect(px + L * (0.24 + i * 0.05), py - fh * 0.45, 1.8, 1.8, fill=(60, 80, 120))
    cv.poly([(px + L * 0.92, py - fh * 0.6), (px + L * 0.97, py - fh * 0.3), (px + L * 0.88, py - fh * 0.3)], fill=(60, 80, 120))
    # gear
    for gx in (px + L * 0.20, px + L * 0.52, px + L * 0.56):
        cv.line([(gx, py + fh), (gx, py + fh * 2.0)], (60, 60, 66), 1.2)
        cv.ell(gx, py + fh * 2.1, 2.4, 2.4, fill=(30, 30, 34))
    # air stair
    cv.poly([(px + L * 0.80, py + fh * 0.6), (px + L * 0.80 + 22, py + fh * 2.8), (px + L * 0.80 + 26, py + fh * 2.8), (px + L * 0.84, py + fh * 0.6)], fill=(200, 200, 206))
    # two figures embracing on the carpet
    for fx, dark in ((w * 0.395, (26, 24, 40)), (w * 0.425, (40, 30, 30))):
        fy = h * 0.70
        cv.ell(fx, fy + 3, 2.6, 2.6, fill=dark)
        cv.poly([(fx - 4, fy + 20), (fx - 3.4, fy + 6), (fx + 3.4, fy + 6), (fx + 4, fy + 20)], fill=dark)
    # flags: China, US, Russia
    for i, kind in enumerate(("cn", "us", "ru")):
        fx = w * 0.055 + i * 15
        cv.line([(fx, h * 0.62), (fx, h * 0.30)], (230, 230, 230), 1.2)
        fw, fhh = 11, 7
        fy = h * 0.30
        if kind == "cn":
            cv.rect(fx, fy, fw, fhh, fill=(222, 41, 16))
            cv.star(fx + 2.4, fy + 2.2, 1.6, 0.7, (255, 222, 0))
        elif kind == "us":
            for s in range(7):
                cv.rect(fx, fy + s * fhh / 7, fw, fhh / 7, fill=(178, 34, 52) if s % 2 == 0 else (255, 255, 255))
            cv.rect(fx, fy, fw * 0.42, fhh * 0.55, fill=(60, 59, 110))
        else:
            cv.rect(fx, fy, fw, fhh / 3, fill=(255, 255, 255))
            cv.rect(fx, fy + fhh / 3, fw, fhh / 3, fill=(0, 57, 166))
            cv.rect(fx, fy + 2 * fhh / 3, fw, fhh / 3, fill=(213, 43, 30))
    chip(cv, 6, h - 6, "XI GREETS TRUMP · SHENZHEN BAO'AN AIRPORT", SANS_B, 8.5, top=True)
    chip(cv, w - 6, 6, "APEC 2026", SANS_B, 8, fg=(255, 255, 255), bg=(112, 48, 150), right=True)
    return cv


def art_gulf(w, h):
    sea = (12, 30, 62)
    cv = Canvas(w, h, bg=sea)
    proj = project((40.5, 23.8, 61.5, 31.6), (0, 0, w, h))
    land = (62, 78, 104)
    for name in ("Iraq", "Iran", "Saudi Arabia", "Kuwait", "Bahrain", "Qatar", "United Arab Emirates", "Oman", "Yemen"):
        draw_polys(cv, REGIONS[name], proj, land, outline=(90, 108, 140), width=0.5)
    draw_polys(cv, REGIONS["Kuwait"], proj, (118, 96, 60), outline=(200, 170, 110), width=0.6)
    draw_polys(cv, REGIONS["Iran"], proj, (84, 72, 86), outline=(120, 108, 130), width=0.5)
    lab = (178, 196, 222)
    cv.text(*proj(43.5, 30.5), "IRAQ", SANS_B, 8.5, lab)
    cv.text(*proj(53.6, 30.9), "IRAN", SANS_B, 9.5, (230, 220, 240))
    cv.text(*proj(41.4, 24.9), "SAUDI ARABIA", SANS_B, 8.5, lab)
    cv.text(*proj(50.3, 29.4), "THE GULF", SANS_B, 8, (120, 150, 200))
    # Ali Al Salem, Kuwait
    kx, ky = proj(47.52, 29.35)
    burst(cv, kx, ky, 8, (255, 120, 40))
    burst(cv, kx, ky, 4.5, (255, 230, 120))
    chip(cv, kx + 7, ky - 2, "ALI AL SALEM AIR BASE · KUWAIT", SANS_B, 8, fg=(255, 255, 255), bg=(196, 86, 20))
    # Qeshm
    qx, qy = proj(56.27, 26.8)
    burst(cv, qx, qy, 7, (255, 255, 255))
    burst(cv, qx, qy, 3.5, (255, 90, 60))
    chip(cv, qx - 8, qy - 12, "US STRIKE · QESHM ISLAND", SANS_B, 8, fg=INK, bg=(255, 255, 255), right=True)
    # Bahrain intercepted
    bx, by = proj(50.55, 26.1)
    cv.ell(bx, by, 4.5, 4.5, outline=(255, 255, 255), width=1.2)
    cv.ell(bx, by, 1.6, 1.6, fill=(255, 255, 255))
    chip(cv, bx - 7, by + 6, "BAHRAIN: 3RD ATTACK IN A WEEK", SANS_B, 7.5, fg=(255, 255, 255), bg=(40, 60, 100), right=True)
    # drone arcs Iran -> Kuwait
    ix, iy = proj(50.6, 30.3)
    mid = ((ix + kx) / 2, min(iy, ky) - 7)
    pts = []
    for i in range(21):
        t = i / 20
        x = (1 - t) ** 2 * ix + 2 * (1 - t) * t * mid[0] + t ** 2 * kx
        y = (1 - t) ** 2 * iy + 2 * (1 - t) * t * mid[1] + t ** 2 * ky
        pts.append((x, y))
    for i in range(0, 20, 2):
        cv.line([pts[i], pts[i + 1]], (255, 170, 90), 1.3)
    drone(cv, pts[8][0], pts[8][1] - 1, 4, (255, 210, 150))
    drone(cv, pts[12][0] + 3, pts[12][1] + 4, 3.2, (255, 210, 150))
    # US -> Qeshm arrow from the sea
    cv.dashed((qx + 30, qy + 26), (qx + 4, qy + 4), (255, 255, 255), 1.1, 3, 2.5)
    cv.text(6, 5, "THE GULF · 18 NOV", SANS_B, 7.5, (150, 175, 210))
    return cv


def art_voyager(w, h):
    cv = Canvas(w, h, bg=(8, 10, 32))
    rnd = random.Random(11)
    for _ in range(120):
        x, y = rnd.random() * w, rnd.random() * h
        r = rnd.choice((0.5, 0.6, 0.8, 1.1))
        c = rnd.choice(((255, 255, 255), (200, 210, 255), (255, 240, 220)))
        cv.ell(x, y, r, r, fill=c)
    # earth
    ex, ey, er = w * 0.13, h * 0.74, h * 0.20
    cv.ell(ex, ey, er * 1.25, er * 1.25, fill=(26, 60, 120))
    cv.ell(ex, ey, er, er, fill=(50, 120, 220))
    cv.ell(ex - er * 0.35, ey - er * 0.35, er * 0.42, er * 0.3, fill=(70, 180, 110))
    cv.ell(ex + er * 0.3, ey + er * 0.2, er * 0.35, er * 0.45, fill=(70, 180, 110))
    cv.ell(ex - er * 0.1, ey + er * 0.5, er * 0.25, er * 0.15, fill=(240, 250, 255))
    cv.text(ex + er * 1.3, ey + er * 0.55, "EARTH", SANS_B, 8, (210, 220, 255))
    # trajectory
    vx, vy = w * 0.86, h * 0.27
    cv.dashed((ex + er * 0.7, ey - er * 0.7), (vx - 14, vy + 4), (160, 175, 240), 1.0, 3, 3)
    # voyager: dish + bus + boom
    ang = math.atan2(vy - ey, vx - ex)
    cv.ell(vx, vy, 13, 13, outline=(235, 238, 248), width=1.6)
    cv.ell(vx, vy, 9.5, 9.5, fill=(60, 64, 90), outline=(235, 238, 248), width=1.0)
    cv.ell(vx, vy, 3.2, 3.2, fill=(235, 238, 248))
    cv.line([(vx, vy), (vx - 9 * math.cos(ang), vy - 9 * math.sin(ang))], (235, 238, 248), 1.2)
    cv.rect(vx + 10, vy - 4, 7, 8, fill=(190, 194, 210))
    cv.line([(vx + 17, vy), (vx + 36, vy - 10)], (200, 204, 220), 1.1)
    cv.line([(vx + 17, vy + 2), (vx + 32, vy + 12)], (200, 204, 220), 1.1)
    cv.rect(vx + 30, vy + 10, 6, 4, fill=(120, 124, 140))
    cv.rtext(vx - 18, vy - 12, "VOYAGER 1", SANS_B, 9, (255, 255, 255))
    cv.rtext(vx - 18, vy - 1, "launched 1977", SANS, 7.5, (180, 190, 230))
    # dimension bracket
    y0 = h * 0.60
    x0, x1 = ex + er + 10, w * 0.76
    cv.line([(x0, y0 - 4), (x0, y0 + 4)], GOLD, 1)
    cv.line([(x1, y0 - 4), (x1, y0 + 4)], GOLD, 1)
    cv.line([(x0, y0), (x1, y0)], GOLD, 1)
    cv.ctext((x0 + x1) / 2, y0 + 5, "1 LIGHT-DAY  ·  25.9 BILLION KM", SANS_B, 9.5, GOLD)
    cv.ctext((x0 + x1) / 2, y0 + 17, "a radio command sent today arrives tomorrow", SANS, 7.5, (210, 216, 245))
    cv.text(6, 5, "10:16 UTC · 18 NOV 2026", SANS_B, 7.5, (160, 170, 215))
    return cv


# --------------------------------------------------------------------------- grid art
def art_eu(w, h):
    cv = Canvas(w, h, bg=(22, 58, 160))
    cx, cy, r = w * 0.2, h * 0.5, h * 0.33
    for i in range(12):
        a = math.radians(-90 + i * 30)
        cv.star(cx + r * math.cos(a), cy + r * math.sin(a), 3.0, 1.3, GOLD)
    cv.text(w * 0.40, h * 0.12, "€45bn", SERIF_XB, 24, GOLD)
    cv.text(w * 0.41, h * 0.70, "LOAN TO UKRAINE · 2027", SANS_B, 7.5, (210, 220, 255))
    return cv


def art_drones(w, h):
    cv = Canvas(w, h, bg=(10, 12, 36))
    rnd = random.Random(5)
    for _ in range(30):
        cv.ell(rnd.random() * w, rnd.random() * h * 0.7, 0.6, 0.6, fill=(255, 255, 255))
    for i, (fx, fy, s) in enumerate(((0.80, 0.22, 5), (0.66, 0.40, 5.5), (0.86, 0.50, 4.5), (0.52, 0.26, 4.5), (0.40, 0.46, 5), (0.70, 0.66, 4))):
        drone(cv, w * fx, h * fy, s, (225, 228, 240))
    # explosions over city silhouette
    bx = 0
    while bx < w * 0.5:
        bw, bh = rnd.uniform(6, 12), rnd.uniform(8, 20)
        cv.rect(bx, h - bh, bw, bh, fill=(30, 30, 50))
        bx += bw + 2
    burst(cv, w * 0.17, h * 0.55, 8, (255, 140, 40))
    burst(cv, w * 0.17, h * 0.55, 4, (255, 240, 160))
    burst(cv, w * 0.31, h * 0.70, 5, (255, 140, 40))
    cv.rect(0, h - 11, w, 11, fill=(0, 0, 0))
    cv.ctext(w / 2, h - 10.5, "141 FIRED · 126 DOWNED · ODESA HIT", SANS_B, 7.5, (255, 255, 255))
    return cv


def art_senate(w, h):
    cv = Canvas(w, h, bg=(255, 255, 255))
    bw = w - 14
    bl = bw * 0.56
    cv.rect(7, 9, bl, 20, fill=(32, 80, 190))
    cv.rect(7 + bl, 9, bw - bl, 20, fill=(185, 36, 34))
    cv.text(12, 11.5, "56", SANS_B, 13, (255, 255, 255))
    cv.rtext(7 + bw - 5, 11.5, "44", SANS_B, 13, (255, 255, 255))
    cv.ctext(7 + bl, 13.5, "D | R", SANS_B, 8, (255, 255, 255))
    cv.line([(7 + bw / 2, 6), (7 + bw / 2, 32)], INK, 1)
    cv.text(7, 36, "US SENATE, JANUARY 2027", SANS_B, 7.5, GREY)
    cv.rtext(w - 7, 36, "AK FLIPS D", SANS_B, 7.5, (32, 80, 190))
    cv.star(w * 0.5, 46, 4, 1.7, (32, 80, 190))
    return cv


def art_cop(w, h):
    cv = Canvas(w, h, bg=(232, 243, 240))
    ex, ey, er = w * 0.22, h * 0.5, h * 0.33
    cv.ell(ex, ey, er, er, fill=(52, 128, 220))
    cv.ell(ex - er * 0.3, ey - er * 0.35, er * 0.42, er * 0.32, fill=(66, 170, 100))
    cv.ell(ex + er * 0.25, ey + er * 0.25, er * 0.35, er * 0.4, fill=(66, 170, 100))
    # torn draft paper
    px, py, pw, ph = w * 0.44, 7, w * 0.26, h - 14
    tear = [(px, py), (px + pw, py), (px + pw, py + ph), (px + pw * 0.75, py + ph * 0.9), (px + pw * 0.5, py + ph), (px + pw * 0.25, py + ph * 0.88), (px, py + ph)]
    cv.poly(tear, fill=(255, 255, 255), outline=(150, 150, 150), width=0.6)
    cv.text(px + 4, py + 3, "DRAFT", SANS_B, 7.5, RED)
    for i in range(4):
        cv.line([(px + 4, py + 16 + i * 6), (px + pw - 6, py + 16 + i * 6)], (170, 170, 170), 0.8)
    cv.line([(px + pw * 0.5, py), (px + pw * 0.5, py + ph)], (200, 60, 60), 0.9)
    # thermometer
    tx = w * 0.83
    cv.rrect(tx - 3, 7, 6, h - 24, 3, fill=(255, 255, 255), outline=RED, width=1)
    cv.rect(tx - 1.2, 16, 2.4, h - 34, fill=(220, 50, 40))
    cv.ell(tx, h - 13, 6, 6, fill=(220, 50, 40))
    cv.text(4, h - 11, "COP31 · ANTALYA", SANS_B, 7.5, GREY)
    return cv


def art_inflation(w, h):
    cv = Canvas(w, h, bg=(255, 255, 255))
    base = h - 12
    for cx, val, hh, c, lab in ((w * 0.30, "3.6%", 22, (110, 115, 125), "UK CPI"), (w * 0.70, "4.0%", 26, (32, 80, 190), "EURO AREA")):
        cv.rect(cx - 16, base - hh, 32, hh, fill=c)
        cv.ctext(cx, base - hh - 13, val, SANS_B, 11, INK)
        cv.ctext(cx, base + 1, lab, SANS_B, 7, GREY)
        cv.poly([(cx + 22, base - hh + 2), (cx + 26, base - hh - 5), (cx + 30, base - hh + 2)], fill=RED)
    cv.line([(8, base), (w - 8, base)], (120, 120, 120), 0.8)
    cv.text(5, 3, "OCT CPI, Y/Y", SANS_B, 7, GREY)
    return cv


def art_cyclone(w, h):
    cv = Canvas(w, h, bg=(176, 216, 232))
    proj = project((73.0, 8.6, 104.0, 19.6), (0, 0, w, h))
    for name in ("India", "Sri Lanka", "Bangladesh", "Myanmar"):
        draw_polys(cv, REGIONS[name], proj, (236, 222, 180), outline=(190, 170, 120), width=0.5)
    cx, cy = proj(85.4, 13.1)
    # track to Andhra coast
    lx, ly = proj(81.2, 16.2)
    cv.dashed((cx, cy), (lx, ly), (200, 40, 40), 1.2, 3, 2)
    cv.poly([(lx, ly), (lx + 5, ly + 3), (lx + 3, ly + 6)], fill=(200, 40, 40))
    # spiral
    for r, a0, a1 in ((13, 30, 330), (9, 200, 120), (5, 20, 300)):
        cv.arc(cx, cy, r, a0, a1, (255, 255, 255), 2.2)
    cv.ell(cx, cy, 2.5, 2.5, fill=(255, 255, 255))
    cv.ell(cx, cy, 15, 15, outline=(255, 255, 255), width=0.6)
    cv.text(6, h - 20, "INDIA", SANS_B, 7.5, (90, 80, 50))
    cv.text(cx + 16, cy - 4, "AKVAN", SANS_B, 7.5, (160, 20, 20))
    cv.text(cx + 16, cy + 5, "90–100 km/h", SANS, 6.5, (40, 40, 40))
    cv.text(cx - 20, h - 11, "BAY OF BENGAL", SANS_B, 7, (40, 90, 140))
    cv.text(lx - 40, ly - 16, "ANDHRA", SANS_B, 7, (90, 80, 50))
    return cv


def art_sudan(w, h):
    cv = Canvas(w, h)
    cv.vgrad(0, 0, w, h, (214, 170, 110), (240, 214, 160))
    rnd = random.Random(9)
    bx = 0
    while bx < w:
        bw, bh = rnd.uniform(14, 26), rnd.uniform(12, 24)
        cv.rect(bx, h - bh, bw, bh, fill=(130, 96, 50))
        bx += bw + rnd.uniform(2, 5)
    cv.poly([(w * 0.30, h), (w * 0.30, h * 0.35), (w * 0.33, h * 0.22), (w * 0.36, h * 0.35), (w * 0.36, h)], fill=(110, 80, 40))
    drone(cv, w * 0.72, h * 0.28, 6, (50, 40, 36))
    drone(cv, w * 0.90, h * 0.18, 4, (50, 40, 36))
    cx, cy = w * 0.55, h * 0.62
    cv.ell(cx, cy, 9, 9, outline=(190, 30, 30), width=1.2)
    cv.line([(cx - 13, cy), (cx + 13, cy)], (190, 30, 30), 1)
    cv.line([(cx, cy - 13), (cx, cy + 13)], (190, 30, 30), 1)
    cv.text(4, 3, "EL OBEID · NORTH KORDOFAN", SANS_B, 7.5, (70, 50, 30))
    chip(cv, w - 4, h - 4, "37 KILLED · 9 STRIKES", SANS_B, 7.5, fg=(255, 255, 255), bg=(150, 24, 24), right=True, top=True)
    return cv


def art_gold(w, h):
    cv = Canvas(w, h, bg=(253, 247, 228))
    # bars
    for i, (bx, by) in enumerate(((8, h - 14), (26, h - 14), (17, h - 24))):
        cv.poly([(bx, by + 10), (bx + 3, by), (bx + 19, by), (bx + 22, by + 10)], fill=(232, 182, 48), outline=(170, 120, 20), width=0.6)
    pts = [(w * 0.30, 10), (w * 0.44, 15), (w * 0.56, 12), (w * 0.70, 26), (w * 0.84, 34), (w * 0.93, 46)]
    cv.line(pts, (190, 30, 30), 2.2)
    ex, ey = pts[-1]
    cv.poly([(ex + 2, ey + 4), (ex - 9, ey + 1), (ex - 1, ey - 8)], fill=(190, 30, 30))
    cv.text(w * 0.44, 24, "$3,788", SERIF_XB, 15, INK)
    cv.text(w * 0.44, 44, "14-MONTH LOW", SANS_B, 7, (190, 30, 30))
    cv.text(4, 3, "SPOT GOLD", SANS_B, 7, GREY)
    return cv


def art_gta(w, h):
    cv = Canvas(w, h)
    cv.vgrad(0, 0, w, h * 0.7, (70, 20, 110), (255, 110, 90))
    cv.vgrad(0, h * 0.7, w, h * 0.3, (255, 150, 90), (30, 20, 50))
    cv.ell(w * 0.78, h * 0.46, 14, 14, fill=(255, 220, 120))
    for i in range(5):
        cv.line([(w * 0.60, h * (0.36 + i * 0.05)), (w * 0.96, h * (0.36 + i * 0.05))], (255, 110, 90), 1.0)
    cv.rect(0, h * 0.72, w, h * 0.28, fill=(22, 16, 40))
    # palms
    for px in (w * 0.08, w * 0.20, w * 0.90):
        cv.line([(px, h * 0.75), (px + 2, h * 0.30)], (22, 16, 40), 1.6)
        for a in range(-80, 100, 36):
            r = math.radians(a)
            cv.line([(px + 2, h * 0.30), (px + 2 + 9 * math.cos(r), h * 0.30 - 5 * math.sin(r) + 3)], (22, 16, 40), 1.6)
    # controller
    cx, cy, cw, ch = w * 0.33, h * 0.34, w * 0.30, h * 0.30
    cv.rrect(cx, cy, cw, ch, 5, fill=(245, 245, 250), outline=INK, width=0.8)
    cv.ell(cx + cw * 0.18, cy + ch * 0.5, 4, 4, outline=INK, width=0.8)
    for dx, dy in ((0.78, 0.3), (0.86, 0.5), (0.78, 0.7), (0.70, 0.5)):
        cv.ell(cx + cw * dx, cy + ch * dy, 1.8, 1.8, fill=INK)
    cv.text(4, 3, "GTA VI · 00:00 NZDT", SANS_B, 7.5, (255, 255, 255))
    cv.rtext(w - 4, h - 11, "13 YEARS AFTER GTA V", SANS_B, 7, (255, 220, 120))
    return cv


def art_horn(w, h):
    cv = Canvas(w, h, bg=(176, 216, 232))
    proj = project((33.0, 11.6, 49.0, 17.4), (0, 0, w, h))
    for name in ("Sudan", "South Sudan", "Kenya", "Somalia", "Somaliland", "Djibouti", "Yemen", "Saudi Arabia"):
        draw_polys(cv, REGIONS[name], proj, (236, 226, 196), outline=(200, 185, 150), width=0.4)
    draw_polys(cv, REGIONS["Ethiopia"], proj, (120, 180, 110), outline=(60, 110, 60), width=0.5)
    draw_polys(cv, REGIONS["Eritrea"], proj, (220, 120, 100), outline=(150, 60, 50), width=0.5)
    # troop markers either side of the border
    for lon, lat in ((38.2, 14.0), (39.4, 14.1), (37.2, 13.9)):
        x, y = proj(lon, lat)
        cv.poly([(x, y + 4), (x - 4, y + 4), (x, y - 3), (x + 4, y + 4)], fill=(20, 70, 30))
    for lon, lat in ((38.4, 15.2), (39.6, 15.0), (37.4, 15.3)):
        x, y = proj(lon, lat)
        cv.poly([(x, y - 4), (x - 4, y - 4), (x, y + 3), (x + 4, y - 4)], fill=(130, 20, 20))
    x, y = proj(39.0, 12.9)
    cv.text(x, y, "ETHIOPIA", SANS_B, 8, (20, 60, 25))
    x, y = proj(36.2, 16.9)
    cv.text(x, y, "ERITREA", SANS_B, 8, (120, 20, 20))
    x, y = proj(38.1, 13.4)
    cv.text(x, y, "TIGRAY", SANS, 6.5, (30, 50, 30))
    chip(cv, w - 4, 4, "1,000 KM BORDER", SANS_B, 7, fg=INK, bg=(255, 255, 255), right=True)
    return cv


ART = {"apec": art_apec, "gulf": art_gulf, "voyager": art_voyager, "eu": art_eu,
       "drones": art_drones, "senate": art_senate, "climate": art_cop, "inflation": art_inflation,
       "cyclone": art_cyclone, "elobeid": art_sudan, "gold": art_gold, "gta": art_gta,
       "horn": art_horn}


# --------------------------------------------------------------------------- page pieces
def kicker(cv, x, y, w, n, c, label, src=None, nsize=15, ksize=10):
    r = nsize / 2
    cv.ell(x + r, y + r, r, r, fill=c)
    cv.ctext(x + r, y + r - nsize * 0.40, str(n), SANS_B, nsize * 0.62, (255, 255, 255))
    cv.text(x + nsize + 5, y + r - ksize * 0.68, label, SANS_B, ksize, c)
    if src:
        cv.rtext(x + w, y + r - 9 * 0.68, src, SANS, 9, GREY)


def place_dots():
    """lat/lon for every story 1..39 (index places are approximate city/country centroids)."""
    return {
        1: (22.54, 114.06), 2: (29.35, 47.52), 4: (50.85, 4.35), 5: (46.48, 30.73), 6: (64.2, -152.0),
        7: (36.9, 30.7), 8: (51.5, -0.1), 9: (13.1, 85.4), 10: (13.18, 30.22), 11: (40.7, -74.0),
        12: (-41.3, 174.8), 13: (14.5, 38.5),
        14: (38.9, -77.0), 15: (37.57, 126.98), 16: (22.9, 114.5), 17: (22.2, 113.6), 18: (23.0, 113.3),
        19: (15.35, 44.2), 20: (31.8, 35.2), 21: (23.8, 90.4), 22: (-6.2, 106.8), 23: (33.6, 75.0),
        24: (19.8, 96.1), 25: (12.7, 28.4), 26: (-29.0, 25.0), 27: (1.4, 32.3), 28: (52.52, 13.4),
        29: (45.7, 26.6), 30: (45.07, 7.69), 31: (51.5, -0.1), 32: (40.7, -74.0), 33: (-33.45, -70.67),
        34: (-36.0, -71.5), 35: (4.7, -74.1), 36: (-25.0, 134.0), 37: (-17.7, 178.0), 38: (-21.2, -159.8),
        39: (-42.9, 147.3),
    }


def main():
    page = Canvas(W, H, bg=PAPER)
    cv = page
    X0, X1 = 18, 1006
    CW = X1 - X0
    meta = DATA["meta"]

    # ---- masthead
    cv.text(X0, 11, meta["kicker_left"], SANS_B, 13, RED)
    cv.rtext(X1, 11.5, meta["kicker_right"], SANS_B, 12, INK)
    cv.line([(X0, 29), (X1, 29)], INK, 0.8)
    title = meta["masthead"]
    for sz in (62, 60, 58, 56, 54):
        if cv.tw(title, DISPLAY, sz) <= CW:
            break
    cv.text(X0 - 2, 31, title, DISPLAY, sz, INK)
    cv.text(X0, 104, meta["subline"], SERIF_I, 13, (40, 40, 44))
    cv.line([(X0, 123), (X1, 123)], INK, 2.2)

    # ---- region strip
    sy = 128
    total = sum(c["w"] for c in DATA["continents"])
    sx = X0
    for c in DATA["continents"]:
        wdt = CW * c["w"] / total
        cv.rect(sx, sy, wdt - 1.5, 19, fill=col(c["color"]))
        cv.ctext(sx + wdt / 2, sy + 3.2, f'{c["name"]} {c["count"]}', SANS_B, 9.5, (255, 255, 255))
        sx += wdt

    # ---- heroes
    HY, AH = 154, 118
    gap = 12
    hw = (CW - 2 * gap) / 3
    for i, st in enumerate(DATA["heroes"]):
        hx = X0 + i * (hw + gap)
        art = ART[st["art"]](hw, AH)
        cv.paste(art, hx, HY)
        cv.rect(hx, HY, hw, AH, outline=INK, width=1.2)
        c = col(st["color"])
        kicker(cv, hx, HY + AH + 7, hw, st["n"], c, st["cat"], st.get("source"))
        used = cv.fit(hx, HY + AH + 26, hw, st["headline"], SERIF_XB, [20, 19, 18, 17], 1.12, 2)
        cv.fit(hx, HY + AH + 26 + used + 4, hw, st["dek"], SERIF, [11.5, 11, 10.5], 1.3, 3, (36, 36, 40))

    # ---- grid rows
    def row(y, items):
        gw = (CW - 4 * gap) / 5
        for i, st in enumerate(items):
            gx = X0 + i * (gw + gap)
            art = ART[st["art"]](gw, 58)
            cv.paste(art, gx, y)
            cv.rect(gx, y, gw, 58, outline=INK, width=1.0)
            c = col(st["color"])
            kicker(cv, gx, y + 63, gw, st["n"], c, st["cat"], nsize=13, ksize=9)
            used = cv.fit(gx, y + 79, gw, st["headline"], SERIF_B, [13.5, 13, 12.5], 1.12, 2)
            cv.fit(gx, y + 79 + used + 3, gw, st["dek"], SERIF, [10, 9.5, 9], 1.26, 2, (40, 40, 44))

    cv.line([(X0, 397), (X1, 397)], RULE, 0.6)
    row(404, DATA["grid"][:5])
    cv.line([(X0, 549), (X1, 549)], RULE, 0.6)
    row(556, DATA["grid"][5:])

    # ---- also section
    AY = 702
    cv.line([(X0, AY), (X1, AY)], INK, 2.2)
    cv.text(X0, AY + 5, meta["also_line"], SANS_B, 12.5, INK)
    cv.rtext(X1, AY + 6, "26 MORE STORIES · NUMBERS 14–39 ON THE MAP", SANS_B, 9, GREY)
    BY = AY + 26

    # map
    MX, MW, MH = X0, 310, 150
    sea = (206, 230, 240)
    mp = Canvas(MW, MH, bg=sea)
    proj = project((-176, -57, 188, 83), (0, 0, MW, MH))
    draw_polys(mp, WORLD, proj, (228, 216, 180), outline=(196, 182, 140), width=0.4)
    dots = place_dots()
    regcol = {s["n"]: col(s["color"]) for s in DATA["heroes"] + DATA["grid"] + DATA["list"]}
    for n in range(14, 40):
        lat, lon = dots[n]
        x, y = proj(lon, lat)
        mp.ell(x, y, 3.4, 3.4, fill=regcol[n], outline=(255, 255, 255), width=0.6)
    # numbered featured dots with light collision nudging
    nudge = {8: (-7, -7), 4: (3, 6), 5: (4, -5), 7: (-3, 7), 10: (-5, 1), 13: (5, 3), 2: (3, -3), 9: (2, 4)}
    for n in list(range(1, 3)) + list(range(4, 14)):
        lat, lon = dots[n]
        x, y = proj(lon, lat)
        dx, dy = nudge.get(n, (0, 0))
        if (dx, dy) != (0, 0):
            mp.line([(x, y), (x + dx, y + dy)], (255, 255, 255), 1.2)
        x, y = x + dx, y + dy
        mp.ell(x, y, 6.8, 6.8, fill=regcol[n], outline=(255, 255, 255), width=1)
        mp.ctext(x, y - 4.4, str(n), SANS_B, 7.5, (255, 255, 255))
    mp.text(6, 4, "WHERE IT HAPPENED", SANS_B, 9, INK)
    mp.text(6, 15, "big dots 1–13 · small dots 14–39", SANS, 7.5, GREY)
    chip(mp, 6, MH - 5, "3 = VOYAGER 1 · 25.9bn KM, OFF THE MAP", SANS_B, 8, top=True)
    cv.paste(mp, MX, BY)
    cv.rect(MX, BY, MW, MH, outline=INK, width=1.0)

    # stats 2x2 under the map
    SY = BY + MH + 8
    sw = MW / 2
    sh = 46
    for i, s in enumerate(DATA["stats"]):
        sx = MX + (i % 2) * sw
        yy = SY + (i // 2) * (sh + 4)
        tx = sx + (0 if i % 2 == 0 else 10)
        tw = sw - 14
        if i % 2 == 1:
            cv.line([(sx + 2, yy + 2), (sx + 2, yy + sh - 4)], RULE, 0.7)
        if i < 2:
            cv.line([(sx + (0 if i % 2 == 0 else 10), yy + sh), (sx + sw - 8, yy + sh)], RULE, 0.7)
        cv.text(tx, yy - 3, s["big"], DISPLAY2, 23, INK)
        cv.fit(tx, yy + 25, tw, s["label"], SANS, [8.5, 8], 1.2, 2, (50, 50, 54))

    # index: two columns
    IX = MX + MW + 14
    IW = X1 - IX
    ICW = (IW - 14) / 2
    items = DATA["list"]
    colA, colB = items[:13], items[13:]
    avail = (SY + 2 * sh + 4) - BY
    for sz in (10.5, 10, 9.5, 9):
        rowh = sz * 1.3 + 3.4

        def needs(coll):
            tot = 0
            for it in coll:
                full = it["place"] + ": " + it["text"]
                tot += len(cv.wrap(full, SERIF, sz, ICW - 20)) * sz * 1.3 + 3.4
            return tot
        if max(needs(colA), needs(colB)) <= avail:
            break
    spare = avail - max(needs(colA), needs(colB))
    extra = min(6.0, max(0.0, spare / 13))
    for ci, coll in enumerate((colA, colB)):
        cx = IX + ci * (ICW + 14)
        yy = BY + 1
        for it in coll:
            c = col(it["color"])
            cv.ell(cx + 7, yy + sz * 0.68, 7, 7, fill=c)
            cv.ctext(cx + 7, yy + sz * 0.68 - 4.3, str(it["n"]), SANS_B, 7.5, (255, 255, 255))
            place = it["place"] + ":"
            lines = cv.wrap(place + " " + it["text"], SERIF, sz, ICW - 20)
            ly = yy
            for li, ln in enumerate(lines):
                if li == 0 and ln.startswith(place):
                    cv.text(cx + 19, ly, place, SERIF_B, sz, INK)
                    cv.text(cx + 19 + cv.tw(place, SERIF_B, sz), ly, ln[len(place):], SERIF, sz, (30, 30, 34))
                else:
                    cv.text(cx + 19, ly, ln, SERIF, sz, (30, 30, 34))
                ly += sz * 1.3
            yy = ly + 3.4 + extra
        if ci == 0:
            cv.line([(cx + ICW + 7, BY), (cx + ICW + 7, SY + 2 * sh)], RULE, 0.6)

    # ---- footer
    FY = 996
    cv.line([(X0, FY), (X1, FY)], INK, 1.2)
    cv.text(X0, FY + 5, meta["footer_left"], SANS, 8.5, GREY)
    cv.rtext(X1, FY + 5, meta["footer_right"], SANS, 8.5, GREY)

    # frame
    cv.rect(0.5, 0.5, W - 1, H - 1, outline=INK, width=2.5)

    out = page.img.resize((W, H), Image.LANCZOS)
    out.save(OUT, optimize=True)
    print("saved", OUT, out.size, os.path.getsize(OUT), "bytes")


if __name__ == "__main__":
    main()
