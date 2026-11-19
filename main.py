#!/usr/bin/env python3
"""The Day in World News — Wednesday 18 November 2026.

Renders a 1024x1024 newspaper-style front page with Pillow at runtime.
Standard library + Pillow only, no network, deterministic output.
"""
import os
import math
from PIL import Image, ImageDraw, ImageFont

# --------------------------------------------------------------------------
# canvas + palette
# --------------------------------------------------------------------------
W = 1024                     # final size
S = 2                        # supersample factor (draw at 2048, downsample)
HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(HERE, "fonts")

PAPER = (247, 243, 232)
INK = (22, 22, 26)
INK2 = (60, 60, 66)
GREY = (120, 118, 112)
RULE = (170, 166, 156)
RED = (168, 32, 38)
GOLD = (196, 150, 50)

# region colours for the index + map dots
REGION = {
    "ASIA": (108, 54, 150),
    "MIDDLE EAST": (190, 100, 30),
    "EUROPE": (36, 78, 150),
    "AFRICA": (36, 120, 70),
    "AMERICAS": (170, 40, 46),
    "OCEANIA": (24, 120, 120),
    "GLOBAL": (80, 80, 86),
    "SPACE": (40, 40, 80),
}

FONT_FILES = {
    "head": "PlayfairDisplay-Bold.ttf",
    "head_bk": "PlayfairDisplay-Black.ttf",
    "body": "PTSerif-Regular.ttf",
    "body_b": "PTSerif-Bold.ttf",
    "body_i": "PTSerif-Italic.ttf",
    "label": "Inter-Bold.ttf",
}
_font_cache = {}


def font(name, size):
    key = (name, round(size * S))
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(os.path.join(FONT_DIR, FONT_FILES[name]), key[1])
    return _font_cache[key]


# --------------------------------------------------------------------------
# drawing helpers (all coordinates in final 1024 units; scaled by S inside)
# --------------------------------------------------------------------------
class Page:
    def __init__(self, w, h, bg=PAPER):
        self.w, self.h = w, h
        self.im = Image.new("RGB", (round(w * S), round(h * S)), bg)
        self.d = ImageDraw.Draw(self.im)

    # ---- primitives
    def line(self, pts, fill, width=1.0):
        self.d.line([(x * S, y * S) for x, y in pts], fill=fill, width=max(1, round(width * S)))

    def rect(self, x, y, w, h, fill=None, outline=None, width=1.0):
        self.d.rectangle([x * S, y * S, (x + w) * S, (y + h) * S], fill=fill, outline=outline,
                         width=round(width * S) if outline else 0)

    def rrect(self, x, y, w, h, r, fill=None, outline=None, width=1.0):
        self.d.rounded_rectangle([x * S, y * S, (x + w) * S, (y + h) * S], radius=r * S, fill=fill,
                                 outline=outline, width=round(width * S) if outline else 0)

    def ell(self, cx, cy, rx, ry, fill=None, outline=None, width=1.0):
        self.d.ellipse([(cx - rx) * S, (cy - ry) * S, (cx + rx) * S, (cy + ry) * S], fill=fill,
                       outline=outline, width=round(width * S) if outline else 0)

    def poly(self, pts, fill=None, outline=None, width=1.0):
        pts = [(x * S, y * S) for x, y in pts]
        if fill is not None:
            self.d.polygon(pts, fill=fill)
        if outline is not None:
            self.d.line(pts + [pts[0]], fill=outline, width=max(1, round(width * S)), joint="curve")

    def star(self, cx, cy, r_out, r_in, fill, rot=-90):
        pts = []
        for i in range(10):
            r = r_out if i % 2 == 0 else r_in
            a = math.radians(rot + i * 36)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
        self.poly(pts, fill=fill)

    def vgrad(self, x, y, w, h, c0, c1):
        n = max(2, round(h * S))
        for i in range(n):
            t = i / (n - 1)
            c = tuple(round(c0[k] + (c1[k] - c0[k]) * t) for k in range(3))
            yy = y * S + i
            self.d.line([(x * S, yy), ((x + w) * S, yy)], fill=c)

    def dashed(self, p0, p1, fill, width=1.0, dash=3.0, gap=2.0):
        (x0, y0), (x1, y1) = p0, p1
        L = math.hypot(x1 - x0, y1 - y0)
        if L == 0:
            return
        ux, uy = (x1 - x0) / L, (y1 - y0) / L
        t = 0.0
        while t < L:
            e = min(L, t + dash)
            self.line([(x0 + ux * t, y0 + uy * t), (x0 + ux * e, y0 + uy * e)], fill, width)
            t += dash + gap

    def paste(self, other, x, y):
        self.im.paste(other.im, (round(x * S), round(y * S)))

    # ---- text
    def tw(self, s, fname, size):
        return font(fname, size).getlength(s) / S

    def text(self, x, y, s, fname, size, fill=INK):
        self.d.text((x * S, y * S), s, font=font(fname, size), fill=fill)

    def text_r(self, x, y, s, fname, size, fill=INK):
        self.text(x - self.tw(s, fname, size), y, s, fname, size, fill)

    def text_c(self, cx, y, s, fname, size, fill=INK):
        self.text(cx - self.tw(s, fname, size) / 2, y, s, fname, size, fill)

    def caps(self, x, y, s, size, fill=INK, track=1.8, anchor="l"):
        """Inter Bold, uppercase, letter-spaced. Returns total width."""
        s = s.upper()
        f = font("label", size)
        widths = [f.getlength(ch) / S for ch in s]
        total = sum(widths) + track * (len(s) - 1)
        if anchor == "r":
            x -= total
        elif anchor == "c":
            x -= total / 2
        for ch, cw in zip(s, widths):
            self.d.text((x * S, y * S), ch, font=f, fill=fill)
            x += cw + track
        return total

    def wrap(self, s, fname, size, width):
        words = s.split()
        lines, cur = [], ""
        for w_ in words:
            t = (cur + " " + w_).strip()
            if self.tw(t, fname, size) <= width or not cur:
                cur = t
            else:
                lines.append(cur)
                cur = w_
        if cur:
            lines.append(cur)
        return lines

    def para(self, x, y, width, s, fname, sizes, leading, max_lines, fill=INK):
        """Draw wrapped text, trying sizes in order until it fits max_lines.
        Returns the height used."""
        if isinstance(sizes, (int, float)):
            sizes = [sizes]
        for sz in sizes:
            lines = self.wrap(s, fname, sz, width)
            if len(lines) <= max_lines:
                break
        else:
            lines = lines[:max_lines]
            print("WARNING: overflow:", s[:60])
        lh = sz * leading
        for i, ln in enumerate(lines):
            self.text(x, y + i * lh, ln, fname, sz, fill)
        return len(lines) * lh

    def finish(self):
        return self.im.resize((self.w, self.h), Image.LANCZOS)


class Lcg:
    """Tiny deterministic generator for star fields (no `random` module)."""

    def __init__(self, seed):
        self.s = seed & 0xFFFFFFFF

    def rand(self):
        self.s = (1103515245 * self.s + 12345) & 0x7FFFFFFF
        return self.s / 0x7FFFFFFF


def soft_shadow(pg, x, y, w, h):
    for i, a in ((3, (226, 222, 210)), (2, (214, 210, 198)), (1, (200, 196, 184))):
        pg.rect(x + i, y + i, w, h, fill=a)


# --------------------------------------------------------------------------
# content
# --------------------------------------------------------------------------
DATE_LINE = "Wednesday 18 November 2026"

HEROES = [
    {
        "region": "ASIA", "kicker": "APEC summit · Shenzhen", "source": "Reuters · AP",
        "headline": "Xi welcomes Trump to Shenzhen as the APEC summit opens",
        "dek": "Xi Jinping greeted Donald Trump at Bao'an airport on Wednesday morning ahead of the "
               "leaders' meeting that anchors this year's Asia-Pacific summit; trade and tariffs top "
               "their agenda.",
    },
    {
        "region": "MIDDLE EAST", "kicker": "Iran war · Gulf", "source": "Reuters",
        "headline": "US hits IRGC missile site on Qeshm; Iran drones target Kuwait base",
        "dek": "Iran says its drones targeted Patriot batteries at Ali Al-Salem Air Base in Kuwait. "
               "Bahrain intercepted several attacks; no major damage was reported.",
    },
    {
        "region": "SPACE", "kicker": "Space · Voyager 1", "source": "NASA",
        "headline": "Voyager 1 is the first human-made object a light-day from Earth",
        "dek": "Launched in 1977, it is now 25.9bn km away. A signal sent today arrives tomorrow.",
    },
]

NUMBERS = [
    ("25.9bn km", "Voyager 1 from Earth: one light-day"),
    ("€45bn", "EU loan proposed for Ukraine in 2027"),
    ("56–44", "Democratic Senate majority after Alaska"),
    ("$3,788", "gold per ounce, a 14-month low"),
    ("3.6% · 4.0%", "inflation, UK and euro area"),
    ("141", "Russian drones at Ukraine overnight, Kyiv says"),
]

# index: (region, place, lon, lat, summary)
def icon_globe(pg, cx, cy, r):
    pg.ell(cx, cy, r, r, outline=INK2, width=0.7)
    pg.ell(cx, cy, r * 0.45, r, outline=INK2, width=0.5)
    pg.line([(cx - r, cy), (cx + r, cy)], INK2, 0.5)


def icon_coin(pg, cx, cy, r):
    pg.ell(cx, cy, r, r, outline=INK2, width=0.7)
    pg.line([(cx - r * 0.5, cy), (cx + r * 0.5, cy)], INK2, 0.6)
    pg.line([(cx, cy - r * 0.5), (cx, cy + r * 0.5)], INK2, 0.6)


def icon_flask(pg, cx, cy, r):
    pg.poly([(cx - r * 0.35, cy - r), (cx + r * 0.35, cy - r), (cx + r * 0.35, cy - r * 0.2),
             (cx + r, cy + r), (cx - r, cy + r), (cx - r * 0.35, cy - r * 0.2)], outline=INK2, width=0.6)


def icon_trophy(pg, cx, cy, r):
    pg.poly([(cx - r * 0.8, cy - r), (cx + r * 0.8, cy - r), (cx + r * 0.5, cy + r * 0.2), (cx - r * 0.5, cy + r * 0.2)],
            outline=INK2, width=0.6)
    pg.line([(cx, cy + r * 0.2), (cx, cy + r * 0.8)], INK2, 0.6)
    pg.line([(cx - r * 0.5, cy + r), (cx + r * 0.5, cy + r)], INK2, 0.7)


INDEX = [
    ("World", icon_globe, [
        ("EUROPE", "Kyiv", 30.5, 50.4, "141 Russian drones overnight, 126 downed, Kyiv says; four killed in Odesa"),
        ("EUROPE", "Brussels", 4.4, 50.8, "Von der Leyen proposes a €45bn loan for Ukraine in 2027"),
        ("AMERICAS", "Alaska", -150, 64, "AP calls the Senate race for Mary Peltola; Democrats now 56–44"),
        ("AMERICAS", "Washington", -77, 38.9, "Democrats nominate Hakeem Jeffries for speaker, 251–11"),
        ("AFRICA", "El Obeid", 30.2, 13.2, "Amnesty: RSF drone strikes killed 37 civilians in nine attacks"),
        ("AFRICA", "Horn of Africa", 39.5, 13.5, "Reuters: Ethiopia and Eritrea mass troops along the border"),
        ("MIDDLE EAST", "Yemen", 44.2, 15.4, "Saudi-led coalition says it struck 60 Houthi targets"),
        ("MIDDLE EAST", "Jerusalem", 35.2, 31.8, "Katz says troops stay in Lebanon, Syria and Gaza buffer zones"),
        ("ASIA", "Shenzhen", 114.1, 22.5, "Japan's Takaichi makes her first China visit as prime minister"),
        ("ASIA", "Shenzhen", 114.1, 22.6, "Trump announces a US–Philippines trade deal; no terms given"),
        ("ASIA", "Dhaka", 90.4, 23.8, "Troops deployed as unrest over Hasina's verdict spreads"),
        ("ASIA", "Kashmir", 75.0, 33.7, "Indian forces say a senior LeT commander killed in Kulgam"),
        ("ASIA", "Kemerovo", 86.1, 55.4, "An-12 cargo plane crash kills all 19 aboard, Russia's MoD says"),
        ("ASIA", "Naypyidaw", 96.1, 19.8, "Myanmar junta says it will \"review\" its ties with ASEAN"),
        ("EUROPE", "Belgrade", 20.5, 44.8, "Serbian MiG-29 crashes on a training flight; pilot killed"),
        ("EUROPE", "London", -0.1, 51.5, "UK sanctions eight firms linked to West Bank settlements"),
        ("AFRICA", "Port Louis", 57.5, -20.2, "Mauritius sets the UK a deadline on the Chagos handover"),
        ("AMERICAS", "Caracas", -66.9, 10.5, "Opposition calls a 24-hour national strike"),
        ("AMERICAS", "Bogotá", -74.1, 4.7, "Hegseth visits to deepen military ties with Colombia"),
        ("MIDDLE EAST", "Gulf", 58.0, 24.0, "USS Theodore Roosevelt becomes the third US carrier in the region"),
        ("MIDDLE EAST", "Jerusalem", 35.3, 31.7, "Knesset elects Kahana as speaker, Israeli media report"),
        ("OCEANIA", "Canberra", 149.2, -35.2, "Australia sanctions West Bank settler groups alongside the UK"),
    ]),
    ("Economy & Markets", icon_coin, [
        ("EUROPE", "London", -0.1, 51.4, "UK inflation rises to 3.6%; core holds at 2.8%"),
        ("EUROPE", "Frankfurt", 8.7, 50.1, "Euro-area inflation hits 4.0%, driven by energy"),
        ("GLOBAL", "Gold", 0, 0, "Falls to about $3,788 an ounce, a 14-month low"),
        ("ASIA", "Seoul", 127, 37.5, "Kospi jumps 2.7% as chip stocks rally"),
        ("ASIA", "Jakarta", 106.8, -6.2, "Bank Indonesia raises its policy rate to 6.00%"),
        ("AMERICAS", "New York", -74, 40.7, "Anthropic expected to price its IPO tonight; debut Thursday"),
        ("AMERICAS", "Santiago", -70.7, -33.4, "ECLAC: Latin American poverty falls to 24.4%"),
        ("AMERICAS", "Chile", -70.7, -33.6, "Economy shrinks 1.1% in the third quarter"),
        ("AFRICA", "Pretoria", 28.2, -25.7, "South African inflation rises to 5.2%"),
        ("EUROPE", "Berlin", 13.4, 52.5, "Coalition cuts electricity tax to the EU minimum"),
        ("OCEANIA", "Canberra", 149.1, -35.3, "Wages rise 1.1% in the quarter"),
        ("AFRICA", "Kampala", 32.6, 0.3, "Uganda fast-tracks the EACOP oil pipeline"),
        ("MIDDLE EAST", "Hormuz", 56.5, 26.5, "ADNOC vessel hit; 11 injured, one missing, TASS reports"),
        ("GLOBAL", "Oil", 0, 0, "Brent trades near $92.6 a barrel after the Gulf attacks"),
    ]),
    ("Science, Climate & Tech", icon_flask, [
        ("GLOBAL", "Antalya", 30.7, 36.9, "COP31 draft text splits delegates on fossil-fuel wording"),
        ("ASIA", "Bay of Bengal", 85.4, 13.1, "Severe Cyclone Akvan heads for Andhra; landfall due 20 Nov"),
        ("OCEANIA", "Cook Islands", -159.8, -21.2, "Cyclone Xavier holds at Category 5"),
        ("OCEANIA", "Fiji", 178.4, -18.1, "National drought disaster declared"),
        ("EUROPE", "Vrancea", 26.5, 45.7, "M5.7 earthquake in Romania; two lightly hurt"),
        ("GLOBAL", "Apple", 0, 0, "Outage hits iCloud and App Store, users report"),
        ("AMERICAS", "Visa", -122.1, 37.5, "Confirms a cyberattack on its systems, reports say"),
        ("EUROPE", "Equinor", 5.7, 58.9, "Norwegian energy group reports a cyberattack"),
    ]),
    ("Culture & Sport", icon_trophy, [
        ("OCEANIA", "Auckland", 174.8, -36.9, "GTA VI goes on sale first in New Zealand, 11:00 UTC"),
        ("EUROPE", "Turin", 7.7, 45.1, "Alcaraz beats Medvedev at the ATP Finals"),
        ("OCEANIA", "Hobart", 147.3, -42.9, "England beat Australia to win the ODI series 2–1"),
    ]),
]
N_STORIES = len(HEROES) + sum(len(g[2]) for g in INDEX)

SOURCES = "Sources: Reuters · AP · NASA · European Commission · ONS · Eurostat · IMD · Amnesty · Ukraine Air Force · UK FCDO · ECLAC"


# --------------------------------------------------------------------------
# world map (coarse continent outlines, lon/lat, hand-drawn)
# --------------------------------------------------------------------------
CONTINENTS = [
    # North America
    [(-168, 66), (-160, 70), (-140, 70), (-125, 72), (-110, 73), (-95, 74), (-80, 73), (-70, 68),
     (-62, 60), (-65, 55), (-55, 52), (-60, 47), (-66, 44), (-70, 42), (-76, 36), (-81, 31),
     (-80, 25), (-84, 30), (-90, 29), (-97, 27), (-97, 22), (-92, 18), (-87, 21), (-88, 16),
     (-83, 10), (-78, 8), (-80, 9), (-85, 12), (-95, 16), (-105, 20), (-110, 24), (-114, 31),
     (-118, 34), (-124, 40), (-124, 48), (-130, 54), (-140, 60), (-152, 60), (-158, 57), (-165, 62)],
    # Greenland
    [(-55, 60), (-45, 60), (-40, 65), (-20, 70), (-20, 78), (-35, 83), (-60, 82), (-70, 78), (-60, 75), (-55, 68)],
    # South America
    [(-80, 9), (-75, 11), (-71, 12), (-62, 10), (-52, 5), (-50, 0), (-44, -2), (-35, -6), (-38, -13),
     (-40, -20), (-48, -26), (-52, -33), (-58, -38), (-65, -42), (-68, -50), (-72, -54), (-75, -48),
     (-73, -40), (-71, -30), (-70, -18), (-76, -14), (-81, -6), (-80, 0), (-78, 5)],
    # Eurasia
    [(-9, 43), (-9, 37), (-5, 36), (3, 43), (10, 44), (12, 38), (16, 39), (14, 45), (19, 42),
     (23, 36), (26, 40), (30, 41), (36, 36), (35, 33), (34, 28), (43, 13), (52, 17), (58, 23),
     (57, 26), (52, 30), (49, 28), (50, 25), (56, 24), (60, 25), (67, 24), (72, 20), (77, 8),
     (80, 15), (87, 22), (92, 22), (98, 10), (103, 2), (104, 8), (109, 12), (108, 21), (114, 22),
     (122, 28), (121, 32), (119, 36), (123, 40), (130, 42), (132, 44), (141, 53), (137, 55),
     (142, 59), (156, 51), (163, 56), (160, 60), (170, 60), (180, 66), (180, 71), (170, 70),
     (160, 70), (150, 72), (140, 73), (128, 73), (113, 74), (105, 78), (90, 76), (80, 73),
     (70, 73), (68, 69), (60, 69), (52, 68), (44, 68), (40, 66), (33, 69), (28, 71), (20, 70),
     (14, 67), (5, 62), (5, 58), (10, 59), (12, 56), (8, 57), (8, 54), (4, 52), (-2, 49),
     (-5, 48), (-2, 46), (-2, 44)],
    # Britain
    [(-5, 50), (1, 51), (2, 53), (-2, 56), (-5, 58), (-6, 56), (-3, 54), (-5, 52)],
    # Africa
    [(-17, 21), (-17, 15), (-14, 10), (-8, 5), (0, 5), (8, 4), (10, 2), (9, -2), (13, -6), (12, -15),
     (15, -25), (18, -34), (26, -34), (32, -28), (36, -20), (40, -15), (40, -10), (42, -2), (48, 3),
     (51, 11), (43, 12), (40, 16), (37, 20), (34, 28), (32, 31), (25, 32), (20, 31), (10, 37),
     (0, 36), (-6, 35), (-10, 30), (-15, 25)],
    # Madagascar
    [(44, -25), (47, -25), (50, -16), (49, -12), (44, -17)],
    # Australia
    [(114, -22), (114, -34), (118, -35), (124, -33), (132, -32), (137, -35), (140, -38), (147, -39),
     (150, -37), (153, -30), (153, -25), (146, -19), (142, -11), (137, -12), (136, -15), (130, -12),
     (126, -14), (122, -18)],
    # Japan
    [(130, 31), (135, 34), (140, 36), (142, 40), (141, 45), (145, 44), (142, 42), (140, 38), (137, 36), (133, 33)],
    # Sumatra, Borneo, New Guinea, New Zealand
    [(95, 5), (104, -5), (106, -6), (98, 2)],
    [(109, 1), (117, 7), (119, 0), (116, -4), (110, -3)],
    [(131, -1), (141, -2), (150, -6), (146, -8), (138, -8), (132, -4)],
    [(166, -46), (170, -46), (174, -41), (173, -35), (178, -38), (174, -40), (168, -44)],
]


def draw_world_map(pg, x, y, w, h):
    lon0, lon1, lat0, lat1 = -170, 180, 78, -56

    def proj(lon, lat):
        return (x + (lon - lon0) / (lon1 - lon0) * w, y + (lat0 - lat) / (lat0 - lat1) * h)

    pg.rect(x, y, w, h, fill=(226, 230, 232))
    for poly in CONTINENTS:
        pg.poly([proj(*p) for p in poly], fill=(204, 200, 188), outline=(178, 172, 158), width=0.5)
    return proj


# --------------------------------------------------------------------------
# hero illustrations
# --------------------------------------------------------------------------
def flag_us(pg, x, y, w, h):
    for i in range(13):
        pg.rect(x, y + i * h / 13, w, h / 13 + 0.05, fill=(178, 34, 52) if i % 2 == 0 else (255, 255, 255))
    cw, ch = w * 0.4, h * 7 / 13
    pg.rect(x, y, cw, ch, fill=(60, 59, 110))
    r = min(cw / 6, ch / 9) * 0.3
    for row in range(9):
        n = 6 if row % 2 == 0 else 5
        for k in range(n):
            sx = x + cw * ((k + 0.5) / 6 if n == 6 else (k + 1.0) / 6)
            pg.star(sx, y + ch * (row + 0.5) / 9, r, r * 0.45, (255, 255, 255))


def flag_cn(pg, x, y, w, h):
    pg.rect(x, y, w, h, fill=(222, 41, 16))
    pg.star(x + w * 0.17, y + h * 0.25, h * 0.15, h * 0.065, (255, 222, 0))
    for dx, dy in ((0.33, 0.10), (0.40, 0.22), (0.40, 0.38), (0.33, 0.50)):
        pg.star(x + w * dx, y + h * dy, h * 0.05, h * 0.022, (255, 222, 0))


def flag_on_pole(pg, x, base, H, kind, side):
    top = base - H
    pg.line([(x, base), (x, top)], (170, 164, 146), 1.5)
    pg.ell(x, top - 1.5, 1.8, 1.8, fill=(206, 172, 90))
    fw, fh = H * 0.42, H * 0.27
    fx = x + 1 if side > 0 else x - 1 - fw
    (flag_us if kind == "us" else flag_cn)(pg, fx, top + 2, fw, fh)


def figure(pg, x, base, H, hair, tie, suit, skin, swept=False):
    """Standing, forward-facing figure. Feet at (x, base); total height H."""
    hw = H * 0.165
    hr = H * 0.07
    sh_y = base - H * 0.75
    hem_y = base - H * 0.42
    # ground shadow
    pg.ell(x, base + 1.5, hw * 1.5, H * 0.02, fill=(205, 205, 206))
    # shoes + trousers
    for sgn in (-1, 1):
        lx = x + sgn * hw * 0.42
        pg.rrect(lx - hw * 0.30, base - H * 0.03, hw * 0.60, H * 0.03, H * 0.012, fill=(26, 26, 30))
        pg.rrect(lx - hw * 0.34, hem_y - H * 0.02, hw * 0.68, base - H * 0.03 - hem_y + H * 0.02, H * 0.01, fill=suit)
    # jacket
    pg.poly([(x - hw, sh_y + H * 0.01), (x + hw, sh_y + H * 0.01), (x + hw * 0.86, hem_y), (x - hw * 0.86, hem_y)], fill=suit)
    pg.ell(x - hw * 0.7, sh_y + H * 0.03, hw * 0.34, H * 0.03, fill=suit)
    pg.ell(x + hw * 0.7, sh_y + H * 0.03, hw * 0.34, H * 0.03, fill=suit)
    for sgn in (-1, 1):
        ax = x + sgn * hw * 0.98
        pg.rrect(ax - hw * 0.22, sh_y + H * 0.04, hw * 0.44, H * 0.30, hw * 0.2, fill=suit)
        pg.ell(ax + sgn * hw * 0.02, sh_y + H * 0.355, hw * 0.17, H * 0.022, fill=skin)
    # shirt, lapels, tie
    lap = tuple(min(255, c + 18) for c in suit)
    pg.poly([(x - hw * 0.36, sh_y + H * 0.01), (x + hw * 0.36, sh_y + H * 0.01), (x, sh_y + H * 0.17)], fill=(246, 246, 248))
    for sgn in (-1, 1):
        pg.poly([(x + sgn * hw * 0.40, sh_y + H * 0.005), (x + sgn * hw * 0.10, sh_y + H * 0.005),
                 (x + sgn * hw * 0.02, sh_y + H * 0.19), (x + sgn * hw * 0.16, sh_y + H * 0.17)], fill=lap)
    pg.poly([(x - hw * 0.085, sh_y + H * 0.02), (x + hw * 0.085, sh_y + H * 0.02), (x + hw * 0.07, sh_y + H * 0.20),
             (x, sh_y + H * 0.23), (x - hw * 0.07, sh_y + H * 0.20)], fill=tie)
    pg.rect(x - hw * 0.62, sh_y + H * 0.085, hw * 0.16, H * 0.012, fill=(246, 246, 248))
    pg.ell(x - hw * 0.30, sh_y + H * 0.11, hw * 0.045, hw * 0.045, fill=(214, 182, 96))
    # neck + head
    neck_y = sh_y - H * 0.02
    pg.rect(x - hr * 0.42, neck_y - H * 0.03, hr * 0.84, H * 0.06, fill=skin)
    hy = neck_y - hr * 1.15
    pg.ell(x - hr * 0.98, hy + hr * 0.1, hr * 0.16, hr * 0.26, fill=skin)
    pg.ell(x + hr * 0.98, hy + hr * 0.1, hr * 0.16, hr * 0.26, fill=skin)
    pg.ell(x, hy, hr, hr * 1.22, fill=skin)
    # hair
    bb = [(x - hr * 1.02) * S, (hy - hr * 1.34) * S, (x + hr * 1.02) * S, (hy + hr * 0.95) * S]
    if swept:
        pg.d.pieslice(bb, 185, 355, fill=hair)
        pg.poly([(x - hr, hy - hr * 0.25), (x - hr * 0.95, hy - hr * 0.85), (x + hr * 0.5, hy - hr * 1.1),
                 (x + hr * 0.95, hy - hr * 0.6), (x + hr * 0.5, hy - hr * 0.55), (x - hr * 0.3, hy - hr * 0.45)], fill=hair)
    else:
        bb[1] = (hy - hr * 1.26) * S
        pg.d.pieslice(bb, 190, 350, fill=hair)
        pg.poly([(x - hr * 0.98, hy - hr * 0.3), (x - hr * 0.9, hy - hr * 0.8), (x + hr * 0.3, hy - hr * 0.95),
                 (x + hr * 0.98, hy - hr * 0.55), (x + hr * 0.98, hy - hr * 0.3), (x + hr * 0.6, hy - hr * 0.55),
                 (x - hr * 0.2, hy - hr * 0.5)], fill=hair)
    # features
    ey = hy - hr * 0.05
    brow = (170, 140, 90) if swept else tuple(max(0, c - 10) for c in hair)
    for sgn in (-1, 1):
        pg.ell(x + sgn * hr * 0.38, ey, hr * 0.11, hr * 0.075, fill=(60, 48, 44))
        pg.line([(x + sgn * hr * 0.58, ey - hr * 0.28), (x + sgn * hr * 0.2, ey - hr * 0.24)], brow, hr * 0.07)
    pg.line([(x, ey + hr * 0.05), (x - hr * 0.07, ey + hr * 0.45), (x + hr * 0.08, ey + hr * 0.48)], (196, 150, 124), hr * 0.06)
    pg.line([(x - hr * 0.28, ey + hr * 0.78), (x, ey + hr * 0.84), (x + hr * 0.28, ey + hr * 0.78)], (160, 96, 90), hr * 0.07)


def art_lead(w, h):
    pg = Page(w, h)
    pg.vgrad(0, 0, w, h, (204, 214, 228), (236, 238, 240))
    hz = h * 0.80
    # faint skyline
    rnd = Lcg(2026)
    x = -4.0
    while x < w:
        bw = 7 + rnd.rand() * 16
        bh = 8 + rnd.rand() * 30
        pg.rect(x, hz - bh, bw, bh, fill=(212, 218, 231))
        if rnd.rand() > 0.5:
            pg.rect(x + bw * 0.3, hz - bh - 4, bw * 0.4, 4, fill=(212, 218, 231))
        x += bw + 1 + rnd.rand() * 4
    x = -2.0
    while x < w:                        # nearer, lighter layer
        bw = 10 + rnd.rand() * 20
        bh = 4 + rnd.rand() * 14
        pg.rect(x, hz - bh, bw, bh, fill=(222, 227, 236))
        x += bw + 2 + rnd.rand() * 6
    px = w * 0.17
    pg.poly([(px - 5, hz), (px - 3.5, h * 0.22), (px, h * 0.1), (px + 3.5, h * 0.22), (px + 5, hz)], fill=(206, 213, 226))
    # floor + carpet
    pg.vgrad(0, hz, w, h - hz, (222, 222, 224), (238, 238, 238))
    pg.line([(0, hz), (w, hz)], (200, 202, 208), 0.6)
    pg.poly([(w * 0.30, hz + 1), (w * 0.70, hz + 1), (w * 0.76, h), (w * 0.24, h)], fill=(168, 38, 46))
    pg.poly([(w * 0.31, hz + 1), (w * 0.69, hz + 1), (w * 0.75, h), (w * 0.25, h)], fill=(184, 46, 54))
    # rope stanchions along the carpet
    for sx in (w * 0.20, w * 0.80):
        pg.line([(sx, hz + 2), (sx, hz - 22)], (150, 140, 110), 1.2)
        pg.ell(sx, hz - 23, 2, 2, fill=(206, 172, 90))
        pg.ell(sx, hz + 2, 4, 1.3, fill=(150, 140, 110))
    for a, b in ((w * 0.20, w * 0.36), (w * 0.64, w * 0.80)):
        mid = ((a + b) / 2, hz - 13)
        pts = [((1 - t) ** 2 * a + 2 * (1 - t) * t * mid[0] + t ** 2 * b,
                (1 - t) ** 2 * (hz - 20) + 2 * (1 - t) * t * mid[1] + t ** 2 * (hz - 20)) for t in [k / 12 for k in range(13)]]
        pg.line(pts, (150, 40, 50), 1.0)
    base = h * 0.93
    H = h * 0.90
    cx = w * 0.5
    sep = H * 0.30
    flag_on_pole(pg, cx - sep - H * 0.5, base, H * 1.04, "us", +1)
    flag_on_pole(pg, cx + sep + H * 0.5, base, H * 1.04, "cn", -1)
    figure(pg, cx - sep, base, H, hair=(226, 196, 120), tie=(196, 30, 40), suit=(30, 34, 54), skin=(236, 198, 166), swept=True)
    figure(pg, cx + sep, base, H, hair=(34, 30, 32), tie=(120, 24, 40), suit=(28, 30, 44), skin=(228, 192, 156))
    return pg


GULF_ARABIA = [(47.6, 30.0), (47.98, 29.38), (48.2, 28.9), (48.5, 28.3), (48.8, 27.8), (49.6, 27.0),
               (50.1, 26.5), (50.2, 26.0), (50.5, 25.5), (50.8, 25.0), (50.8, 24.7), (51.0, 25.5),
               (51.05, 26.1), (51.3, 26.15), (51.6, 25.6), (51.55, 24.6), (51.3, 24.3), (52.0, 24.1),
               (53.5, 24.1), (54.4, 24.4), (55.0, 25.0), (55.4, 25.35), (56.0, 25.85), (56.4, 26.4),
               (56.4, 25.6), (56.35, 24.9), (56.6, 24.4), (57.5, 23.7), (58.6, 23.6), (59.5, 22.6),
               (59.5, 20.0), (46.0, 20.0), (46.0, 29.6)]
GULF_IRAQ = [(46.0, 33.0), (46.0, 29.6), (47.6, 30.0), (47.98, 29.38), (48.5, 29.9), (48.6, 30.5),
             (48.0, 31.2), (47.2, 32.4)]
GULF_IRAN = [(48.6, 30.5), (48.5, 29.9), (49.2, 30.4), (49.6, 30.0), (50.2, 29.5), (50.8, 28.9),
             (51.3, 27.9), (52.6, 27.4), (53.6, 26.9), (54.9, 26.5), (55.8, 26.8), (56.3, 27.15),
             (56.9, 26.6), (57.1, 25.8), (57.8, 25.6), (59.5, 25.4), (59.5, 33.0), (47.2, 32.4),
             (48.0, 31.2)]
GULF_QESHM = [(55.3, 26.6), (55.9, 26.85), (56.28, 27.0), (56.2, 26.85), (55.8, 26.7), (55.4, 26.5)]
GULF_BAHRAIN = [(50.45, 26.25), (50.62, 26.25), (50.62, 25.8), (50.5, 25.85)]


def art_gulf(w, h):
    pg = Page(w, h, bg=(14, 32, 64))
    lon0, lon1, lat0, lat1 = 46.6, 59.0, 31.2, 23.0

    def proj(lon, lat):
        return ((lon - lon0) / (lon1 - lon0) * w, (lat0 - lat) / (lat0 - lat1) * h)

    for lon in range(47, 59, 2):
        pg.line([proj(lon, 20), proj(lon, 34)], (22, 44, 80), 0.4)
    for lat in range(24, 32, 2):
        pg.line([proj(45, lat), proj(60, lat)], (22, 44, 80), 0.4)
    pg.poly([proj(*p) for p in GULF_ARABIA], fill=(66, 82, 108), outline=(96, 114, 146), width=0.5)
    pg.poly([proj(*p) for p in GULF_IRAQ], fill=(72, 86, 104), outline=(96, 114, 146), width=0.5)
    pg.poly([proj(*p) for p in GULF_IRAN], fill=(86, 72, 88), outline=(124, 108, 132), width=0.5)
    pg.poly([proj(*p) for p in GULF_BAHRAIN], fill=(96, 110, 136))
    pg.poly([proj(*p) for p in GULF_QESHM], fill=(130, 106, 120))
    # events
    kx, ky = proj(47.5, 29.3)
    qx, qy = proj(55.9, 26.75)
    bx, by = proj(50.55, 26.05)
    for r_, c_ in ((7, (255, 130, 50)), (4, (255, 220, 120))):
        pg.star(kx, ky, r_, r_ * 0.45, c_)
    for r_, c_ in ((6.5, (255, 255, 255)), (3.5, (255, 90, 60))):
        pg.star(qx, qy, r_, r_ * 0.45, c_)
    pg.ell(bx, by, 4, 4, outline=(255, 255, 255), width=1.0)
    pg.ell(bx, by, 1.4, 1.4, fill=(255, 255, 255))
    # drone track from Iran toward Kuwait
    ix, iy = proj(51.2, 28.6)
    pg.dashed((ix, iy), (kx + 4, ky + 1), (255, 180, 100), 1.0, 2.5, 2)
    # labels
    lab = (190, 204, 226)
    pg.caps(*proj(53.0, 29.6), "Iran", 7.5, (236, 226, 240), track=1.2)
    pg.caps(*proj(47.0, 31.0), "Iraq", 6.0, lab, track=1.0)
    pg.caps(*proj(47.0, 25.0), "Saudi Arabia", 6.5, lab, track=1.0)
    pg.caps(*proj(53.2, 24.0), "UAE", 6.0, lab, track=1.0)
    pg.caps(kx + 9, ky - 4, "Kuwait", 6.5, (255, 255, 255), track=1.0)
    pg.caps(qx - 2, qy + 6, "Qeshm", 6.5, (255, 255, 255), track=1.0, anchor="r")
    pg.caps(bx - 6, by - 3, "Bahrain", 6.5, (255, 255, 255), track=1.0, anchor="r")
    pg.caps(*proj(51.4, 26.9), "The Gulf", 6.0, (130, 160, 210), track=1.4)
    return pg


def art_voyager(w, h):
    pg = Page(w, h, bg=(8, 10, 30))
    rnd = Lcg(1977)
    # Milky Way band (diagonal), then stars
    for i in range(26):
        t = i / 25
        k = 1 - abs(t - 0.5) * 2
        c = tuple(round(8 + (24 - 8) * k * j) for j in (1, 1.1, 2.4))
        off = (t - 0.5) * w * 0.5
        cx0 = w * 0.55 + off
        pg.poly([(cx0 - w * 0.02 - h * 0.45, h + 2), (cx0 + w * 0.02 - h * 0.45, h + 2),
                 (cx0 + w * 0.02 + h * 0.45, -2), (cx0 - w * 0.02 + h * 0.45, -2)], fill=c)
    for _ in range(90):
        sx, sy = rnd.rand() * w, rnd.rand() * h
        r = (0.35, 0.5, 0.7, 0.9)[int(rnd.rand() * 4)]
        pg.ell(sx, sy, r, r, fill=((255, 255, 255), (200, 210, 255), (255, 240, 220))[int(rnd.rand() * 3)])
    # Earth
    ex, ey, er = w * 0.22, h * 0.76, h * 0.16
    pg.ell(ex, ey, er * 1.25, er * 1.25, fill=(24, 56, 112))
    pg.ell(ex, ey, er, er, fill=(50, 120, 220))
    pg.ell(ex - er * 0.35, ey - er * 0.35, er * 0.42, er * 0.3, fill=(70, 180, 110))
    pg.ell(ex + er * 0.3, ey + er * 0.2, er * 0.35, er * 0.45, fill=(70, 180, 110))
    pg.d.chord([(ex - er) * S, (ey - er) * S, (ex + er) * S, (ey + er) * S], 318, 42, fill=(30, 78, 160))
    pg.ell(ex - er * 0.5, ey - er * 0.58, er * 0.15, er * 0.09, fill=(255, 255, 255))
    # probe
    vx, vy = w * 0.78, h * 0.24
    pg.dashed((ex + er * 0.7, ey - er * 0.7), (vx - 10, vy + 6), (160, 175, 240), 0.9, 2.5, 2.5)
    pg.ell(vx, vy, 9, 9, outline=(235, 238, 248), width=1.3)
    pg.ell(vx, vy, 6.5, 6.5, fill=(60, 64, 90), outline=(235, 238, 248), width=0.9)
    pg.ell(vx, vy, 2.2, 2.2, fill=(235, 238, 248))
    pg.rect(vx + 7, vy - 3, 5, 6, fill=(190, 194, 210))
    pg.line([(vx + 12, vy), (vx + 26, vy - 8)], (200, 204, 220), 0.9)
    pg.line([(vx + 12, vy + 2), (vx + 24, vy + 10)], (200, 204, 220), 0.9)
    pg.caps(vx - 12, vy - 14, "Voyager 1", 6.5, (255, 255, 255), track=1.0, anchor="r")
    pg.caps(ex + er + 4, ey + 4, "Earth", 6.5, (200, 214, 255), track=1.0)
    return pg


# --------------------------------------------------------------------------
# page composition
# --------------------------------------------------------------------------
X0, X1 = 24, 1000
CW = X1 - X0


def kicker(pg, x, y, w, region, label, source=None, size=8.5):
    c = REGION[region]
    pg.rect(x, y + 1, 3, size + 2, fill=c)
    pg.caps(x + 8, y, label, size, c, track=1.7)
    if source:
        pg.caps(x + w, y + 1, source, 7, GREY, track=1.3, anchor="r")


def hrule(pg, y, weight=0.8, color=RULE, x0=X0, x1=X1):
    pg.line([(x0, y), (x1, y)], color, weight)


def render():
    pg = Page(W, W)

    # ---- masthead
    pg.caps(X0, 16, "Vol. I · No. 322", 8, GREY, track=2.0)
    pg.caps(X1, 16, f"{N_STORIES} stories · six continents · one day", 8, GREY, track=2.0, anchor="r")
    pg.text_c(W / 2, 22, "The Day in World News", "head_bk", 52)
    pg.text_c(W / 2, 92, "Everything on this page happened, or was first reported, on this one day.", "body_i", 14, INK2)
    hrule(pg, 118, 0.8)
    pg.caps(W / 2, 126, DATE_LINE, 19, INK, track=4.5, anchor="c")
    hrule(pg, 155, 2.0, INK)
    hrule(pg, 158.5, 0.8, INK)

    # ---- hero zone
    HY, HB = 170, 452
    gap = 14
    LW = round((CW - gap) * 0.6)
    RX = X0 + LW + gap
    RW = X1 - RX
    lead = HEROES[0]
    LAH = 154
    soft_shadow(pg, X0, HY, LW, LAH)
    pg.paste(art_lead(LW, LAH), X0, HY)
    pg.rect(X0, HY, LW, LAH, outline=INK, width=1.0)
    ty = HY + LAH + 9
    kicker(pg, X0, ty, LW, lead["region"], lead["kicker"], lead["source"], 9)
    used = pg.para(X0, ty + 17, LW, lead["headline"], "head", [29, 28, 27, 26, 25], 1.08, 2)
    pg.para(X0, ty + 17 + used + 5, LW, lead["dek"], "body", [12, 11.5, 11], 1.3, 2, INK2)

    RH = (HB - HY - gap) / 2
    AW = 150
    for i, st in enumerate(HEROES[1:]):
        y = HY + i * (RH + gap)
        art = (art_gulf if i == 0 else art_voyager)(AW, RH)
        soft_shadow(pg, RX, y, AW, RH)
        pg.paste(art, RX, y)
        pg.rect(RX, y, AW, RH, outline=INK, width=1.0)
        tx = RX + AW + 10
        tw = X1 - tx
        kicker(pg, tx, y + 1, tw, st["region"], st["kicker"], st["source"], 8)
        used = pg.para(tx, y + 18, tw, st["headline"], "head", [16, 15, 14, 13.5], 1.1, 3)
        dh = pg.para(tx, y + 18 + used + 5, tw, st["dek"], "body", [10.5, 10, 9.5], 1.28, 3, INK2)
        dek_end = y + 18 + used + 5 + dh
        if i == 0:
            hrule(pg, y + RH + gap / 2, 0.6, RULE, RX, X1)
        else:
            # distance scale: Earth -> Neptune (4.5bn km) -> Voyager 1 (25.9bn km)
            sy = y + RH - 12
            if dek_end + 14 > sy:
                print("WARNING: Voyager scale bar collides with dek")
            sx0, sx1 = tx, X1 - 2
            pg.line([(sx0, sy), (sx1, sy)], INK2, 0.6)
            for v, name, anchor in ((0, "", "l"), (4.5, "Neptune 4.5bn", "l"), (25.9, "Voyager 1 · 25.9bn km", "r")):
                px = sx0 + (sx1 - sx0) * v / 25.9
                pg.line([(px, sy - 3), (px, sy + 3)], INK2, 0.6)
                if name:
                    pg.caps(px + 2 if anchor == "l" else px, sy + 5, name, 5.5, INK2, track=0.8, anchor=anchor)
            pg.ell(sx0 + (sx1 - sx0) * 4.5 / 25.9, sy, 1.5, 1.5, fill=INK2)
            pg.ell(sx1, sy, 1.8, 1.8, fill=REGION["SPACE"])
            pg.caps(sx0, sy - 11, "distance from Earth, drawn to scale", 5.5, GREY, track=0.8)

    # ---- numbers strip
    NY = HB + 12
    hrule(pg, NY, 1.6, INK)
    pg.caps(X0, NY + 8, "Today's numbers", 8.5, INK, track=2.2)
    pg.caps(X1, NY + 8, "verified figures from the day's reporting", 7, GREY, track=1.5, anchor="r")
    n = len(NUMBERS)
    cw = CW / n
    for i, (big, lab) in enumerate(NUMBERS):
        x = X0 + i * cw
        if i:
            pg.line([(x - 8, NY + 26), (x - 8, NY + 70)], RULE, 0.6)
        pg.text(x, NY + 24, big, "head", 23)
        bw = pg.tw(big, "head", 23)
        if big.startswith("$"):           # gold: down marker
            pg.poly([(x + bw + 6, NY + 34), (x + bw + 13, NY + 34), (x + bw + 9.5, NY + 41)], fill=RED)
        if big.startswith("3.6"):          # inflation: two tiny bars, same scale
            bx = x + bw + 8
            for k, (v, c) in enumerate(((3.6, (36, 78, 150)), (4.0, (36, 78, 150)))):
                hh = v * 5.5
                pg.rect(bx + k * 9, NY + 47 - hh, 6, hh, fill=c if k else (120, 140, 180))
            pg.line([(bx - 2, NY + 47), (bx + 17, NY + 47)], INK2, 0.5)
        pg.para(x, NY + 54, cw - 18, lab, "body", [9.5, 9], 1.2, 2, INK2)
    hrule(pg, NY + 80, 0.8)

    # ---- index
    IY = NY + 92
    pg.caps(X0, IY, "Also on Wednesday 18 November", 9, INK, track=2.2)
    pg.caps(X1, IY + 1, "more stories by region and topic", 7, GREY, track=1.5, anchor="r")
    hrule(pg, IY + 16, 0.6)
    # map column
    MX, MY, MW = X0, IY + 26, 300
    MH = round(MW * 134 / 350)
    pg.caps(MX, MY, "Where it happened", 7.5, INK2, track=1.8)
    proj = draw_world_map(pg, MX, MY + 13, MW, MH)
    pg.rect(MX, MY + 13, MW, MH, outline=RULE, width=0.6)
    dots = []
    for _, _, group in INDEX:
        for region, place, lon, lat, _ in group:
            if lon == 0 and lat == 0:
                continue
            dots.append((proj(lon, lat), REGION[region]))
    for (px, py), c in dots:
        pg.ell(px, py, 2.6, 2.6, fill=(255, 255, 255))
        pg.ell(px, py, 1.9, 1.9, fill=c)
    # hero markers
    for k, (lon, lat) in enumerate(((114.1, 22.5), (56.3, 26.8))):
        px, py = proj(lon, lat)
        pg.ell(px, py, 6, 6, fill=(255, 255, 255))
        pg.ell(px, py, 5, 5, fill=INK)
        pg.caps(px, py - 3.2, str(k + 1), 6.5, (255, 255, 255), track=0, anchor="c")
    # legend
    ly = MY + 13 + MH + 8
    lx = MX
    for name in ("ASIA", "MIDDLE EAST", "EUROPE", "AFRICA", "AMERICAS", "OCEANIA"):
        pg.ell(lx + 3, ly + 4, 2.4, 2.4, fill=REGION[name])
        wdt = pg.caps(lx + 9, ly, name, 6, INK2, track=1.0)
        lx += 9 + wdt + 9
    # text columns: flow A (under the map) -> B -> C
    FOOT = 992
    colw_bc = (X1 - (X0 + MW + 22) - 20) / 2
    cols = [
        (MX, ly + 16, MW, FOOT),
        (X0 + MW + 22, MY, colw_bc, FOOT),
        (X0 + MW + 22 + colw_bc + 20, MY, colw_bc, FOOT),
    ]
    pg.line([(cols[1][0] - 11, MY), (cols[1][0] - 11, FOOT - 6)], RULE, 0.5)
    pg.line([(cols[2][0] - 10, MY), (cols[2][0] - 10, FOOT - 6)], RULE, 0.5)
    ci = 0
    x, y, cw_, yend = cols[ci]
    ROW = 14.4
    SZ = 10

    def next_col():
        nonlocal ci, x, y, cw_, yend
        ci += 1
        if ci >= len(cols):
            print("WARNING: index overflow - drop a story")
            ci = len(cols) - 1
            return
        x, y, cw_, yend = cols[ci]

    def header(name, icon):
        nonlocal y
        if y + 17 + 2 * ROW > yend:
            next_col()
        icon(pg, x + 5, y + 5, 4.2)
        pg.caps(x + 14, y, name, 7.5, INK2, track=1.8)
        hrule(pg, y + 11, 0.5, RULE, x, x + cw_)
        y += 17

    for gname, icon, items in INDEX:
        header(gname, icon)
        for region, place, lon, lat, text in items:
            pl = place + ": "
            pw = pg.tw(pl, "body_b", SZ)
            lines = pg.wrap(text, "body", SZ, cw_ - 10 - pw)
            need = ROW * len(lines)
            if y + need > yend:
                next_col()
                header(gname + " (cont.)", icon)
            pg.ell(x + 3, y + 6, 2.2, 2.2, fill=REGION[region])
            pg.text(x + 10, y, pl, "body_b", SZ)
            pg.text(x + 10 + pw, y, lines[0], "body", SZ, INK2)
            y += ROW
            for ln in lines[1:]:
                pg.text(x + 10, y, ln, "body", SZ, INK2)
                y += ROW
        y += 7

    # ---- footer
    hrule(pg, 996, 0.8)
    pg.text(X0, 1001, "Claims by warring parties are attributed. Illustrations original; map outlines schematic.", "body", 8.5, GREY)
    pg.text_r(X1, 1001, SOURCES, "body", 8.5, GREY)
    return pg.finish()


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "news-image-20261118.png")
    im = render()
    assert im.size == (1024, 1024)
    im.save(path, format="PNG", optimize=True, compress_level=9)
    print("wrote", path, os.path.getsize(path), "bytes")


if __name__ == "__main__":
    main()
